"""
Proper DSPy-based Hard-Coded Credentials Detection Agent

This agent follows the exact pattern shown in the README and implements
a true Natural Language Code Policy approach using DSPy signatures.
"""

from typing import Dict, Any, List
import json

try:
    import dspy
    DSPY_AVAILABLE = True
except ImportError:
    # Fallback for when DSPy is not available
    DSPY_AVAILABLE = False
    dspy = None


class CredentialAnalysisSignature(dspy.Signature if DSPY_AVAILABLE else object):
    """DSPy signature for credential analysis following NLCP methodology."""
    
    if DSPY_AVAILABLE:
        diff: str = dspy.InputField(desc="Code diff to analyze for hard-coded credentials")
        file_path: str = dspy.InputField(desc="File path for context")
        
        findings: str = dspy.OutputField(desc="""
        JSON array of findings for any hard-coded credentials, with each finding containing:
        - reasoning: Detailed explanation of why this is likely a credential
        - finding: Brief description of the issue found
        - confidence: Float between 0.0 and 1.0 indicating confidence level
        - line_number: Line number where the issue occurs
        - category: Always "security" for this agent
        - severity: "high" for credentials, "medium" for potential credentials
        """)


class HardCodedCredsAgent(dspy.Module if DSPY_AVAILABLE else object):
    """
    DSPy agent implementing Natural Language Code Policy for hard-coded credentials.
    
    This agent follows the exact pattern shown in the MicroReview README,
    using proper DSPy signatures and LLM-based analysis.
    """
    
    def __init__(self):
        super().__init__()
        
        if DSPY_AVAILABLE:
            # Use modern DSPy Predict module with our signature
            self.credential_analyzer = dspy.Predict(CredentialAnalysisSignature)
            self.analyze_credentials = dspy.Predict(CredentialAnalysisSignature)
        
        # Natural Language Code Policy (NLCP) - from DryRun Security examples
        self.policy_question = """Does this change introduce hard-coded credentials such as passwords, API keys, tokens, or secret access keys?"""
        
        self.policy_background = """Hard-coding credentials directly into source code poses a serious security risk. These secrets can be inadvertently leaked, stored in version control, or exposed during logging or error handling. This policy should return true if the code includes any strings or variables that suggest credentials are embedded, such as:

• Assignments to variables like password, secret, token, apikey, auth, or access_key
• Sensitive keys or secrets committed into .env, .yaml, .json, or configuration files

When detected, include the file path and line number where the issue appears. Do not repeat the credentials in the results."""
    
    def forward(self, diff: str, file_path: str = "") -> Dict[str, Any]:
        """
        Analyze a code diff using Natural Language Code Policy.
        
        This method follows the exact pattern shown in the README example.
        
        Args:
            diff: The code diff to analyze
            file_path: Optional file path for context
            
        Returns:
            Dict containing findings with reasoning, finding text, and confidence
        """
        if not DSPY_AVAILABLE:
            return self._fallback_analysis(diff, file_path)
        
        try:
            # Use the DSPy signature for analysis
            result = self.analyze_credentials(diff=diff, file_path=file_path)
            
            # Parse the LLM response
            findings = self._parse_llm_findings(result.findings, file_path)
            
            return {"findings": findings}
            
        except Exception as e:
            print(f"DSPy analysis failed: {e}, falling back to simple analysis")
            return self._fallback_analysis(diff, file_path)
    
    def _parse_llm_findings(self, llm_response: str, file_path: str) -> List[Dict[str, Any]]:
        """Parse LLM response into structured findings."""
        try:
            # Try to parse as JSON
            if isinstance(llm_response, str):
                # Clean up the response if needed
                if llm_response.startswith('```json'):
                    llm_response = llm_response.replace('```json', '').replace('```', '')
                
                findings_data = json.loads(llm_response)
            else:
                findings_data = llm_response
            
            # Ensure it's a list
            if not isinstance(findings_data, list):
                findings_data = [findings_data] if findings_data else []
            
            # Validate and structure findings
            structured_findings = []
            for finding in findings_data:
                if isinstance(finding, dict) and 'finding' in finding:
                    # Ensure required fields
                    structured_finding = {
                        "reasoning": finding.get("reasoning", "Credential pattern detected"),
                        "finding": finding.get("finding", "Possible hard-coded credential"),
                        "confidence": float(finding.get("confidence", 0.8)),
                        "line_number": int(finding.get("line_number", 0)) if finding.get("line_number") else None,
                        "file_path": file_path,
                        "category": "security",
                        "severity": finding.get("severity", "high"),
                        "agent": "HardCodedCredsAgent"
                    }
                    structured_findings.append(structured_finding)
            
            return structured_findings
            
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            print(f"Failed to parse LLM response: {e}")
            # Return empty list if parsing fails
            return []
    
    def _fallback_analysis(self, diff: str, file_path: str) -> Dict[str, Any]:
        """
        Simplified fallback analysis when DSPy is not available.
        
        This implements basic NLCP principles without full LLM analysis.
        """
        findings = []
        lines = diff.split('\n')
        
        # Simple credential indicators based on NLCP background
        credential_patterns = [
            ('password', 'password'),
            ('secret', 'secret'),
            ('token', 'token'),
            ('apikey', 'API key'),
            ('api_key', 'API key'),
            ('access_key', 'access key'),
            ('auth', 'authentication credential')
        ]
        
        for line_num, line in enumerate(lines, 1):
            if not line.startswith('+'):
                continue
                
            clean_line = line[1:].strip()
            
            # Skip comments and obvious non-credentials
            if (not clean_line or 
                clean_line.startswith(('#', '//', '/*')) or
                'test' in clean_line.lower() or
                'example' in clean_line.lower()):
                continue
            
            # Look for credential-like assignments
            for pattern, cred_type in credential_patterns:
                if (pattern in clean_line.lower() and 
                    ('=' in clean_line or ':' in clean_line) and
                    ('"' in clean_line or "'" in clean_line)):
                    
                    confidence = self._calculate_fallback_confidence(clean_line, pattern)
                    
                    finding = {
                        "reasoning": f"Line {line_num}: Variable containing '{pattern}' assigned a string value. {self._build_nlcp_reasoning(clean_line, cred_type)}",
                        "finding": f"Possible hard-coded {cred_type} detected",
                        "confidence": confidence,
                        "line_number": line_num,
                        "file_path": file_path,
                        "category": "security",
                        "severity": "high" if confidence > 0.7 else "medium",
                        "agent": "HardCodedCredsAgent"
                    }
                    findings.append(finding)
                    break  # Only report one finding per line
        
        return {"findings": findings}
    
    def _calculate_fallback_confidence(self, line: str, pattern: str) -> float:
        """Calculate confidence for fallback mode following NLCP principles."""
        confidence = 0.7  # Base confidence
        
        # Increase confidence for actual credential patterns
        if len([c for c in line if c.isalnum()]) > 20:
            confidence += 0.1
        
        # Decrease for test/demo context (NLCP background consideration)
        if any(word in line.lower() for word in ['test', 'demo', 'example', 'dummy', 'fake']):
            confidence -= 0.3
        
        # Decrease for obvious placeholders
        if line.count('x') > 3 or 'xxx' in line.lower() or 'placeholder' in line.lower():
            confidence -= 0.4
        
        # Increase for high-risk patterns
        if pattern in ['secret', 'password', 'token']:
            confidence += 0.1
        
        return max(0.1, min(0.9, confidence))
    
    def _build_nlcp_reasoning(self, line: str, cred_type: str) -> str:
        """Build reasoning following NLCP methodology."""
        reasoning_parts = []
        
        # NLCP-style reasoning
        reasoning_parts.append(f"Detected {cred_type} assignment pattern")
        
        if len(line) > 50:
            reasoning_parts.append("Long string value suggests actual credential")
        
        if any(word in line.lower() for word in ['test', 'demo', 'example']):
            reasoning_parts.append("Test context reduces risk but should still be reviewed")
        
        if cred_type in ['password', 'secret', 'token']:
            reasoning_parts.append("High-risk credential type requiring immediate attention")
        
        reasoning_parts.append("Review for compliance with security policies")
        
        return ". ".join(reasoning_parts)


# Test function following README example
def test_agent():
    """Test function demonstrating proper DSPy agent usage."""
    agent = HardCodedCredsAgent()
    
    sample_diff = '''
+ API_KEY = "sk-1234567890abcdef1234567890abcdef"
+ password = "supersecret123"
+ token = "ghp_abcdefghijklmnopqrstuvwxyz123456"
+ test_key = "dummy_value_for_testing"
- old_key = "dummy"
+ # This is just a comment
+ normal_var = "hello world"
'''
    
    results = agent.forward(sample_diff, "src/config.py")
    print("DSPy Agent Test Results:")
    print("=" * 40)
    for finding in results["findings"]:
        print(f"- {finding['finding']} (confidence: {finding['confidence']:.2f})")
        print(f"  Reasoning: {finding['reasoning']}")
        print(f"  Severity: {finding['severity']}")
        print()


if __name__ == "__main__":
    test_agent()
