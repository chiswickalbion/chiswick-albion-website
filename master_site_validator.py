#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime

class MasterSiteValidator:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "site_info": {
                "original_base": "https://0002n8y.wcomhost.com/website/",
                "new_base": "https://chiswickalbion.github.io/chiswick-albion-website/pages/",
                "local_path": str(Path("pages").absolute())
            },
            "test_results": {},
            "recommendations": [],
            "overall_assessment": {}
        }
    
    def run_functional_tests(self):
        """Run the functional test suite"""
        print("🧪 RUNNING FUNCTIONAL TESTS")
        print("=" * 30)
        
        try:
            result = subprocess.run(['python3', 'functional_testing_suite.py'], 
                                  capture_output=True, text=True, check=True)
            
            # Parse the functional test results
            if Path('functional_test_results.json').exists():
                with open('functional_test_results.json', 'r') as f:
                    functional_data = json.load(f)
                self.results["test_results"]["functional"] = functional_data
            
            # Extract score from output
            output_lines = result.stdout.split('\n')
            functional_score = 0
            for line in output_lines:
                if "Final Functional Score:" in line:
                    score_text = line.split(':')[-1].strip().replace('%', '')
                    functional_score = float(score_text)
                    break
            
            print(f"✅ Functional tests completed: {functional_score:.1f}%")
            return functional_score
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Functional tests failed: {e}")
            return 0
        except Exception as e:
            print(f"❌ Error running functional tests: {e}")
            return 0
    
    def run_comparison_tests(self):
        """Run the site comparison tests"""
        print("\n🔍 RUNNING SITE COMPARISON TESTS")
        print("=" * 35)
        
        try:
            result = subprocess.run(['python3', 'systematic_site_comparison.py'], 
                                  capture_output=True, text=True, check=True)
            
            # Parse the comparison test results
            if Path('site_comparison_report.json').exists():
                with open('site_comparison_report.json', 'r') as f:
                    comparison_data = json.load(f)
                self.results["test_results"]["comparison"] = comparison_data
            
            # Extract score from output
            output_lines = result.stdout.split('\n')
            comparison_score = 0
            for line in output_lines:
                if "Final Score:" in line:
                    score_text = line.split(':')[-1].strip().replace('%', '')
                    comparison_score = float(score_text)
                    break
            
            print(f"✅ Comparison tests completed: {comparison_score:.1f}%")
            return comparison_score
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Comparison tests failed: {e}")
            return 0
        except Exception as e:
            print(f"❌ Error running comparison tests: {e}")
            return 0
    
    def analyze_site_statistics(self):
        """Analyze basic site statistics"""
        print("\n📊 ANALYZING SITE STATISTICS")
        print("=" * 30)
        
        pages_dir = Path("pages")
        assets_dir = Path("assets")
        
        # Count files
        html_files = list(pages_dir.glob("*.html")) if pages_dir.exists() else []
        image_files = list(assets_dir.glob("**/*.gif")) if assets_dir.exists() else []
        
        # Analyze content
        total_content_size = 0
        pages_with_404 = 0
        pages_with_content = 0
        
        for html_file in html_files:
            try:
                content = html_file.read_text(encoding='utf-8', errors='ignore')
                total_content_size += len(content)
                
                if "404: Page not found" in content:
                    pages_with_404 += 1
                elif len(content) > 1000:  # Reasonable content threshold
                    pages_with_content += 1
            except:
                continue
        
        stats = {
            "total_html_files": len(html_files),
            "total_image_files": len(image_files),
            "total_content_size_mb": round(total_content_size / (1024*1024), 2),
            "pages_with_404": pages_with_404,
            "pages_with_content": pages_with_content,
            "content_ratio": round(pages_with_content / len(html_files) * 100, 1) if html_files else 0
        }
        
        self.results["test_results"]["statistics"] = stats
        
        print(f"📄 HTML files: {stats['total_html_files']}")
        print(f"🖼️  Image files: {stats['total_image_files']}")
        print(f"💾 Total content: {stats['total_content_size_mb']} MB")
        print(f"✅ Pages with content: {stats['pages_with_content']}/{stats['total_html_files']} ({stats['content_ratio']}%)")
        print(f"❌ 404 pages: {stats['pages_with_404']}")
        
        return stats
    
    def generate_recommendations(self, functional_score, comparison_score, stats):
        """Generate specific recommendations based on test results"""
        recommendations = []
        
        # Functional score recommendations
        if functional_score < 90:
            recommendations.append({
                "priority": "HIGH",
                "category": "Functionality",
                "issue": f"Functional score is {functional_score:.1f}% (target: 90%+)",
                "action": "Review functional test results and fix failing tests"
            })
        
        # Comparison score recommendations
        if comparison_score < 85:
            recommendations.append({
                "priority": "HIGH",
                "category": "Compatibility",
                "issue": f"Site comparison score is {comparison_score:.1f}% (target: 85%+)",
                "action": "Address accessibility and content integrity issues"
            })
        
        # Content recommendations
        if stats['content_ratio'] < 95:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Content",
                "issue": f"Only {stats['content_ratio']}% of pages have substantial content",
                "action": "Investigate and fix pages with minimal content"
            })
        
        # 404 page recommendations
        if stats['pages_with_404'] > 1:
            recommendations.append({
                "priority": "HIGH",
                "category": "Content",
                "issue": f"{stats['pages_with_404']} pages show 404 errors",
                "action": "Fix or remove broken pages that still show 404 errors"
            })
        
        # File count recommendations
        if stats['total_html_files'] < 1000:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Completeness",
                "issue": f"Only {stats['total_html_files']} HTML files (expected: 1000+)",
                "action": "Verify all pages from original site have been migrated"
            })
        
        # Positive recommendations
        if functional_score >= 90 and comparison_score >= 85:
            recommendations.append({
                "priority": "SUCCESS",
                "category": "Ready",
                "issue": "Site meets quality thresholds",
                "action": "Site is ready for production use as replacement"
            })
        
        self.results["recommendations"] = recommendations
        return recommendations
    
    def calculate_overall_readiness(self, functional_score, comparison_score, stats):
        """Calculate overall readiness score and status"""
        
        # Weighted scoring
        weights = {
            "functional": 0.4,
            "comparison": 0.3,
            "content_ratio": 0.2,
            "error_penalty": 0.1
        }
        
        content_score = min(stats['content_ratio'], 100)
        error_penalty = max(0, 100 - (stats['pages_with_404'] * 5))  # Penalty for 404s
        
        overall_score = (
            functional_score * weights["functional"] +
            comparison_score * weights["comparison"] +
            content_score * weights["content_ratio"] +
            error_penalty * weights["error_penalty"]
        )
        
        # Determine readiness status
        if overall_score >= 90:
            status = "READY FOR PRODUCTION"
            readiness = "🚀 EXCELLENT"
            message = "Site is a complete working replacement for the original!"
        elif overall_score >= 80:
            status = "MOSTLY READY"
            readiness = "✅ GOOD"
            message = "Site is mostly ready with minor issues to address"
        elif overall_score >= 70:
            status = "NEEDS MINOR WORK"
            readiness = "⚠️  FAIR"
            message = "Site needs some improvements before full deployment"
        else:
            status = "NEEDS MAJOR WORK"
            readiness = "❌ NEEDS WORK"
            message = "Site has significant issues that must be addressed"
        
        assessment = {
            "overall_score": round(overall_score, 1),
            "status": status,
            "readiness": readiness,
            "message": message,
            "component_scores": {
                "functional": functional_score,
                "comparison": comparison_score,
                "content": content_score,
                "error_penalty": error_penalty
            }
        }
        
        self.results["overall_assessment"] = assessment
        return assessment
    
    def run_complete_validation(self):
        """Run the complete validation process"""
        print("🎯 MASTER SITE VALIDATION")
        print("=" * 50)
        print("Complete systematic validation of new site vs original")
        print(f"Validating: {self.results['site_info']['local_path']}")
        print(f"Target: {self.results['site_info']['new_base']}\n")
        
        # Run all tests
        functional_score = self.run_functional_tests()
        comparison_score = self.run_comparison_tests()
        stats = self.analyze_site_statistics()
        
        # Generate analysis
        recommendations = self.generate_recommendations(functional_score, comparison_score, stats)
        assessment = self.calculate_overall_readiness(functional_score, comparison_score, stats)
        
        # Display final results
        print(f"\n🎯 MASTER VALIDATION RESULTS")
        print("=" * 35)
        print(f"📊 Overall Readiness Score: {assessment['overall_score']}%")
        print(f"🎯 Status: {assessment['readiness']} - {assessment['status']}")
        print(f"💬 {assessment['message']}")
        
        print(f"\n📈 Component Scores:")
        print(f"   🧪 Functional: {assessment['component_scores']['functional']:.1f}%")
        print(f"   🔍 Comparison: {assessment['component_scores']['comparison']:.1f}%")
        print(f"   📝 Content: {assessment['component_scores']['content']:.1f}%")
        print(f"   ⚠️  Error Penalty: {assessment['component_scores']['error_penalty']:.1f}%")
        
        # Show priority recommendations
        high_priority = [r for r in recommendations if r.get('priority') == 'HIGH']
        if high_priority:
            print(f"\n🚨 HIGH PRIORITY ACTIONS:")
            for rec in high_priority:
                print(f"   - {rec['category']}: {rec['issue']}")
                print(f"     Action: {rec['action']}")
        
        success_items = [r for r in recommendations if r.get('priority') == 'SUCCESS']
        if success_items:
            print(f"\n✅ SUCCESS INDICATORS:")
            for rec in success_items:
                print(f"   - {rec['action']}")
        
        # Save complete report
        with open('master_validation_report.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Complete validation report saved to: master_validation_report.json")
        
        # Final recommendation
        if assessment['overall_score'] >= 85:
            print(f"\n🎉 CONCLUSION: Your new GitHub Pages site is ready to serve as a complete working replacement for the original site!")
            print("✅ Proceed with confidence - the migration is successful!")
        else:
            print(f"\n🔧 CONCLUSION: Address the high-priority issues above before deploying as the primary site.")
            print("📋 Review the detailed reports for specific fixes needed.")
        
        return assessment

def main():
    validator = MasterSiteValidator()
    assessment = validator.run_complete_validation()
    
    # Return success if score is good enough
    return assessment['overall_score'] >= 75

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 