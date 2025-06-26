"""
Result Synthesizer for MicroReview

This module aggregates and synthesizes findings from all micro-agents
into a single, well-formatted PR review comment.
"""

from typing import List, Dict, Any, Set
from collections import defaultdict
import hashlib

from config.loader import MicroReviewConfig


class ResultSynthesizer:
    """
    Synthesizes micro-agent findings into formatted PR review comments.
    
    This class handles:
    - Deduplication of similar findings
    - Grouping findings by file or category
    - Formatting findings into markdown
    - Creating actionable, readable review comments
    """
    
    def __init__(self, config: MicroReviewConfig):
        """
        Initialize synthesizer with configuration.
        
        Args:
            config: MicroReviewConfig object with synthesis settings
        """
        self.config = config
    
    def synthesize_findings(self, findings: List[Dict[str, Any]]) -> str:
        """
        Synthesize all findings into a formatted PR review comment.
        
        Args:
            findings: List of findings from all agents
            
        Returns:
            Formatted markdown review comment
        """
        if not findings:
            return self._generate_no_issues_comment()
        
        # Deduplicate findings
        deduplicated_findings = self._deduplicate_findings(findings)
        
        # Group findings according to configuration
        grouped_findings = self._group_findings(deduplicated_findings)
        
        # Generate the comment
        return self._format_review_comment(grouped_findings, len(findings), len(deduplicated_findings))
    
    def _deduplicate_findings(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate findings based on content similarity.
        
        Args:
            findings: List of findings to deduplicate
            
        Returns:
            List of unique findings
        """
        seen_hashes = set()
        unique_findings = []
        
        for finding in findings:
            # Create a hash based on finding content and location
            content = f"{finding.get('finding', '')}{finding.get('file_path', '')}{finding.get('line_number', '')}"
            finding_hash = hashlib.md5(content.encode()).hexdigest()
            
            if finding_hash not in seen_hashes:
                seen_hashes.add(finding_hash)
                unique_findings.append(finding)
        
        return unique_findings
    
    def _group_findings(self, findings: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group findings according to the configured grouping strategy.
        
        Args:
            findings: List of findings to group
            
        Returns:
            Dictionary with grouped findings
        """
        if self.config.group_by == "file":
            return self._group_by_file(findings)
        elif self.config.group_by == "category":
            return self._group_by_category(findings)
        else:  # "none"
            return {"All Findings": findings}
    
    def _group_by_file(self, findings: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group findings by file path."""
        grouped = defaultdict(list)
        for finding in findings:
            file_path = finding.get('file_path', 'Unknown File')
            grouped[file_path].append(finding)
        return dict(grouped)
    
    def _group_by_category(self, findings: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group findings by category."""
        grouped = defaultdict(list)
        for finding in findings:
            category = finding.get('category', 'General').title()
            grouped[category].append(finding)
        return dict(grouped)
    
    def _format_review_comment(self, grouped_findings: Dict[str, List[Dict[str, Any]]], 
                             total_findings: int, unique_findings: int) -> str:
        """
        Format grouped findings into a markdown PR review comment.
        
        Args:
            grouped_findings: Dictionary of grouped findings
            total_findings: Total number of findings before deduplication
            unique_findings: Number of unique findings after deduplication
            
        Returns:
            Formatted markdown comment
        """
        lines = []
        
        # Header
        lines.append("#### 🤖 MicroReview Automated Code Review")
        lines.append("")
        
        # Summary
        summary = self._generate_summary(grouped_findings, total_findings, unique_findings)
        lines.append(summary)
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Findings by group
        for group_name, group_findings in grouped_findings.items():
            if not group_findings:
                continue
                
            # Group header with emoji
            emoji = self._get_category_emoji(group_name)
            lines.append(f"**{emoji} {group_name}**")
            lines.append("")
            
            # Sort findings by severity and confidence
            sorted_findings = sorted(group_findings, 
                                   key=lambda x: (x.get('severity', 'medium'), -x.get('confidence', 0)))
            
            for finding in sorted_findings:
                formatted_finding = self._format_finding(finding)
                lines.extend(formatted_finding)
            
            lines.append("")
        
        # Footer
        lines.append("---")
        lines.append("")
        lines.append("_This is an automated review by MicroReview. Please address any blocking issues before merging._")
        lines.append("")
        lines.append("*To learn more about MicroReview or suggest new policies, visit our docs.*")
        
        return '\n'.join(lines)
    
    def _generate_summary(self, grouped_findings: Dict[str, List[Dict[str, Any]]], 
                         total_findings: int, unique_findings: int) -> str:
        """Generate summary text for the review comment."""
        total_issues = sum(len(findings) for findings in grouped_findings.values())
        file_count = len(set(f.get('file_path', 'unknown') for findings in grouped_findings.values() for f in findings))
        
        if total_issues == 0:
            return "**Summary:** No issues found! 🎉"
        
        summary = f"**Summary:** {total_issues} potential issue{'s' if total_issues != 1 else ''} found"
        if file_count > 1:
            summary += f" across {file_count} file{'s' if file_count != 1 else ''}"
        summary += "."
        
        if total_findings != unique_findings:
            summary += f" ({total_findings - unique_findings} duplicate{'s' if total_findings - unique_findings != 1 else ''} removed)"
        
        return summary
    
    def _get_category_emoji(self, category: str) -> str:
        """Get emoji for category."""
        emoji_map = {
            'Security': '🔒',
            'Documentation': '📄',
            'Performance': '⚡',
            'Style': '🎨',
            'Duplication': '🌀',
            'General': '📋',
            'Quality': '✨'
        }
        return emoji_map.get(category, '📋')
    
    def _format_finding(self, finding: Dict[str, Any]) -> List[str]:
        """
        Format a single finding into markdown lines.
        
        Args:
            finding: Single finding dictionary
            
        Returns:
            List of markdown lines for the finding
        """
        lines = []
        
        # File path and line number context
        file_path = finding.get('file_path', 'Unknown')
        line_num = finding.get('line_number')
        if line_num and file_path != 'Unknown':
            lines.append(f"- `{file_path}` (line {line_num})")
        elif file_path != 'Unknown':
            lines.append(f"- `{file_path}`")
        else:
            lines.append("- Unknown location")
        
        # Finding description
        finding_text = finding.get('finding', 'Issue detected')
        lines.append(f"  - **{finding_text}**")
        
        # Reasoning and confidence
        reasoning = finding.get('reasoning', 'No reasoning provided')
        confidence = finding.get('confidence', 0)
        lines.append(f"    > Reasoning: {reasoning}")
        lines.append(f"    > Confidence: {confidence:.2f}")
        
        # Agent information
        agent = finding.get('agent', 'Unknown Agent')
        lines.append(f"    > Agent: {agent}")
        
        lines.append("")
        
        return lines
    
    def _generate_no_issues_comment(self) -> str:
        """Generate comment when no issues are found."""
        return """#### 🤖 MicroReview Automated Code Review

**Summary:** No issues found! 🎉

All enabled micro-agents have reviewed the changes and found no policy violations or potential issues.

---

_This is an automated review by MicroReview._

*To learn more about MicroReview or suggest new policies, visit our docs.*"""


# Example usage
if __name__ == "__main__":
    from config.loader import ConfigLoader
    
    # Sample findings
    sample_findings = [
        {
            "reasoning": "Variable 'API_KEY' assigned a string literal on line 12.",
            "finding": "Possible hard-coded API key",
            "confidence": 0.93,
            "line_number": 12,
            "file_path": "src/api.py",
            "category": "security",
            "severity": "high",
            "agent": "HardCodedCredsAgent"
        },
        {
            "reasoning": "Function 'get_user_data' lacks documentation.",
            "finding": "Missing function documentation",
            "confidence": 0.87,
            "line_number": 24,
            "file_path": "src/api.py",
            "category": "documentation",
            "severity": "medium",
            "agent": "DocsCompletenessAgent"
        }
    ]
    
    # Load config and synthesize
    config_loader = ConfigLoader()
    config = config_loader._get_default_config()
    synthesizer = ResultSynthesizer(config)
    
    comment = synthesizer.synthesize_findings(sample_findings)
    print(comment)