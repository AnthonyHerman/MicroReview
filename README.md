# MicroReview

**MicroReview** is a modular, explainable, and policy-driven AI code review system for GitHub pull requests. Powered by [DSPy](https://github.com/stanfordnlp/dspy), it uses “micro-agents”—each focused on a single code policy (NLCP)—to deliver actionable, low-noise, and trustworthy feedback, all synthesized into a single PR review comment.

---

> **Status: Alpha – Experimental**  
> MicroReview is under active development and may have breaking changes, bugs, or incomplete features. Not recommended for production use yet.

---

## 🧩 Key Features

- **Micro-agent Architecture:** Each NLCP (Natural Language Code Policy) is enforced by a dedicated DSPy module.
- **Language-Agnostic by Default:** Works across most programming languages; add language-specific agents as needed.
- **Structured Output:** Each agent returns explicit reasoning, findings, and confidence—making results explainable and filterable.
- **Provider-Agnostic:** Supports OpenAI, Anthropic, and other major LLMs via simple configuration.
- **Extensible:** Easily add new policies as your org’s risks and needs evolve.
- **Low Noise, High Trust:** Explicit reasoning and confidence scores reduce false positives and boost developer trust.
- **Hybrid Context:** Agents may analyze PR diffs, relevant files, or full-repo code (with optional retrieval/expansion for business logic checks).
- **Single Synthesized PR Comment:** All agent findings are aggregated, deduplicated, and summarized into one well-formatted review comment for each pull request.
- **GitHub App Integration:** Easily installable as a GitHub App for automated PR review across repositories.

---

## 👩‍💻 Example Micro-Agents (NLCPs)

- **Hard-Coded Credentials Detection:** Flags possible secrets in code.
- **PHI/PII Exposure:** Detects leaks of sensitive user data.
- **GitHub Actions Policy:** Reviews workflow file changes for security risks.
- **Duplication Agent:** Warns of code copied from elsewhere in the repo.
- **Documentation Completeness:** Checks for missing or inadequate docs on new code.

---

## 🚦 How It Works

1. **On Pull Request:**  
   The GitHub App triggers all relevant micro-agents, passing in the PR diff and context.
2. **Agent Review:**  
   Each DSPy agent analyzes the code according to its policy, producing structured findings:
   ```json
   {
     "reasoning": "Variable 'API_KEY' assigned a string literal on line 12.",
     "finding": "Possible hard-coded credential.",
     "confidence": 0.93
   }
   ```
3. **Aggregation & Synthesis:**  
   The system aggregates all findings, deduplicates them, and synthesizes them into a single, concise, and readable review comment. MicroReview updates its comment if re-run, preventing duplicate bot noise.
4. **Developer Experience:**  
   - Only actionable, well-explained comments appear.
   - Links to reasoning allow developers to trust, learn from, and debug the system.

---

## 🏗️ Architecture Overview

```
[ GitHub PR Event ]
        |
        v
[ Preprocessing: Diff, context extraction ]
        |
        v
[ NLCP Micro-Agents (DSPy Modules) ]
    |      |      |      |
    v      v      v      v
 [ Structured Findings ]
        |
        v
[ Aggregation, Deduplication & Synthesis ]
        |
        v
[ Single PR Review Comment ]
```

---

## ⚙️ Agent Example (DSPy)

```python
import dspy
from dspy import InputField, OutputField

class HardCodedCredsAgent(dspy.Module):
    diff = InputField()
    findings = OutputField(desc="File path and line number for any hard-coded credentials, with reasoning and confidence.")

    def forward(self, diff):
        prompt = (
            "You are a code security reviewer. Examine the following code diff for any instances of hard-coded credentials "
            "such as passwords, API keys, tokens, or secret access keys. For each finding, output a JSON object with 'reasoning', 'finding', and 'confidence' (0-1).\n\n"
            f"Code diff:\n{diff}"
        )
        findings = self.llm(prompt)
        return {"findings": findings}
```

---

## 🌐 Multi-Provider Support

Configure your LLM provider (OpenAI, Anthropic, etc.) in one place:
```python
import dspy
dspy.configure(lm=dspy.LM("anthropic/claude-3-sonnet-20240229"))
# or
dspy.configure(lm=dspy.LM("openai/gpt-4o"))
```

---

## 🚀 Getting Started

1. **Clone this repo**
2. **Install requirements:** `uv sync`
3. **Configure your LLM API key and provider**
4. **Run the main review pipeline on your PR diff**
5. **Add/modify agents as needed by editing the `agents/` directory**

---

## ⚙️ Configuration: `.microreview.yml` Options

You can control MicroReview’s behavior per-repository via a `.microreview.yml` file in your repo root.  
**Example:**

```yaml
enabled_agents:
  - HardCodedCredsAgent
  - PiiExposureAgent
confidence_threshold: 0.9          # Only include findings above this confidence
group_by: "category"               # Group results by 'file', 'category', or 'none'
max_findings_per_agent: 5          # Maximum findings to report per agent
exclude_paths:
  - tests/
  - docs/
comment_mode: "update"             # "update": update one comment, "append": post new each time
```

**Available options:**
- `enabled_agents`: List of agent/module names to run on PRs.
- `confidence_threshold`: Float between 0 and 1; only findings above this are shown.
- `group_by`: How to group results in the PR comment (`file`, `category`, or `none`).
- `max_findings_per_agent`: Cap number of comments per agent.
- `exclude_paths`: Paths or globs to skip.
- `comment_mode`: Whether to update a single comment or append new ones.

---

## 📝 Sample Output: Synthesized PR Review Comment

````markdown
#### 🤖 MicroReview Automated Code Review

**Summary:**  
3 potential issues found across 2 files.  
_This is an automated micro-agent review. Please address blocking issues before merging._

---

**🔒 Security**

- `src/api/user.js`  
  - **Hard-coded API key on line 46.**  
    > Reasoning: Detected assignment to `API_KEY` with a string literal.  
    > Confidence: 0.92

**📄 Documentation**

- `src/api/user.js`  
  - **Missing docstring for `getUserProfile`.**  
    > Reasoning: New function lacks docstring.  
    > Confidence: 0.87

**🌀 Duplication**

- `src/utils/helpers.js`  
  - **Duplicated code detected (matches `src/api/user.js` lines 22–30).**  
    > Reasoning: Code block is nearly identical to another location.  
    > Confidence: 0.91

---

*To learn more about MicroReview or suggest new policies, [visit our docs](#).*
