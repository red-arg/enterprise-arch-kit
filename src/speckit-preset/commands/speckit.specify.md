## Enterprise Rules for Specifications (read first)

The person describing this feature is usually **not a software engineer**.
The spec captures business value only; the agents decide all technology
later from the enterprise standards.

1. **No technology in the spec.** No languages, frameworks, databases,
   hosting, APIs or code structure — even if the builder mentions them. If
   they named a technology, capture the *outcome* they want (e.g. "data is
   kept after restarts") and note the preference for the technical team in
   `docs/production-handoff.md` §7.
2. **Fill the Business Context section.** Infer what you can from the
   description. Use the wording and defaults in the `business-context`
   skill's question bank (Q1–Q8). Mark each row Confirmed or Assumed.
3. **[NEEDS CLARIFICATION] markers must be business questions** taken from
   the question bank (prefer Q1 who uses it, Q3 what information, Q5 other
   systems), phrased in everyday words with simple options and the default
   marked as recommended. Never mark a technical choice as needing
   clarification — technical gaps are resolved during planning from the
   standards.
4. **Communicate in plain language.** In your completion report to the
   builder, summarize what the feature will let people do; don't mention
   branches, scripts, templates or IDs unless asked.
5. **Seed the production handoff.** After the spec is written, create or
   update `docs/production-handoff.md` §1 (summary) and §2 (business
   context, linking this spec) using the `production-handoff` skill, or ask
   the `handoff_scribe` agent to do it.
