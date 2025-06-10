#!/usr/bin/env python3
import requests
import time
from pathlib import Path
import re

# Map of pages to their missing images and original URLs
MISSING_IMAGES_MAP = {
    'videos.html': {
        'base_url': 'https://0002n8y.wcomhost.com/website/videos/',
        'images': ['img1.gif']  # Already downloaded, but keeping for reference
    },
    'SWay2002.html': {
        'base_url': 'https://0002n8y.wcomhost.com/website/SWay2002/',
        'images': ['img2.gif', 'img3.gif']
    },
    'hist0304.html': {
        'base_url': 'https://0002n8y.wcomhost.com/website/hist0304/',
        'images': ['img2.gif', 'img3.gif', 'img4.gif', 'img5.gif', 'img6.gif']
    },
    'horbach.html': {
        'base_url': 'https://0002n8y.wcomhost.com/website/horbach/',
        'images': ['img2.gif', 'img3.gif', 'img4.gif', 'img5.gif', 'img6.gif', 'img7.gif']
    },
    'hist0405.html': {
        'base_url': 'https://0002n8y.wcomhost.com/website/hist0405/',
        'images': ['img2.gif', 'img3.gif', 'img4.gif', 'img5.gif']
    },
    'hist0203.html': {
        'base_url': 'https://0002n8y.wcomhost.com/website/hist0203/',
        'images': ['img2.gif', 'img3.gif', 'img4.gif', 'img5.gif', 'img6.gif']
    },
    'hist0506.html': {
        'base_url': 'https://0002n8y.wcomhost.com/website/hist0506/',
        'images': ['img2.gif', 'img3.gif', 'img4.gif', 'img5.gif']
    }
}

def download_missing_images():
    pages_dir = Path("pages")
    total_downloaded = 0
    total_failed = 0
    
    print("📥 DOWNLOADING ALL MISSING IMAGES...")
    print(f"Processing {len(MISSING_IMAGES_MAP)} pages with missing images\n")
    
    for page_name, info in MISSING_IMAGES_MAP.items():
        print(f"🔍 Processing {page_name}...")
        base_url = info['base_url']
        images = info['images']
        
        page_downloaded = 0
        page_failed = 0
        
        for img_name in images:
            img_path = pages_dir / img_name
            
            # Skip if already exists
            if img_path.exists():
                print(f"   ✅ {img_name} (already exists)")
                continue
                
            try:
                img_url = base_url + img_name
                print(f"   📥 Downloading {img_name} from {img_url}...", end=" ")
                
                response = requests.get(img_url, timeout=15)
                
                if response.status_code == 200:
                    img_path.write_bytes(response.content)
                    print("✅ SUCCESS")
                    page_downloaded += 1
                    total_downloaded += 1
                else:
                    print(f"❌ HTTP {response.status_code}")
                    page_failed += 1
                    total_failed += 1
                    
            except Exception as e:
                print(f"❌ ERROR: {e}")
                page_failed += 1
                total_failed += 1
            
            # Be nice to the server
            time.sleep(0.3)
        
        print(f"   📊 {page_name}: {page_downloaded} downloaded, {page_failed} failed\n")
    
    print(f"🎯 FINAL SUMMARY:")
    print(f"✅ Total images downloaded: {total_downloaded}")
    print(f"❌ Total failed: {total_failed}")
    
    return total_downloaded, total_failed

def verify_fixes():
    """Re-run image analysis to see what's still broken"""
    print("\n🔍 VERIFYING FIXES...")
    
    from fix_image_paths import analyze_and_fix_image_issues
    
    try:
        fixed, broken = analyze_and_fix_image_issues()
        return len(broken) == 0
    except:
        print("❌ Could not verify - please run the image path analyzer manually")
        return False

if __name__ == "__main__":
    # Download all missing images
    downloaded, failed = download_missing_images()
    
    if downloaded > 0:
        print(f"\n🚀 SUCCESS! Downloaded {downloaded} missing images")
        
        # Verify the fixes
        if verify_fixes():
            print("🎉 ALL IMAGE ISSUES RESOLVED!")
        else:
            print("⚠️  Some issues may remain - check the verification output above")
    else:
        print("\n📝 No new images were downloaded") 