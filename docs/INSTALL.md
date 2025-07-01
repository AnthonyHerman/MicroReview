# Installation Guide for MicroReview

## Overview

MicroReview is a modular, explainable AI code review system for GitHub pull requests. This guide covers installation, configuration, and basic usage.

**Modern Python Project**: MicroReview uses `pyproject.toml` and `uv` for fast, reliable dependency management.

## Prerequisites

- Python 3.9 or higher (required by DSPy)
- `uv` package manager ([install guide](https://docs.astral.sh/uv/getting-started/installation/))
- GitHub repository with admin access (for GitHub App installation)
- API key for supported LLM provider (OpenAI, Anthropic, etc.)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/AnthonyHerman/MicroReview.git
cd MicroReview
```

### 2. Install Dependencies

```bash
# Install all dependencies (automatically creates virtual env)
uv sync

# Include development dependencies (for contributing)
uv sync --extra dev
```

**Note**: `uv` automatically creates and manages a virtual environment for your project using the `pyproject.toml` configuration!

### 3. Configure LLM Provider

Set up your LLM provider configuration. Create a `.env` file or set environment variables:

```bash
# For OpenAI
export OPENAI_API_KEY="your-openai-api-key"

# For Anthropic
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

### 4. Create Configuration File

Copy the example configuration and customize for your repository:

```bash
cp config/example.microreview.yml .microreview.yml
```

Edit `.microreview.yml` to enable desired agents and set thresholds:

```yaml
enabled_agents:
  - HardCodedCredsAgent
confidence_threshold: 0.8
group_by: "category"
max_findings_per_agent: 10
exclude_paths:
  - "tests/"
  - "docs/"
comment_mode: "update"
```

## Basic Usage

### Command Line

Run MicroReview on a PR diff:

```bash
# Analyze a diff file
uv run python main.py --pr-diff path/to/diff.patch --config .microreview.yml

# Analyze diff content directly
uv run python main.py --pr-diff "$(git diff HEAD~1)" --config .microreview.yml
```

### Testing Your Configuration

Test with the sample agent:

```bash
uv run python agents/hard_coded_creds.py
```

## GitHub App Installation (Production)

*Note: GitHub App integration is not yet implemented in this alpha version.*

For production deployment as a GitHub App:

1. Create a GitHub App in your organization
2. Configure webhook endpoints
3. Set up authentication and permissions
4. Deploy the application to your infrastructure

## Configuration Options

See [Configuration Reference](../README.md#configuration-microreview-yml-options) for detailed information about all available configuration options.

## Troubleshooting

### Common Issues

1. **"Module not found" errors**: Ensure all dependencies are installed with `uv sync`

2. **Agent loading failures**: Check that agent names in `enabled_agents` match the actual class names in the `agents/` directory

3. **Configuration validation errors**: Verify your `.microreview.yml` syntax with a YAML validator

4. **LLM API errors**: Ensure your API keys are set correctly and have sufficient quota

### Getting Help

- Check the [README](../README.md) for architecture details
- Review the [Copilot Instructions](../.github/copilot-instructions.md) for development guidelines
- Open an issue on GitHub for bugs or feature requests

## Development

To contribute to MicroReview or develop custom agents:

1. Follow the architecture principles in `.github/copilot-instructions.md`
2. Create new agents as DSPy modules in the `agents/` directory
3. Add tests for new functionality in the `tests/` directory
4. Update documentation for new features

## Dependency Management

### Adding New Dependencies

```bash
# Add a new runtime dependency
uv add package-name

# Add a new development dependency
uv add --dev package-name

# Sync dependencies after changes
uv sync
```

### Updating Dependencies

```bash
# Update all dependencies
uv sync --upgrade

# Update specific package
uv add package-name@latest
```

## Local Testing

### 🚀 Quick Start Test

The easiest way to test your installation:

```bash
# Run the automated test script
uv run python test_local.py
```

This script will:
- ✅ Verify all dependencies are installed
- ✅ Test DSPy configuration 
- ✅ Create sample code with security issues
- ✅ Run MicroReview analysis
- ✅ Show you the expected output format

### Manual Testing Steps

1. **Verify Installation**:
```bash
# Check if DSPy is properly configured
uv run python -c "import dspy; print('DSPy available:', dspy.__version__)"

# Test configuration loading
uv run python -c "from core.dspy_config import setup_dspy_for_microreview; setup_dspy_for_microreview()"
```

2. **Create a Test Diff**:
```bash
# Create a sample file with hard-coded credentials (for testing)
cat > test_sample.py << 'EOF'
# This is a test file with intentional security issues
api_key = "sk-1234567890abcdef"
password = "super_secret_password"
token = "ghp_abcdefghijklmnopqrstuvwxyz"

def connect_to_db():
    return connect("mysql://user:password@localhost/db")
EOF

# Generate a diff
git add test_sample.py
git diff --cached > test.patch
```

3. **Run MicroReview**:
```bash
# Test with the sample diff
uv run python main.py --pr-diff test.patch --config config/example.microreview.yml

# Or test with git diff directly
uv run python main.py --pr-diff "$(git diff --cached)" --config config/example.microreview.yml
```

### Testing Individual Agents

Test specific agents in isolation:

```bash
# Test the hard-coded credentials agent
uv run python agents/hard_coded_creds.py

# Test with DSPy-based agent (if LLM is configured)
uv run python agents/hard_coded_creds_dspy.py
```

### Testing with Real PRs

1. **From GitHub CLI**:
```bash
# Install GitHub CLI if needed
# brew install gh  # macOS
# sudo apt install gh  # Ubuntu

# Get PR diff
gh pr diff 123 > pr_123.patch
uv run python main.py --pr-diff pr_123.patch --config .microreview.yml
```

2. **From Git**:
```bash
# Test against specific commits
git diff HEAD~2..HEAD > recent_changes.patch
uv run python main.py --pr-diff recent_changes.patch --config .microreview.yml

# Test against a branch
git diff main..feature-branch > feature.patch
uv run python main.py --pr-diff feature.patch --config .microreview.yml
```

### Demo Mode (No API Keys Required)

If you don't have LLM API keys yet, you can still test with fallback mode:

```bash
# Test without API keys (uses pattern-based analysis)
unset OPENAI_API_KEY ANTHROPIC_API_KEY
uv run python main.py --pr-diff test.patch --config config/example.microreview.yml
```

### Expected Output

A successful run should produce output like:

```
🔧 Setting up DSPy for MicroReview...
✅ Configured DSPy with openai/gpt-4o
📊 Running analysis with 1 agents...
🔍 HardCodedCredsAgent found 3 issues
📝 Generating review comment...

## 🤖 MicroReview Analysis

### 🔒 Security Issues (3 findings)

**test_sample.py**
- Line 2: Hard-coded API key detected (confidence: 0.95)
- Line 3: Hard-coded password detected (confidence: 0.90)
- Line 4: Hard-coded token detected (confidence: 0.92)
```

## Next Steps

- Customize agent configurations for your repository
- Add custom agents for organization-specific policies
- Integrate with your CI/CD pipeline
- Set up monitoring and alerting for the GitHub App

For more advanced usage and development, see the main [README](../README.md).