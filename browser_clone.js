const puppeteer = require('puppeteer');
const fs = require('fs').promises;
const path = require('path');
const readline = require('readline');

// Configuration
const config = {
    baseUrl: 'https://0002n8y.wcomhost.com/website/',
    outputDir: 'web',
    pagesDir: 'web/pages',
    imagesDir: 'web/assets/images',
    validationReport: 'master_validation_report.json',
    delayBetweenPages: 2000 // 2 seconds delay between pages
};

// Create readline interface for user input
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

// Promisify readline question
const question = (query) => new Promise((resolve) => rl.question(query, resolve));

// Create necessary directories
async function createDirectories() {
    await fs.mkdir(config.pagesDir, { recursive: true });
    await fs.mkdir(config.imagesDir, { recursive: true });
    console.log('Created directories:', config.pagesDir, config.imagesDir);
}

// Load page mapping from validation report
async function loadPageMapping() {
    const report = JSON.parse(await fs.readFile(config.validationReport, 'utf8'));
    const pages = new Set();
    
    // Add pages from navigation links
    const navLinks = report.test_results.functional.navigation_test.navigation_links;
    for (const pageLinks of Object.values(navLinks)) {
        pageLinks.forEach(page => {
            // Convert .html to directory-style URL
            const dirPage = page.replace('.html', '/');
            pages.add(dirPage);
        });
    }
    
    // Add pages from banner usage
    const bannerUsage = report.test_results.functional.banner_consistency_test.banner_usage;
    for (const pageList of Object.values(bannerUsage)) {
        pageList.forEach(page => {
            // Convert .html to directory-style URL
            const dirPage = page.replace('.html', '/');
            pages.add(dirPage);
        });
    }
    
    // Add pages from image map test
    const imageMapPages = report.test_results.functional.image_map_test.pages_with_maps;
    if (imageMapPages) {
        // Get all pages from the local path
        const localPath = report.site_info.local_path;
        try {
            const files = await fs.readdir(localPath);
            files.forEach(file => {
                if (file.endsWith('.html')) {
                    const dirPage = file.replace('.html', '/');
                    pages.add(dirPage);
                }
            });
        } catch (error) {
            console.error('Error reading local path:', error);
        }
    }
    
    return Array.from(pages);
}

// Download a single page and its resources
async function downloadPage(browser, pageName, index, total) {
    const page = await browser.newPage();
    const url = new URL(pageName, config.baseUrl).toString();
    
    try {
        console.log(`\n[${index + 1}/${total}] Loading page: ${url}`);
        const response = await page.goto(url, { waitUntil: 'networkidle0' });
        
        if (!response) {
            console.error(`Failed to load ${url}: No response`);
            return false;
        }
        
        if (response.status() !== 200) {
            console.error(`Failed to load ${url}: HTTP ${response.status()}`);
            return false;
        }
        
        // Save HTML with .html extension for local files
        const localFileName = pageName.replace(/\/$/, '.html');
        const content = await page.content();
        await fs.writeFile(path.join(config.pagesDir, localFileName), content);
        console.log(`✓ Saved HTML: ${localFileName}`);
        
        // Download images
        const images = await page.$$eval('img', imgs => imgs.map(img => img.src));
        const imageMapping = {};
        let downloadedImages = 0;
        
        for (const [index, src] of images.entries()) {
            if (!src) continue;
            
            try {
                const imageName = `img${index}.gif`;
                const imagePath = path.join(config.imagesDir, imageName);
                
                // Download image
                const response = await page.goto(src);
                if (response && response.ok()) {
                    const buffer = await response.buffer();
                    await fs.writeFile(imagePath, buffer);
                    imageMapping[src] = imageName;
                    downloadedImages++;
                }
            } catch (error) {
                console.error(`Error downloading image ${src}:`, error.message);
            }
        }
        
        if (downloadedImages > 0) {
            console.log(`✓ Downloaded ${downloadedImages} images`);
        }
        
        // Save image mapping
        await fs.writeFile(
            path.join(config.outputDir, 'image_mapping.json'),
            JSON.stringify(imageMapping, null, 2)
        );
        
        return true;
        
    } catch (error) {
        console.error(`Error processing ${url}:`, error.message);
        return false;
    } finally {
        await page.close();
    }
}

// Main function
async function main() {
    try {
        // Create directories
        await createDirectories();
        
        // Load page mapping
        const pages = await loadPageMapping();
        console.log(`Found ${pages.length} pages to process`);
        
        // Ask for confirmation once
        const answer = await question(`\nReady to process ${pages.length} pages. Continue? (y/n): `);
        if (answer.toLowerCase() !== 'y') {
            console.log('\nStopping at user request');
            return;
        }
        
        // Launch browser
        const browser = await puppeteer.launch({
            headless: false, // Use real browser
            defaultViewport: null,
            args: ['--start-maximized']
        });
        
        // Process all pages
        let successCount = 0;
        let failCount = 0;
        
        for (let i = 0; i < pages.length; i++) {
            const pageName = pages[i];
            const success = await downloadPage(browser, pageName, i, pages.length);
            
            if (success) {
                successCount++;
                console.log(`\nPage ${i + 1}/${pages.length} completed successfully`);
            } else {
                failCount++;
                console.log(`\nPage ${i + 1}/${pages.length} failed`);
            }
            
            // Add delay between pages
            await new Promise(resolve => setTimeout(resolve, config.delayBetweenPages));
        }
        
        await browser.close();
        console.log('\nSite clone completed');
        console.log(`Successfully processed: ${successCount} pages`);
        console.log(`Failed to process: ${failCount} pages`);
        
    } catch (error) {
        console.error('Error during site clone:', error);
        process.exit(1);
    } finally {
        rl.close();
    }
}

// Run the script
main(); 