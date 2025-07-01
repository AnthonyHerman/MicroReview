# Natural Language Code Policies (NLCP) Implementation Guide

## Overview

MicroReview implements **Natural Language Code Policies (NLCPs)** instead of complex regex patterns.

## Why NLCPs over Regex?

### The Problem with Regex-Based Approaches
- **Brittle**: Regex patterns break with minor syntax changes
- **Limited**: Can't understand context or intent
- **Maintenance Nightmare**: Each new edge case requires a new pattern
- **False Positives**: Rigid patterns trigger on legitimate code

### The NLCP Advantage
- **Context-Aware**: LLMs understand code context and intent
- **Flexible**: Handles variations in syntax and style
- **Extensible**: Easy to add new policies without pattern complexity
- **Fewer False Positives**: Better understanding of test vs. production code

## NLCP Structure

Each NLCP consists of two key components:

### 1. Policy Question
A clear, specific question about what to detect:
```
"Does this change introduce hard-coded credentials such as passwords, API keys, tokens, or secret access keys?"
```

### 2. Policy Background
Detailed context explaining:
- Why this is a security concern
- What patterns to look for
- How to assess severity
- What to include/exclude

```
Hard-coding credentials directly into source code poses a serious security risk. These secrets can be inadvertently leaked, stored in version control, or exposed during logging or error handling...
```

## Available NLCPs in MicroReview

### Security Policies

1. **Hard-Coded Credentials Detection**
   - Detects embedded passwords, API keys, tokens
   - Context-aware (distinguishes test vs. production)
   - File path and line number reporting

2. **PII/PHI Exposure Detection**
   - Identifies personal information in code/logs
   - GDPR/HIPAA compliance focus
   - Logging exposure detection

3. **GitHub Actions Security**
   - Untrusted action usage
   - Secrets exposure in workflows
   - Privilege escalation risks

### Additional NLCPs (Ready to Implement)

Common security policies that can be implemented:

- **New API Endpoint Authorization**
- **Third Party Scripts Detection**
- **Logging Sensitive Data**
- **Username Enumeration Flaws**
- **Token Validation Logic**
- **Insecure File Upload Handling**
- **Improper Error Handling**
- **CORS Configuration Issues**
- **Inter-Service Communication Security**
- **Insecure Deserialization**

## Implementation Pattern

### DSPy Agent Structure
```python
class SecurityAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        
        # NLCP Definition
        self.policy_question = "Does this code...?"
        self.policy_background = "Context explaining the risk..."
    
    def forward(self, diff: str, file_path: str = ""):
        # Construct prompt with NLCP
        prompt = f"""
        POLICY: {self.policy_question}
        BACKGROUND: {self.policy_background}
        
        ANALYZE: {diff}
        
        Provide structured findings with reasoning and confidence.
        """
        
        # Use LLM to analyze
        response = dspy.Predict("reasoning, findings")(prompt=prompt)
        return self._structure_response(response)
```

### Fallback Implementation
For testing without LLM access, each agent includes simplified heuristics:

```python
def _fallback_analysis(self, diff: str, file_path: str):
    """Simple heuristics when LLM unavailable"""
    # Basic pattern matching as backup
    # Much simpler than full regex approach
```

## Configuration

Enable/disable NLCPs in `.microreview.yml`:

```yaml
enabled_agents:
  - HardCodedCredsAgent
  - PiiExposureAgent
  - GitHubActionsSecurityAgent

agent_config:
  HardCodedCredsAgent:
    confidence_threshold: 0.8
    max_findings: 5
```

## Benefits of This Approach

1. **Reduced False Positives**: LLMs understand context better than regex
2. **Easier Maintenance**: Natural language policies vs. complex patterns
3. **Better Reasoning**: Explicit explanations for each finding
4. **Extensible**: Add new policies without regex expertise
5. **Language Agnostic**: Works across programming languages

## Migration from Regex

The transition from regex-based to NLCP-based detection:

### Before (Regex)
```python
patterns = [
    r'(?i)(password|pwd|pass)\s*[:=]\s*["\'][^"\']{8,}["\']',
    r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\'][^"\']{16,}["\']',
    # 50+ more complex patterns...
]
```

### After (NLCP)
```python
policy_question = "Does this change introduce hard-coded credentials?"
policy_background = "Clear explanation of the security risk..."
# LLM handles the complexity
```

## Best Practices

1. **Clear Policy Questions**: Be specific about what to detect
2. **Rich Background Context**: Explain why it matters and what to look for
3. **Confidence Scoring**: Let the LLM assess likelihood
4. **Fallback Mechanisms**: Simple heuristics for when LLM unavailable
5. **Test Coverage**: Include test cases for edge cases

This approach aligns with the blog's key insights:
- ✅ **Explicit Reasoning**: Each finding includes detailed explanation
- ✅ **Specialized Micro-Agents**: One NLCP per security concern
- ✅ **Reduced Noise**: Better context understanding = fewer false positives
