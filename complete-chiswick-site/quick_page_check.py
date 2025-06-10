#!/usr/bin/env python3
"""
Quick Page Checker
Simple tool to check key pages without heavy dependencies
"""

import requests
import time

def check_page_pair(page_name):
    """Check if both old and new versions of a page are accessible"""
    
    old_url = f"https://0002n8y.wcomhost.com/website/{page_name}/"
    new_url = f"https://chiswickalbion.github.io/chiswick-albion-website/pages/{page_name}.html"
    
    try:
        print(f"\n📄 Checking: {page_name}")
        
        # Check old site
        old_response = requests.get(old_url, timeout=10)
        old_status = old_response.status_code
        old_size = len(old_response.text)
        
        # Check new site  
        new_response = requests.get(new_url, timeout=10)
        new_status = new_response.status_code
        new_size = len(new_response.text)
        
        print(f"   Old: {old_status} ({old_size} chars) - {old_url}")
        print(f"   New: {new_status} ({new_size} chars) - {new_url}")
        
        if old_status == 200 and new_status == 200:
            size_ratio = min(old_size, new_size) / max(old_size, new_size) if max(old_size, new_size) > 0 else 0
            if size_ratio < 0.5:
                print(f"   ⚠️  SIGNIFICANT SIZE DIFFERENCE: {size_ratio:.1%}")
                return 'size_diff'
            else:
                print(f"   ✅ Both accessible, similar size ({size_ratio:.1%})")
                return 'good'
        elif old_status != 200 and new_status == 200:
            print(f"   ℹ️  New site only (old site 404)")
            return 'new_only'
        elif old_status == 200 and new_status != 200:
            print(f"   ❌ OLD SITE WORKS, NEW SITE BROKEN")
            return 'broken'
        else:
            print(f"   ❌ Both inaccessible")
            return 'both_broken'
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return 'error'

def main():
    """Check critical pages"""
    
    # Focus on most important pages that users are likely to visit
    critical_pages = [
        'home',
        'honours', 
        'records',
        'top25', 
        'videos',
        'nextgame',
        'History1',
        'everyplayer',
        'squad_page2',
        'season2022',
        'latest_page2'
    ]
    
    print("🔍 QUICK PAGE ACCESSIBILITY CHECK")
    print("=" * 50)
    
    results = {'good': 0, 'size_diff': 0, 'new_only': 0, 'broken': 0, 'both_broken': 0, 'error': 0}
    
    for page in critical_pages:
        result = check_page_pair(page)
        results[result] += 1
        time.sleep(0.5)  # Brief pause
    
    print(f"\n📊 RESULTS SUMMARY:")
    print(f"✅ Working well: {results['good']}")
    print(f"⚠️  Size differences: {results['size_diff']}")
    print(f"ℹ️  New site only: {results['new_only']}")
    print(f"❌ Broken on new site: {results['broken']}")
    print(f"❌ Both broken: {results['both_broken']}")
    print(f"❌ Errors: {results['error']}")
    
    if results['broken'] > 0:
        print(f"\n🚨 HIGH PRIORITY: {results['broken']} pages broken on new site!")
    elif results['size_diff'] > 0:
        print(f"\n⚠️  MEDIUM PRIORITY: {results['size_diff']} pages have content differences")
    else:
        print(f"\n✅ All critical pages look good!")

if __name__ == "__main__":
    main() 