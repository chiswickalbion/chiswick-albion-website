const puppeteer = require('puppeteer');
const fs = require('fs').promises;
const path = require('path');

// Configuration
const config = {
    baseUrl: 'https://0002n8y.wcomhost.com/website/',
    maxRetries: 3,
    timeout: 10000,
    delayBetweenRequests: 500,
    batchSize: 50,
    maxPaginationTest: 50,
    outputFile: 'comprehensive_discovery_results.json'
};

class ComprehensiveUrlDiscovery {
    constructor() {
        this.browser = null;
        this.page = null;
        this.workingUrls = [];
        this.testedUrls = new Set();
        this.failedUrls = [];
        this.stats = {
            totalTested: 0,
            working: 0,
            failed: 0,
            startTime: null,
            currentStrategy: ''
        };
    }

    async initialize() {
        console.log('🚀 Initializing comprehensive URL discovery...\n');
        
        this.browser = await puppeteer.launch({ 
            headless: false,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        this.page = await this.browser.newPage();
        await this.page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
        
        this.stats.startTime = Date.now();
        console.log('✅ Browser initialized successfully\n');
    }

    async testUrl(url, retries = 0) {
        if (this.testedUrls.has(url)) {
            return null; // Already tested
        }

        try {
            const response = await this.page.goto(url, { 
                timeout: config.timeout,
                waitUntil: 'domcontentloaded'
            });
            
            if (response && response.ok()) {
                const title = await this.page.title();
                const contentLength = (await this.page.content()).length;
                
                // Consider it working if it has a meaningful title or substantial content
                const isWorking = !title.toLowerCase().includes('404') && 
                                !title.toLowerCase().includes('not found') &&
                                contentLength > 500;
                
                if (isWorking) {
                    this.workingUrls.push({
                        url,
                        title,
                        contentLength,
                        timestamp: new Date().toISOString()
                    });
                    this.stats.working++;
                    return { url, title, contentLength, working: true };
                }
            }
            
            this.failedUrls.push({ url, reason: 'Invalid response or 404' });
            this.stats.failed++;
            return null;
            
        } catch (error) {
            if (retries < config.maxRetries) {
                await new Promise(resolve => setTimeout(resolve, 1000));
                return this.testUrl(url, retries + 1);
            }
            
            this.failedUrls.push({ url, reason: error.message });
            this.stats.failed++;
            return null;
        } finally {
            this.testedUrls.add(url);
            this.stats.totalTested++;
            
            if (this.stats.totalTested % 10 === 0) {
                this.printProgress();
            }
            
            await new Promise(resolve => setTimeout(resolve, config.delayBetweenRequests));
        }
    }

    async testPaginationForSection(sectionName, maxPages = config.maxPaginationTest) {
        console.log(`  🔍 Testing pagination for: ${sectionName}`);
        const paginatedUrls = [];
        let consecutiveFailures = 0;
        
        for (let page = 2; page <= maxPages; page++) {
            const url = `${config.baseUrl}${sectionName}/page${page}.html`;
            const result = await this.testUrl(url);
            
            if (result && result.working) {
                paginatedUrls.push(result);
                consecutiveFailures = 0;
                console.log(`    ✅ Found: page${page}.html`);
            } else {
                consecutiveFailures++;
                if (consecutiveFailures >= 5) {
                    console.log(`    ⏸️  Stopping after 5 consecutive failures at page ${page}`);
                    break;
                }
            }
        }
        
        return paginatedUrls;
    }

    generateSectionNames() {
        const sections = [];
        
        // 1. Year-based sections (extensive range)
        console.log('📅 Generating year-based sections...');
        for (let year = 1990; year <= 2024; year++) {
            sections.push(`season${year}`);
            sections.push(`${year}`);
            sections.push(`year${year}`);
        }
        
        // 2. Historical sections (numbered)
        console.log('📚 Generating historical sections...');
        for (let i = 1; i <= 20; i++) {
            sections.push(`History${i}`);
            sections.push(`history${i}`);
            sections.push(`Season${i}`);
            sections.push(`season${i}`);
        }
        
        // 3. Common football/sports sections
        console.log('⚽ Generating sports sections...');
        const sportsTerms = [
            'players', 'everyplayer', 'allplayers', 'squad', 'team',
            'matches', 'games', 'fixtures', 'results', 'scores',
            'honours', 'honors', 'awards', 'trophies', 'achievements',
            'records', 'statistics', 'stats', 'facts',
            'photos', 'images', 'pictures', 'gallery', 'media',
            'videos', 'clips', 'highlights',
            'news', 'reports', 'articles', 'stories',
            'club', 'about', 'info', 'details',
            'contact', 'ground', 'stadium', 'venue',
            'supporters', 'fans', 'membership',
            'youth', 'academy', 'juniors', 'development',
            'first', 'reserves', 'seconds', 'thirds',
            'ladies', 'women', 'mens', 'senior'
        ];
        
        sections.push(...sportsTerms);
        
        // Add numbered versions
        sportsTerms.forEach(term => {
            for (let i = 1; i <= 5; i++) {
                sections.push(`${term}${i}`);
            }
        });
        
        // 4. Award-specific sections
        console.log('🏆 Generating award sections...');
        const awardTerms = [
            'playerawards', 'player_awards', 'awards',
            'playerstats', 'player_stats', 'topscorers',
            'goalscorers', 'assists', 'appearances',
            'motm', 'manofmatch', 'playerofyear'
        ];
        sections.push(...awardTerms);
        
        // 5. League/Competition sections
        console.log('🏁 Generating competition sections...');
        const competitions = [
            'league', 'cup', 'trophy', 'championship',
            'premier', 'division', 'conference', 'national'
        ];
        competitions.forEach(comp => {
            sections.push(comp);
            for (let i = 1; i <= 10; i++) {
                sections.push(`${comp}${i}`);
            }
        });
        
        // 6. Archive sections
        console.log('📦 Generating archive sections...');
        for (let i = 1; i <= 50; i++) {
            sections.push(`archive${i}`);
            sections.push(`page${i}`);
            sections.push(`section${i}`);
        }
        
        console.log(`📋 Generated ${sections.length} section names to test\n`);
        return [...new Set(sections)]; // Remove duplicates
    }

    async testBaseSections() {
        this.stats.currentStrategy = 'Base Sections Discovery';
        console.log('🔍 PHASE 1: Testing base sections...\n');
        
        const sections = this.generateSectionNames();
        const workingSections = [];
        
        console.log(`Testing ${sections.length} potential sections...\n`);
        
        for (const section of sections) {
            const url = `${config.baseUrl}${section}/`;
            const result = await this.testUrl(url);
            
            if (result && result.working) {
                workingSections.push({ section, ...result });
                console.log(`✅ FOUND SECTION: ${section} - "${result.title}"`);
                
                // Test pagination for this working section
                const paginatedUrls = await this.testPaginationForSection(section);
                if (paginatedUrls.length > 0) {
                    console.log(`   📄 Found ${paginatedUrls.length} additional pages`);
                }
            }
            
            // Save progress periodically
            if (this.stats.totalTested % config.batchSize === 0) {
                await this.saveProgress();
            }
        }
        
        console.log(`\n✅ Phase 1 Complete: Found ${workingSections.length} working sections\n`);
        return workingSections;
    }

    async testDirectPages() {
        this.stats.currentStrategy = 'Direct Pages Discovery';
        console.log('🔍 PHASE 2: Testing direct pages...\n');
        
        const pageNames = [];
        
        // Test direct .html files
        for (let i = 1; i <= 100; i++) {
            pageNames.push(`page${i}.html`);
            pageNames.push(`${i}.html`);
        }
        
        // Test named pages
        const namedPages = [
            'index.html', 'home.html', 'main.html',
            'about.html', 'contact.html', 'history.html',
            'players.html', 'team.html', 'squad.html',
            'news.html', 'matches.html', 'results.html'
        ];
        pageNames.push(...namedPages);
        
        for (const pageName of pageNames) {
            const url = `${config.baseUrl}${pageName}`;
            const result = await this.testUrl(url);
            
            if (result && result.working) {
                console.log(`✅ FOUND DIRECT PAGE: ${pageName} - "${result.title}"`);
            }
        }
        
        console.log(`\n✅ Phase 2 Complete\n`);
    }

    async testAlternativePatterns() {
        this.stats.currentStrategy = 'Alternative Patterns';
        console.log('🔍 PHASE 3: Testing alternative URL patterns...\n');
        
        // Test different URL structures
        const patterns = [
            // Underscore patterns
            'player_stats/', 'match_results/', 'club_history/',
            'team_news/', 'photo_gallery/', 'video_archive/',
            
            // Hyphen patterns  
            'player-stats/', 'match-results/', 'club-history/',
            'team-news/', 'photo-gallery/', 'video-archive/',
            
            // Capitalized patterns
            'Players/', 'History/', 'Matches/', 'News/', 'Photos/',
            'Videos/', 'Awards/', 'Statistics/', 'Results/',
            
            // Mixed patterns
            'clubInfo/', 'playerData/', 'matchStats/',
            'newsArchive/', 'photoGallery/', 'videoLibrary/'
        ];
        
        for (const pattern of patterns) {
            const url = `${config.baseUrl}${pattern}`;
            const result = await this.testUrl(url);
            
            if (result && result.working) {
                console.log(`✅ FOUND ALTERNATIVE: ${pattern} - "${result.title}"`);
                
                // Test pagination for working alternatives
                const sectionName = pattern.replace('/', '');
                await this.testPaginationForSection(sectionName);
            }
        }
        
        console.log(`\n✅ Phase 3 Complete\n`);
    }

    printProgress() {
        const elapsed = Date.now() - this.stats.startTime;
        const rate = (this.stats.totalTested / (elapsed / 1000)).toFixed(1);
        
        console.log(`\n📊 Progress [${this.stats.currentStrategy}]:`);
        console.log(`   Tested: ${this.stats.totalTested} | Working: ${this.stats.working} | Failed: ${this.stats.failed}`);
        console.log(`   Rate: ${rate} URLs/sec | Elapsed: ${Math.round(elapsed/1000)}s`);
        console.log(`   Success Rate: ${((this.stats.working / this.stats.totalTested) * 100).toFixed(1)}%\n`);
    }

    async saveProgress() {
        const progressData = {
            timestamp: new Date().toISOString(),
            stats: {
                ...this.stats,
                elapsedTime: Date.now() - this.stats.startTime
            },
            workingUrls: this.workingUrls,
            totalUrls: this.workingUrls.length,
            failedUrls: this.failedUrls.length,
            summary: {
                totalFound: this.workingUrls.length,
                sections: [...new Set(this.workingUrls.map(u => u.url.split('/')[4]))].length
            }
        };
        
        await fs.writeFile(config.outputFile, JSON.stringify(progressData, null, 2));
        console.log(`💾 Progress saved: ${this.workingUrls.length} URLs found`);
    }

    async run() {
        try {
            await this.initialize();
            
            // Load any existing URLs to avoid retesting
            try {
                const existing = JSON.parse(await fs.readFile(config.outputFile, 'utf8'));
                if (existing.workingUrls) {
                    existing.workingUrls.forEach(url => this.testedUrls.add(url.url));
                    console.log(`📂 Loaded ${existing.workingUrls.length} existing URLs\n`);
                }
            } catch (e) {
                console.log('📂 Starting fresh discovery\n');
            }
            
            // Execute discovery phases
            await this.testBaseSections();
            await this.testDirectPages();
            await this.testAlternativePatterns();
            
            // Final save and summary
            await this.saveProgress();
            
            console.log('\n🎉 === COMPREHENSIVE DISCOVERY COMPLETE ===');
            console.log(`📊 Final Results:`);
            console.log(`   Total URLs Found: ${this.workingUrls.length}`);
            console.log(`   Total URLs Tested: ${this.stats.totalTested}`);
            console.log(`   Success Rate: ${((this.stats.working / this.stats.totalTested) * 100).toFixed(1)}%`);
            console.log(`   Sections Discovered: ${[...new Set(this.workingUrls.map(u => u.url.split('/')[4]))].length}`);
            
            const elapsed = Date.now() - this.stats.startTime;
            console.log(`   Total Time: ${Math.round(elapsed/1000/60)} minutes`);
            console.log(`   Output File: ${config.outputFile}\n`);
            
            if (this.workingUrls.length >= 1000) {
                console.log('🎯 TARGET ACHIEVED: Found 1000+ URLs!');
            } else {
                console.log(`🎯 Progress: ${this.workingUrls.length}/1000+ URLs found`);
            }
            
        } catch (error) {
            console.error('💥 Fatal error:', error);
        } finally {
            if (this.browser) {
                await this.browser.close();
            }
        }
    }
}

// Run the comprehensive discovery
const discovery = new ComprehensiveUrlDiscovery();
discovery.run().catch(console.error); 