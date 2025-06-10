#!/usr/bin/env python3
import os
import re
import shutil

def fix_image_paths(directory):
    # Create assets/images directory if it doesn't exist
    assets_dir = os.path.join(directory, 'assets', 'images')
    os.makedirs(assets_dir, exist_ok=True)
    
    # Walk through all HTML files
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Find all image references
                img_refs = re.findall(r'src="([^"]*\.(gif|jpg|jpeg|png))"', content, re.IGNORECASE)
                modified = False
                
                for img_ref, ext in img_refs:
                    # Handle relative paths
                    if not img_ref.startswith(('http://', 'https://')):
                        # Extract filename
                        filename = os.path.basename(img_ref)
                        new_path = f'../assets/images/{filename}'
                        
                        # Copy image to assets directory if it exists and is not already there
                        old_path = os.path.join(os.path.dirname(file_path), img_ref)
                        dest_path = os.path.join(assets_dir, filename)
                        if os.path.exists(old_path) and os.path.abspath(old_path) != os.path.abspath(dest_path):
                            shutil.copy2(old_path, dest_path)
                        if img_ref != new_path:
                            content = content.replace(f'src="{img_ref}"', f'src="{new_path}"')
                            modified = True
                
                # Save changes if modified
                if modified:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Updated image paths in {file_path}")

def verify_images(directory):
    broken_images = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Find all image references
                img_refs = re.findall(r'src="([^"]*\.(gif|jpg|jpeg|png))"', content, re.IGNORECASE)
                
                for img_ref, _ in img_refs:
                    if not img_ref.startswith(('http://', 'https://')):
                        img_path = os.path.join(os.path.dirname(file_path), img_ref)
                        if not os.path.exists(img_path):
                            broken_images.append({
                                'file': file_path,
                                'image': img_ref,
                                'path': img_path
                            })
    
    return broken_images

if __name__ == "__main__":
    site_dir = os.path.dirname(os.path.abspath(__file__))
    print("Fixing image paths...")
    fix_image_paths(site_dir)
    
    print("\nVerifying images...")
    broken = verify_images(site_dir)
    if broken:
        print("\nBroken images found:")
        for item in broken:
            print(f"File: {item['file']}")
            print(f"Image: {item['image']}")
            print(f"Path: {item['path']}\n")
    else:
        print("All images are valid!") 