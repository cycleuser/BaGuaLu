"""CLI entry point for BaGuaLu."""

import asyncio
from bagualu.entrypoints.cli import main

if __name__ == "__main__":
    asyncio.run(main())
