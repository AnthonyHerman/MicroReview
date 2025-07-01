"""
Configuration Loader for MicroReview

This module handles loading and validating .microreview.yml configuration files.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class MicroReviewConfig:
    """Configuration class for MicroReview settings."""
    enabled_agents: List[str] = field(default_factory=list)
    confidence_threshold: float = 0.8
    group_by: str = "category"  # "file", "category", "none"
    max_findings_per_agent: int = 10
    exclude_paths: List[str] = field(default_factory=list)
    comment_mode: str = "update"  # "update", "append"
    agent_config: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError("confidence_threshold must be between 0.0 and 1.0")
        
        if self.group_by not in ["file", "category", "none"]:
            raise ValueError("group_by must be 'file', 'category', or 'none'")
        
        if self.comment_mode not in ["update", "append"]:
            raise ValueError("comment_mode must be 'update' or 'append'")
        
        if self.max_findings_per_agent <= 0:
            raise ValueError("max_findings_per_agent must be positive")


class ConfigLoader:
    """Loads and validates MicroReview configuration files."""
    
    def __init__(self):
        self.default_config = MicroReviewConfig()
    
    def load_config(self, config_path: str) -> MicroReviewConfig:
        """
        Load configuration from a YAML file.
        
        Args:
            config_path: Path to the .microreview.yml file
            
        Returns:
            MicroReviewConfig object with loaded settings
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid YAML
            ValueError: If config values are invalid
        """
        config_file = Path(config_path)
        
        if not config_file.exists():
            print(f"Warning: Config file {config_path} not found. Using defaults.")
            return self._get_default_config()
        
        try:
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML in config file {config_path}: {e}")
        
        return self._parse_config(config_data)
    
    def _parse_config(self, config_data: Dict[str, Any]) -> MicroReviewConfig:
        """Parse configuration data into MicroReviewConfig object."""
        config = MicroReviewConfig()
        
        # Update config with provided values
        if 'enabled_agents' in config_data:
            config.enabled_agents = config_data['enabled_agents']
        
        if 'confidence_threshold' in config_data:
            config.confidence_threshold = float(config_data['confidence_threshold'])
        
        if 'group_by' in config_data:
            config.group_by = config_data['group_by']
        
        if 'max_findings_per_agent' in config_data:
            config.max_findings_per_agent = int(config_data['max_findings_per_agent'])
        
        if 'exclude_paths' in config_data:
            config.exclude_paths = config_data['exclude_paths']
        
        if 'comment_mode' in config_data:
            config.comment_mode = config_data['comment_mode']
        
        if 'agent_config' in config_data:
            config.agent_config = config_data['agent_config']
        
        return config
    
    def _get_default_config(self) -> MicroReviewConfig:
        """Get default configuration with basic settings."""
        return MicroReviewConfig(
            enabled_agents=[
                "HardCodedCredsAgent",
                # New specialized agents (following best practices - opt-in)
                # "PiiExposureAgent",  # Uncomment to enable PII detection
                # "GitHubActionsSecurityAgent",  # Uncomment to enable GitHub Actions security
            ],
            confidence_threshold=0.8,
            group_by="category",
            max_findings_per_agent=10,
            exclude_paths=["tests/", "docs/", "*.md"],
            comment_mode="update"
        )
    
    def save_example_config(self, output_path: str = ".microreview.yml"):
        """Save an example configuration file."""
        example_config = {
            'enabled_agents': [
                'HardCodedCredsAgent',
                # 'PiiExposureAgent',  # Uncomment to enable PII/PHI detection
                # 'GitHubActionsSecurityAgent',  # Uncomment to enable GitHub Actions security
            ],
            'confidence_threshold': 0.8,
            'group_by': 'category',
            'max_findings_per_agent': 10,
            'exclude_paths': ['tests/', 'docs/', '*.md'],
            'comment_mode': 'update',
            'agent_config': {
                'HardCodedCredsAgent': {
                    'confidence_threshold': 0.8,
                    'max_findings': 5
                },
                'PiiExposureAgent': {
                    'confidence_threshold': 0.7,
                    'max_findings': 8
                },
                'GitHubActionsSecurityAgent': {
                    'confidence_threshold': 0.8,
                    'max_findings': 10
                }
            }
        }
        
        with open(output_path, 'w') as f:
            yaml.dump(example_config, f, default_flow_style=False, sort_keys=False)


# Example usage
if __name__ == "__main__":
    loader = ConfigLoader()
    
    # Create example config file
    loader.save_example_config("example.microreview.yml")
    print("Created example.microreview.yml")
    
    # Test loading
    try:
        config = loader.load_config("example.microreview.yml")
        print(f"Loaded config: {config}")
    except Exception as e:
        print(f"Error loading config: {e}")