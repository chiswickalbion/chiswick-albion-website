#!/usr/bin/env python3
"""
Image Fixer - Download missing or mismatched images
Compare images between old and new sites and download fixes
"""

import requests
import os
import hashlib
import time
from pathlib import Path
import re

def get_file_hash(filepath):
    """Get MD5 hash of a local file"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def download_image(old_url, local_path):
    """Download an image from the old site"""
    try:
        print(f"📥 Downloading: {old_url}")
        response = requests.get(old_url, timeout=15)
        if response.status_code == 200:
            # Create directory if needed
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            size_kb = len(response.content) / 1024
            print(f"✅ Downloaded: {local_path} ({size_kb:.1f} KB)")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def compare_page_images(page_name):
    """Compare images used in a specific page between old and new sites"""
    
    old_url = f"https://0002n8y.wcomhost.com/website/{page_name}/"
    
    print(f"\n🔍 CHECKING IMAGES FOR: {page_name}")
    print("=" * 60)
    
    try:
        # Get the old page content
        response = requests.get(old_url, timeout=10)
        if response.status_code != 200:
            print(f"❌ Old page not accessible: {response.status_code}")
            return []
            
        page_content = response.text
        
        # Extract image references using regex
        img_pattern = r'src="([^"]*\.(gif|jpg|png|jpeg))"'
        image_refs = re.findall(img_pattern, page_content, re.IGNORECASE)
        
        if not image_refs:
            print("ℹ️  No images found in page")
            return []
        
        print(f"🖼️  Found {len(image_refs)} image references")
        
        downloads_needed = []
        
        for img_ref, ext in image_refs:
            # Clean up the image reference
            img_ref = img_ref.strip()
            
            # Skip if it's already a full URL
            if img_ref.startswith('http'):
                print(f"⏭️  Skipping external URL: {img_ref}")
                continue
            
            # Construct full old URL
            if img_ref.startswith('/'):
                old_img_url = f"https://0002n8y.wcomhost.com{img_ref}"
            else:
                old_img_url = f"https://0002n8y.wcomhost.com/website/{page_name}/{img_ref}"
            
            # Determine local path - try several possible locations
            possible_local_paths = [
                f"assets/images/{os.path.basename(img_ref)}",
                f"assets/images/{page_name}_{os.path.basename(img_ref)}",
                f"assets/images/{img_ref}",
            ]
            
            # Check if image exists locally
            local_exists = False
            local_path = None
            
            for path in possible_local_paths:
                if os.path.exists(path):
                    local_exists = True
                    local_path = path
                    break
            
            if not local_exists:
                # Image missing - needs download
                local_path = f"assets/images/{page_name}_{os.path.basename(img_ref)}"
                print(f"❌ Missing: {img_ref} → will download to {local_path}")
                downloads_needed.append((old_img_url, local_path))
                
            else:
                # Image exists - could check if it's the right one
                print(f"✅ Exists: {img_ref} → {local_path}")
        
        return downloads_needed
        
    except Exception as e:
        print(f"❌ Error checking {page_name}: {e}")
        return []

def fix_common_image_issues():
    """Fix known common image issues"""
    
    print("\n🛠️  FIXING COMMON IMAGE ISSUES")
    print("=" * 60)
    
    common_missing = [
        # Home page banner
        ("https://0002n8y.wcomhost.com/website/home/img0.gif", "assets/images/home_img0.gif"),
        
        # Club logo/banner variations
        ("https://0002n8y.wcomhost.com/website/home/img1.gif", "assets/images/home_img1.gif"),
        
        # Common page banners that might be missing
        ("https://0002n8y.wcomhost.com/website/honours/img1.gif", "assets/images/honours_img1.gif"),
        ("https://0002n8y.wcomhost.com/website/records/img1.gif", "assets/images/records_img1.gif"),
        ("https://0002n8y.wcomhost.com/website/videos/img1.gif", "assets/images/videos_img1.gif"),
        
        # Navigation elements
        ("https://0002n8y.wcomhost.com/website/History1/img1.gif", "assets/images/History1_img1.gif"),
    ]
    
    downloaded = 0
    
    for old_url, local_path in common_missing:
        if not os.path.exists(local_path):
            if download_image(old_url, local_path):
                downloaded += 1
            time.sleep(0.5)  # Be respectful
    
    return downloaded

def main():
    """Main image fixing function"""
    
    print("🖼️  IMAGE FIXER")
    print("=" * 60)
    print("Finding and downloading missing/mismatched images...")
    
    # Fix common issues first
    common_downloads = fix_common_image_issues()
    
    # Check specific pages that were identified as having issues
    problem_pages = [
        'season2021', 'season1920', 'season1819', 'season1718',
        'clubhistory', 'honours', 'records', 'videos', 'nextgame',
        'legends_index', 'everyplayer_index'
    ]
    
    print(f"\n🎯 CHECKING IMAGES IN PROBLEM PAGES")
    print("=" * 60)
    
    total_downloads = []
    
    for page in problem_pages:
        downloads = compare_page_images(page)
        total_downloads.extend(downloads)
        time.sleep(1)  # Be respectful to servers
    
    # Download all missing images
    if total_downloads:
        print(f"\n📥 DOWNLOADING {len(total_downloads)} MISSING IMAGES")
        print("=" * 60)
        
        successful = 0
        for old_url, local_path in total_downloads:
            if download_image(old_url, local_path):
                successful += 1
            time.sleep(1)  # Be respectful
        
        print(f"\n📊 DOWNLOAD SUMMARY")
        print("=" * 60)
        print(f"✅ Successfully downloaded: {successful}/{len(total_downloads)} images")
        print(f"✅ Common images fixed: {common_downloads}")
        print(f"🎯 Total new images: {successful + common_downloads}")
        
    else:
        print(f"\n✅ No missing images found in checked pages")
        print(f"✅ Common images fixed: {common_downloads}")

if __name__ == "__main__":
    main() 