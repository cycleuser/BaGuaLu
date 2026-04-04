#!/usr/bin/env python3
"""Generate project documentation and architecture diagrams."""

import subprocess
from pathlib import Path


def generate_docs():
    """Generate documentation."""
    print("Generating documentation...")

    readme = Path("README.md")
    if readme.exists():
        print(f"✓ {readme} exists")

    agents_md = Path("AGENTS.md")
    if agents_md.exists():
        print(f"✓ {agents_md} exists")


def generate_architecture_diagram():
    """Generate architecture diagram."""
    print("Generating architecture diagram...")
    print("Architecture:")
    print("""
    BaGuaLu Architecture
    ====================
    
    ┌─────────────────────────────────────────┐
    │           CLI / Web Interface           │
    └─────────────────┬───────────────────────┘
                      │
    ┌─────────────────┴───────────────────────┐
    │           BaGuaLu Core                   │
    │  ┌──────────────────────────────────┐  │
    │  │       Orchestrator               │  │
    │  └──────────────────────────────────┘  │
    │  ┌──────────────────────────────────┐  │
    │  │     Resource Manager             │  │
    │  └──────────────────────────────────┘  │
    └─────────────────┬───────────────────────┘
                      │
    ┌─────────────────┴───────────────────────┐
    │         Agent Cluster                    │
    │  ┌──────┐ ┌──────┐ ┌─────────┐        │
    │  │Exec  │ │Super │ │Scheduler│        │
    │  └──────┘ └──────┘ └─────────┘        │
    └─────────────────┬───────────────────────┘
                      │
    ┌─────────────────┴───────────────────────┐
    │       Skill & Tool Systems              │
    │  ┌──────────┐ ┌──────────────────┐    │
    │  │  Skills  │ │  Evolution Engine │    │
    │  └──────────┘ └──────────────────┘    │
    └─────────────────┬───────────────────────┘
                      │
    ┌─────────────────┴───────────────────────┐
    │      LLM Providers                      │
    │  Ollama | LMStudio | OpenAI | Claude   │
    └─────────────────────────────────────────┘
    """)


def main():
    """Main function."""
    generate_docs()
    generate_architecture_diagram()
    print("\n✓ Done!")


if __name__ == "__main__":
    main()
