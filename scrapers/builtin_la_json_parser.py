#!/usr/bin/env python3
"""
Enhanced scraper v2 - Uses JSON-LD structured data
Much more reliable than HTML parsing!
"""

import json
import re
from bs4 import BeautifulSoup
import requests

TEST_URL = "https://www.builtinla.com/job/senior-data-engineer/2276480"

def extract_job_from_json_ld(url):
    """
    Extract job data from JSON-LD structured data (Schema.org JobPosting)
    This is the BEST way to scrape job sites!
    """
    print(f"🔍 Fetching: {url}\n")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find JSON-LD script tags
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    
    job_posting = None
    for script in json_ld_scripts:
        try:
            data = json.loads(script.string)
            
            # Handle both single objects and @graph arrays
            if isinstance(data, dict):
                if data.get('@type') == 'JobPosting':
                    job_posting = data
                    break
                elif '@graph' in data:
                    for item in data['@graph']:
                        if item.get('@type') == 'JobPosting':
                            job_posting = item
                            break
        except:
            continue
    
    if not job_posting:
        print("❌ No JobPosting JSON-LD found")
        return None
    
    # Extract data from structured JSON
    job_data = {
        'url': url,
        'apply_url': url,  # Default to listing URL
        'company': '',
        'company_website': '',
        'company_linkedin': '',  # For Hunter.io
        'title': '',
        'job_type': '',
        'experience_level': '',
        'location': '',
        'address': '',  # Full street address
        'remote_option': '',
        'salary_min': '',
        'salary_max': '',
        'salary_currency': 'USD',
        'posted_date': '',
        'valid_through': '',
        'department': 'Data Engineering',  # Default
        'top_skills': [],
        'required_skills': [],
        'benefits': [],
        'description_html': '',
        'description_text': '',
        'qualifications': '',
        'responsibilities': ''
    }
    
    # Title
    job_data['title'] = job_posting.get('title', '')
    
    # Company info
    hiring_org = job_posting.get('hiringOrganization', {})
    job_data['company'] = hiring_org.get('name', '')
    job_data['company_website'] = hiring_org.get('sameAs', '')
    
    # Determine experience level from title
    title_lower = job_data['title'].lower()
    if any(x in title_lower for x in ['senior', 'sr.', 'staff', 'lead']):
        job_data['experience_level'] = 'Senior'
    elif any(x in title_lower for x in ['principal', 'architect']):
        job_data['experience_level'] = 'Principal'
    elif any(x in title_lower for x in ['junior', 'jr.', 'entry']):
        job_data['experience_level'] = 'Junior'
    else:
        job_data['experience_level'] = 'Mid'
    
    # Job type
    employment_type = job_posting.get('employmentType', 'FULL_TIME')
    type_map = {
        'FULL_TIME': 'Full-time',
        'PART_TIME': 'Part-time',
        'CONTRACT': 'Contract',
        'TEMPORARY': 'Temporary',
        'INTERN': 'Internship'
    }
    job_data['job_type'] = type_map.get(employment_type, 'Full-time')
    
    # Location
    job_location = job_posting.get('jobLocation', {})
    address = job_location.get('address', {})
    
    if address:
        locality = address.get('addressLocality', '')
        region = address.get('addressRegion', '')
        street = address.get('streetAddress', '')
        postal_code = address.get('postalCode', '')
        
        job_data['location'] = f"{locality}, {region}" if locality and region else ''
        job_data['address'] = f"{street}, {locality}, {region} {postal_code}".strip(', ')
    
    # Remote option (check description for keywords)
    desc_lower = job_posting.get('description', '').lower()
    if 'fully remote' in desc_lower or 'work from home' in desc_lower:
        job_data['remote_option'] = 'Remote'
    elif 'hybrid' in desc_lower:
        job_data['remote_option'] = 'Hybrid'
    else:
        job_data['remote_option'] = 'Onsite'
    
    # Salary
    base_salary = job_posting.get('baseSalary', {})
    if base_salary:
        job_data['salary_currency'] = base_salary.get('currency', 'USD')
        value = base_salary.get('value', {})
        if isinstance(value, dict):
            job_data['salary_min'] = value.get('minValue', '')
            job_data['salary_max'] = value.get('maxValue', '')
    
    # Dates
    job_data['posted_date'] = job_posting.get('datePosted', '')
    job_data['valid_through'] = job_posting.get('validThrough', '')
    
    # Benefits
    benefits_str = job_posting.get('jobBenefits', '')
    if benefits_str:
        job_data['benefits'] = [b.strip() for b in benefits_str.split(',')]
    
    # Description
    job_data['description_html'] = job_posting.get('description', '')
    
    # Parse HTML description to extract sections
    if job_data['description_html']:
        desc_soup = BeautifulSoup(job_data['description_html'], 'html.parser')
        job_data['description_text'] = desc_soup.get_text(separator='\n', strip=True)
        
        # Extract skills from description
        tech_keywords = [
            'aws', 'gcp', 'azure', 'snowflake', 'bigquery', 'redshift',
            'python', 'sql', 'java', 'scala', 'spark', 'hadoop',
            'airflow', 'dbt', 'kafka', 'kubernetes', 'docker',
            'terraform', 'dataflow', 'pub/sub', 'lambda', 's3',
            'elasticsearch', 'mongodb', 'postgresql', 'mysql',
            'glue', 'emr', 'kinesis', 'pyspark', 'cassandra',
            'tableau', 'looker', 'power bi', 'jenkins', 'git',
            'rag', 'llm', 'embeddings', 'vector database', 'alloydb'
        ]
        
        found_skills = []
        desc_lower = job_data['description_text'].lower()
        for keyword in tech_keywords:
            if re.search(r'\b' + keyword + r'\b', desc_lower):
                found_skills.append(keyword.upper())
        
        job_data['top_skills'] = found_skills
        
        # Extract sections (QUALIFICATIONS, RESPONSIBILITIES, etc.)
        sections = desc_soup.find_all(['h2', 'h3', 'strong', 'b'])
        for section in sections:
            section_text = section.get_text().lower()
            if 'qualification' in section_text or 'requirement' in section_text:
                parent = section.find_parent()
                if parent:
                    job_data['qualifications'] = parent.get_text(separator='\n', strip=True)
            elif 'responsibilit' in section_text:
                parent = section.find_parent()
                if parent:
                    job_data['responsibilities'] = parent.get_text(separator='\n', strip=True)
    
    # Industry
    industries = job_posting.get('industry', [])
    if industries:
        job_data['industry'] = ', '.join(industries) if isinstance(industries, list) else industries
    
    # Look for Apply URL in the page
    apply_button = soup.find('a', class_=re.compile('apply', re.I))
    if not apply_button:
        apply_button = soup.find('a', string=re.compile('apply', re.I))
    
    if apply_button and apply_button.get('href'):
        href = apply_button.get('href')
        if href.startswith('http'):
            job_data['apply_url'] = href
        elif href.startswith('/'):
            job_data['apply_url'] = 'https://www.builtinla.com' + href
    
    return job_data

