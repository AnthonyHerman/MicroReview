"""
Hard-Coded Credentials Detection Agent

This DSPy micro-agent analyzes code diffs to detect potential hard-coded
credentials such as API keys, passwords, tokens, and secret access keys.
"""

import re
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


class HardCodedCredsAgent(DSPyBase):
    """
    DSPy agent for detecting hard-coded credentials in code diffs.
    
    This agent examines code changes for patterns that suggest the presence
    of hard-coded secrets, passwords, API keys, or other sensitive credentials.
    """
    
    def __init__(self):
        super().__init__()
        # Common patterns for credential detection
        self.credential_patterns = [
            r'(?i)(password|pwd|pass)\s*[:=]\s*["\'][^"\']{8,}["\']',
            r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\'][^"\']{16,}["\']',
            r'(?i)(secret|token)\s*[:=]\s*["\'][^"\']{16,}["\']',
            r'(?i)(access[_-]?key)\s*[:=]\s*["\'][^"\']{16,}["\']',
            r'(?i)(private[_-]?key)\s*[:=]\s*["\'][^"\']{32,}["\']',
        ]
    
    def forward(self, diff: str, file_path: str = "") -> Dict[str, Any]:
        """
        Analyze a code diff for hard-coded credentials.
        
        Args:
            diff: The code diff to analyze
            file_path: Optional file path for context
            
        Returns:
            Dict containing findings with reasoning, finding text, and confidence
        """
        findings = []
        
        # Split diff into lines for analysis
        lines = diff.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Only analyze added lines (those starting with '+')
            if not line.startswith('+'):
                continue
                
            # Remove the '+' prefix for pattern matching
            clean_line = line[1:].strip()
            
            # Check each credential pattern
            for pattern in self.credential_patterns:
                matches = re.finditer(pattern, clean_line)
                for match in matches:
                    # Extract the credential type from the pattern
                    cred_type = self._extract_credential_type(match.group())
                    
                    finding = {
                        "reasoning": f"Line {line_num}: Variable assignment with pattern matching {cred_type} on line: '{clean_line.strip()}'",
                        "finding": f"Possible hard-coded {cred_type} detected",
                        "confidence": self._calculate_confidence(clean_line, cred_type),
                        "line_number": line_num,
                        "file_path": file_path,
                        "category": "security",
                        "severity": "high"
                    }
                    findings.append(finding)
        
        return {"findings": findings}
    
    def _extract_credential_type(self, match_text: str) -> str:
        """Extract the type of credential from the matched text."""
        match_lower = match_text.lower()
        if 'password' in match_lower or 'pwd' in match_lower or 'pass' in match_lower:
            return "password"
        elif 'api' in match_lower and 'key' in match_lower:
            return "API key"
        elif 'secret' in match_lower:
            return "secret"
        elif 'token' in match_lower:
            return "token"
        elif 'access' in match_lower and 'key' in match_lower:
            return "access key"
        elif 'private' in match_lower and 'key' in match_lower:
            return "private key"
        else:
            return "credential"
    
    def _calculate_confidence(self, line: str, cred_type: str) -> float:
        """Calculate confidence score based on various factors."""
        confidence = 0.8  # Base confidence (increased from 0.7)
        
        # Increase confidence for certain patterns
        if re.search(r'["\'][A-Za-z0-9+/]{32,}["\']', line):  # Long base64-like strings
            confidence += 0.15
        if re.search(r'["\'][a-f0-9]{32,}["\']', line):  # Long hex strings
            confidence += 0.15
        if 'test' in line.lower() or 'demo' in line.lower():  # Decrease for test/demo
            confidence -= 0.3
        if line.count('x') > 5:  # Placeholder patterns like 'xxxxxxxx'
            confidence -= 0.4
            
        return max(0.1, min(0.95, confidence))  # Clamp between 0.1 and 0.95


# Example usage/testing function
def test_agent():
    """Test function to demonstrate agent functionality."""
    agent = HardCodedCredsAgent()
    
    sample_diff = '''
+ API_KEY = "sk-1234567890abcdef1234567890abcdef"
+ password = "supersecret123"
+ token = "ghp_abcdefghijklmnopqrstuvwxyz123456"
- old_key = "dummy"
+ # This is just a comment
+ normal_var = "hello world"
'''
    
    results = agent.forward(sample_diff)
    print("Test results:")
    for finding in results["findings"]:
        print(f"- {finding['finding']} (confidence: {finding['confidence']:.2f})")
        print(f"  Reasoning: {finding['reasoning']}")


if __name__ == "__main__":
    test_agent()