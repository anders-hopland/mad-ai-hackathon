#!/usr/bin/env python3
"""Entry point for the AutoQA system."""

import asyncio
from autoqa.cli import main

if __name__ == "__main__":
    asyncio.run(main())
