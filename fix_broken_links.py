#!/usr/bin/env python3
import requests
import time
from pathlib import Path
import re

# The 20 broken files that need fixing
BROKEN_FILES = [
    'SW07.html',
    'SWay2002.html', 
    'champs08.html',
    'champs200203.html',
    'clubhistory.html',
    'details.html',
    'hist0203.html',
    'hist0304.html',
    'hist0405.html',
    'hist0506.html',
    'hist0607.html',
    'history3.html',
    'homegrounds.html',
    'honours.html',
    'horbach.html',
    'nextgame.html',
    'records.html',
    'top25.html',
    'videos.html',
    'yearbyyear.html'
]

BASE_ORIGINAL_URL = "https://0002n8y.wcomhost.com/website"

def fix_broken_files():
    pages_dir = Path("pages")
    fixed_count = 0
    failed_count = 0
    
    print("🔧 FIXING BROKEN FILES...")
    print(f"Found {len(BROKEN_FILES)} files to fix\n")
    
    for filename in BROKEN_FILES:
        print(f"Processing {filename}...", end=" ")
        
        # Convert filename to URL path (remove .html)
        page_name = filename.replace('.html', '')
        original_url = f"{BASE_ORIGINAL_URL}/{page_name}/"
        
        try:
            # Fetch content from original site
            response = requests.get(original_url, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # Basic check - make sure it's not a 404 page
                if "404" not in content.lower() and "not found" not in content.lower():
                    # Write the content to our file
                    file_path = pages_dir / filename
                    file_path.write_text(content, encoding='utf-8')
                    print("✅ FIXED")
                    fixed_count += 1
                else:
                    print("❌ ORIGINAL ALSO 404")
                    failed_count += 1
            else:
                print(f"❌ HTTP {response.status_code}")
                failed_count += 1
                
        except requests.RequestException as e:
            print(f"❌ ERROR: {e}")
            failed_count += 1
        except Exception as e:
            print(f"❌ UNEXPECTED ERROR: {e}")
            failed_count += 1
        
        # Be nice to the server
        time.sleep(0.5)
    
    print(f"\n📊 SUMMARY:")
    print(f"✅ Fixed: {fixed_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📝 Total: {len(BROKEN_FILES)}")
    
    if fixed_count > 0:
        print(f"\n🚀 SUCCESS! Fixed {fixed_count} files.")
        print("You can now commit and push these changes to GitHub!")
    
    return fixed_count, failed_count

if __name__ == "__main__":
    fix_broken_files() 