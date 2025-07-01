"""
Agent Orchestrator for MicroReview

This module coordinates the execution of all enabled micro-agents
and collects their findings for synthesis.
"""

import importlib
from typing import List, Dict, Any, Optional
from pathlib import Path
import fnmatch

from config.loader import MicroReviewConfig


class AgentOrchestrator:
    """
    Orchestrates the execution of micro-agents on PR diffs.
    
    This class is responsible for:
    - Loading enabled agents based on configuration
    - Filtering files based on exclude patterns
    - Running agents on appropriate content
    - Collecting and organizing findings
    """
    
    def __init__(self, config: MicroReviewConfig):
        """
        Initialize the orchestrator with configuration.
        
        Args:
            config: MicroReviewConfig object with agent settings
        """
        self.config = config
        self.agents = {}
        self._load_agents()
    
    def _load_agents(self):
        """Load all enabled agents from the agents package."""
        for agent_name in self.config.enabled_agents:
            try:
                # Import the agent module
                module_name = self._agent_name_to_module(agent_name)
                module = importlib.import_module(f"agents.{module_name}")
                
                # Get the agent class
                agent_class = getattr(module, agent_name)
                
                # Instantiate the agent
                self.agents[agent_name] = agent_class()
                print(f"Loaded agent: {agent_name}")
                
            except (ImportError, AttributeError) as e:
                print(f"Warning: Could not load agent {agent_name}: {e}")
    
    def _agent_name_to_module(self, agent_name: str) -> str:
        """Convert agent class name to module name."""
        # Convert CamelCase to snake_case
        import re
        module_name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', agent_name)
        module_name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', module_name).lower()
        # Remove trailing 's' from 'creds' -> 'cred' issue
        if module_name.endswith('_creds_agent'):
            module_name = module_name.replace('_creds_agent', '_creds')
        return module_name
    
    def run_analysis(self, pr_diff: str, repo_path: str = ".") -> List[Dict[str, Any]]:
        """
        Run analysis on a PR diff using all enabled agents.
        
        Args:
            pr_diff: The PR diff content to analyze
            repo_path: Path to the repository (for file context)
            
        Returns:
            List of findings from all agents
        """
        all_findings = []
        
        # Parse diff to extract file-specific changes
        file_diffs = self._parse_diff_by_file(pr_diff)
        
        for file_path, file_diff in file_diffs.items():
            # Skip excluded files
            if self._should_exclude_file(file_path):
                print(f"Skipping excluded file: {file_path}")
                continue
            
            print(f"Analyzing file: {file_path}")
            
            # Run each agent on this file
            for agent_name, agent in self.agents.items():
                try:
                    # Get agent-specific config
                    agent_config = self.config.agent_config.get(agent_name, {})
                    agent_threshold = agent_config.get('confidence_threshold', 
                                                     self.config.confidence_threshold)
                    agent_max_findings = agent_config.get('max_findings', 
                                                        self.config.max_findings_per_agent)
                    
                    # Run the agent
                    result = agent.forward(file_diff, file_path)
                    findings = result.get("findings", [])
                    
                    # Filter findings by confidence threshold
                    filtered_findings = [
                        f for f in findings 
                        if f.get("confidence", 0) >= agent_threshold
                    ]
                    
                    # Limit number of findings per agent
                    if len(filtered_findings) > agent_max_findings:
                        filtered_findings = filtered_findings[:agent_max_findings]
                        print(f"Limited {agent_name} findings to {agent_max_findings}")
                    
                    # Add agent name to each finding
                    for finding in filtered_findings:
                        finding["agent"] = agent_name
                        finding["file_path"] = file_path
                    
                    all_findings.extend(filtered_findings)
                    print(f"Agent {agent_name} found {len(filtered_findings)} issues in {file_path}")
                    
                except Exception as e:
                    print(f"Error running agent {agent_name} on {file_path}: {e}")
        
        print(f"Total findings collected: {len(all_findings)}")
        return all_findings
    
    def _parse_diff_by_file(self, pr_diff: str) -> Dict[str, str]:
        """
        Parse a PR diff and split it by file.
        
        Args:
            pr_diff: The complete PR diff
            
        Returns:
            Dictionary mapping file paths to their specific diffs
        """
        file_diffs = {}
        current_file = None
        current_diff_lines = []
        
        for line in pr_diff.split('\n'):
            # Check for file header (e.g., "diff --git a/file.py b/file.py")
            if line.startswith('diff --git'):
                # Save previous file if exists
                if current_file and current_diff_lines:
                    file_diffs[current_file] = '\n'.join(current_diff_lines)
                
                # Extract file path (assuming format "diff --git a/path b/path")
                parts = line.split()
                if len(parts) >= 4:
                    current_file = parts[2][2:]  # Remove "a/" prefix
                else:
                    current_file = "unknown"
                current_diff_lines = []
            
            # Check for alternative file header format
            elif line.startswith('+++') and line.startswith('+++ b/'):
                current_file = line[6:]  # Remove "+++ b/" prefix
            
            # Add line to current file's diff
            if current_file:
                current_diff_lines.append(line)
        
        # Don't forget the last file
        if current_file and current_diff_lines:
            file_diffs[current_file] = '\n'.join(current_diff_lines)
        
        # If no file headers found, treat as single file
        if not file_diffs and pr_diff.strip():
            file_diffs["unknown"] = pr_diff
        
        return file_diffs
    
    def _should_exclude_file(self, file_path: str) -> bool:
        """
        Check if a file should be excluded based on exclude patterns.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file should be excluded, False otherwise
        """
        for pattern in self.config.exclude_paths:
            if fnmatch.fnmatch(file_path, pattern):
                return True
            # Also check if file path starts with pattern (for directory exclusions)
            if file_path.startswith(pattern.rstrip('/')):
                return True
        return False


# Example usage
if __name__ == "__main__":
    from config.loader import ConfigLoader
    
    # Load config
    config_loader = ConfigLoader()
    config = config_loader._get_default_config()
    
    # Create orchestrator
    orchestrator = AgentOrchestrator(config)
    
    # Sample diff
    sample_diff = '''
diff --git a/src/api.py b/src/api.py
index 1234567..abcdefg 100644
--- a/src/api.py
+++ b/src/api.py
@@ -1,3 +1,4 @@
 import requests
 
+API_KEY = "sk-1234567890abcdef1234567890abcdef"
 def get_data():
'''
    
    # Run analysis
    findings = orchestrator.run_analysis(sample_diff)
    print(f"\nFindings: {findings}")