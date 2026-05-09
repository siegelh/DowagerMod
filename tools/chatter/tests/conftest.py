"""Pytest conftest for tools/chatter/tests.

Ensures tests don't accidentally load the user's real .env file (which would
inject API keys into os.environ and break tests that expect bare DEFAULTS).
"""
import os
os.environ["DOWAGER_CHATTER_SKIP_DOTENV"] = "1"
