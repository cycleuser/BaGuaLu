#!/bin/bash
# Example: CLI usage for BaGuaLu
# This script demonstrates all CLI commands and features

set -e

echo "============================================================"
echo "BaGuaLu CLI Usage Examples"
echo "============================================================"

echo ""
echo "1. Initialize and Configure"
echo "------------------------------------------------------------"
echo "# Initialize configuration"
echo "bagualu --init"
echo ""
echo "# Set configuration file"
echo "bagualu -c ~/.bagualu/config.yaml"
echo ""
echo "# Configure provider and model"
echo "bagualu config --provider ollama --model llama2"
echo "bagualu config --provider openai --model gpt-4"

echo ""
echo "2. Show Version and Help"
echo "------------------------------------------------------------"
echo "# Show version"
echo "bagualu --version"
echo ""
echo "# Show help"
echo "bagualu --help"
echo "bagualu skill --help"
echo "bagualu deploy --help"

echo ""
echo "3. Skill Management"
echo "------------------------------------------------------------"
echo "# List all available skills"
echo "bagualu skill list"
echo ""
echo "# List skills from specific source"
echo "bagualu skill list --source opencode"
echo "bagualu skill list --source claude-code"
echo "bagualu skill list --source openlaoke"
echo ""
echo "# Get skill details"
echo "bagualu skill info data-analysis"
echo ""
echo "# Install skill from GitHub"
echo "bagualu skill install https://github.com/user/skill-repo --name my-skill"
echo ""
echo "# Rescan skill directories"
echo "bagualu skill rescan"
echo ""
echo "# List skill directories"
echo "bagualu skill sources"

echo ""
echo "4. Agent Deployment"
echo "------------------------------------------------------------"
echo "# Deploy single agent"
echo "bagualu deploy my-agent --role executor --provider ollama --model llama2"
echo ""
echo "# Deploy agent with skills"
echo "bagualu deploy code-agent --role executor --provider ollama --model llama2 --skills code-analysis,test-generator"
echo ""
echo "# Deploy supervisor agent"
echo "bagualu deploy supervisor-agent --role supervisor --provider openai --model gpt-4"

echo ""
echo "5. Workflow Execution"
echo "------------------------------------------------------------"
echo "# Create workflow file (workflow.yaml)"
cat << 'EOF'
# workflow.yaml example
name: data-pipeline
nodes:
  - id: extract
    role: executor
    instruction: Extract data from source
  - id: transform
    role: executor
    instruction: Transform and clean data
    dependencies:
      - extract
  - id: load
    role: executor
    instruction: Load data to destination
    dependencies:
      - transform
edges:
  - from: extract
    to: transform
  - from: transform
    to: load
EOF

echo ""
echo "# Execute workflow"
echo "bagualu run workflow.yaml"
echo ""
echo "# Execute workflow with inputs"
echo "bagualu run workflow.yaml --inputs '{\"source\": \"database\", \"target\": \"warehouse\"}'"

echo ""
echo "6. Web Server"
echo "------------------------------------------------------------"
echo "# Start web server"
echo "bagualu server"
echo ""
echo "# Start with custom host and port"
echo "bagualu server --host 0.0.0.0 --port 8080"

echo ""
echo "7. Status and Monitoring"
echo "------------------------------------------------------------"
echo "# Show cluster status"
echo "bagualu status"

echo ""
echo "8. Common Workflows"
echo "------------------------------------------------------------"
echo "# Development workflow"
cat << 'EOF'
# Initialize
bagualu --init

# Configure local development
bagualu config --provider ollama --model llama2

# List available skills
bagualu skill list

# Deploy development agent
bagualu deploy dev-agent --role executor --skills code-analysis

# Start web UI
bagualu server &
open http://localhost:8000

# Monitor status
bagualu status
EOF

echo ""
echo "# Production workflow"
cat << 'EOF'
# Configure production
bagualu config --provider openai --model gpt-4

# Deploy production cluster
bagualu deploy api-agent --role executor
bagualu deploy monitor-agent --role supervisor
bagualu deploy scheduler-agent --role scheduler

# Run production workflow
bagualu run production-workflow.yaml
EOF

echo ""
echo "9. Advanced Usage"
echo "------------------------------------------------------------"
echo "# Use with multiple providers"
cat << 'EOF'
# Local development
bagualu deploy local-agent --provider ollama --model llama2

# Cloud deployment
bagualu deploy cloud-agent --provider openai --model gpt-4

# Hybrid workflow
bagualu run hybrid-workflow.yaml
EOF

echo ""
echo "# Skill development workflow"
cat << 'EOF'
# Create custom skill
mkdir -p ~/.bagualu/skills/my-skill
cat > ~/.bagualu/skills/my-skill/SKILL.md << 'SKILL_EOF'
# My Custom Skill

## Description
Description of what this skill does

## Commands
- /mycommand: Execute the skill

## Capabilities
- Capability 1
- Capability 2
SKILL_EOF

# Rescan to discover new skill
bagualu skill rescan

# Verify skill is available
bagualu skill list | grep my-skill

# Use skill in agent
bagualu deploy custom-agent --skills my-skill
EOF

echo ""
echo "============================================================"
echo "CLI usage examples completed!"
echo "============================================================"