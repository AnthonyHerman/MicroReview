"""
PII/PHI Exposure Detection Agent

This DSPy micro-agent analyzes code diffs to detect potential exposure
of Personal Identifiable Information (PII) or Protected Health Information (PHI).
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


class PiiExposureAgent(DSPyBase):
    """
    DSPy agent for detecting PII/PHI exposure in code diffs.
    
    This agent examines code changes for patterns that suggest the exposure
    of sensitive personal or health information through logging, comments,
    or poor data handling practices.
    """
    
    def __init__(self):
        super().__init__()
        # Common PII patterns
        self.pii_patterns = [
            # Email addresses
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            # SSN patterns (XXX-XX-XXXX)
            r'\b\d{3}-\d{2}-\d{4}\b',
            # Phone numbers
            r'\b\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})\b',
            # Credit card patterns (simplified)
            r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        ]
        
        # PII-related variable names and contexts
        self.pii_contexts = [
            r'(?i)(ssn|social_security|social_security_number)',
            r'(?i)(email|email_address)',
            r'(?i)(phone|phone_number|mobile)',
            r'(?i)(address|street|zip|postal)',
            r'(?i)(credit_card|card_number|ccn)',
            r'(?i)(dob|date_of_birth|birthdate)',
            r'(?i)(medical|health|patient|diagnosis)',
        ]
        
        # Logging and exposure patterns
        self.exposure_patterns = [
            r'(?i)(log|print|console\.|debug|trace)\s*\([^)]*(?:user|customer|patient|person)',
            r'(?i)(log|print|console\.|debug|trace)\s*\([^)]*(?:email|phone|ssn|address)',
        ]
    
    def forward(self, diff: str, file_path: str = "") -> Dict[str, Any]:
        """
        Analyze a code diff for PII/PHI exposure risks.
        
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
            
            # Check for direct PII patterns
            findings.extend(self._check_pii_patterns(clean_line, line_num, file_path))
            
            # Check for PII in logging/output contexts
            findings.extend(self._check_exposure_patterns(clean_line, line_num, file_path))
            
            # Check for PII-related variable usage
            findings.extend(self._check_pii_contexts(clean_line, line_num, file_path))
        
        return {"findings": findings}
    
    def _check_pii_patterns(self, line: str, line_num: int, file_path: str) -> List[Dict[str, Any]]:
        """Check for direct PII patterns in the code."""
        findings = []
        
        for pattern in self.pii_patterns:
            matches = re.finditer(pattern, line)
            for match in matches:
                pii_type = self._identify_pii_type(match.group())
                confidence = self._calculate_confidence(line, pii_type, "direct_pattern")
                
                finding = {
                    "reasoning": self._build_detailed_reasoning(
                        line, pii_type, line_num, confidence, "direct_pattern"
                    ),
                    "finding": f"Potential {pii_type} exposure in code",
                    "confidence": confidence,
                    "line_number": line_num,
                    "file_path": file_path,
                    "category": "privacy",
                    "severity": "high",
                    "evidence": {
                        "pattern_type": pii_type,
                        "detection_method": "direct_pattern",
                        "line_context": line[:50] + "..." if len(line) > 50 else line
                    }
                }
                findings.append(finding)
        
        return findings
    
    def _check_exposure_patterns(self, line: str, line_num: int, file_path: str) -> List[Dict[str, Any]]:
        """Check for PII being logged or exposed."""
        findings = []
        
        for pattern in self.exposure_patterns:
            if re.search(pattern, line):
                confidence = self._calculate_confidence(line, "PII logging", "exposure_pattern")
                
                finding = {
                    "reasoning": self._build_detailed_reasoning(
                        line, "PII logging", line_num, confidence, "exposure_pattern"
                    ),
                    "finding": "Potential PII exposure through logging/output",
                    "confidence": confidence,
                    "line_number": line_num,
                    "file_path": file_path,
                    "category": "privacy",
                    "severity": "medium",
                    "evidence": {
                        "pattern_type": "logging_exposure",
                        "detection_method": "exposure_pattern",
                        "line_context": line[:50] + "..." if len(line) > 50 else line
                    }
                }
                findings.append(finding)
        
        return findings
    
    def _check_pii_contexts(self, line: str, line_num: int, file_path: str) -> List[Dict[str, Any]]:
        """Check for PII-related variable names and contexts."""
        findings = []
        
        for pattern in self.pii_contexts:
            if re.search(pattern, line):
                pii_type = self._extract_pii_type_from_context(pattern)
                confidence = self._calculate_confidence(line, pii_type, "context_pattern")
                
                finding = {
                    "reasoning": self._build_detailed_reasoning(
                        line, pii_type, line_num, confidence, "context_pattern"
                    ),
                    "finding": f"Potential {pii_type} handling without proper protection",
                    "confidence": confidence,
                    "line_number": line_num,
                    "file_path": file_path,
                    "category": "privacy",
                    "severity": "medium",
                    "evidence": {
                        "pattern_type": pii_type,
                        "detection_method": "context_pattern",
                        "line_context": line[:50] + "..." if len(line) > 50 else line
                    }
                }
                findings.append(finding)
        
        return findings
    
    def _identify_pii_type(self, match_text: str) -> str:
        """Identify the type of PII from the matched text."""
        if '@' in match_text:
            return "email address"
        elif re.match(r'\d{3}-\d{2}-\d{4}', match_text):
            return "Social Security Number"
        elif re.match(r'\b\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})\b', match_text):
            return "phone number"
        elif re.match(r'\b(?:\d{4}[-\s]?){3}\d{4}\b', match_text):
            return "credit card number"
        else:
            return "personal information"
    
    def _extract_pii_type_from_context(self, pattern: str) -> str:
        """Extract PII type from context pattern."""
        pattern_lower = pattern.lower()
        if 'ssn' in pattern_lower or 'social' in pattern_lower:
            return "SSN"
        elif 'email' in pattern_lower:
            return "email"
        elif 'phone' in pattern_lower:
            return "phone number"
        elif 'address' in pattern_lower:
            return "address"
        elif 'credit' in pattern_lower or 'card' in pattern_lower:
            return "credit card"
        elif 'medical' in pattern_lower or 'health' in pattern_lower:
            return "health information"
        else:
            return "personal information"
    
    def _calculate_confidence(self, line: str, pii_type: str, detection_method: str) -> float:
        """Calculate confidence score based on various factors."""
        base_confidence = {
            "direct_pattern": 0.9,
            "exposure_pattern": 0.7,
            "context_pattern": 0.6
        }.get(detection_method, 0.5)
        
        # Adjust based on context
        if 'test' in line.lower() or 'example' in line.lower() or 'demo' in line.lower():
            base_confidence -= 0.3
        if 'mock' in line.lower() or 'fake' in line.lower() or 'dummy' in line.lower():
            base_confidence -= 0.4
        if line.count('x') > 3:  # Placeholder patterns
            base_confidence -= 0.3
        
        # Increase confidence for high-risk contexts
        if 'log' in line.lower() or 'print' in line.lower():
            base_confidence += 0.1
        if 'database' in line.lower() or 'db' in line.lower():
            base_confidence += 0.1
        
        return max(0.1, min(0.95, base_confidence))
    
    def _build_detailed_reasoning(self, line: str, pii_type: str, line_num: int, 
                                 confidence: float, detection_method: str) -> str:
        """Build detailed reasoning for the finding."""
        reasoning_parts = []
        
        # Core detection explanation
        method_desc = {
            "direct_pattern": "Direct PII pattern detected",
            "exposure_pattern": "PII exposure through logging/output detected",
            "context_pattern": "PII-related variable/context detected"
        }.get(detection_method, "PII-related pattern detected")
        
        reasoning_parts.append(f"{method_desc} on line {line_num}")
        reasoning_parts.append(f"Pattern suggests handling of {pii_type}")
        
        # Context analysis
        if 'log' in line.lower() or 'print' in line.lower():
            reasoning_parts.append("Logging context increases exposure risk")
        if 'test' in line.lower() or 'demo' in line.lower():
            reasoning_parts.append("Test/demo context reduces risk")
        
        # Risk assessment
        if confidence >= 0.8:
            reasoning_parts.append("High risk of PII exposure")
        elif confidence >= 0.6:
            reasoning_parts.append("Moderate risk - review for compliance")
        else:
            reasoning_parts.append("Low risk - verify if intentional")
        
        return ". ".join(reasoning_parts)


# Example usage/testing function
def test_agent():
    """Test function to demonstrate agent functionality."""
    agent = PiiExposureAgent()
    
    sample_diff = '''
+ user_email = "john.doe@example.com"
+ print(f"User SSN: {user.ssn}")
+ patient_data = {"dob": "1990-01-01", "medical_id": "12345"}
+ log.info(f"Processing user: {user.email}")
- old_data = "dummy"
'''
    
    results = agent.forward(sample_diff)
    print("Test results:")
    for finding in results["findings"]:
        print(f"- {finding['finding']} (confidence: {finding['confidence']:.2f})")
        print(f"  Reasoning: {finding['reasoning']}")


if __name__ == "__main__":
    test_agent()
