# Phase 0: Pre-Flight & Design Setup

In the design phase, we lay out the core specifications and guidelines of the cold outreach assistant before writing a single line of code.

## Core Accomplishments & Learnings:
1. **Human-in-the-Loop (HITL) Policy**: Outlined that outreach emails must never be sent blindly. A manual keyboard stroke from the operator must validate each message.
2. **Safety by Default**: Defined `DRY_RUN=true` as the default state. This acts as a circuit-breaker so no live network requests are attempted during student builds and live demos.
3. **Email Anatomy Rules**: Established the structural requirements for a high-converting, professional cold email:
   * **Subject Line**: Targeted, short, and opportunity-specific.
   * **Personalization Hook**: Opening line utilizing specific company or recruiter details to show authenticity.
   * **Relevant Introduction**: Concise introduction of the sender's background.
   * **Value & Fit Statement**: Connecting candidate skills directly to target role requirements.
   * **Low-Friction Ask**: Exactly one call-to-action (e.g. advice, directions, or portfolio reviews).
4. **Word Constraints**: Limited the outreach body to strictly less than 150 words to maintain readability and increase response rates.
