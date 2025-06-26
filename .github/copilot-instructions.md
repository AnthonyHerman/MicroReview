# Copilot Instructions for MicroRevie

Welcome! This repository powers **MicroReview**, a modular, explainable AI code review GitHub App. Please follow these instructions to ensure generated code, documentation, or configuration aligns with project goals, architecture, and best practices.

---

## 🌟 Purpose of This Repo

- Automate pull request (PR) reviews using "micro-agents" (each enforcing a single code policy) powered by LLMs via DSPy.
- Aggregate all agent findings into a single, clear, actionable PR comment.
- Be language-agnostic and easily extensible.
- Integrate as a GitHub App configurable via `.microreview.yml`.

---

## 🧩 Architecture Principles

- **Micro-agents:** Each policy is a small, focused DSPy module with an explicit prompt/output contract.
- **Structured Outputs:** Agents must output structured reasoning, finding, and confidence.
- **Synthesis:** All agent outputs are aggregated and deduplicated before posting a PR comment.
- **Configuration:** Users customize which agents run and how results are displayed via `.microreview.yml`.
- **GitHub App:** All user interaction is via PR comments; the app updates its own comment to avoid clutter.

---

## 📝 Coding Guidelines

- **Add new agents as DSPy modules under `agents/`**. Each agent should:
  - Take relevant PR context (diff, files, etc.) as input.
  - Output findings as a list of objects: `{reasoning, finding, confidence}`.
  - Be language-agnostic unless a specific language is required.
- **Use clear, focused prompts** within agents. Avoid ambiguity.
- **Respect the `.microreview.yml`** config (agent enables, thresholds, grouping, etc.).
- **Synthesize comments** as Markdown, grouping findings by file or category as configured.
- **Test agents** using sample diffs and edge cases.

---

## 🛠️ When Generating Code or Config

- Favor clarity and explicitness over magic.
- Make all new agents opt-in (not enabled by default).
- Provide docstrings and inline comments.
- Ensure all new config options are documented in the README and `.microreview.yml` example.
- Update tests and documentation if relevant.

---

## 🔒 Security & Privacy

- Never log or persist user code outside PR context.
- Only use PR context and minimal repo metadata for analysis.
- Never introduce output that exposes secrets or proprietary data.

---

## 🚦 Review/PR Process

- All bot-generated PRs should update the synthesized review comment, never spam additional comments.
- Link to agent reasoning in PR comments where possible.
- Ensure all outputs are actionable and low-noise.

---

## 🙏 Documentation

- Update the README and /docs for any new features, agents, or configuration options.
- Add usage examples as needed.

---

**Thank you for contributing to MicroReview!**
