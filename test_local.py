#!/usr/bin/env python3
"""
MicroReview Local Testing Script

This script helps you test MicroReview locally with sample data.
Run this after installation to verify everything works correctly.
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path

def create_sample_diff():
    """Create a sample diff file with security issues for testing."""
    
    sample_code = '''# Sample file with intentional security issues for testing
api_key = "sk-1234567890abcdefghijklmnopqrstuvwxyz123456"
password = "super_secret_password_123"
github_token = "ghp_abcdefghijklmnopqrstuvwxyz123456789"
aws_secret = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

def connect_to_database():
    # Hard-coded database credentials
    connection_string = "postgresql://admin:password123@localhost:5432/mydb"
    return connect(connection_string)

def api_request():
    headers = {
        "Authorization": "Bearer abc123def456ghi789",
        "X-API-Key": "secret-api-key-do-not-share"
    }
    return headers

# TODO: Move these to environment variables
STRIPE_SECRET = "sk_test_abcdefghijklmnopqrstuvwxyz"
JWT_SECRET = "my-super-secret-jwt-key-2024"
'''
    
    # Create a temporary diff file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.patch', delete=False) as f:
        f.write("diff --git a/sample_code.py b/sample_code.py\n")
        f.write("new file mode 100644\n")
        f.write("index 0000000..1234567\n")
        f.write("--- /dev/null\n")
        f.write("+++ b/sample_code.py\n")
        f.write("@@ -0,0 +1,20 @@\n")
        
        for line in sample_code.strip().split('\n'):
            f.write(f"+{line}\n")
        
        return f.name

def test_installation():
    """Test if MicroReview is properly installed."""
    print("🔧 Testing MicroReview installation...")
    
    try:
        # Test DSPy import
        result = subprocess.run([
            sys.executable, "-c", 
            "import dspy; print(f'DSPy version: {dspy.__version__}')"
        ], capture_output=True, text=True, check=True)
        print(f"✅ {result.stdout.strip()}")
    except subprocess.CalledProcessError:
        print("❌ DSPy not available - install with: uv sync")
        return False
    
    try:
        # Test MicroReview imports
        result = subprocess.run([
            sys.executable, "-c",
            "from core.dspy_config import dspy_config; print('MicroReview core modules loaded')"
        ], capture_output=True, text=True, check=True)
        print(f"✅ {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"❌ MicroReview import failed: {e.stderr}")
        return False
    
    return True

def test_configuration():
    """Test DSPy configuration."""
    print("\n🔧 Testing DSPy configuration...")
    
    has_openai = bool(os.getenv('OPENAI_API_KEY'))
    has_anthropic = bool(os.getenv('ANTHROPIC_API_KEY'))
    
    if has_openai:
        print("✅ OpenAI API key found")
    elif has_anthropic:
        print("✅ Anthropic API key found")
    else:
        print("⚠️  No LLM API keys found - will use fallback mode")
        print("   Set OPENAI_API_KEY or ANTHROPIC_API_KEY for full LLM analysis")
    
    try:
        result = subprocess.run([
            sys.executable, "-c",
            "from core.dspy_config import setup_dspy_for_microreview; setup_dspy_for_microreview()"
        ], capture_output=True, text=True)
        
        if "configured successfully" in result.stdout.lower():
            print("✅ DSPy configured with LLM provider")
        else:
            print("⚠️  DSPy using fallback mode (no LLM)")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")

def run_analysis(diff_file):
    """Run MicroReview analysis on the sample diff."""
    print(f"\n🔍 Running MicroReview analysis...")
    
    config_file = "config/example.microreview.yml"
    if not Path(config_file).exists():
        print(f"❌ Config file not found: {config_file}")
        return False
    
    cmd = [
        sys.executable, "main.py",
        "--pr-diff", diff_file,
        "--config", config_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        print("📋 Analysis Output:")
        print("=" * 50)
        print(result.stdout)
        
        if result.stderr:
            print("\n⚠️  Warnings/Errors:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("\n✅ Analysis completed successfully!")
            return True
        else:
            print(f"\n❌ Analysis failed with return code: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Analysis timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False

def main():
    """Main testing function."""
    print("🚀 MicroReview Local Testing")
    print("=" * 40)
    
    # Change to the MicroReview directory
    os.chdir(Path(__file__).parent)
    
    # Test installation
    if not test_installation():
        print("\n❌ Installation test failed. Please run: uv sync")
        sys.exit(1)
    
    # Test configuration
    test_configuration()
    
    # Create sample diff
    print("\n📝 Creating sample diff with security issues...")
    diff_file = create_sample_diff()
    print(f"✅ Created test diff: {diff_file}")
    
    try:
        # Run analysis
        success = run_analysis(diff_file)
        
        if success:
            print("\n🎉 All tests passed! MicroReview is working correctly.")
            print("\nNext steps:")
            print("1. Set up your API keys (OPENAI_API_KEY or ANTHROPIC_API_KEY)")
            print("2. Copy config/example.microreview.yml to .microreview.yml")
            print("3. Customize the configuration for your needs")
            print("4. Run on real PR diffs!")
        else:
            print("\n❌ Some tests failed. Check the output above for details.")
            sys.exit(1)
            
    finally:
        # Clean up
        try:
            os.unlink(diff_file)
            print(f"\n🧹 Cleaned up test file: {diff_file}")
        except:
            pass

if __name__ == "__main__":
    main()
