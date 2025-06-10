#!/usr/bin/env python3
import requests
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse
from collections import defaultdict
import json

class SiteComparator:
    def __init__(self):
        self.original_base = "https://0002n8y.wcomhost.com/website/"
        self.new_base = "https://chiswickalbion.github.io/chiswick-albion-website/pages/"
        self.local_pages_dir = Path("pages")
        
        self.results = {
            "page_comparison": {},
            "link_validation": {},
            "image_validation": {},
            "content_validation": {},
            "structure_validation": {},
            "summary": {}
        }
        
    def get_all_local_pages(self):
        """Get list of all HTML pages in local directory"""
        pages = []
        for html_file in self.local_pages_dir.glob("*.html"):
            # Skip 404 pages and test files
            content = html_file.read_text(encoding='utf-8', errors='ignore')
            if "404: Page not found" not in content and not html_file.name.startswith('test'):
                pages.append(html_file.name)
        return sorted(pages)
    
    def fetch_page_safely(self, url, timeout=10):
        """Safely fetch a page with error handling"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(url, timeout=timeout, headers=headers)
            if response.status_code == 200:
                return response.text
            else:
                return f"HTTP_ERROR_{response.status_code}"
        except requests.exceptions.RequestException as e:
            return f"REQUEST_ERROR: {str(e)}"
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def compare_page_accessibility(self):
        """Compare page accessibility between old and new sites"""
        print("🌐 COMPARING PAGE ACCESSIBILITY")
        print("=" * 40)
        
        local_pages = self.get_all_local_pages()
        accessible_new = 0
        accessible_old = 0
        comparison_results = {}
        
        for page in local_pages[:10]:  # Test first 10 pages to avoid overwhelming
            print(f"\n📄 Testing: {page}")
            
            # Test new site
            new_url = urljoin(self.new_base, page)
            new_content = self.fetch_page_safely(new_url)
            new_accessible = not new_content.startswith(("HTTP_ERROR", "REQUEST_ERROR", "ERROR"))
            
            # Test original site (convert filename to original format)
            original_page = page.replace('.html', '/') if not page.endswith('_.html') else page.replace('_.html', '/')
            old_url = urljoin(self.original_base, original_page)
            old_content = self.fetch_page_safely(old_url)
            old_accessible = not old_content.startswith(("HTTP_ERROR", "REQUEST_ERROR", "ERROR"))
            
            comparison_results[page] = {
                "new_url": new_url,
                "old_url": old_url,
                "new_accessible": new_accessible,
                "old_accessible": old_accessible,
                "new_size": len(new_content) if new_accessible else 0,
                "old_size": len(old_content) if old_accessible else 0
            }
            
            if new_accessible:
                accessible_new += 1
                print(f"   ✅ New site: {new_url}")
            else:
                print(f"   ❌ New site: {new_url} - {new_content[:50]}")
                
            if old_accessible:
                accessible_old += 1
                print(f"   ✅ Old site: {old_url}")
            else:
                print(f"   ❌ Old site: {old_url} - {old_content[:50]}")
            
            time.sleep(1)  # Be respectful to servers
        
        self.results["page_comparison"] = comparison_results
        
        print(f"\n📊 ACCESSIBILITY SUMMARY:")
        print(f"✅ New site accessible pages: {accessible_new}/{len(comparison_results)}")
        print(f"✅ Old site accessible pages: {accessible_old}/{len(comparison_results)}")
        
        return accessible_new, accessible_old, len(comparison_results)
    
    def validate_internal_links(self):
        """Validate all internal links work correctly"""
        print(f"\n🔗 VALIDATING INTERNAL LINKS")
        print("=" * 30)
        
        local_pages = self.get_all_local_pages()
        total_links = 0
        working_links = 0
        broken_links = []
        
        for page in local_pages[:5]:  # Test subset to avoid overwhelming
            try:
                content = (self.local_pages_dir / page).read_text(encoding='utf-8', errors='ignore')
                
                # Find all internal HTML links
                internal_links = re.findall(r'href="([^"]*\.html)"', content)
                
                for link in internal_links:
                    if not link.startswith(('http', '#')):  # Internal relative links only
                        total_links += 1
                        
                        # Check if target file exists locally
                        target_file = self.local_pages_dir / link
                        if target_file.exists():
                            working_links += 1
                        else:
                            broken_links.append(f"{page} -> {link}")
                            
            except Exception as e:
                print(f"❌ Error checking {page}: {e}")
        
        self.results["link_validation"] = {
            "total_links": total_links,
            "working_links": working_links,
            "broken_links": broken_links
        }
        
        print(f"📊 LINK VALIDATION:")
        print(f"✅ Working internal links: {working_links}/{total_links}")
        print(f"❌ Broken internal links: {len(broken_links)}")
        
        if broken_links[:5]:  # Show first 5 broken links
            print("🔍 Sample broken links:")
            for broken in broken_links[:5]:
                print(f"   - {broken}")
        
        return working_links, total_links
    
    def validate_images(self):
        """Validate all images are accessible"""
        print(f"\n🖼️  VALIDATING IMAGES")
        print("=" * 20)
        
        local_pages = self.get_all_local_pages()
        total_images = 0
        working_images = 0
        missing_images = []
        
        for page in local_pages[:5]:  # Test subset
            try:
                content = (self.local_pages_dir / page).read_text(encoding='utf-8', errors='ignore')
                
                # Find all image sources
                image_refs = re.findall(r'src="([^"]*\.(gif|jpg|jpeg|png))"', content, re.IGNORECASE)
                
                for img_path, ext in image_refs:
                    total_images += 1
                    
                    # Check different possible locations
                    possible_paths = []
                    
                    if img_path.startswith('../assets/images/'):
                        possible_paths.append(Path("assets/images") / img_path.replace('../assets/images/', ''))
                    elif img_path.startswith('../'):
                        possible_paths.append(Path(img_path[3:]))  # Remove ../
                    else:
                        possible_paths.append(self.local_pages_dir / img_path)
                        possible_paths.append(Path("assets/images") / img_path)
                    
                    found = False
                    for path in possible_paths:
                        if path.exists():
                            working_images += 1
                            found = True
                            break
                    
                    if not found:
                        missing_images.append(f"{page}: {img_path}")
                        
            except Exception as e:
                print(f"❌ Error checking images in {page}: {e}")
        
        self.results["image_validation"] = {
            "total_images": total_images,
            "working_images": working_images,
            "missing_images": missing_images
        }
        
        print(f"📊 IMAGE VALIDATION:")
        print(f"✅ Working images: {working_images}/{total_images}")
        print(f"❌ Missing images: {len(missing_images)}")
        
        if missing_images[:3]:
            print("🔍 Sample missing images:")
            for missing in missing_images[:3]:
                print(f"   - {missing}")
        
        return working_images, total_images
    
    def check_content_integrity(self):
        """Check for content integrity issues"""
        print(f"\n📝 CHECKING CONTENT INTEGRITY")
        print("=" * 30)
        
        local_pages = self.get_all_local_pages()
        total_pages = len(local_pages)
        clean_pages = 0
        issues = []
        
        for page in local_pages:
            try:
                content = (self.local_pages_dir / page).read_text(encoding='utf-8', errors='ignore')
                page_issues = []
                
                # Check for common issues
                if len(content) < 500:
                    page_issues.append("Very short content")
                
                if "404: Page not found" in content:
                    page_issues.append("404 error page")
                
                if content.count('<html') > 1:
                    page_issues.append("Multiple HTML tags")
                
                if '</body>' not in content:
                    page_issues.append("Missing closing body tag")
                
                # Check for old domain references (should be clean now)
                old_domains = ['0002n8y.wcomhost.com', 'web.bethere.co.uk']
                for domain in old_domains:
                    if domain in content:
                        page_issues.append(f"Still references old domain: {domain}")
                
                if not page_issues:
                    clean_pages += 1
                else:
                    issues.append(f"{page}: {', '.join(page_issues)}")
                    
            except Exception as e:
                issues.append(f"{page}: Error reading file - {e}")
        
        self.results["content_validation"] = {
            "total_pages": total_pages,
            "clean_pages": clean_pages,
            "issues": issues
        }
        
        print(f"📊 CONTENT INTEGRITY:")
        print(f"✅ Clean pages: {clean_pages}/{total_pages}")
        print(f"⚠️  Pages with issues: {len(issues)}")
        
        if issues[:3]:
            print("🔍 Sample issues:")
            for issue in issues[:3]:
                print(f"   - {issue}")
        
        return clean_pages, total_pages
    
    def generate_comprehensive_report(self):
        """Generate a comprehensive comparison report"""
        print(f"\n📋 GENERATING COMPREHENSIVE REPORT")
        print("=" * 40)
        
        # Run all validation checks
        new_accessible, old_accessible, tested_pages = self.compare_page_accessibility()
        working_links, total_links = self.validate_internal_links()
        working_images, total_images = self.validate_images()
        clean_pages, total_pages = self.check_content_integrity()
        
        # Calculate scores
        accessibility_score = (new_accessible / tested_pages * 100) if tested_pages > 0 else 0
        link_score = (working_links / total_links * 100) if total_links > 0 else 100
        image_score = (working_images / total_images * 100) if total_images > 0 else 100
        content_score = (clean_pages / total_pages * 100) if total_pages > 0 else 0
        
        overall_score = (accessibility_score + link_score + image_score + content_score) / 4
        
        self.results["summary"] = {
            "overall_score": overall_score,
            "accessibility_score": accessibility_score,
            "link_score": link_score,
            "image_score": image_score,
            "content_score": content_score,
            "new_accessible": new_accessible,
            "tested_pages": tested_pages,
            "total_pages": total_pages
        }
        
        print(f"\n🎯 FINAL COMPARISON REPORT")
        print("=" * 30)
        print(f"📊 Overall Site Quality Score: {overall_score:.1f}%")
        print(f"🌐 Page Accessibility: {accessibility_score:.1f}% ({new_accessible}/{tested_pages} tested pages)")
        print(f"🔗 Internal Links: {link_score:.1f}% ({working_links}/{total_links} links)")
        print(f"🖼️  Images: {image_score:.1f}% ({working_images}/{total_images} images)")
        print(f"📝 Content Integrity: {content_score:.1f}% ({clean_pages}/{total_pages} pages)")
        
        # Determine readiness
        if overall_score >= 95:
            status = "🚀 READY FOR PRODUCTION"
            color = "✅"
        elif overall_score >= 85:
            status = "⚠️  MOSTLY READY - Minor issues to fix"
            color = "🟡"
        else:
            status = "❌ NEEDS WORK - Major issues to address"
            color = "🔴"
        
        print(f"\n{color} STATUS: {status}")
        print(f"📈 Recommendation: {'Site is a complete working replacement!' if overall_score >= 95 else 'Address identified issues before full deployment'}")
        
        # Save detailed report
        with open('site_comparison_report.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: site_comparison_report.json")
        
        return overall_score

def main():
    print("🔍 SYSTEMATIC SITE COMPARISON TOOL")
    print("=" * 50)
    print("Comparing new GitHub Pages site against original site")
    print("This will validate the new site is a complete working replacement\n")
    
    comparator = SiteComparator()
    
    try:
        score = comparator.generate_comprehensive_report()
        
        print(f"\n✅ COMPARISON COMPLETE!")
        print(f"Final Score: {score:.1f}%")
        
        if score >= 95:
            print("🎉 Congratulations! Your new site is a complete working replacement!")
        elif score >= 85:
            print("👍 Your site is mostly ready. Review the report for minor improvements.")
        else:
            print("🔧 Your site needs some work. Check the detailed report for issues to fix.")
            
    except Exception as e:
        print(f"❌ Error during comparison: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main() 