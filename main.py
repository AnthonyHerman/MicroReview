#!/usr/bin/env python3
"""
MicroReview Main Entry Point

This is the main entry point for PR review processing in MicroReview.
It orchestrates the execution of micro-agents on PR diffs and synthesizes
the results into a single review comment.

Following the README requirements:
- DSPy configuration for LLM providers
- Micro-agent orchestration
- Single synthesized PR comment

Usage:
    python main.py --pr-diff <diff_file> --config <config_file>
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Any

from core.orchestrator import AgentOrchestrator
from core.synthesizer import ResultSynthesizer
from core.dspy_config import setup_dspy_for_microreview
from config.loader import ConfigLoader


def main():
    """Main entry point for MicroReview PR processing."""
    parser = argparse.ArgumentParser(description="MicroReview PR Analysis")
    parser.add_argument(
        "--pr-diff", 
        type=str, 
        help="Path to PR diff file or diff content"
    )
    parser.add_argument(
        "--config", 
        type=str, 
        default=".microreview.yml",
        help="Path to MicroReview configuration file"
    )
    parser.add_argument(
        "--repo-path",
        type=str,
        default=".",
        help="Path to the repository being analyzed"
    )
    
    args = parser.parse_args()
    
    try:
        # Step 1: Configure DSPy as shown in README
        print("🔧 Configuring DSPy for LLM providers...")
        dspy_configured = setup_dspy_for_microreview()
        
        if dspy_configured:
            print("✅ DSPy configured successfully - using LLM-based analysis")
        else:
            print("⚠️  DSPy not configured - using fallback pattern-based analysis")
        
        # Step 2: Load configuration
        config_loader = ConfigLoader()
        config = config_loader.load_config(args.config)
        
        # Step 3: Initialize orchestrator
        orchestrator = AgentOrchestrator(config)
        
        # Step 4: Read PR diff
        if args.pr_diff:
            if Path(args.pr_diff).exists():
                with open(args.pr_diff, 'r') as f:
                    pr_diff = f.read()
            else:
                pr_diff = args.pr_diff
        else:
            print("Error: --pr-diff is required", file=sys.stderr)
            return 1
        
        # Step 5: Run analysis (following README architecture)
        print("🔍 Running MicroReview micro-agent analysis...")
        findings = orchestrator.run_analysis(pr_diff, args.repo_path)
        
        # Step 6: Synthesize results into single PR comment
        print("📝 Synthesizing findings into PR review comment...")
        synthesizer = ResultSynthesizer(config)
        review_comment = synthesizer.synthesize_findings(findings)
        
        # Step 7: Output results
        print("\n" + "="*50)
        print("🤖 MicroReview Analysis Complete")
        print("="*50)
        print(review_comment)
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())