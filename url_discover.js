const puppeteer = require('puppeteer');
const fs = require('fs').promises;
const path = require('path');

// Configuration
const config = {
    baseUrl: 'https://0002n8y.wcomhost.com/website/',
    outputFile: 'discovered_urls.json',
    startUrls: [
        'everyplayer/',
        'top25/',
        'nextgame/'
    ]
};

async function discoverUrls() {
    console.log('Starting URL discovery...');
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();
    
    // Set to store unique URLs
    const discoveredUrls = new Set();
    // Queue for URLs to process
    const urlQueue = [...config.startUrls];
    // Set to track visited URLs
    const visitedUrls = new Set();
    
    console.log(`Starting with ${urlQueue.length} initial URLs`);
    
    while (urlQueue.length > 0) {
        const currentUrl = urlQueue.shift();
        const fullUrl = `${config.baseUrl}${currentUrl}`;
        
        if (visitedUrls.has(currentUrl)) {
            continue;
        }
        
        console.log(`\nProcessing: ${fullUrl}`);
        visitedUrls.add(currentUrl);
        
        try {
            // Navigate with longer timeout
            await page.goto(fullUrl, { 
                waitUntil: 'networkidle2',
                timeout: 30000
            });
            
            // Wait an additional 3 seconds for any JavaScript to finish
            await new Promise(resolve => setTimeout(resolve, 3000));
            
            // Debug: Check what's on the page
            const pageContent = await page.evaluate(() => {
                return {
                    title: document.title,
                    bodyText: document.body ? document.body.innerText.substring(0, 200) : 'No body',
                    linkCount: document.querySelectorAll('a').length,
                    allLinks: Array.from(document.querySelectorAll('a')).map(a => ({
                        href: a.href,
                        text: a.innerText?.trim()
                    }))
                };
            });
            
            console.log(`Page title: ${pageContent.title}`);
            console.log(`Body content preview: ${pageContent.bodyText}`);
            console.log(`Total links found: ${pageContent.linkCount}`);
            
            // Log all found links for debugging
            if (pageContent.allLinks.length > 0) {
                console.log('All links on page:');
                pageContent.allLinks.forEach((link, i) => {
                    if (i < 10) { // Show first 10 links
                        console.log(`  ${link.href} - "${link.text}"`);
                    }
                });
                if (pageContent.allLinks.length > 10) {
                    console.log(`  ... and ${pageContent.allLinks.length - 10} more`);
                }
            }
            
            // Extract all links from the page (including relative links)
            const links = await page.evaluate((baseUrl) => {
                const allLinks = Array.from(document.querySelectorAll('a'))
                    .map(a => {
                        let href = a.href || a.getAttribute('href');
                        if (!href) return null;
                        
                        // Convert relative URLs to absolute
                        if (href.startsWith('/')) {
                            href = 'https://0002n8y.wcomhost.com' + href;
                        } else if (href.startsWith('../') || !href.includes('://')) {
                            href = baseUrl + href;
                        }
                        
                        console.log('Processing link:', href);
                        return href;
                    })
                    .filter(href => href && href.startsWith('https://0002n8y.wcomhost.com/website/'))
                    .map(href => href.replace('https://0002n8y.wcomhost.com/website/', ''));
                
                return allLinks;
            }, fullUrl);
            
            // Add new URLs to queue
            for (const link of links) {
                if (!visitedUrls.has(link) && !urlQueue.includes(link)) {
                    urlQueue.push(link);
                    discoveredUrls.add(link);
                }
            }
            
            console.log(`Found ${links.length} matching links on page`);
            console.log(`Queue size: ${urlQueue.length}, Discovered: ${discoveredUrls.size}`);
            
        } catch (error) {
            console.error(`Error processing ${fullUrl}:`, error.message);
        }
        
        // Save progress periodically
        if (discoveredUrls.size % 10 === 0 && discoveredUrls.size > 0) {
            await saveProgress(discoveredUrls);
        }
    }
    
    await browser.close();
    await saveProgress(discoveredUrls);
    console.log('\nURL discovery complete!');
    console.log(`Total URLs discovered: ${discoveredUrls.size}`);
}

async function saveProgress(urls) {
    const urlArray = Array.from(urls);
    await fs.writeFile(
        config.outputFile,
        JSON.stringify(urlArray, null, 2)
    );
    console.log(`Progress saved to ${config.outputFile}`);
}

// Run the discovery process
discoverUrls().catch(console.error); 