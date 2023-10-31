# Scrapy settings for quotes_js_scraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'quotes_js_scraper'

SPIDER_MODULES = ['quotes_js_scraper.spiders']
NEWSPIDER_MODULE = 'quotes_js_scraper.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'quotes_js_scraper (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True
IMAGES_STORE = 'Images'



DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
PLAYWRIGHT_LAUNCH_OPTIONS = {"headless":True}

IMAGES_THUMBS = {
    'transparent': (500, 500)
}


# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'quotes_js_scraper.pipelines.QuotesJsScraperPipeline': 300,
    'scrapy.pipelines.images.ImagesPipeline':1,
    'quotes_js_scraper.pipelines.CustomImagesPipeline':300,
  
}

IMAGES_EXPIRES = 180 #default is 90 days
IMAGES_MIN_WIDTH = 800

