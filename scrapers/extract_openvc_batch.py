#!/usr/bin/env python3
"""
Extract VC data from scraped OpenVC pages
This processes the Firecrawl output and creates a clean CSV
"""

import csv
import re
from datetime import datetime

# Mapping of VC name to scraped data (will be populated as we scrape)
vc_data_map = {
    "Upfront Ventures": {
        "address": "1314 7th St, Santa Monica, CA 90401",
        "stage": "Idea, Prototype, Early Revenue, Scaling",
        "focus": "healthtech, biotech, life sciences, digital health, diagnostics, therapeutics",
        "website": "https://upfront.com/",
        "check_size": "$1M to $8M"
    },
    # Will add more as we scrape
}

def extract_address_from_markdown(markdown_text):
    """Extract address from OpenVC markdown"""
    # Look for pattern: "Global HQ | ADDRESS<br>"
    match = re.search(r'Global HQ \| ([^\n<]+)', markdown_text)
    if match:
        return match.group(1).strip()
    return None

def extract_focus_from_markdown(markdown_text):
    """Extract investment focus"""
    match = re.search(r'Funding requirements \| ([^\n\|]+)', markdown_text)
    if match:
        return match.group(1).strip()
    return None

def extract_stages_from_markdown(markdown_text):
    """Extract funding stages"""
    match = re.search(r'Funding stages \| ([^\n\|]+)', markdown_text)
    if match:
        stages_raw = match.group(1).strip()
        # Clean up: "1. Idea or Patent2. Prototype" -> "Idea, Prototype"
        stages = re.findall(r'\d+\.\s*([^0-9]+?)(?=\d+\.|$)', stages_raw)
        return ", ".join([s.strip() for s in stages])
    return None

def extract_check_size_from_markdown(markdown_text):
    """Extract check size"""
    match = re.search(r'Check size \| ([^\n\|]+)', markdown_text)
    if match:
        return match.group(1).strip()
    return None

def extract_website_from_markdown(markdown_text):
    """Extract website"""
    match = re.search(r'Website \| (https?://[^\s\n]+)', markdown_text)
    if match:
        return match.group(1).strip()
    return None

# Test with Upfront Ventures data
test_markdown = """
| Global HQ | 1314 7th St, Santa Monica, CA 90401<br>
| Funding requirements | We invest in healthtech, biotech, life sciences, digital health, diagnostics, therapeutics, care delivery, value-based care, healthcare SaaS, mental health, women's health, aging, AI/ML in healthcare, and regulated healthcare services. |
| Funding stages | 1. Idea or Patent2. Prototype3. Early Revenue4. Scaling |
| Check size | $1M to $8M |
| Website | https://upfront.com/ |
"""

print("Testing extraction functions...")
print(f"Address: {extract_address_from_markdown(test_markdown)}")
print(f"Focus: {extract_focus_from_markdown(test_markdown)}")
print(f"Stages: {extract_stages_from_markdown(test_markdown)}")
print(f"Check Size: {extract_check_size_from_markdown(test_markdown)}")
print(f"Website: {extract_website_from_markdown(test_markdown)}")

print("\n✅ Extraction functions ready!")
print("\n📋 Next: Use MCP Firecrawl to scrape all 38 VCs in parallel")
print("   Then process with this script to create CSV")

