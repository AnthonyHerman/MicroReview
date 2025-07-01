#!/usr/bin/env python3
"""
MicroReview Demo Script

This script demonstrates the README workflow and validates that our
implementation matches the documented behavior.

Usage:
    python demo.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.dspy_config import setup_dspy_for_microreview, dspy_config
from config.loader import ConfigLoader
from core.orchestrator import AgentOrchestrator
from core.synthesizer import ResultSynthesizer


def demo_readme_workflow():
    """
    Demonstrate the exact workflow described in the README.
    
    README Section: "How It Works"
    1. On Pull Request: GitHub App triggers micro-agents
    2. Agent Review: Each DSPy agent analyzes code
    3. Aggregation & Synthesis: Single review comment
    4. Developer Experience: Actionable, explained comments
    """
    
    print("🎯 MicroReview Demo - Following README Workflow")
    print("=" * 60)
    
    # Step 1: Configure DSPy (README: Multi-Provider Support)
    print("\n1️⃣  Configuring DSPy LLM Provider...")
    dspy_configured = setup_dspy_for_microreview()
    
    if dspy_configured:
        status = dspy_config.get_status()
        print(f"   ✅ Using {status['provider']} with {status['model']}")
    else:
        print("   ⚠️  Using fallback pattern-based analysis")
    
    # Step 2: Load Configuration (README: Configuration Options)
    print("\n2️⃣  Loading .microreview.yml Configuration...")
    config_loader = ConfigLoader()
    config = config_loader._get_default_config()  # Use default for demo
    print(f"   ✅ Enabled agents: {config.enabled_agents}")
    print(f"   ✅ Confidence threshold: {config.confidence_threshold}")
    print(f"   ✅ Grouping by: {config.group_by}")
    
    # Step 3: Initialize Orchestrator (README: NLCP Micro-Agents)
    print("\n3️⃣  Initializing Micro-Agent Orchestrator...")
    orchestrator = AgentOrchestrator(config)
    print(f"   ✅ Loaded {len(orchestrator.agents)} micro-agents")
    
    # Step 4: Sample PR Diff (README: Agent Review)
    print("\n4️⃣  Analyzing Sample PR Diff...")
    sample_diff = '''diff --git a/src/api.py b/src/api.py
index 1234567..abcdefg 100644
--- a/src/api.py
+++ b/src/api.py
@@ -1,5 +1,8 @@
 import requests
 import json
 
+# New API configuration
+API_KEY = "sk-1234567890abcdef1234567890abcdef"
+SECRET_TOKEN = "ghp_abcdefghijklmnopqrstuvwxyz123456"
+
 def get_user_data(user_id):
     """Fetch user data from API."""
'''
    
    # Step 5: Run Micro-Agent Analysis
    print("   🔍 Running micro-agent analysis...")
    findings = orchestrator.run_analysis(sample_diff, "demo_repo")
    print(f"   ✅ Found {len(findings)} potential issues")
    
    # Step 6: Synthesize Results (README: Single Synthesized PR Comment)
    print("\n5️⃣  Synthesizing into Single PR Review Comment...")
    synthesizer = ResultSynthesizer(config)
    review_comment = synthesizer.synthesize_findings(findings)
    
    # Step 7: Display Results (README: Sample Output)
    print("\n6️⃣  Generated PR Review Comment:")
    print("=" * 60)
    print(review_comment)
    print("=" * 60)
    
    # Validate README requirements
    print("\n📋 README Compliance Check:")
    readme_requirements = [
        ("Micro-agent Architecture", len(orchestrator.agents) > 0),
        ("Structured Output", all('reasoning' in f and 'confidence' in f for f in findings)),
        ("Single PR Comment", "MicroReview Automated Code Review" in review_comment),
        ("Explainable Results", any('reasoning' in str(review_comment) for f in findings)),
        ("Confidence Scores", any('Confidence:' in review_comment for f in findings)),
    ]
    
    for requirement, passed in readme_requirements:
        status = "✅" if passed else "❌"
        print(f"   {status} {requirement}")
    
    print(f"\n🎉 Demo complete! MicroReview is {'✅ compliant' if all(r[1] for r in readme_requirements) else '❌ non-compliant'} with README")


def demo_nlcp_approach():
    """
    Demonstrate the Natural Language Code Policy approach.
    
    This shows how we've moved away from complex regex patterns
    to NLCP-based analysis as suggested in the user feedback.
    """
    
    print("\n🔬 NLCP Approach Demonstration")
    print("=" * 40)
    
    # Import our NLCP-based agent
    try:
        from agents.hard_coded_creds_dspy import HardCodedCredsAgent
        agent = HardCodedCredsAgent()
        
        print("✅ Using NLCP-based HardCodedCredsAgent")
        print("   Policy Question: Does this change introduce hard-coded credentials?")
        print("   Policy Background: Natural language description of risks")
        
        # Test with sample code
        test_diff = '''
+ password = "super_secret_password_123"
+ api_token = "test_token_for_demo"
+ config = {"database_url": "postgres://user:pass@localhost"}
'''
        
        results = agent.forward(test_diff, "config.py")
        print(f"\n   Analysis Results: {len(results['findings'])} findings")
        
        for finding in results['findings']:
            print(f"   - {finding['finding']} (confidence: {finding['confidence']:.2f})")
        
    except Exception as e:
        print(f"❌ NLCP demo failed: {e}")


if __name__ == "__main__":
    try:
        demo_readme_workflow()
        demo_nlcp_approach()
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        sys.exit(1)
