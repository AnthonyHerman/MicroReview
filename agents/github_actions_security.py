"""
GitHub Actions Security Agent

This DSPy micro-agent analyzes GitHub Actions workflow changes
for security risks and misconfigurations.
"""

import re
import yaml
from typing import List, Dict, Any

# Temporarily mock dspy for testing without external dependencies
class MockDSPyModule:
    """Mock DSPy module for testing without dependencies."""
    def __init__(self):
        pass

try:
    import dspy
    DSPyBase = dspy.Module
except ImportError:
    # Fallback for testing without dspy
    dspy = None
    DSPyBase = MockDSPyModule


class GitHubActionsSecurityAgent(DSPyBase):
    """
    DSPy agent for detecting security risks in GitHub Actions workflows.
    
    Based on security best practices, this agent identifies:
    - Untrusted or mutable third-party actions
    - Secrets exposure risks
    - Unsafe run commands
    - Privilege escalation risks
    - Insecure pull_request_target usage
    """
    
    def __init__(self):
        super().__init__()
        
        # Risk patterns for GitHub Actions
        self.security_patterns = {
            "untrusted_action": [
                r'uses:\s*[^@\s]+(?:@(?:main|master|develop|latest))?(?:\s|$)',  # No specific version
                r'uses:\s*[^@\s]+@[a-f0-9]{7}(?:\s|$)',  # Short commit hash
            ],
            "secrets_exposure": [
                r'echo\s+\$\{\{\s*secrets\.',  # Echo secrets
                r'env:\s*[^:]+:\s*\$\{\{\s*secrets\.',  # Secrets in env
                r'run:.*secrets\.',  # Secrets in run commands
            ],
            "unsafe_run": [
                r'run:.*\$\{\{\s*github\.event\.pull_request\.title',  # Unsafe PR title usage
                r'run:.*\$\{\{\s*github\.event\.pull_request\.body',   # Unsafe PR body usage
                r'run:.*\$\{\{\s*github\.event\.head_commit\.message', # Unsafe commit message
                r'shell:\s*bash.*-c.*\$\{',  # Potential shell injection
            ],
            "privilege_escalation": [
                r'permissions:\s*write-all',  # Overly broad permissions
                r'contents:\s*write',         # Write access to repo
                r'actions:\s*write',          # Write access to actions
                r'GITHUB_TOKEN.*trigger',     # Token misuse
            ],
            "pull_request_target": [
                r'on:\s*pull_request_target',  # High-risk trigger
                r'pull_request_target:.*types:.*\[.*opened.*\]',  # Risky PR target
            ]
        }
        
        # Known secure action patterns
        self.trusted_publishers = [
            'actions/',
            'github/',
            'microsoft/',
            'azure/',
            'docker/',
        ]
    
    def forward(self, diff: str, file_path: str = "") -> Dict[str, Any]:
        """
        Analyze a GitHub Actions workflow diff for security risks.
        
        Args:
            diff: The code diff to analyze
            file_path: Optional file path for context
            
        Returns:
            Dict containing findings with reasoning, finding text, and confidence
        """
        findings = []
        
        # Only analyze workflow files
        if not self._is_workflow_file(file_path):
            return {"findings": findings}
        
        # Split diff into lines for analysis
        lines = diff.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Only analyze added lines (those starting with '+')
            if not line.startswith('+'):
                continue
                
            # Remove the '+' prefix for pattern matching
            clean_line = line[1:].strip()
            
            # Check each security pattern category
            for risk_type, patterns in self.security_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, clean_line, re.IGNORECASE):
                        finding = self._create_finding(
                            risk_type, pattern, clean_line, line_num, file_path
                        )
                        findings.append(finding)
        
        return {"findings": findings}
    
    def _is_workflow_file(self, file_path: str) -> bool:
        """Check if the file is a GitHub Actions workflow."""
        if not file_path:
            return False
        
        workflow_indicators = [
            '.github/workflows/',
            '.yml',
            '.yaml',
        ]
        
        return any(indicator in file_path for indicator in workflow_indicators)
    
    def _create_finding(self, risk_type: str, pattern: str, line: str, 
                       line_num: int, file_path: str) -> Dict[str, Any]:
        """Create a finding for a detected security risk."""
        
        risk_descriptions = {
            "untrusted_action": "Untrusted or mutable third-party action",
            "secrets_exposure": "Potential secrets exposure",
            "unsafe_run": "Unsafe run command with user input",
            "privilege_escalation": "Excessive permissions or privilege escalation",
            "pull_request_target": "Insecure pull_request_target usage"
        }
        
        severity_mapping = {
            "untrusted_action": "high",
            "secrets_exposure": "critical",
            "unsafe_run": "high",
            "privilege_escalation": "high",
            "pull_request_target": "critical"
        }
        
        confidence = self._calculate_confidence(risk_type, line)
        
        finding = {
            "reasoning": self._build_detailed_reasoning(risk_type, line, line_num, confidence),
            "finding": f"GitHub Actions Security Risk: {risk_descriptions[risk_type]}",
            "confidence": confidence,
            "line_number": line_num,
            "file_path": file_path,
            "category": "security",
            "severity": severity_mapping[risk_type],
            "evidence": {
                "risk_type": risk_type,
                "pattern_matched": pattern,
                "line_context": line[:100] + "..." if len(line) > 100 else line
            }
        }
        
        return finding
    
    def _calculate_confidence(self, risk_type: str, line: str) -> float:
        """Calculate confidence score for the security risk."""
        
        base_confidence = {
            "untrusted_action": 0.8,
            "secrets_exposure": 0.9,
            "unsafe_run": 0.85,
            "privilege_escalation": 0.8,
            "pull_request_target": 0.9
        }.get(risk_type, 0.7)
        
        # Adjust confidence based on context
        if any(trusted in line for trusted in self.trusted_publishers):
            base_confidence -= 0.2  # Reduce for trusted publishers
        
        if 'test' in line.lower() or 'example' in line.lower():
            base_confidence -= 0.2  # Reduce for test contexts
        
        # Increase confidence for high-risk patterns
        if '${{' in line and 'github.event' in line:
            base_confidence += 0.1  # User input injection risk
        
        if 'secrets.' in line and ('echo' in line.lower() or 'print' in line.lower()):
            base_confidence += 0.1  # Direct secrets exposure
        
        return max(0.1, min(0.95, base_confidence))
    
    def _build_detailed_reasoning(self, risk_type: str, line: str, 
                                 line_num: int, confidence: float) -> str:
        """Build detailed reasoning for the GitHub Actions security finding."""
        
        reasoning_parts = []
        
        # Risk-specific explanations
        risk_explanations = {
            "untrusted_action": [
                f"Action usage without specific version pin detected on line {line_num}",
                "Using mutable references (latest, main, master) or short commit hashes",
                "This allows action code to change unexpectedly, creating supply chain risks"
            ],
            "secrets_exposure": [
                f"Potential secrets exposure detected on line {line_num}",
                "Secrets should never be logged, echoed, or exposed in output",
                "This could leak sensitive credentials in build logs"
            ],
            "unsafe_run": [
                f"Unsafe run command with user-controlled input on line {line_num}",
                "Using pull request titles, bodies, or commit messages in shell commands",
                "This enables command injection attacks from malicious PRs"
            ],
            "privilege_escalation": [
                f"Excessive permissions or privilege escalation on line {line_num}",
                "Broad write permissions can allow attackers to modify repository",
                "Follow principle of least privilege for workflow permissions"
            ],
            "pull_request_target": [
                f"Insecure pull_request_target usage on line {line_num}",
                "This trigger runs with write permissions in the context of the base repository",
                "Extremely dangerous when combined with user input or untrusted code execution"
            ]
        }
        
        explanations = risk_explanations.get(risk_type, [f"Security risk detected on line {line_num}"])
        reasoning_parts.extend(explanations)
        
        # Add mitigation suggestions
        mitigations = {
            "untrusted_action": "Pin to specific commit SHA or use trusted actions only",
            "secrets_exposure": "Remove secrets from output and use secure secret handling",
            "unsafe_run": "Sanitize user inputs or avoid using them in shell commands",
            "privilege_escalation": "Use minimal required permissions for each job",
            "pull_request_target": "Consider using pull_request trigger or add safety checks"
        }
        
        if risk_type in mitigations:
            reasoning_parts.append(f"Mitigation: {mitigations[risk_type]}")
        
        # Confidence assessment
        if confidence >= 0.8:
            reasoning_parts.append("High confidence - immediate review recommended")
        elif confidence >= 0.6:
            reasoning_parts.append("Moderate confidence - security review suggested")
        else:
            reasoning_parts.append("Lower confidence - verify if this is a legitimate pattern")
        
        return ". ".join(reasoning_parts)


# Example usage/testing function
def test_agent():
    """Test function to demonstrate agent functionality."""
    agent = GitHubActionsSecurityAgent()
    
    sample_diff = '''
+ name: Build and Deploy
+ on: 
+   pull_request_target:
+     types: [opened, synchronize]
+ jobs:
+   build:
+     runs-on: ubuntu-latest
+     permissions: write-all
+     steps:
+     - uses: actions/checkout@main
+     - name: Echo PR title
+       run: echo "Processing: ${{ github.event.pull_request.title }}"
+     - name: Use secret
+       run: echo ${{ secrets.API_KEY }}
'''
    
    results = agent.forward(sample_diff, ".github/workflows/deploy.yml")
    print("Test results:")
    for finding in results["findings"]:
        print(f"- {finding['finding']} (confidence: {finding['confidence']:.2f})")
        print(f"  Reasoning: {finding['reasoning'][:100]}...")


if __name__ == "__main__":
    test_agent()
