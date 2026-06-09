# Phase 3: Generator & Formatting Engine

In this phase, we write the programmatic template parsing engine and implement the strict word-count guardrails.

## Core Accomplishments & Learnings:
1. **Deterministic Template Rendering**: Developed `email_generator.py` with custom placeholder interpolation to dynamically assemble recipient names, value hooks, portfolio URLs, and roles into a highly-spaced cold email body.
2. **fallback Management**: Handled potential missing fields (such as a missing recipient name or missing portfolio URL) gracefully using dictionary `.get()` fallbacks.
3. **Safety word-Count Validator**: Implemented a string splitting token count check. If the generated outreach exceeds the strict **150-word constraint**, a clear warning logs to the console to flag potential spam blocks or low-converting copy before it can be processed.
