import scrapy
from scrapy import Request
from scrapy_playwright.page import PageMethod
import asyncio
from scrapy.selector import Selector
from quotes_js_scraper.items import RolexItem
import PIL 

rolex_url = 'https://www.rolex.com'

class RolexspiderSpider(scrapy.Spider):
    name = "scrapy_playwright"
    #allowed_domains = ["www.rolex.com"]
    start_urls = ["https://www.rolex.com/en-us/watches"]

    custom_settings = {
        'DOWNLOAD_DELAY': 3 # 2 seconds of delay
        }
    
    def start_requests(self):
        yield scrapy.Request(
                    url=self.start_urls[0], 
                    callback=self.parse
                    )

    def parse(self, response):
            #identify all models
            model_types = response.css('div.dark-theme.css-1bss45e.e1y25pk71') + response.css('div.light-theme.css-1bss45e.e1y25pk71')
            #model_types_test = model_types[0:1]
            
            
             #loop through model pages to view page with all watch types for each model
            #for model in model_types_test:
            for model in model_types:   
                link_suffix = model.css('a.inline.reverseIcon.css-1s6tw48.eob9b3y0').attrib['href']+'/all-models'

                #there is only one watch type for the air king model 
                if 'air-king' in link_suffix:
                    link_suffix = model.css('a.inline.reverseIcon.css-1s6tw48.eob9b3y0').attrib['href']
                
                link_suffix = link_suffix.lower().replace(" ","-")
                model_link = rolex_url+link_suffix

                #click on link for each model
                yield scrapy.Request(model_link,meta=dict(playwright=True,playwright_include_page=True),callback=self.parse_models_page,errback=self.errback)
               
    async def parse_models_page(self,response):
        page = response.meta["playwright_page"]
    
        #ensure all watches are visible on model page by clicking on 'load more' button until it no
        #longer appears on the page
        view_more_button = page.locator('button:text("View more")')

        content = await page.content()  # get the page content
       
        selector = Selector(text=content)  # place in a scrapy selector
        
        watches = selector.css('a.css-1232gz9.e1wd4zgb7 ::attr(href)').getall()

        await page.close()

        for watch in watches:
            watch_link_suffix = watch.replace("'",'')
            watch_model_link = rolex_url + watch_link_suffix
            
            yield scrapy.Request(
                url=watch_model_link, 
                meta=dict(playwright=True,playwright_include_page=True, playwright_page_methods= [
                    PageMethod("wait_for_timeout",60000)]),
                callback=self.parse_watch_page,
                errback=self.errback
            )

            await page.close()

    async def parse_watch_page(self,response):
        page = response.meta["playwright_page"]
        content = await page.content()  # get the page content
        selector = Selector(text=content)  # place in a scrapy selector
        
        #print/save html page
        # file_name = response.url.split('/')[-1]
        # folder_name = response.url.split('/')[-2]
        # print(response.url)
        # with open("./HTML/"+folder_name+"/"+file_name+".txt", "w") as text_file:
        #     text_file.write(content)

        rolex_item = RolexItem()

        #scrape data
        rolex_item['specific_model'] = response.css('ul.css-1o13pd1.e1yf0wve5 ul:nth-child(2) li p::text').getall()[0],
        rolex_item['oyster_architecture'] = response.css('ul.css-1o13pd1.e1yf0wve5 ul:nth-child(2) li p::text').getall()[1],
        rolex_item['case_diameter'] = response.css('ul.css-1o13pd1.e1yf0wve5 ul:nth-child(2) li p::text').getall()[2],
        rolex_item['case_material'] = response.css('ul.css-1o13pd1.e1yf0wve5 ul:nth-child(2) li p::text').getall()[3],
        rolex_item['bezel_description'] = response.css('ul.css-1o13pd1.e1yf0wve5 ul:nth-child(2) li p::text').getall()[4],
        rolex_item['winding_crown'] = response.css('ul.css-1o13pd1.e1yf0wve5 ul:nth-child(2) li p::text').getall()[5],
        rolex_item['crystal'] = response.css('ul.css-1o13pd1.e1yf0wve5 ul:nth-child(2) li p::text').getall()[6],
        rolex_item['water_resistance'] = response.css('ul.css-1o13pd1.e1yf0wve5 ul:nth-child(2) li p::text').getall()[7],
        rolex_item['movement'] =response.css('ul.css-1o13pd1.e1yf0wve5 ul:nth-child(2) li p::text').getall()[8],
        rolex_item['calibre'] =response.css('ul.css-1o13pd1.e1yf0wve5 ul:nth-child(2) li p::text').getall()[9],
        rolex_item['precision'] =response.css('ul.css-1o13pd1.e1yf0wve5 ul:nth-child(2) li p::text').getall()[10],
        rolex_item['functions'] =response.css('ul.css-1o13pd1.e1yf0wve5 ul:nth-child(2) li p::text').getall()[11],
        rolex_item['oscillator'] =response.css('ul.css-1o13pd1.e1yf0wve5 ul:nth-child(2) li p::text').getall()[12], 
        rolex_item['winding'] =response.css('ul.css-1o13pd1.e1yf0wve5 ul:nth-child(2) li p::text').getall()[13], 
        rolex_item['power_reserve'] =response.css('ul.css-1o13pd1.e1yf0wve5 ul:nth-child(2) li p::text').getall()[14],
        rolex_item['bracelet'] =response.css('ul.css-1o13pd1.e1yf0wve5 ul:nth-child(2) li p::text').getall()[15],
        rolex_item['bracelet_material'] =response.css('ul.css-1o13pd1.e1yf0wve5 ul:nth-child(2) li p::text').getall()[16],
        rolex_item['clasp_type'] =response.css('ul.css-1o13pd1.e1yf0wve5 ul:nth-child(2) li p::text').getall()[17],
        rolex_item['dial_color'] =response.css('ul.css-1o13pd1.e1yf0wve5 ul:nth-child(2) li p::text').getall()[18],
        rolex_item['details'] =response.css('ul.css-1o13pd1.e1yf0wve5 ul:nth-child(2) li p::text').getall()[19],  
        rolex_item['nickname'] =selector.css('section.css-1vaz9md.e11axyq41 h2::text').get(),
        rolex_item['price'] =response.css('p.css-2im8jf.css-1g545ff.e8rn6rx1 ::text').get(),
        rolex_item['reference_number'] =selector.css('p.css-pzm8qd.e1yf0wve6 ::text').getall()[-1],
        rolex_item['external_url'] =response.url,
        rolex_item['image_urls'] =selector.css('figure.wv_reveal img.css-fmei9v.er6nhxj0 ::attr(srcset)').get().split(',')[4],
        rolex_item['parent_model'] =str(response).split('/')[-2],  
        rolex_item['lug_to_lug']='',
        rolex_item['case_thickness'] = '',
        rolex_item['between_lugs'] = '',
        rolex_item['weight'] = '',
        rolex_item['long_description'] = '',
        rolex_item['short_description'] = response.css('div.css-1tggvg6.e1jcjnm81 h2 *::text').getall(),
        rolex_item['marketing_name'] ='',
        rolex_item['sku'] =selector.css('p.css-pzm8qd.e1yf0wve6 ::text').getall()[-1],
        rolex_item['style'] = '',
        rolex_item['brand'] = response.url.split('.')[1],
        rolex_item['year_model_introduced'] = '',
        rolex_item['bezel_material'] ='',
        rolex_item['bezel_color']='',
        rolex_item['numerals'] ='',
        rolex_item['frequency'] ='',
        rolex_item['bracelet_color']='',
        rolex_item['jewels']='',
        rolex_item['type']='',
        rolex_item['features']='',
        rolex_item['listing_title']=selector.css('p.css-pzm8qd.e1yf0wve6 ::text').getall()[-1]

        yield rolex_item
        
        await page.close()

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()

  
