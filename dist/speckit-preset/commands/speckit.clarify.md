---
description: Identify underspecified business facts in the current feature spec by asking up to 3 plain-language business questions, deriving technical requirements without asking the builder.
handoffs:
  - label: Build Technical Plan
    agent: speckit.plan
    prompt: Create the technical plan for this spec from the enterprise standards.
---

## Enterprise Rules for Clarification (read first — these override the steps below where they conflict)

The builder is usually **not a software engineer**. Clarification is about
business facts only.

1. **Only ask business questions.** Use the `business-context` skill's
   question bank (Q1–Q8) for wording, options and defaults. Valid topics:
   who uses it, how many and how often, what information it handles, impact
   if it stops, other systems or data it needs, lifespan, rules to follow,
   ownership — plus functional behaviour, user journeys, edge cases and
   business rules in the builder's own terms.
2. **Never ask about** technology, architecture, protocols, hosting,
   performance numbers, observability, authentication mechanisms, data
   formats or any "technical constraints & tradeoffs". For the taxonomy
   categories *Non-Functional Quality Attributes*, *Integration & External
   Dependencies* and *Constraints & Tradeoffs*, ask the business question
   behind them (Q2, Q3, Q4, Q5, Q7) and derive the technical requirement
   yourself with the question bank's mapping table.
3. **At most 3 questions** in total (not 5). If more facts are unclear, use
   the defaults, mark them **Assumed** in the spec's Business Context section
   and add them to `docs/production-handoff.md` §9 as open business questions.
4. **Recommended option = the question bank default** unless the spec clearly
   implies otherwise. Explain "why it matters" in business terms (cost,
   users affected, risk), never technical terms.
5. **Record derived requirements, not technical questions.** After each
   answer, update the spec's Business Context row (Confirmed) and, in plain
   language, any affected requirement or success criterion. Technical
   consequences go to the plan and the production handoff §3, not the spec.
6. **Completion report to the builder:** plain language only. The technical
   coverage table, if produced, is for the agents — keep it out of the message
   to the builder unless they ask.
