#!/usr/bin/env python3
"""
Fix Broken Season Pages
Replace error pages with actual content from the _suffixed files
"""

import os
import shutil
from pathlib import Path

def fix_season_page(season_name):
    """Fix a broken season page by copying from the actual content file"""
    
    broken_file = f"pages/{season_name}.html"
    content_file = f"pages/{season_name}_.html"
    
    print(f"\n🔧 FIXING: {season_name}")
    print("=" * 50)
    
    if not os.path.exists(content_file):
        print(f"❌ Content file not found: {content_file}")
        return False
        
    if not os.path.exists(broken_file):
        print(f"❌ Broken file not found: {broken_file}")
        return False
    
    try:
        # Check current broken file size
        broken_size = os.path.getsize(broken_file)
        content_size = os.path.getsize(content_file)
        
        print(f"📄 Broken file: {broken_size} bytes")
        print(f"📄 Content file: {content_size} bytes")
        
        if broken_size < 1000 and content_size > 1000:
            # Copy the good content over the broken file
            shutil.copy2(content_file, broken_file)
            print(f"✅ Fixed: Copied {content_file} → {broken_file}")
            return True
        else:
            print(f"ℹ️  File sizes suggest no fix needed")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {season_name}: {e}")
        return False

def fix_clubhistory():
    """Fix clubhistory page which has content mismatch"""
    
    broken_file = "pages/clubhistory.html"
    
    print(f"\n🔧 FIXING: clubhistory")
    print("=" * 50)
    
    # Check if there's a clubhistory_ file
    content_file = "pages/clubhistory_.html"
    if os.path.exists(content_file):
        try:
            shutil.copy2(content_file, broken_file) 
            print(f"✅ Fixed: Copied {content_file} → {broken_file}")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    else:
        print(f"❌ No content file found for clubhistory")
        return False

def main():
    """Fix all broken season pages"""
    
    print("🛠️  FIXING BROKEN SEASON PAGES")
    print("=" * 60)
    
    # Critical season pages that were identified as broken
    broken_seasons = [
        'season2021',
        'season1920', 
        'season1819',
        'season1718',
        'season1617',
        'season1516',
        'season1415',
        'season1314',
        'season1213a',
        'season09-10'
    ]
    
    fixed_count = 0
    
    for season in broken_seasons:
        if fix_season_page(season):
            fixed_count += 1
    
    # Fix clubhistory separately
    if fix_clubhistory():
        fixed_count += 1
    
    print(f"\n📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully fixed: {fixed_count} pages")
    print(f"🎯 These pages should now display proper content instead of error messages")
    
    # Also check for other common redirect patterns
    other_broken = [
        'legends',
        'oldplayers', 
        'players72',
        'doyouremember',
        'playerawards',
        'squad',
        'latest'
    ]
    
    print(f"\n🔍 CHECKING OTHER COMMON BROKEN PAGES")
    print("=" * 60)
    
    for page in other_broken:
        broken_file = f"pages/{page}.html"
        content_file = f"pages/{page}_index.html"
        
        if os.path.exists(broken_file) and os.path.exists(content_file):
            broken_size = os.path.getsize(broken_file)
            if broken_size < 1000:
                try:
                    shutil.copy2(content_file, broken_file)
                    print(f"✅ Fixed: {page}.html")
                    fixed_count += 1
                except Exception as e:
                    print(f"❌ Error fixing {page}: {e}")
        elif os.path.exists(broken_file):
            # Check if there's a page2 version
            content_file = f"pages/{page}_page2.html"
            if os.path.exists(content_file):
                broken_size = os.path.getsize(broken_file)
                if broken_size < 1000:
                    try:
                        shutil.copy2(content_file, broken_file)
                        print(f"✅ Fixed: {page}.html (using page2)")
                        fixed_count += 1
                    except Exception as e:
                        print(f"❌ Error fixing {page}: {e}")
    
    print(f"\n🎉 TOTAL FIXED: {fixed_count} pages")

if __name__ == "__main__":
    main() 