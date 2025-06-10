#!/usr/bin/env python3
"""
Comprehensive Site Fixer
Find broken links and mismatched images, then fix them
"""

import requests
import os
import time
import json
from pathlib import Path
import urllib.parse

def check_page_and_images(page_name, max_retries=2):
    """Check a specific page and compare its images with the original"""
    
    old_url = f"https://0002n8y.wcomhost.com/website/{page_name}/"
    new_url = f"https://chiswickalbion.github.io/chiswick-albion-website/pages/{page_name}.html"
    
    print(f"\n🔍 ANALYZING: {page_name}")
    print("=" * 60)
    
    result = {
        'page': page_name,
        'status': 'unknown',
        'old_accessible': False,
        'new_accessible': False,
        'old_url': old_url,
        'new_url': new_url,
        'old_size': 0,
        'new_size': 0,
        'similarity': 0,
        'image_issues': [],
        'broken_links': []
    }
    
    try:
        # Check old site
        print("📡 Fetching old site...")
        old_response = requests.get(old_url, timeout=10)
        result['old_accessible'] = old_response.status_code == 200
        result['old_size'] = len(old_response.text)
        
        # Check new site  
        print("📡 Fetching new site...")
        new_response = requests.get(new_url, timeout=10)
        result['new_accessible'] = new_response.status_code == 200
        result['new_size'] = len(new_response.text)
        
        print(f"🌐 Old site: {'✅' if result['old_accessible'] else '❌'} {result['old_size']} chars")
        print(f"🌐 New site: {'✅' if result['new_accessible'] else '❌'} {result['new_size']} chars")
        
        if result['old_accessible'] and result['new_accessible']:
            # Calculate similarity
            if max(result['old_size'], result['new_size']) > 0:
                result['similarity'] = min(result['old_size'], result['new_size']) / max(result['old_size'], result['new_size'])
            
            print(f"📊 Content similarity: {result['similarity']:.1%}")
            
            if result['similarity'] < 0.8:
                result['status'] = 'content_mismatch'
                print("⚠️  SIGNIFICANT CONTENT DIFFERENCE")
                
                # Check for specific issues
                if result['new_size'] < 500:
                    print("🚨 NEW SITE APPEARS TO BE ERROR PAGE")
                    result['status'] = 'error_page'
                    
            elif result['similarity'] >= 0.9:
                result['status'] = 'good'
                print("✅ Content appears similar")
            else:
                result['status'] = 'minor_diff'
                print("⚠️  Minor content differences")
                
            # Look for image references in old site
            old_text = old_response.text.lower()
            if '.gif' in old_text or '.jpg' in old_text or '.png' in old_text:
                print("🖼️  Checking for image references...")
                # Extract potential image names
                import re
                img_pattern = r'src="([^"]*\.(gif|jpg|png))"'
                old_images = re.findall(img_pattern, old_text, re.IGNORECASE)
                
                if old_images:
                    print(f"   Found {len(old_images)} image references in old site")
                    result['image_issues'] = [img[0] for img in old_images[:5]]  # First 5 images
                    
        elif not result['old_accessible'] and result['new_accessible']:
            result['status'] = 'new_only'
            print("ℹ️  New site only (old site 404)")
        elif result['old_accessible'] and not result['new_accessible']:
            result['status'] = 'broken'
            print("🚨 OLD SITE WORKS, NEW SITE BROKEN!")
        else:
            result['status'] = 'both_broken'
            print("❌ Both sites inaccessible")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        result['status'] = 'error'
    
    return result

def download_missing_image(image_url, local_path):
    """Download a missing image from the old site"""
    try:
        print(f"📥 Downloading: {image_url}")
        response = requests.get(image_url, timeout=10)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ Saved: {local_path}")
            return True
        else:
            print(f"❌ Failed to download: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Download error: {e}")
        return False

def find_broken_redirects():
    """Find HTML files that contain redirect/error content instead of real content"""
    
    print("\n🔍 SCANNING FOR BROKEN REDIRECT PAGES")
    print("=" * 60)
    
    pages_dir = Path("pages")
    broken_pages = []
    
    error_patterns = [
        "301 Moved Permanently",
        "403 Forbidden", 
        "404 Not Found",
        "The document has moved",
        "<h1>Moved Permanently</h1>",
        "nginx",
        "openresty"
    ]
    
    for html_file in pages_dir.glob("*.html"):
        try:
            content = html_file.read_text(encoding='utf-8', errors='ignore')
            
            # Check if it's a small file with error content
            if len(content) < 1000:  # Less than 1KB is suspicious
                for pattern in error_patterns:
                    if pattern in content:
                        print(f"🚨 BROKEN: {html_file.name} - Contains '{pattern}'")
                        broken_pages.append({
                            'file': html_file.name,
                            'size': len(content),
                            'error_type': pattern
                        })
                        break
                        
        except Exception as e:
            print(f"❌ Error reading {html_file}: {e}")
    
    return broken_pages

def main():
    """Main function to systematically fix the site"""
    
    print("🛠️  COMPREHENSIVE SITE FIXER")
    print("=" * 60)
    print("Finding broken links and mismatched images...")
    
    # First, find obvious broken redirect pages
    broken_redirects = find_broken_redirects()
    print(f"\n📊 Found {len(broken_redirects)} broken redirect pages")
    
    # Test critical pages that users are likely to visit
    critical_pages = [
        'honours', 'records', 'top25', 'videos', 'nextgame', 'History1',
        'everyplayer_index', 'squad_page2', 'season2021', 'season2020', 
        'latest_page2', 'clubhistory', 'legends_index', 'players2020', 
        'fixtures2023', 'season1920', 'season1819', 'season1718',
        'dopple_index', 'playerawards_page2', 'sundaycup_index',
        'tables2022', 'cups2022', 'fac202122_index'
    ]
    
    print(f"\n🎯 TESTING {len(critical_pages)} CRITICAL PAGES")
    print("=" * 60)
    
    results = []
    issues_found = []
    
    for page in critical_pages:
        result = check_page_and_images(page)
        results.append(result)
        
        # Collect issues
        if result['status'] in ['broken', 'error_page', 'content_mismatch']:
            issues_found.append(result)
            
        time.sleep(0.5)  # Be respectful
    
    # Summary
    print(f"\n📊 SUMMARY RESULTS")
    print("=" * 60)
    
    status_counts = {}
    for result in results:
        status = result['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in status_counts.items():
        emoji = {"good": "✅", "minor_diff": "⚠️", "content_mismatch": "⚠️", 
                "error_page": "🚨", "broken": "❌", "new_only": "ℹ️", 
                "both_broken": "❌", "error": "❌"}.get(status, "❓")
        print(f"{emoji} {status}: {count}")
    
    # Save detailed results
    with open('comprehensive_analysis.json', 'w') as f:
        json.dump({
            'broken_redirects': broken_redirects,
            'page_analysis': results,
            'critical_issues': issues_found
        }, f, indent=2)
    
    print(f"\n💾 Detailed analysis saved to: comprehensive_analysis.json")
    
    # Priority actions
    if issues_found:
        print(f"\n🚨 HIGH PRIORITY FIXES NEEDED:")
        for issue in issues_found[:5]:  # Top 5 issues
            print(f"   - {issue['page']}: {issue['status']}")
    
    if broken_redirects:
        print(f"\n🔧 BROKEN REDIRECT PAGES TO FIX:")
        for page in broken_redirects[:5]:  # Top 5
            print(f"   - {page['file']}: {page['error_type']}")

if __name__ == "__main__":
    main() 