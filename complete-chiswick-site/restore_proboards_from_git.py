#!/usr/bin/env python3
import subprocess
import re
from pathlib import Path

def get_proboards_changes_from_git():
    """Get all proboards changes from the last commit"""
    print("🔍 ANALYZING GIT DIFF FOR PROBOARDS CHANGES")
    print("=" * 50)
    
    try:
        # Get the full diff of the last commit
        result = subprocess.run(['git', 'show', 'HEAD'], 
                              capture_output=True, text=True, check=True)
        diff_content = result.stdout
        
        # Find all proboards-related removals
        proboards_removals = []
        
        lines = diff_content.split('\n')
        current_file = None
        
        for line in lines:
            # Track which file we're in
            if line.startswith('diff --git'):
                current_file = line.split('/')[-1] if '/' in line else None
            elif line.startswith('-') and not line.startswith('---'):
                # This is a removed line
                if 'proboards' in line.lower():
                    # Extract the URL from the line
                    url_match = re.search(r'href="(https?://[^"]*proboards[^"]*)"', line)
                    if url_match and current_file:
                        proboards_removals.append({
                            'file': current_file,
                            'removed_line': line.strip(),
                            'url': url_match.group(1),
                            'full_line': line[1:].strip()  # Remove the '-' prefix
                        })
        
        print(f"Found {len(proboards_removals)} proboards URL removals:")
        for removal in proboards_removals:
            print(f"  📁 {removal['file']}: {removal['url']}")
        
        return proboards_removals
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error getting git diff: {e}")
        return []

def restore_proboards_links(proboards_removals):
    """Restore the proboards links based on git analysis"""
    pages_dir = Path("pages")
    restored_count = 0
    files_modified = set()
    
    print(f"\n🔄 RESTORING PROBOARDS LINKS")
    print("=" * 30)
    
    for removal in proboards_removals:
        file_path = pages_dir / removal['file']
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            continue
            
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Find the line that had the proboards URL removed
            # Look for area tags that are missing the href for proboards
            original_line = removal['full_line']
            
            # The removed line should now be missing the href attribute
            # Let's find the corresponding line with missing href
            
            # Extract the coordinates from the original line
            coords_match = re.search(r'coords="([^"]*)"', original_line)
            if coords_match:
                coords = coords_match.group(1)
                
                # Find the line with these coordinates but missing href
                pattern = rf'<area[^>]*coords="{re.escape(coords)}"[^>]*(?<!href="[^"]*")>'
                
                # More specific: find area with coords but no href
                area_pattern = rf'<area([^>]*coords="{re.escape(coords)}"[^>]*)>'
                area_match = re.search(area_pattern, content)
                
                if area_match:
                    area_attrs = area_match.group(1)
                    if 'href=' not in area_attrs:
                        # This area is missing its href - restore it
                        old_area = area_match.group(0)
                        new_area = f'<area{area_attrs} href="{removal["url"]}">'
                        
                        content = content.replace(old_area, new_area)
                        restored_count += 1
                        files_modified.add(removal['file'])
                        
                        print(f"✅ Restored in {removal['file']}: {removal['url']}")
                    else:
                        print(f"⚠️  Area already has href in {removal['file']}")
                else:
                    print(f"❌ Could not find matching area in {removal['file']}")
            
            # Write the updated content
            if removal['file'] in files_modified:
                file_path.write_text(content, encoding='utf-8')
                
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            continue
    
    print(f"\n🎯 RESTORATION SUMMARY:")
    print(f"✅ Proboards links restored: {restored_count}")
    print(f"✅ Files modified: {len(files_modified)}")
    
    return restored_count > 0

def verify_proboards_links():
    """Verify that proboards links are now active"""
    pages_dir = Path("pages")
    
    print(f"\n🔍 VERIFYING PROBOARDS LINKS...")
    
    proboards_links = []
    
    for html_file in pages_dir.glob("*.html"):
        try:
            content = html_file.read_text(encoding='utf-8', errors='ignore')
            
            # Find active proboards links (not in comments)
            non_comment_content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
            
            proboards_matches = re.findall(r'href="(https?://[^"]*proboards[^"]*)"', non_comment_content)
            
            for match in proboards_matches:
                proboards_links.append({
                    'file': html_file.name,
                    'url': match
                })
                
        except Exception as e:
            continue
    
    print(f"✅ Found {len(proboards_links)} active proboards links:")
    for link in proboards_links:
        print(f"  📁 {link['file']}: {link['url']}")
    
    return len(proboards_links) > 0

if __name__ == "__main__":
    # Get proboards changes from git
    proboards_removals = get_proboards_changes_from_git()
    
    if not proboards_removals:
        print("📝 No proboards removals found in git history")
        exit(0)
    
    # Restore the proboards links
    restored = restore_proboards_links(proboards_removals)
    
    # Verify restoration
    verified = verify_proboards_links()
    
    if restored:
        print(f"\n🚀 SUCCESS! Proboards forum links have been restored!")
        print("These legitimate external forum references are now active again.")
        print("\nReady to commit these corrections!")
    else:
        print(f"\n❌ No proboards links were restored")
        
    if verified:
        print(f"\n✅ Verification: Found active proboards links!")
    else:
        print(f"\n⚠️  Verification: No active proboards links found") 