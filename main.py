#!/usr/bin/env python3
"""
MicroReview Main Entry Point

This is the main entry point for PR review processing in MicroReview.
It orchestrates the execution of micro-agents on PR diffs and synthesizes
the results into a single review comment.

Usage:
    python main.py --pr-diff <diff_file> --config <config_file>
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Any

from core.orchestrator import AgentOrchestrator
from core.synthesizer import ResultSynthesizer
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
        # Load configuration
        config_loader = ConfigLoader()
        config = config_loader.load_config(args.config)
        
        # Initialize orchestrator
        orchestrator = AgentOrchestrator(config)
        
        # Read PR diff
        if args.pr_diff:
            if Path(args.pr_diff).exists():
                with open(args.pr_diff, 'r') as f:
                    pr_diff = f.read()
            else:
                pr_diff = args.pr_diff
        else:
            print("Error: --pr-diff is required", file=sys.stderr)
            return 1
        
        # Run analysis
        print("Running MicroReview analysis...")
        findings = orchestrator.run_analysis(pr_diff, args.repo_path)
        
        # Synthesize results
        synthesizer = ResultSynthesizer(config)
        review_comment = synthesizer.synthesize_findings(findings)
        
        # Output results
        print("\n" + "="*50)
        print("MicroReview Analysis Complete")
        print("="*50)
        print(review_comment)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())