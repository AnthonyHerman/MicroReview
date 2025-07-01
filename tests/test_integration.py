"""
Basic integration test for MicroReview

This test validates that the core components work together correctly:
- Configuration loading
- Agent orchestration
- Result synthesis
"""

import unittest
import tempfile
import os
from pathlib import Path

from config.loader import ConfigLoader, MicroReviewConfig
from core.orchestrator import AgentOrchestrator
from core.synthesizer import ResultSynthesizer


class TestMicroReviewIntegration(unittest.TestCase):
    """Integration tests for MicroReview components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_config = MicroReviewConfig(
            enabled_agents=["HardCodedCredsAgent"],
            confidence_threshold=0.8,
            group_by="category",
            max_findings_per_agent=10,
            exclude_paths=["tests/"],
            comment_mode="update"
        )
        
        self.sample_diff = '''diff --git a/src/api.py b/src/api.py
index 1234567..abcdefg 100644
--- a/src/api.py
+++ b/src/api.py
@@ -1,3 +1,4 @@
 import requests
 
+API_KEY = "sk-1234567890abcdef1234567890abcdef"
 def get_data():
     return requests.get("https://api.example.com")'''
    
    def test_config_loader_default(self):
        """Test that config loader provides valid default configuration."""
        loader = ConfigLoader()
        config = loader._get_default_config()
        
        self.assertIsInstance(config, MicroReviewConfig)
        self.assertIn("HardCodedCredsAgent", config.enabled_agents)
        self.assertEqual(config.confidence_threshold, 0.8)
        self.assertEqual(config.group_by, "category")
    
    def test_config_loader_from_file(self):
        """Test loading configuration from YAML file."""
        loader = ConfigLoader()
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write('''
enabled_agents:
  - HardCodedCredsAgent
confidence_threshold: 0.9
group_by: "file"
max_findings_per_agent: 5
exclude_paths:
  - "tests/"
comment_mode: "update"
''')
            temp_config_path = f.name
        
        try:
            config = loader.load_config(temp_config_path)
            
            self.assertEqual(config.confidence_threshold, 0.9)
            self.assertEqual(config.group_by, "file")
            self.assertEqual(config.max_findings_per_agent, 5)
            self.assertIn("tests/", config.exclude_paths)
        finally:
            os.unlink(temp_config_path)
    
    def test_orchestrator_agent_loading(self):
        """Test that orchestrator correctly loads enabled agents."""
        orchestrator = AgentOrchestrator(self.test_config)
        
        # Should load HardCodedCredsAgent
        self.assertIn("HardCodedCredsAgent", orchestrator.agents)
        self.assertEqual(len(orchestrator.agents), 1)
    
    def test_orchestrator_analysis(self):
        """Test end-to-end analysis with orchestrator."""
        orchestrator = AgentOrchestrator(self.test_config)
        
        # Run analysis on sample diff
        findings = orchestrator.run_analysis(self.sample_diff)
        
        # Should find at least one issue (the hard-coded API key)
        self.assertGreater(len(findings), 0)
        
        # Check finding structure
        for finding in findings:
            self.assertIn("reasoning", finding)
            self.assertIn("finding", finding)
            self.assertIn("confidence", finding)
            self.assertIn("agent", finding)
    
    def test_synthesizer_formatting(self):
        """Test that synthesizer correctly formats findings."""
        synthesizer = ResultSynthesizer(self.test_config)
        
        sample_findings = [
            {
                "reasoning": "Variable 'API_KEY' assigned a string literal.",
                "finding": "Possible hard-coded API key",
                "confidence": 0.93,
                "line_number": 4,
                "file_path": "src/api.py",
                "category": "security",
                "agent": "HardCodedCredsAgent"
            }
        ]
        
        comment = synthesizer.synthesize_findings(sample_findings)
        
        # Check that comment contains expected elements
        self.assertIn("MicroReview Automated Code Review", comment)
        self.assertIn("Security", comment)
        self.assertIn("Possible hard-coded API key", comment)
        self.assertIn("src/api.py", comment)
        self.assertIn("0.93", comment)
    
    def test_synthesizer_no_findings(self):
        """Test synthesizer behavior when no findings are present."""
        synthesizer = ResultSynthesizer(self.test_config)
        
        comment = synthesizer.synthesize_findings([])
        
        self.assertIn("No issues found", comment)
        self.assertIn("🎉", comment)
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from diff to formatted comment."""
        # Load configuration
        config = self.test_config
        
        # Run orchestrator
        orchestrator = AgentOrchestrator(config)
        findings = orchestrator.run_analysis(self.sample_diff)
        
        # Synthesize results
        synthesizer = ResultSynthesizer(config)
        comment = synthesizer.synthesize_findings(findings)
        
        # Validate end result
        self.assertIsInstance(comment, str)
        self.assertGreater(len(comment), 100)  # Should be a substantial comment
        self.assertIn("MicroReview", comment)
    
    def test_file_exclusion(self):
        """Test that excluded paths are properly filtered."""
        config = MicroReviewConfig(
            enabled_agents=["HardCodedCredsAgent"],
            exclude_paths=["tests/", "src/"]
        )
        
        orchestrator = AgentOrchestrator(config)
        
        # This diff should be excluded because it's in src/
        excluded_diff = '''diff --git a/src/api.py b/src/api.py
+API_KEY = "secret"'''
        
        findings = orchestrator.run_analysis(excluded_diff)
        
        # Should find no issues because file is excluded
        self.assertEqual(len(findings), 0)


class TestConfigValidation(unittest.TestCase):
    """Test configuration validation."""
    
    def test_invalid_confidence_threshold(self):
        """Test that invalid confidence thresholds raise errors."""
        with self.assertRaises(ValueError):
            MicroReviewConfig(confidence_threshold=1.5)
        
        with self.assertRaises(ValueError):
            MicroReviewConfig(confidence_threshold=-0.1)
    
    def test_invalid_group_by(self):
        """Test that invalid group_by values raise errors."""
        with self.assertRaises(ValueError):
            MicroReviewConfig(group_by="invalid")
    
    def test_invalid_comment_mode(self):
        """Test that invalid comment modes raise errors."""
        with self.assertRaises(ValueError):
            MicroReviewConfig(comment_mode="invalid")


if __name__ == "__main__":
    # Set up test environment
    import sys
    import os
    
    # Add project root to path so imports work
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # Run tests
    unittest.main(verbosity=2)