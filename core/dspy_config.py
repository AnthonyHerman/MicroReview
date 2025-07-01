"""
DSPy Configuration for MicroReview

This module handles DSPy LLM provider configuration as shown in the README.
It supports multiple providers and provides a consistent interface for agents.
"""

import os
from typing import Optional

try:
    import dspy
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False
    dspy = None


class DSPyConfig:
    """
    Handles DSPy configuration and LLM provider setup.
    
    Supports the multi-provider approach shown in the README:
    - OpenAI (GPT-4, GPT-3.5)
    - Anthropic (Claude)
    - Other providers supported by DSPy
    """
    
    def __init__(self):
        self.configured = False
        self.provider = None
        self.model = None
    
    def configure_openai(self, model: str = "openai/gpt-4o", api_key: Optional[str] = None):
        """
        Configure OpenAI provider using modern DSPy patterns.
        
        Args:
            model: OpenAI model to use (openai/gpt-4o, openai/gpt-3.5-turbo, etc.)
            api_key: API key (defaults to OPENAI_API_KEY env var)
        """
        if not DSPY_AVAILABLE:
            print("Warning: DSPy not available, skipping OpenAI configuration")
            return False
        
        try:
            api_key = api_key or os.getenv('OPENAI_API_KEY')
            if not api_key:
                print("Warning: No OpenAI API key found in environment or parameters")
                return False
            
            os.environ['OPENAI_API_KEY'] = api_key  # Ensure env var is set
            lm = dspy.LM(model)
            dspy.configure(lm=lm)
            
            self.configured = True
            self.provider = "openai"
            self.model = model
            
            print(f"✅ Configured DSPy with {model}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to configure OpenAI: {e}")
            return False
    
    def configure_anthropic(self, model: str = "anthropic/claude-3-sonnet-20240229", api_key: Optional[str] = None):
        """
        Configure Anthropic provider using modern DSPy patterns.
        
        Args:
            model: Anthropic model to use (anthropic/claude-3-sonnet, anthropic/claude-3-haiku, etc.)
            api_key: API key (defaults to ANTHROPIC_API_KEY env var)
        """
        if not DSPY_AVAILABLE:
            print("Warning: DSPy not available, skipping Anthropic configuration")
            return False
        
        try:
            api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                print("Warning: No Anthropic API key found in environment or parameters")
                return False
            
            # Modern DSPy configuration pattern
            os.environ['ANTHROPIC_API_KEY'] = api_key  # Ensure env var is set
            lm = dspy.LM(model)
            dspy.configure(lm=lm)
            
            self.configured = True
            self.provider = "anthropic"
            self.model = model
            
            print(f"✅ Configured DSPy with {model}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to configure Anthropic: {e}")
            return False
    
    def auto_configure(self):
        """
        Automatically configure DSPy based on available environment variables.
        
        This follows the README guidance for easy setup.
        """
        if not DSPY_AVAILABLE:
            print("Warning: DSPy not available, cannot auto-configure")
            return False
        
        # Try OpenAI first
        if os.getenv('OPENAI_API_KEY'):
            return self.configure_openai("openai/gpt-4o")
        
        # Try Anthropic second
        if os.getenv('ANTHROPIC_API_KEY'):
            return self.configure_anthropic("anthropic/claude-3-sonnet-20240229")
        
        print("Warning: No API keys found for supported providers (OpenAI, Anthropic)")
        print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable")
        return False
    
    def is_configured(self) -> bool:
        """Check if DSPy is properly configured."""
        return DSPY_AVAILABLE and self.configured
    
    def get_status(self) -> dict:
        """Get current configuration status."""
        return {
            "dspy_available": DSPY_AVAILABLE,
            "configured": self.configured,
            "provider": self.provider,
            "model": self.model
        }


# Global configuration instance
dspy_config = DSPyConfig()


def setup_dspy_for_microreview():
    """
    Main setup function for DSPy in MicroReview.
    
    This should be called during application startup to configure
    the LLM provider as shown in the README examples.
    """
    print("🔧 Setting up DSPy for MicroReview...")
    
    if not DSPY_AVAILABLE:
        print("⚠️  DSPy not installed. Install with: uv sync")
        print("   Agents will fall back to pattern-based analysis")
        return False
    
    # Auto-configure based on environment
    success = dspy_config.auto_configure()
    
    if success:
        status = dspy_config.get_status()
        print(f"✅ DSPy configured successfully!")
        print(f"   Provider: {status['provider']}")
        print(f"   Model: {status['model']}")
    else:
        print("❌ DSPy configuration failed")
        print("   Set up your API key:")
        print("   export OPENAI_API_KEY='your-key-here'")
        print("   # or")
        print("   export ANTHROPIC_API_KEY='your-key-here'")
    
    return success


# Example usage as shown in README
def example_configuration():
    """Example of manual DSPy configuration using modern patterns."""
    
    # Example 1: Configure Anthropic (modern way)
    # import dspy
    # dspy.configure(lm=dspy.LM("anthropic/claude-3-sonnet-20240229"))
    
    # Example 2: Configure OpenAI (modern way)  
    # import dspy
    # dspy.configure(lm=dspy.LM("openai/gpt-4o"))
    
    # Using our configuration wrapper:
    dspy_config.configure_anthropic("anthropic/claude-3-sonnet-20240229")
    # or
    dspy_config.configure_openai("openai/gpt-4o")


if __name__ == "__main__":
    # Test configuration
    setup_dspy_for_microreview()
    
    # Show status
    status = dspy_config.get_status()
    print(f"\nConfiguration Status: {status}")