if __name__ == '__main__':
    print("=" * 80)
    print("🚀 ENHANCED SCRAPER V2 - JSON-LD PARSER TEST")
    print("=" * 80)
    print()
    
    job_data = extract_job_from_json_ld(TEST_URL)
    
    if job_data:
        print("\n" + "=" * 80)
        print("✅ EXTRACTED DATA")
        print("=" * 80)
        
        print(f"\n🏢 Company: {job_data['company']}")
        print(f"📋 Title: {job_data['title']}")
        print(f"📍 Location: {job_data['location']}")
        print(f"🏠 Address: {job_data['address']}")
        print(f"💼 Type: {job_data['job_type']} | {job_data['experience_level']}")
        print(f"🏡 Remote: {job_data['remote_option']}")
        
        if job_data['salary_min'] and job_data['salary_max']:
            print(f"💰 Salary: ${job_data['salary_min']:,} - ${job_data['salary_max']:,} {job_data['salary_currency']}")
        
        print(f"📅 Posted: {job_data['posted_date']}")
        
        if job_data['benefits']:
            print(f"\n✨ Benefits ({len(job_data['benefits'])}):")
            for benefit in job_data['benefits'][:10]:
                print(f"   • {benefit}")
        
        if job_data['top_skills']:
            print(f"\n💻 Tech Stack ({len(job_data['top_skills'])}):")
            print(f"   {', '.join(job_data['top_skills'])}")
        
        print(f"\n🔗 Apply URL: {job_data['apply_url']}")
        
        print(f"\n📝 Description length: {len(job_data['description_text'])} chars")
        
        # Save to JSON
        output_file = 'data/raw/test_job_v2.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(job_data, f, indent=2)
        
        print(f"\n💾 Saved to: {output_file}")
        
        # Show what we can use for Hunter.io
        print("\n" + "=" * 80)
        print("🎯 HUNTER.IO STALKING INFO")
        print("=" * 80)
        print(f"Company: {job_data['company']}")
        print(f"Department: Data Engineering (or search 'engineering')")
        print(f"Office: {job_data['address']}")
        print(f"LinkedIn: Search '{job_data['company']} data engineering manager'")
        
        if job_data['company_website']:
            domain = job_data['company_website'].replace('https://', '').replace('http://', '').split('/')[0]
            print(f"Email domain guess: @{domain}")
        
        print("\n" + "=" * 80)
        print("✅ TEST COMPLETE! Ready to build bulk scraper.")
        print("=" * 80)

