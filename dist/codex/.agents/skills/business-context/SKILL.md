---
name: business-context
description: Ask non-technical builders plain-language business questions and translate their answers into technical requirements (service tier, data classification, access, scale, integrations, compliance). Use whenever a technical decision depends on information you don't have, before designing something new, or when you're tempted to ask the builder a technical question.
---

# Business context

Technical decisions need facts that only the builder knows — but the builder
thinks in terms of users, information and business impact, not tiers,
classifications or protocols. This skill turns one into the other.

## Rules

- **Infer first.** Read the request, README and `docs/production-handoff.md`.
  Only ask what you can't infer and what would change what you build *now*.
- **At most three questions at a time**, ideally one. Ask the rest later, when
  they matter, or leave them as defaults.
- **Plain language, simple choices, a default.** Use the wording in
  `references/question-bank.md`. Offer 3–4 options plus "not sure".
- **"Not sure" is a fine answer.** Use the default, and record it as an
  assumption to confirm before production.
- **Never ask the technical question directly.** Not "which database?",
  "REST or events?", "do you need SSO?" — ask the business question behind it.
- **Don't re-ask.** Everything answered or assumed goes into the production
  handoff (via the `production-handoff` skill), which is the memory for later
  sessions.

## Process

1. Pick the questions you need from `references/question-bank.md` (Q1–Q8).
   Q1, Q3 and Q4 drive the most decisions; start there if nothing is known.
2. Ask in one short message with lettered options and the default marked,
   e.g. "(a) just my team — default".
3. Translate each answer with the table in `references/question-bank.md`
   into technical requirements (tier, classification, access model, scale,
   integration and compliance needs) — with the standard IDs.
4. Record both the business answer (in the builder's words) and the derived
   requirements in the production handoff's *Business context* and *Derived
   requirements* sections, marking each as **Confirmed** (the builder said so)
   or **Assumed** (default used).
5. Continue building. Don't explain the derived requirements to the builder.
