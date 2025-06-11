const puppeteer = require('puppeteer');
const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');

// Configuration
const config = {
    urlsFile: 'targeted_sections_results.json',
    fallbackUrlsFile: 'all_working_urls.json',
    outputDir: 'downloaded_site',
    pagesDir: 'pages',
    imagesDir: 'assets/images',
    maxConcurrency: 3,
    retryAttempts: 3,
    delayBetweenPages: 1000,
    pageTimeout: 15000
};

class RobustDownloader {
    constructor() {
        this.browser = null;
        this.page = null;
        this.downloadedUrls = new Set();
        this.failedUrls = [];
        this.imageMapping = new Map();
        this.stats = {
            totalUrls: 0,
            downloaded: 0,
            failed: 0,
            images: 0,
            startTime: null
        };
    }

    async initialize() {
        console.log('Initializing robust downloader...');
        
        // Create directories
        await this.createDirectories();
        
        // Launch browser
        this.browser = await puppeteer.launch({ 
            headless: false,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        this.page = await this.browser.newPage();
        
        // Set user agent to appear more human-like
        await this.page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
        
        console.log('Browser initialized successfully');
    }

    async createDirectories() {
        const dirs = [
            config.outputDir,
            path.join(config.outputDir, config.pagesDir),
            path.join(config.outputDir, config.imagesDir)
        ];
        
        for (const dir of dirs) {
            await fs.mkdir(dir, { recursive: true });
        }
        console.log('Directories created');
    }

    async loadUrls() {
        let allUrls = [];
        
        // Try to load from targeted sections results first
        try {
            const data = JSON.parse(await fs.readFile(config.urlsFile, 'utf8'));
            allUrls = data.allUrls || [];
            console.log(`Loaded ${allUrls.length} URLs from ${config.urlsFile}`);
        } catch (error) {
            console.log(`Could not load ${config.urlsFile}, trying fallback...`);
            
            // Fallback to the original working URLs
            try {
                const data = JSON.parse(await fs.readFile(config.fallbackUrlsFile, 'utf8'));
                allUrls = (data.workingUrls || []).map(url => ({
                    sectionName: url.baseName || 'unknown',
                    url: url.workingUrl,
                    pageNumber: 0,
                    title: url.title,
                    contentLength: url.contentLength
                }));
                console.log(`Loaded ${allUrls.length} URLs from fallback file`);
            } catch (fallbackError) {
                console.error('Could not load URLs from either file:', fallbackError.message);
                return [];
            }
        }
        
        this.stats.totalUrls = allUrls.length;
        return allUrls;
    }

    async downloadPage(urlData, attempt = 1) {
        const { url, sectionName, pageNumber, title } = urlData;
        
        try {
            console.log(`\n[${this.stats.downloaded + 1}/${this.stats.totalUrls}] Downloading: ${url}`);
            console.log(`  Section: ${sectionName}, Page: ${pageNumber}, Title: ${title}`);
            
            // Navigate to page
            await this.page.goto(url, { 
                waitUntil: 'networkidle2',
                timeout: config.pageTimeout
            });

            // Wait a bit for any dynamic content
            await new Promise(resolve => setTimeout(resolve, 1000));

            // Get page content
            const htmlContent = await this.page.content();
            
            // Extract and download images
            const images = await this.extractImages();
            
            // Save HTML file
            const filename = this.generateFilename(sectionName, pageNumber);
            const htmlPath = path.join(config.outputDir, config.pagesDir, `${filename}.html`);
            
            // Process HTML to update image paths
            const processedHtml = this.processHtmlContent(htmlContent, images);
            await fs.writeFile(htmlPath, processedHtml);
            
            // Download images
            const downloadedImages = await this.downloadImages(images);
            
            console.log(`  ✓ Saved: ${filename}.html (${downloadedImages.length} images)`);
            
            this.stats.downloaded++;
            this.stats.images += downloadedImages.length;
            this.downloadedUrls.add(url);
            
            return {
                success: true,
                url,
                filename: `${filename}.html`,
                images: downloadedImages.length
            };
            
        } catch (error) {
            console.error(`  ✗ Error downloading ${url} (attempt ${attempt}):`, error.message);
            
            if (attempt < config.retryAttempts) {
                console.log(`  ↻ Retrying... (${attempt + 1}/${config.retryAttempts})`);
                await new Promise(resolve => setTimeout(resolve, 2000));
                return this.downloadPage(urlData, attempt + 1);
            } else {
                this.failedUrls.push({ url, error: error.message });
                this.stats.failed++;
                return { success: false, url, error: error.message };
            }
        }
    }

    async extractImages() {
        return await this.page.evaluate(() => {
            const images = Array.from(document.querySelectorAll('img[src]'));
            return images.map(img => ({
                src: img.src,
                originalSrc: img.getAttribute('src'),
                alt: img.alt || '',
                width: img.width || 0,
                height: img.height || 0
            }));
        });
    }

    async downloadImages(images) {
        const downloadedImages = [];
        
        for (const imageData of images) {
            try {
                const imageUrl = imageData.src;
                if (!imageUrl || imageUrl.startsWith('data:')) continue;
                
                // Generate unique filename for image
                const imageExtension = this.getImageExtension(imageUrl);
                const imageHash = crypto.createHash('md5').update(imageUrl).digest('hex').substring(0, 8);
                const imageFilename = `img${downloadedImages.length}_${imageHash}.${imageExtension}`;
                
                // Download image
                const imagePath = path.join(config.outputDir, config.imagesDir, imageFilename);
                
                // Use page to navigate to image and get its content
                const imageResponse = await this.page.goto(imageUrl, { timeout: 10000 });
                
                if (imageResponse && imageResponse.ok()) {
                    const imageBuffer = await imageResponse.buffer();
                    await fs.writeFile(imagePath, imageBuffer);
                    
                    // Store mapping for HTML processing
                    this.imageMapping.set(imageData.originalSrc, `assets/images/${imageFilename}`);
                    
                    downloadedImages.push({
                        originalSrc: imageData.originalSrc,
                        newPath: `assets/images/${imageFilename}`,
                        filename: imageFilename,
                        size: imageBuffer.length
                    });
                }
            } catch (error) {
                console.log(`    ⚠ Could not download image: ${imageData.src} - ${error.message}`);
            }
        }
        
        return downloadedImages;
    }

    processHtmlContent(htmlContent, images) {
        let processedHtml = htmlContent;
        
        // Update image paths in HTML
        for (const [originalSrc, newPath] of this.imageMapping) {
            const regex = new RegExp(`src=["']${originalSrc.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}["']`, 'g');
            processedHtml = processedHtml.replace(regex, `src="${newPath}"`);
        }
        
        return processedHtml;
    }

    generateFilename(sectionName, pageNumber) {
        const safeSectionName = sectionName.replace(/[^a-zA-Z0-9]/g, '_');
        return pageNumber === 0 ? safeSectionName : `${safeSectionName}_page${pageNumber}`;
    }

    getImageExtension(url) {
        const match = url.match(/\.([a-zA-Z0-9]+)(?:\?|$)/);
        return match ? match[1].toLowerCase() : 'jpg';
    }

    async saveProgress() {
        const progressData = {
            timestamp: new Date().toISOString(),
            stats: {
                ...this.stats,
                elapsedTime: this.stats.startTime ? Date.now() - this.stats.startTime : 0,
                successRate: ((this.stats.downloaded / this.stats.totalUrls) * 100).toFixed(1)
            },
            downloadedUrls: Array.from(this.downloadedUrls),
            failedUrls: this.failedUrls,
            imageMapping: Object.fromEntries(this.imageMapping)
        };
        
        await fs.writeFile(
            path.join(config.outputDir, 'download_progress.json'),
            JSON.stringify(progressData, null, 2)
        );
    }

    async run() {
        try {
            await this.initialize();
            
            const urls = await this.loadUrls();
            if (urls.length === 0) {
                console.log('No URLs to download');
                return;
            }

            this.stats.startTime = Date.now();
            console.log(`\nStarting download of ${urls.length} URLs...\n`);

            // Process URLs sequentially to avoid overwhelming the server
            for (const urlData of urls) {
                await this.downloadPage(urlData);
                
                // Save progress every 10 downloads
                if (this.stats.downloaded % 10 === 0) {
                    await this.saveProgress();
                }
                
                // Delay between downloads
                if (this.stats.downloaded < urls.length) {
                    await new Promise(resolve => setTimeout(resolve, config.delayBetweenPages));
                }
            }
            
            // Final save
            await this.saveProgress();
            
            console.log('\n=== Download Complete ===');
            console.log(`Total URLs: ${this.stats.totalUrls}`);
            console.log(`Downloaded: ${this.stats.downloaded}`);
            console.log(`Failed: ${this.stats.failed}`);
            console.log(`Images: ${this.stats.images}`);
            console.log(`Success rate: ${((this.stats.downloaded / this.stats.totalUrls) * 100).toFixed(1)}%`);
            console.log(`Output directory: ${config.outputDir}`);
            
            if (this.failedUrls.length > 0) {
                console.log('\nFailed URLs:');
                this.failedUrls.forEach(fail => {
                    console.log(`  - ${fail.url}: ${fail.error}`);
                });
            }
            
        } catch (error) {
            console.error('Fatal error:', error);
        } finally {
            if (this.browser) {
                await this.browser.close();
            }
        }
    }
}

// Run the downloader
const downloader = new RobustDownloader();
downloader.run().catch(console.error); 