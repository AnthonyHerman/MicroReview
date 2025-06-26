"""
MicroReview Agents Package

This package contains all the DSPy micro-agents (NLCPs - Natural Language Code Policies)
that analyze code and produce structured findings.

Each agent should:
- Be a DSPy module with explicit input/output contracts
- Take PR context (diff, files, etc.) as input
- Output findings as structured objects: {reasoning, finding, confidence}
- Be language-agnostic unless specific language support is required
- Be opt-in (not enabled by default)
"""