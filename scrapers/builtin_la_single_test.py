#!/usr/bin/env python3
"""
Test scraper for a SINGLE job to extract ALL possible fields
Goal: Get everything useful for job applications
"""

import json
import requests
from bs4 import BeautifulSoup
import re

# Test with Alo Yoga - we know it's in Beverly Hills (~4 miles)
TEST_JOB_URL = "https://www.builtinla.com/job/senior-data-engineer/2276480"

def extract_all_job_data(url):
    """
    Extract EVERYTHING we can from a Built In LA job posting
    """
    print(f"🔍 Scraping: {url}\n")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Initialize data structure
        job_data = {
            'url': url,
            'apply_url': '',
            'company': '',
            'company_website': '',
            'company_size': '',
            'company_industry': '',
            'title': '',
            'job_type': '',  # Full-time, Contract, etc.
            'experience_level': '',  # Senior, Mid, Junior
            'location': '',
            'remote_option': '',
            'salary_min': '',
            'salary_max': '',
            'salary_text': '',
            'posted_date': '',
            'department': '',
            'reports_to': '',
            'recruiter_name': '',
            'recruiter_email': '',
            'hiring_manager': '',
            'top_skills': [],
            'required_skills': [],
            'nice_to_have_skills': [],
            'benefits': [],
            'description': '',
            'responsibilities': '',
            'qualifications': '',
            'company_description': ''
        }
        
        # ============================================================
        # COMPANY INFORMATION
        # ============================================================
        print("=" * 80)
        print("🏢 COMPANY INFORMATION")
        print("=" * 80)
        
        # Company name
        company_elem = soup.find('a', {'data-id': 'company-title-link'})
        if not company_elem:
            company_elem = soup.find('h2', class_=re.compile('company', re.I))
        if company_elem:
            job_data['company'] = company_elem.get_text(strip=True)
            print(f"Company: {job_data['company']}")
            # Try to get company URL
            if company_elem.name == 'a' and company_elem.get('href'):
                job_data['company_website'] = company_elem.get('href')
        
        # Company size
        company_size = soup.find(string=re.compile('employees|company size', re.I))
        if company_size:
            parent = company_size.find_parent()
            if parent:
                job_data['company_size'] = parent.get_text(strip=True)
                print(f"Company Size: {job_data['company_size']}")
        
        # Company industry
        industry = soup.find(string=re.compile('industry', re.I))
        if industry:
            parent = industry.find_parent()
            if parent:
                job_data['company_industry'] = parent.get_text(strip=True).replace('Industry:', '').strip()
                print(f"Industry: {job_data['company_industry']}")
        
        # ============================================================
        # JOB BASICS
        # ============================================================
        print("\n" + "=" * 80)
        print("💼 JOB BASICS")
        print("=" * 80)
        
        # Job title
        title_elem = soup.find('h1')
        if title_elem:
            job_data['title'] = title_elem.get_text(strip=True)
            print(f"Title: {job_data['title']}")
        
        # Experience level (Senior, Mid, Junior)
        if job_data['title']:
            title_lower = job_data['title'].lower()
            if 'senior' in title_lower or 'sr.' in title_lower or 'staff' in title_lower:
                job_data['experience_level'] = 'Senior'
            elif 'junior' in title_lower or 'jr.' in title_lower or 'entry' in title_lower:
                job_data['experience_level'] = 'Junior'
            elif 'lead' in title_lower or 'principal' in title_lower:
                job_data['experience_level'] = 'Lead/Principal'
            else:
                job_data['experience_level'] = 'Mid'
            print(f"Experience Level: {job_data['experience_level']}")
        
        # Job type (Full-time, Contract, etc.)
        job_type_elem = soup.find(string=re.compile('full.time|part.time|contract', re.I))
        if job_type_elem:
            job_data['job_type'] = job_type_elem.strip()
            print(f"Job Type: {job_data['job_type']}")
        else:
            job_data['job_type'] = 'Full-time'  # Default
        
        # Location
        location_elem = soup.find(string=re.compile('location|office', re.I))
        if location_elem:
            parent = location_elem.find_parent()
            if parent:
                location_text = parent.get_text(strip=True)
                job_data['location'] = location_text.replace('Location:', '').replace('Office:', '').strip()
                print(f"Location: {job_data['location']}")
        
        # Remote/Hybrid/Onsite
        page_text = soup.get_text().lower()
        if 'fully remote' in page_text or 'work from home' in page_text:
            job_data['remote_option'] = 'Remote'
        elif 'hybrid' in page_text:
            job_data['remote_option'] = 'Hybrid'
        else:
            job_data['remote_option'] = 'Onsite'
        print(f"Remote Option: {job_data['remote_option']}")
        
        # Posted date
        posted_elem = soup.find(string=re.compile('posted|updated', re.I))
        if posted_elem:
            parent = posted_elem.find_parent()
            if parent:
                job_data['posted_date'] = parent.get_text(strip=True)
                print(f"Posted: {job_data['posted_date']}")
        
        # ============================================================
        # SALARY
        # ============================================================
        print("\n" + "=" * 80)
        print("💰 SALARY")
        print("=" * 80)
        
        # Look for salary patterns
        salary_patterns = [
            r'\$(\d{2,3})[,k]\s*-\s*\$(\d{2,3})[,k]',  # $120k - $150k
            r'\$(\d{2,3},\d{3})\s*-\s*\$(\d{2,3},\d{3})',  # $120,000 - $150,000
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, soup.get_text(), re.I)
            if match:
                job_data['salary_min'] = match.group(1)
                job_data['salary_max'] = match.group(2)
                job_data['salary_text'] = match.group(0)
                print(f"Salary: {job_data['salary_text']}")
                break
        
        if not job_data['salary_text']:
            print("Salary: Not listed")
        
        # ============================================================
        # APPLY URL (MOST IMPORTANT!)
        # ============================================================
        print("\n" + "=" * 80)
        print("🎯 APPLICATION LINK")
        print("=" * 80)
        
        # Look for apply button/link
        apply_button = soup.find('a', string=re.compile('apply', re.I))
        if not apply_button:
            apply_button = soup.find('a', class_=re.compile('apply', re.I))
        if not apply_button:
            apply_button = soup.find('button', string=re.compile('apply', re.I))
        
        if apply_button and apply_button.get('href'):
            job_data['apply_url'] = apply_button.get('href')
            if not job_data['apply_url'].startswith('http'):
                job_data['apply_url'] = 'https://www.builtinla.com' + job_data['apply_url']
            print(f"✅ Apply URL: {job_data['apply_url']}")
        else:
            print("❌ Apply URL: Not found (may need to click through)")
        
        # ============================================================
        # CONTACT INFORMATION (for Hunter.io stalking!)
        # ============================================================
        print("\n" + "=" * 80)
        print("📧 CONTACT INFORMATION (for Hunter.io)")
        print("=" * 80)
        
        # Department
        dept_elem = soup.find(string=re.compile('department|team', re.I))
        if dept_elem:
            parent = dept_elem.find_parent()
            if parent:
                job_data['department'] = parent.get_text(strip=True)
                print(f"Department: {job_data['department']}")
        
        # Look for recruiter/contact info
        contact_patterns = [
            r'recruiter[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'hiring manager[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'contact[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)',
        ]
        
        for pattern in contact_patterns:
            match = re.search(pattern, soup.get_text())
            if match:
                name = match.group(1)
                if 'recruiter' in pattern:
                    job_data['recruiter_name'] = name
                    print(f"Recruiter: {name}")
                elif 'hiring' in pattern:
                    job_data['hiring_manager'] = name
                    print(f"Hiring Manager: {name}")
        
        # Email pattern
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, soup.get_text())
        if emails:
            job_data['recruiter_email'] = emails[0]
            print(f"Email: {emails[0]}")
        
        if not job_data['recruiter_name'] and not job_data['recruiter_email']:
            print("❌ No direct contact info (use Hunter.io with company name)")
            print(f"   → Search: {job_data['company']} + 'data engineering' + 'hiring manager'")
        
        # ============================================================
        # SKILLS (TOP PRIORITY!)
        # ============================================================
        print("\n" + "=" * 80)
        print("💻 SKILLS & REQUIREMENTS")
        print("=" * 80)
        
        # Look for skills section
        skills_section = soup.find(['div', 'section'], class_=re.compile('skill|requirement|qualification', re.I))
        if not skills_section:
            # Try finding by heading
            skills_heading = soup.find(['h2', 'h3'], string=re.compile('skill|requirement|qualification', re.I))
            if skills_heading:
                skills_section = skills_heading.find_parent()
        
        if skills_section:
            # Extract all list items and text
            skills_text = skills_section.get_text()
            
            # Common tech keywords
            tech_keywords = [
                'aws', 'gcp', 'azure', 'snowflake', 'bigquery', 'redshift',
                'python', 'sql', 'java', 'scala', 'spark', 'hadoop',
                'airflow', 'dbt', 'kafka', 'kubernetes', 'docker',
                'terraform', 'dataflow', 'pub/sub', 'lambda', 's3',
                'elasticsearch', 'mongodb', 'postgresql', 'mysql',
                'tableau', 'looker', 'power bi', 'jenkins', 'git',
                'rag', 'llm', 'embeddings', 'vector database'
            ]
            
            found_skills = []
            for keyword in tech_keywords:
                if re.search(r'\b' + keyword + r'\b', skills_text, re.I):
                    found_skills.append(keyword.upper())
            
            job_data['top_skills'] = found_skills
            print(f"Top Skills Found: {', '.join(found_skills)}")
        
        # ============================================================
        # JOB DESCRIPTION
        # ============================================================
        print("\n" + "=" * 80)
        print("📋 JOB DESCRIPTION")
        print("=" * 80)
        
        # Full description
        desc_elem = soup.find('div', class_=re.compile('description|content|detail', re.I))
        if desc_elem:
            job_data['description'] = desc_elem.get_text(separator='\n', strip=True)
            print(f"Description length: {len(job_data['description'])} chars")
            print(f"Preview: {job_data['description'][:200]}...")
        
        # ============================================================
        # BENEFITS
        # ============================================================
        print("\n" + "=" * 80)
        print("✨ BENEFITS")
        print("=" * 80)
        
        benefits_keywords = [
            '401k', 'health insurance', 'dental', 'vision', 'pto',
            'unlimited pto', 'stock options', 'equity', 'rsu',
            'remote work', 'flexible hours', 'gym', 'learning budget'
        ]
        
        found_benefits = []
        for benefit in benefits_keywords:
            if re.search(r'\b' + benefit + r'\b', soup.get_text(), re.I):
                found_benefits.append(benefit)
        
        job_data['benefits'] = found_benefits
        if found_benefits:
            print(f"Benefits: {', '.join(found_benefits)}")
        else:
            print("Benefits: Not listed")
        
        # ============================================================
        # SUMMARY
        # ============================================================
        print("\n" + "=" * 80)
        print("📊 DATA COMPLETENESS SUMMARY")
        print("=" * 80)
        
        completeness = {
            'Company Info': bool(job_data['company']),
            'Job Title': bool(job_data['title']),
            'Location': bool(job_data['location']),
            'Apply URL': bool(job_data['apply_url']),
            'Salary': bool(job_data['salary_text']),
            'Skills': bool(job_data['top_skills']),
            'Contact Info': bool(job_data['recruiter_name'] or job_data['recruiter_email']),
            'Department': bool(job_data['department']),
            'Description': bool(job_data['description']),
        }
        
        for field, has_data in completeness.items():
            status = "✅" if has_data else "❌"
            print(f"{status} {field}")
        
        # ============================================================
        # EXPORT
        # ============================================================
        print("\n" + "=" * 80)
        print("💾 EXPORTING DATA")
        print("=" * 80)
        
        # Save to JSON for inspection
        output_file = 'data/raw/test_job_single.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(job_data, f, indent=2)
        
        print(f"✅ Saved to: {output_file}")
        
        return job_data
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def suggest_csv_fields(job_data):
    """
    Based on what we found, suggest CSV fields
    """
    print("\n" + "=" * 80)
    print("📋 SUGGESTED CSV FIELDS FOR BULK SCRAPER")
    print("=" * 80)
    
    important_fields = [
        # Critical for applications
        ('apply_url', 'CRITICAL - where to apply'),
        ('company', 'CRITICAL - who to research'),
        ('title', 'CRITICAL - job title'),
        ('location', 'For commute calculation'),
        ('remote_option', 'Remote/Hybrid/Onsite'),
        
        # Contact stalking fields
        ('company_website', 'For Hunter.io domain'),
        ('department', 'For Hunter.io targeting'),
        ('recruiter_name', 'Direct contact'),
        ('recruiter_email', 'Direct contact'),
        ('hiring_manager', 'LinkedIn search target'),
        
        # Salary & fit
        ('salary_text', 'Compensation range'),
        ('experience_level', 'Junior/Mid/Senior'),
        ('top_skills', 'Tech stack match'),
        
        # Commute (from our calculator)
        ('distance_miles', 'From Culver City'),
        ('transit_duration', 'Bus/train time'),
        ('transit_changes', 'Number of transfers'),
        ('commute_rating', '⭐⭐⭐ rating'),
        ('bike_duration', 'Bike time'),
        
        # Application strategy
        ('posted_date', 'How fresh is posting'),
        ('benefits', 'Perks'),
        ('company_size', 'Startup vs corporate'),
        
        # URLs
        ('url', 'Built In LA listing'),
    ]
    
    print("\n✅ RECOMMENDED CSV COLUMNS:\n")
    for i, (field, description) in enumerate(important_fields, 1):
        has_data = "✅" if job_data.get(field) else "❌"
        print(f"{i:2d}. {has_data} {field:25s} - {description}")
    
    print("\n" + "=" * 80)
    print("🎯 HUNTER.IO STRATEGY")
    print("=" * 80)
    print(f"""
With this data, you can:

1. Search Hunter.io with:
   - Company: {job_data['company']}
   - Department: {job_data.get('department', 'Data Engineering')}
   - Title: "Hiring Manager" or "VP Engineering"

2. LinkedIn Boolean search:
   - "{job_data['company']}" AND "data engineering" AND "manager"
   - Look for: Engineering Managers, VPs, CTOs

3. Email pattern guess:
   - firstname.lastname@{job_data.get('company_website', 'company.com').replace('https://', '').replace('http://', '')}
   - Use Hunter.io to verify pattern
    """)

if __name__ == '__main__':
    print("\n")
    print("🎯" * 40)
    print("SINGLE JOB DETAILED SCRAPER - TEST RUN")
    print("🎯" * 40)
    print("\n")
    
    job_data = extract_all_job_data(TEST_JOB_URL)
    
    if job_data:
        suggest_csv_fields(job_data)
        
        print("\n" + "=" * 80)
        print("✅ TEST COMPLETE!")
        print("=" * 80)
        print("\nNext: Check data/raw/test_job_single.json")
        print("Then: We'll add these fields to the bulk scraper!")

