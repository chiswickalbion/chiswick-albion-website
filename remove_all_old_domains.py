#!/usr/bin/env python3
import re
from pathlib import Path

# All old domains to remove
OLD_DOMAINS = [
    "0002n8y.wcomhost.com",
    "web.bethere.co.uk",
    "bethere.co.uk", 
    "chiswickalbion.proboards.com",
    "chiswickalbion.proboards20.com"
]

def remove_all_old_domain_references():
    """Remove all references to old domains"""
    pages_dir = Path("pages")
    
    print("🧹 COMPREHENSIVE OLD DOMAIN CLEANUP")
    print("=" * 50)
    
    total_files_cleaned = 0
    total_refs_removed = 0
    
    for domain in OLD_DOMAINS:
        print(f"\n🔍 Processing domain: {domain}")
        
        files_cleaned = 0
        refs_removed = 0
        
        for html_file in pages_dir.glob("*.html"):
            try:
                content = html_file.read_text(encoding='utf-8', errors='ignore')
                
                # Skip 404 pages
                if "404: Page not found" in content:
                    continue
                
                original_content = content
                changes_made = False
                
                # Find all references to this domain
                patterns = [
                    rf'https?://{re.escape(domain)}[^"\s]*',
                    rf'href="https?://{re.escape(domain)}[^"]*"',
                    rf'{re.escape(domain)}[^"\s]*'
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    
                    for match in matches:
                        # Comment out the reference
                        if match in content:
                            content = content.replace(match, f"<!-- REMOVED: {match} -->")
                            changes_made = True
                            refs_removed += 1
                
                # Also disable area map links
                area_pattern = rf'<area[^>]*href="[^"]*{re.escape(domain)}[^"]*"[^>]*>'
                area_matches = re.findall(area_pattern, content)
                
                for area_match in area_matches:
                    # Remove the href attribute
                    disabled_area = re.sub(r'href="[^"]*"', '', area_match)
                    content = content.replace(area_match, disabled_area)
                    changes_made = True
                    refs_removed += 1
                
                if changes_made:
                    html_file.write_text(content, encoding='utf-8')
                    files_cleaned += 1
                    
            except Exception as e:
                continue
        
        print(f"   ✅ {files_cleaned} files cleaned, {refs_removed} references removed")
        total_files_cleaned += files_cleaned
        total_refs_removed += refs_removed
    
    print(f"\n🎯 FINAL SUMMARY:")
    print(f"✅ Total files cleaned: {total_files_cleaned}")  
    print(f"✅ Total references removed: {total_refs_removed}")
    
    return total_files_cleaned, total_refs_removed

def verify_complete_cleanup():
    """Verify all old domains have been removed"""
    pages_dir = Path("pages")
    
    print(f"\n🔍 VERIFICATION - Checking for remaining old domains...")
    
    remaining_issues = {}
    
    for domain in OLD_DOMAINS:
        remaining_count = 0
        
        for html_file in pages_dir.glob("*.html"):
            try:
                content = html_file.read_text(encoding='utf-8', errors='ignore')
                
                # Check if domain exists outside of comments
                non_comment_content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
                
                if domain in non_comment_content:
                    remaining_count += 1
                    
            except Exception as e:
                continue
        
        if remaining_count > 0:
            remaining_issues[domain] = remaining_count
            print(f"⚠️  {domain}: {remaining_count} files still have active references")
        else:
            print(f"✅ {domain}: All references removed")
    
    if not remaining_issues:
        print("\n🎉 ALL OLD DOMAIN REFERENCES COMPLETELY REMOVED!")
        return True
    else:
        print(f"\n⚠️  {len(remaining_issues)} domains still have active references")
        return False

if __name__ == "__main__":
    # Clean all old domains
    files_cleaned, refs_removed = remove_all_old_domain_references()
    
    # Verify cleanup
    success = verify_complete_cleanup()
    
    if success and files_cleaned > 0:
        print(f"\n🚀 MISSION ACCOMPLISHED!")
        print("All old website references have been removed.")
        print("Your new GitHub Pages site is now completely independent!")
        print("\nReady to commit these changes!")
    elif files_cleaned > 0:
        print(f"\n⚠️  Partial cleanup completed - some references may remain")
    else:
        print(f"\n📝 No changes needed - site already clean!") 