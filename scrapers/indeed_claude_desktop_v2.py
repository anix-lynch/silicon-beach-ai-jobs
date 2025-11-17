#!/usr/bin/env python3
"""
🚀 INDEED JOB SCRAPER - Claude Desktop + Anthropic Indeed MCP
TESTED & WORKING - November 10, 2025

This script demonstrates the integration but Claude Desktop handles the MCP calls.
Run this through Claude Desktop chat, not directly as a Python script.
"""

import json
import csv
import time
import re
from datetime import datetime
import requests

# ==============================================================================
# CONFIGURATION - FROM YOUR EXISTING SETUP
# ==============================================================================

HOME_ADDRESS = "YOUR_HOME_ADDRESS"
MAX_DISTANCE_MILES = 10

# API Keys from your existing builtin_la_ultimate.py
HUNTER_API_KEY = "REDACTED_HUNTER_KEY"
GOOGLE_MAPS_API_KEY = "REDACTED_MAPS_KEY"

# ==============================================================================
# INDEED MCP INTEGRATION - CLAUDE DESKTOP HANDLES THIS
# ==============================================================================

def parse_indeed_job(job_text):
    """
    Parse Indeed MCP formatted job result into structured data
    Example input from Indeed MCP:
    **Job Title:** Staff Data Engineer
    **Job Id:** 5-cmh1-0-1j9o8u7p2goij806-8665eb2f707f1045
    **Company:** Scribd
    **Location:** Los Angeles, CA
    **Posted on:** October 23, 2025
    **Job Type:** Fulltime
    **Compensation:** $137,500 - $247,500 a year
    **View Job URL:** https://to.indeed.com/...
    """
    job_data = {
        'title': '',
        'job_id': '',
