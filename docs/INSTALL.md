# Installation Guide for MicroReview

## Overview

MicroReview is a modular, explainable AI code review system for GitHub pull requests. This guide covers installation, configuration, and basic usage.

## Prerequisites

- Python 3.8 or higher
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
pip install -r requirements.txt
```

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
python main.py --pr-diff path/to/diff.patch --config .microreview.yml

# Analyze diff content directly
python main.py --pr-diff "$(git diff HEAD~1)" --config .microreview.yml
```

### Testing Your Configuration

Test with the sample agent:

```bash
cd agents
python hard_coded_creds.py
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

1. **"Module not found" errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`

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

## Next Steps

- Customize agent configurations for your repository
- Add custom agents for organization-specific policies
- Integrate with your CI/CD pipeline
- Set up monitoring and alerting for the GitHub App

For more advanced usage and development, see the main [README](../README.md).