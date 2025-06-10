#!/usr/bin/env python3
import re
from pathlib import Path
import json
from collections import defaultdict

class FunctionalTester:
    def __init__(self):
        self.pages_dir = Path("pages")
        self.assets_dir = Path("assets")
        self.test_results = {
            "navigation_test": {},
            "image_map_test": {},
            "external_links_test": {},
            "banner_consistency_test": {},
            "content_completeness_test": {},
            "file_structure_test": {}
        }
    
    def test_navigation_structure(self):
        """Test that navigation structure is complete and functional"""
        print("🧭 TESTING NAVIGATION STRUCTURE")
        print("=" * 35)
        
        # Key pages that should exist and be accessible
        critical_pages = [
            'home_.html',
            'honours.html', 
            'videos.html',
            'season2022_.html',
            'nextgame.html',
            'details.html',
            'records.html'
        ]
        
        existing_pages = []
        missing_pages = []
        navigation_links = defaultdict(list)
        
        for page in critical_pages:
            page_path = self.pages_dir / page
            if page_path.exists():
                existing_pages.append(page)
                
                # Analyze navigation links in this page
                try:
                    content = page_path.read_text(encoding='utf-8', errors='ignore')
                    # Find all internal navigation links
                    nav_links = re.findall(r'href="([^"]*\.html)"', content)
                    navigation_links[page] = [link for link in nav_links if not link.startswith('http')]
                except Exception as e:
                    print(f"❌ Error reading {page}: {e}")
            else:
                missing_pages.append(page)
        
        self.test_results["navigation_test"] = {
            "critical_pages_found": len(existing_pages),
            "critical_pages_total": len(critical_pages),
            "missing_pages": missing_pages,
            "navigation_links": dict(navigation_links)
        }
        
        print(f"📊 Critical pages found: {len(existing_pages)}/{len(critical_pages)}")
        if missing_pages:
            print(f"❌ Missing critical pages: {', '.join(missing_pages)}")
        else:
            print("✅ All critical pages found")
        
        return len(existing_pages) == len(critical_pages)
    
    def test_image_maps_functionality(self):
        """Test that image maps (clickable areas) are working correctly"""
        print(f"\n🗺️  TESTING IMAGE MAPS FUNCTIONALITY")
        print("=" * 35)
        
        pages_with_maps = []
        total_areas = 0
        working_areas = 0
        broken_areas = []
        
        for html_file in self.pages_dir.glob("*.html"):
            try:
                content = html_file.read_text(encoding='utf-8', errors='ignore')
                
                # Find image maps
                maps = re.findall(r'<map[^>]*name="([^"]*)"[^>]*>(.*?)</map>', content, re.DOTALL)
                
                if maps:
                    pages_with_maps.append(html_file.name)
                    
                    for map_name, map_content in maps:
                        # Find all areas in this map
                        areas = re.findall(r'<area[^>]*>', map_content)
                        
                        for area in areas:
                            total_areas += 1
                            
                            # Check if area has required attributes
                            has_coords = 'coords=' in area
                            has_shape = 'shape=' in area
                            has_href = 'href=' in area
                            
                            if has_coords and has_shape:
                                working_areas += 1
                            else:
                                broken_areas.append(f"{html_file.name}: {area[:50]}...")
                                
            except Exception as e:
                print(f"❌ Error checking {html_file.name}: {e}")
        
        self.test_results["image_map_test"] = {
            "pages_with_maps": len(pages_with_maps),
            "total_areas": total_areas,
            "working_areas": working_areas,
            "broken_areas": broken_areas[:5]  # First 5 only
        }
        
        print(f"📊 Pages with image maps: {len(pages_with_maps)}")
        print(f"📊 Image map areas: {working_areas}/{total_areas} properly formatted")
        
        if broken_areas:
            print(f"⚠️  Sample broken areas:")
            for broken in broken_areas[:3]:
                print(f"   - {broken}")
        
        return working_areas == total_areas
    
    def test_external_links_preserved(self):
        """Test that important external links are preserved"""
        print(f"\n🌍 TESTING EXTERNAL LINKS PRESERVATION")
        print("=" * 40)
        
        expected_external_domains = [
            'youtube.com',
            'youtu.be',
            'proboards.com',
            'proboards20.com',
            'streetmap.co.uk',
            'twitter.com',
            'deliveroo.co.uk'
        ]
        
        found_domains = set()
        external_links = []
        
        for html_file in self.pages_dir.glob("*.html"):
            try:
                content = html_file.read_text(encoding='utf-8', errors='ignore')
                
                # Find all external links
                external_refs = re.findall(r'href="(https?://[^"]*)"', content)
                
                for link in external_refs:
                    external_links.append(f"{html_file.name}: {link}")
                    
                    # Check which expected domains we found
                    for domain in expected_external_domains:
                        if domain in link:
                            found_domains.add(domain)
                            
            except Exception as e:
                continue
        
        self.test_results["external_links_test"] = {
            "expected_domains": expected_external_domains,
            "found_domains": list(found_domains),
            "missing_domains": [d for d in expected_external_domains if d not in found_domains],
            "total_external_links": len(external_links)
        }
        
        print(f"📊 External domains found: {len(found_domains)}/{len(expected_external_domains)}")
        print(f"✅ Found domains: {', '.join(sorted(found_domains))}")
        
        missing = [d for d in expected_external_domains if d not in found_domains]
        if missing:
            print(f"❌ Missing domains: {', '.join(missing)}")
        
        return len(found_domains) >= len(expected_external_domains) * 0.8  # 80% threshold
    
    def test_banner_consistency(self):
        """Test that banner images are consistent and correct"""
        print(f"\n🎯 TESTING BANNER CONSISTENCY")
        print("=" * 30)
        
        banner_usage = defaultdict(list)
        total_pages = 0
        
        for html_file in self.pages_dir.glob("*.html"):
            try:
                content = html_file.read_text(encoding='utf-8', errors='ignore')
                total_pages += 1
                
                # Find image sources that might be banners
                img_sources = re.findall(r'src="([^"]*\.(gif|jpg|jpeg|png))"', content, re.IGNORECASE)
                
                for src, ext in img_sources:
                    if any(keyword in src.lower() for keyword in ['banner', 'img0', 'header']):
                        banner_usage[src].append(html_file.name)
                        
            except Exception as e:
                continue
        
        # Check for consistency
        consistent_banners = 0
        inconsistent_banners = 0
        
        for banner, pages in banner_usage.items():
            if len(pages) > 1:  # Used by multiple pages
                consistent_banners += 1
            else:
                inconsistent_banners += 1
        
        self.test_results["banner_consistency_test"] = {
            "total_pages": total_pages,
            "banner_types": len(banner_usage),
            "consistent_banners": consistent_banners,
            "banner_usage": dict(banner_usage)
        }
        
        print(f"📊 Pages analyzed: {total_pages}")
        print(f"📊 Banner types found: {len(banner_usage)}")
        
        # Show most common banners
        most_used = sorted(banner_usage.items(), key=lambda x: len(x[1]), reverse=True)[:3]
        for banner, pages in most_used:
            print(f"✅ {banner}: used by {len(pages)} pages")
        
        return len(banner_usage) > 0
    
    def test_content_completeness(self):
        """Test that content appears complete and not truncated"""
        print(f"\n📄 TESTING CONTENT COMPLETENESS")
        print("=" * 35)
        
        total_pages = 0
        complete_pages = 0
        incomplete_pages = []
        
        for html_file in self.pages_dir.glob("*.html"):
            try:
                content = html_file.read_text(encoding='utf-8', errors='ignore')
                total_pages += 1
                
                # Check for signs of complete content
                has_html_tags = '<html' in content and '</html>' in content
                has_body_tags = '<body' in content and '</body>' in content
                has_reasonable_length = len(content) > 1000  # Reasonable minimum
                not_error_page = "404: Page not found" not in content
                
                if has_html_tags and has_body_tags and has_reasonable_length and not_error_page:
                    complete_pages += 1
                else:
                    issues = []
                    if not has_html_tags:
                        issues.append("missing HTML tags")
                    if not has_body_tags:
                        issues.append("missing body tags")
                    if not has_reasonable_length:
                        issues.append(f"too short ({len(content)} chars)")
                    if not not_error_page:
                        issues.append("404 error page")
                    
                    incomplete_pages.append(f"{html_file.name}: {', '.join(issues)}")
                    
            except Exception as e:
                incomplete_pages.append(f"{html_file.name}: read error - {e}")
        
        self.test_results["content_completeness_test"] = {
            "total_pages": total_pages,
            "complete_pages": complete_pages,
            "incomplete_pages": incomplete_pages[:5]  # First 5 only
        }
        
        completion_rate = (complete_pages / total_pages * 100) if total_pages > 0 else 0
        
        print(f"📊 Content completeness: {complete_pages}/{total_pages} ({completion_rate:.1f}%)")
        
        if incomplete_pages:
            print(f"⚠️  Sample incomplete pages:")
            for incomplete in incomplete_pages[:3]:
                print(f"   - {incomplete}")
        
        return completion_rate >= 95  # 95% threshold
    
    def test_file_structure_integrity(self):
        """Test that file structure is complete"""
        print(f"\n📁 TESTING FILE STRUCTURE INTEGRITY")
        print("=" * 40)
        
        # Count different file types
        html_files = list(self.pages_dir.glob("*.html"))
        image_files = list(self.assets_dir.glob("images/*.gif")) if self.assets_dir.exists() else []
        
        # Expected structure elements
        critical_files = [
            self.pages_dir / "home_.html",
            self.pages_dir / "img0.gif",
            self.assets_dir / "images" / "banner.gif"
        ]
        
        existing_critical = [f for f in critical_files if f.exists()]
        
        self.test_results["file_structure_test"] = {
            "html_files": len(html_files),
            "image_files": len(image_files),
            "critical_files_found": len(existing_critical),
            "critical_files_total": len(critical_files)
        }
        
        print(f"📊 HTML files: {len(html_files)}")
        print(f"📊 Image files: {len(image_files)}")
        print(f"📊 Critical files: {len(existing_critical)}/{len(critical_files)}")
        
        return len(html_files) > 1000 and len(image_files) > 100  # Reasonable thresholds
    
    def run_full_functional_test_suite(self):
        """Run the complete functional test suite"""
        print("🧪 FUNCTIONAL TESTING SUITE")
        print("=" * 50)
        print("Testing specific functionality to ensure new site works like original\n")
        
        # Run all tests
        tests = [
            ("Navigation Structure", self.test_navigation_structure),
            ("Image Maps", self.test_image_maps_functionality),
            ("External Links", self.test_external_links_preserved),
            ("Banner Consistency", self.test_banner_consistency),
            ("Content Completeness", self.test_content_completeness),
            ("File Structure", self.test_file_structure_integrity)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                if result:
                    passed_tests += 1
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                print(f"💥 {test_name}: ERROR - {e}")
        
        # Calculate overall score
        functional_score = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n🎯 FUNCTIONAL TEST SUMMARY")
        print("=" * 30)
        print(f"📊 Tests passed: {passed_tests}/{total_tests}")
        print(f"📊 Functional score: {functional_score:.1f}%")
        
        if functional_score >= 90:
            status = "🚀 EXCELLENT - Site functions like original"
        elif functional_score >= 75:
            status = "👍 GOOD - Minor functional issues"
        else:
            status = "⚠️  NEEDS WORK - Major functional problems"
        
        print(f"🎯 Status: {status}")
        
        # Save detailed results
        with open('functional_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: functional_test_results.json")
        
        return functional_score

def main():
    tester = FunctionalTester()
    score = tester.run_full_functional_test_suite()
    
    print(f"\n✅ FUNCTIONAL TESTING COMPLETE!")
    print(f"Final Functional Score: {score:.1f}%")
    
    return score >= 75  # Success threshold

if __name__ == "__main__":
    main() 