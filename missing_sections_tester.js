const puppeteer = require('puppeteer');
const fs = require('fs').promises;

// Configuration
const config = {
    baseUrl: 'https://0002n8y.wcomhost.com/website/',
    outputFile: 'additional_paginated_sections.json',
    maxPagesToTest: 25,
    // Potential section names to test based on your examples and common patterns
    potentialSections: [
        'season2022', 'everyplayer', 'season2021', 'season2020', 'season2019', 'season2018',
        'season2017', 'season2016', 'season2015', 'season2014', 'season2013', 'season2012',
        'season2011', 'season2010', 'season2009', 'season2008', 'season2007', 'season2006',
        'season2005', 'season2004', 'season2003', 'season2002', 'season2001', 'season2000',
        'fixtures', 'fixtures2022', 'fixtures2021', 'fixtures2020', 'fixtures2019',
        'tables', 'tables2022', 'tables2021', 'tables2020', 'tables2019',
        'players', 'legends', 'squad', 'allplayers', 'playerstats',
        'cups', 'cups2022', 'cups2021', 'cups2020', 'cups2019',
        'fac', 'facup', 'facup2022', 'facup2021', 'facup2020', 'facup2019',
        'history', 'hist', 'archives', 'results', 'stats', 'photos', 'gallery'
    ]
};

async function testUrl(page, url) {
    try {
        const response = await page.goto(url, { 
            waitUntil: 'networkidle2',
            timeout: 5000
        });
        
        if (response && response.status() === 200) {
            const title = await page.title();
            const bodyText = await page.evaluate(() => 
                document.body ? document.body.innerText.trim() : ''
            );
            
            // Accept page if it has content OR if it has a meaningful title
            if (bodyText.length > 5 || (title && title.length > 0 && title !== 'Untitled')) {
                return { success: true, title, contentLength: bodyText.length };
            }
        }
        return { success: false, status: response ? response.status() : 'No response' };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function testMissingSections() {
    console.log('Testing for additional paginated sections...');
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();
    
    const foundSections = [];
    const results = {
        sectionsWithPages: 0,
        totalPagesFound: 0,
        sectionsProcessed: 0
    };
    
    console.log(`Testing ${config.potentialSections.length} potential sections...`);
    
    for (const sectionName of config.potentialSections) {
        console.log(`\n=== Testing Section: ${sectionName} ===`);
        
        const sectionData = {
            sectionName: sectionName,
            pages: [],
            totalPages: 0
        };
        
        let consecutiveFailures = 0;
        let foundAnyPages = false;
        
        // Test pages 1-25 for this section
        for (let pageNum = 1; pageNum <= config.maxPagesToTest; pageNum++) {
            const pageUrl = `${config.baseUrl}${sectionName}/page${pageNum}.html`;
            
            const result = await testUrl(page, pageUrl);
            
            if (result.success) {
                console.log(`  ✓ page${pageNum}.html: ${result.title} (${result.contentLength} chars)`);
                
                sectionData.pages.push({
                    url: pageUrl,
                    pageNumber: pageNum,
                    title: result.title,
                    contentLength: result.contentLength
                });
                
                sectionData.totalPages++;
                results.totalPagesFound++;
                foundAnyPages = true;
                consecutiveFailures = 0;
            } else {
                consecutiveFailures++;
                
                // If we found some pages but then hit 5 consecutive failures, 
                // assume we've reached the end of this section
                if (foundAnyPages && consecutiveFailures >= 5) {
                    console.log(`  Stopping ${sectionName} after 5 consecutive failures`);
                    break;
                }
                
                // If we haven't found any pages and hit 10 consecutive failures,
                // assume this section doesn't exist
                if (!foundAnyPages && consecutiveFailures >= 10) {
                    break;
                }
            }
            
            // Small delay between requests
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        if (foundAnyPages) {
            foundSections.push(sectionData);
            results.sectionsWithPages++;
            console.log(`  ✓ Section ${sectionName}: ${sectionData.totalPages} pages found`);
        } else {
            console.log(`  ✗ Section ${sectionName}: No pages found`);
        }
        
        results.sectionsProcessed++;
        
        // Save progress every 10 sections
        if (results.sectionsProcessed % 10 === 0) {
            await saveProgress(foundSections, results);
        }
    }
    
    await browser.close();
    await saveProgress(foundSections, results);
    
    console.log('\n=== Missing Sections Discovery Complete ===');
    console.log(`Sections processed: ${results.sectionsProcessed}`);
    console.log(`Sections with pages: ${results.sectionsWithPages}`);
    console.log(`Total pages found: ${results.totalPagesFound}`);
}

async function saveProgress(foundSections, results) {
    const allPages = [];
    foundSections.forEach(section => {
        section.pages.forEach(page => {
            allPages.push({
                sectionName: section.sectionName,
                ...page
            });
        });
    });
    
    const output = {
        timestamp: new Date().toISOString(),
        summary: {
            sectionsWithPages: results.sectionsWithPages,
            totalPagesFound: results.totalPagesFound,
            sectionsProcessed: results.sectionsProcessed
        },
        sections: foundSections,
        allPages: allPages
    };
    
    await fs.writeFile(config.outputFile, JSON.stringify(output, null, 2));
    console.log(`\nProgress saved: ${results.totalPagesFound} pages across ${results.sectionsWithPages} sections`);
}

// Run the missing sections discovery
testMissingSections().catch(console.error); 