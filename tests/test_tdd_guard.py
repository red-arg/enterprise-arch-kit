"""Tests for src/skills/tdd/scripts/tdd_guard.py (run: python3 -m unittest discover tests)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

GUARD = Path(__file__).resolve().parent.parent / "src" / "skills" / "tdd" / "scripts" / "tdd_guard.py"


def run(args: list[str], cwd: Path, stdin: str = "", env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(GUARD), *args], cwd=cwd, input=stdin, text=True,
                          capture_output=True, env={**os.environ, **(env or {})})


def junit(path: Path, cases: dict[str, str]) -> None:
    """cases: {"file::name": "passed|failed|error|skipped[:message]"}"""
    path.mkdir(parents=True, exist_ok=True)
    rows = []
    for tid, outcome in cases.items():
        cls, name = tid.split("::")
        status, _, msg = outcome.partition(":")
        child = {"failed": f'<failure message="{msg}"/>', "error": f'<error message="{msg}"/>',
                 "skipped": "<skipped/>"}.get(status, "")
        rows.append(f'<testcase classname="{cls}" name="{name}">{child}</testcase>')
    (path / "junit.xml").write_text(f"<testsuites><testsuite>{''.join(rows)}</testsuite></testsuites>")


class HookTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def decide(self, role: str, tool: str, **tool_input) -> str:
        if "file_path" in tool_input:
            tool_input["file_path"] = str(self.root / tool_input["file_path"])
        data = json.dumps({"tool_name": tool, "tool_input": tool_input})
        rc = run(["hook", role], self.root, data, {"CLAUDE_PROJECT_DIR": str(self.root)}).returncode
        return "block" if rc == 2 else "allow"

    def test_test_writer_cannot_read_implementation(self):
        self.assertEqual(self.decide("test-writer", "Read", file_path="src/modules/leave/domain/rules.ts"), "block")
        self.assertEqual(self.decide("test-writer", "Read", file_path="src/main/java/x/leave/adapters/Pg.java"), "block")
        self.assertEqual(self.decide("test-writer", "Bash", command="cat src/modules/leave/application/a.ts"), "block")
        self.assertEqual(self.decide("test-writer", "Bash", command="git diff HEAD~1"), "block")
        self.assertEqual(self.decide("test-writer", "Grep", pattern="approve"), "block")
        # Nothing behind the public interface: domain, ports, adapters, nested index files, entry code.
        for path in ("src/modules/leave/ports/repo.ts", "src/modules/leave/domain/index.ts",
                     "src/modules/leave/application/submit.ts", "app/main.py",
                     "apps/api/src/main.ts", "src/main/java/x/App.java"):
            self.assertEqual(self.decide("test-writer", "Read", file_path=path), "block", path)
        self.assertEqual(self.decide("test-writer", "Bash", command="grep -rn approve src"), "block")

    def test_test_writer_can_read_spec_tests_and_public_interfaces(self):
        for path in ("specs/001-leave/spec.md", "specs/001-leave/plan.md",
                     "test/functional/leave.test.ts", "docs/production-handoff.md",
                     "src/modules/leave/index.ts", "src/modules/leave/__init__.py",
                     "apps/api/src/modules/leave/index.ts", "src/modules/leave/public/LeaveRequests.java",
                     "src/app/test-app.ts", "app/test_app.py", "src/test/java/x/LeaveFunctionalTest.java"):
            self.assertEqual(self.decide("test-writer", "Read", file_path=path), "allow", path)
        self.assertEqual(self.decide("test-writer", "Grep", pattern="x", path="test"), "allow")
        self.assertEqual(self.decide("test-writer", "Grep", pattern="x", path="specs"), "allow")
        self.assertEqual(self.decide("test-writer", "Bash", command="npx vitest run test/functional"), "allow")

    def test_test_writer_writes_only_tests(self):
        self.assertEqual(self.decide("test-writer", "Write", file_path="test/leave/new.test.ts"), "allow")
        self.assertEqual(self.decide("test-writer", "Write", file_path="tests/test_leave.py"), "allow")
        self.assertEqual(self.decide("test-writer", "Write", file_path="src/modules/leave/index.ts"), "block")

    def test_implementer_cannot_touch_tests(self):
        for path in ("test/leave/a.test.ts", "tests/test_leave.py", "src/test/java/x/LeaveTest.java",
                     "src/modules/leave/a.spec.ts", "leave/rules_test.go"):
            self.assertEqual(self.decide("implementer", "Edit", file_path=path), "block", path)
        self.assertEqual(self.decide("implementer", "Bash", command="rm test/leave/a.test.ts"), "block")
        self.assertEqual(self.decide("implementer", "Bash", command="sed -i 's/5/3/' tests/test_leave.py"), "block")

    def test_implementer_can_change_code_and_run_tests(self):
        self.assertEqual(self.decide("implementer", "Edit", file_path="src/modules/leave/application/a.ts"), "allow")
        self.assertEqual(self.decide("implementer", "Edit", file_path="specs/001-leave/plan.md"), "allow")
        self.assertEqual(self.decide("implementer", "Bash", command="npx vitest run"), "allow")

    def test_malformed_hook_input_fails_open(self):
        self.assertEqual(run(["hook", "implementer"], self.root, "not json").returncode, 0)


class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for args in (["init", "-q", "-b", "main"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
            subprocess.run(["git", *args], cwd=self.root, check=True)
        (self.root / ".gitignore").write_text(".tdd/\n")
        (self.root / "tests").mkdir()
        (self.root / "tests" / "test_leave.py").write_text("def test_x(): pass\n")
        subprocess.run(["git", "add", "-A"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "red"], cwd=self.root, check=True)
        self.red = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.root, capture_output=True,
                                  text=True).stdout.strip()
        junit(self.root / ".tdd/before", {"tests/test_smoke.py::smoke": "passed"})

    def tearDown(self):
        self.tmp.cleanup()

    def red_gate(self, cases: dict[str, str]) -> subprocess.CompletedProcess:
        junit(self.root / ".tdd/after", cases)
        return run(["verify-red", "--before", ".tdd/before", "--after", ".tdd/after"], self.root)

    def test_red_passes_when_every_new_test_fails_on_behaviour(self):
        r = self.red_gate({"tests/test_smoke.py::smoke": "passed",
                           "tests/test_leave.py::rejects": "failed:NotImplementedError"})
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_red_flags_a_vacuous_test(self):
        r = self.red_gate({"tests/test_leave.py::rejects": "failed:NotImplementedError",
                           "tests/test_leave.py::mock_returns_mock": "passed"})
        self.assertEqual(r.returncode, 1)
        self.assertIn("VACUOUS", r.stdout)

    def test_red_flags_tests_that_cannot_load(self):
        r = self.red_gate({"tests/test_leave.py::rejects": "error:ModuleNotFoundError: No module named leave"})
        self.assertIn("WRONG REASON", r.stdout)
        self.assertEqual(r.returncode, 1)

    def test_red_accepts_failures_against_not_implemented_stubs(self):
        r = self.red_gate({"tests/test_leave.py::rejects": "failed:NotImplementedError: submit_leave"})
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_red_requires_new_tests(self):
        r = self.red_gate({"tests/test_smoke.py::smoke": "passed"})
        self.assertEqual(r.returncode, 1)

    def green_gate(self) -> subprocess.CompletedProcess:
        junit(self.root / ".tdd/green", {"tests/test_leave.py::rejects": "passed"})
        return run(["verify-green", "--since", self.red, "--results", ".tdd/green"], self.root)

    def test_green_passes_when_tests_untouched_and_passing(self):
        self.assertEqual(self.green_gate().returncode, 0)

    def test_green_fails_when_a_test_is_edited_or_added(self):
        (self.root / "tests" / "test_leave.py").write_text("def test_x(): assert True\n")
        self.assertIn("tests/test_leave.py", self.green_gate().stdout)
        subprocess.run(["git", "checkout", "-q", self.red, "--", "tests/test_leave.py"], cwd=self.root, check=True)
        (self.root / "tests" / "test_more.py").write_text("def test_y(): pass\n")
        r = self.green_gate()
        self.assertEqual(r.returncode, 1)
        self.assertIn("tests/test_more.py", r.stdout)

    def test_green_ignores_build_artefacts(self):
        (self.root / "tests" / "__pycache__").mkdir()
        (self.root / "tests" / "__pycache__" / "test_leave.cpython-312.pyc").write_bytes(b"\0")
        self.assertEqual(self.green_gate().returncode, 0)

    def test_green_fails_when_a_test_fails(self):
        junit(self.root / ".tdd/green", {"tests/test_leave.py::rejects": "failed:assert 3 == 1"})
        r = run(["verify-green", "--since", self.red, "--results", ".tdd/green"], self.root)
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
