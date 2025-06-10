#!/usr/bin/env python3
"""
Compare Specific Pages
Detailed comparison of specific pages to identify content differences
"""

import requests
import os
from bs4 import BeautifulSoup
import time

def compare_page_content(page_name):
    """Compare a specific page between old and new sites"""
    
    old_url = f"https://0002n8y.wcomhost.com/website/{page_name}/"
    new_url = f"https://chiswickalbion.github.io/chiswick-albion-website/pages/{page_name}.html"
    
    print(f"\n🔍 COMPARING: {page_name}")
    print("=" * 60)
    
    try:
        # Get old site content
        print("📡 Fetching old site...")
        old_response = requests.get(old_url, timeout=10)
        old_accessible = old_response.status_code == 200
        
        # Get new site content
        print("📡 Fetching new site...")
        new_response = requests.get(new_url, timeout=10)
        new_accessible = new_response.status_code == 200
        
        print(f"🌐 Old site ({old_url}): {'✅ Accessible' if old_accessible else '❌ Not accessible'}")
        print(f"🌐 New site ({new_url}): {'✅ Accessible' if new_accessible else '❌ Not accessible'}")
        
        if old_accessible and new_accessible:
            # Parse content
            old_soup = BeautifulSoup(old_response.text, 'html.parser')
            new_soup = BeautifulSoup(new_response.text, 'html.parser')
            
            # Remove script and style elements
            for soup in [old_soup, new_soup]:
                for script in soup(["script", "style"]):
                    script.decompose()
            
            old_text = old_soup.get_text().strip()
            new_text = new_soup.get_text().strip()
            
            print(f"📄 Old site content: {len(old_text)} characters")
            print(f"📄 New site content: {len(new_text)} characters")
            
            # Basic content comparison
            if len(old_text) > 0 and len(new_text) > 0:
                similarity = min(len(old_text), len(new_text)) / max(len(old_text), len(new_text))
                print(f"📊 Content similarity: {similarity:.1%}")
                
                if similarity < 0.8:
                    print("⚠️  SIGNIFICANT CONTENT DIFFERENCE DETECTED")
                    
                    # Show first few lines of each
                    print("\n📝 OLD SITE PREVIEW:")
                    print("─" * 40)
                    print(old_text[:300] + "..." if len(old_text) > 300 else old_text)
                    
                    print("\n📝 NEW SITE PREVIEW:")
                    print("─" * 40)
                    print(new_text[:300] + "..." if len(new_text) > 300 else new_text)
                else:
                    print("✅ Content appears similar")
            
            # Check for specific elements
            old_images = len(old_soup.find_all('img'))
            new_images = len(new_soup.find_all('img'))
            print(f"🖼️  Images: Old={old_images}, New={new_images}")
            
            old_links = len(old_soup.find_all('a', href=True))
            new_links = len(new_soup.find_all('a', href=True))
            print(f"🔗 Links: Old={old_links}, New={new_links}")
            
        return {
            'page': page_name,
            'old_accessible': old_accessible,
            'new_accessible': new_accessible,
            'old_url': old_url,
            'new_url': new_url
        }
        
    except Exception as e:
        print(f"❌ Error comparing {page_name}: {e}")
        return None

def main():
    """Compare key pages that might have issues"""
    
    # Pages that were identified as having short content or potential issues
    problem_pages = [
        'FAC201617',
        'Fixtures0203', 
        'Fixtures0304',
        'honours',
        'records', 
        'top25',
        'videos',
        'nextgame',
        'History1',
        'everyplayer',
        'season1920',
        'season1819'
    ]
    
    print("🔍 SYSTEMATIC PAGE COMPARISON")
    print("=" * 60)
    print("Comparing specific pages between old and new sites")
    
    results = []
    
    for page in problem_pages:
        result = compare_page_content(page)
        if result:
            results.append(result)
        time.sleep(1)  # Be respectful to servers
    
    print("\n📊 COMPARISON SUMMARY")
    print("=" * 60)
    
    accessible_both = 0
    accessible_new_only = 0
    accessible_old_only = 0
    
    for result in results:
        if result['old_accessible'] and result['new_accessible']:
            accessible_both += 1
            status = "✅ Both accessible"
        elif result['new_accessible']:
            accessible_new_only += 1
            status = "⚠️  New only"
        elif result['old_accessible']:
            accessible_old_only += 1
            status = "❌ Old only"
        else:
            status = "❌ Neither accessible"
        
        print(f"{result['page']:<20} {status}")
    
    print(f"\n📈 SUMMARY:")
    print(f"✅ Both accessible: {accessible_both}")
    print(f"⚠️  New site only: {accessible_new_only}")
    print(f"❌ Old site only: {accessible_old_only}")

if __name__ == "__main__":
    main() 