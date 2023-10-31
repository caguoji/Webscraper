import scrapy
from scrapy import Request
from scrapy_playwright.page import PageMethod
import asyncio
from scrapy.selector import Selector
from quotes_js_scraper.items import RolexItem
import PIL 
import os
import boto3

rolex_url = 'https://www.rolex.com'

class RolexspiderSpider(scrapy.Spider):
    name = "scrapy_playwright2"
    #allowed_domains = ["www.rolex.com"]
    start_urls = ["https://www.rolex.com/en-us/"]

    custom_settings = {
        'DOWNLOAD_DELAY': 3 # 2 seconds of delay
        }

    def start_requests(self):
        yield scrapy.Request(
                    url=self.start_urls[0], 
                    callback=self.parse
                    )

    def parse(self, response):
            #identify all mens and womens models

            model_types = [item for item in response.css('li.css-1avotsj.ey03tbv0  ::attr(href)').getall() if 'man' in item]
            
            #remove non-watch related link
            model_types.pop(2)

             #loop through model pages to view page with all watch types for each model
            #for model in model_types_test:
            for model in model_types:   
                # link_suffix = model.css('a.inline.reverseIcon.css-1s6tw48.eob9b3y0').attrib['href']+'/all-models'

                # #there is only one watch type for the air king model 
                # if 'air-king' in link_suffix:
                #     link_suffix = model.css('a.inline.reverseIcon.css-1s6tw48.eob9b3y0').attrib['href']
                
                # link_suffix = link_suffix.lower().replace(" ","-")
                #model_link = rolex_url+link_suffix
                model_link = rolex_url + model

                #click on link for each model
                yield scrapy.Request(model_link,meta=dict(playwright=True,playwright_include_page=True),callback=self.parse_models_page,errback=self.errback)
               
    async def parse_models_page(self,response):
        page = response.meta["playwright_page"]
        page.set_default_timeout(60000)

        #click on consent button if visible
        try:
            while consent_button := page.locator('button.css-1slsuqb'):
                await consent_button.click()
        except:
             pass

        #click on view more button if visible
        try:
             while button := page.locator('button.css-ke5f4e.eyz9ve20'):
                  await button.scroll_into_view_if_needed()
                  await button.click()
        except:
             pass
    

        content = await page.content()  # get the page content
       
        sel = Selector(text=content)  # place in a scrapy selector
        #list of all of the watch links on the page
        watches = sel.css('li.css-zjik7.eyz9ve24 ::attr(href)').getall()
        #save watch type based on original response
        watch_type = response.url.split('/')[-1]

        await page.close()

        for watch in watches:
            watch_link_suffix = watch.replace("'",'')
            watch_model_link = rolex_url + watch_link_suffix
            
            yield scrapy.Request(
                url=watch_model_link, 
                meta=dict(playwright=True,playwright_include_page=True, playwright_page_methods= [
                    PageMethod("wait_for_timeout",60000)],type= watch_type),
                callback=self.parse_watch_page,
                errback=self.errback
            )

            await page.close()

    async def parse_watch_page(self,response):
        page = response.meta["playwright_page"]
        content = await page.content()  # get the page content
        selector = Selector(text=content)  # place in a scrapy selector
        
        # #print/save html page
        file_name = response.url.split('/')[-1]
        folder_name = response.url.split('/')[-2]
        # print(f"The working directory is:",os.getcwd())
        
        # if os.path.exists('./HTML'+'/'+folder_name):
        #     os.chdir('./HTML')
        #     os.chdir(folder_name)
        # else:
        #     os.chdir('./HTML')
        #     os.mkdir(folder_name)
        #     os.chdir(folder_name)

        # with open(file_name+".txt", "w") as text_file:
        # #with open(f, "w") as text_file:
        #     text_file.write(content)
        
        # os.chdir('../..')

        rolex_item = RolexItem()

        #scrape fields
        rolex_item['nickname'] = response.css('ul.css-1o13pd1.e1yf0wve5 li p::text').getall()[0],
        rolex_item['diameter'] = response.css('ul.css-1o13pd1.e1yf0wve5 li p::text').getall()[2],
        rolex_item['case_material'] = response.css('ul.css-1o13pd1.e1yf0wve5 li p::text').getall()[3],
        rolex_item['crystal'] = response.css('ul.css-1o13pd1.e1yf0wve5 li p::text').getall()[6],
        rolex_item['water_resistance'] = response.css('ul.css-1o13pd1.e1yf0wve5 li p::text').getall()[7],
        rolex_item['movement'] =response.css('ul.css-1o13pd1.e1yf0wve5 li p::text').getall()[8],
        rolex_item['caliber'] =response.css('ul.css-1o13pd1.e1yf0wve5 li p::text').getall()[9],  
        rolex_item['power_reserve'] =response.css('ul.css-1o13pd1.e1yf0wve5 li p::text').getall()[14],
        rolex_item['bracelet_material'] =response.css('ul.css-1o13pd1.e1yf0wve5 li p::text').getall()[16],
        rolex_item['clasp_type'] =response.css('ul.css-1o13pd1.e1yf0wve5 li p::text').getall()[17],
        rolex_item['case_shape'] = '',
        rolex_item['made_in'] = '',
        rolex_item['case_finish']='',
        rolex_item['caseback']='',
        rolex_item['dial_color'] =response.css('ul.css-1o13pd1.e1yf0wve5 li p::text').getall()[18],  
        rolex_item['specific_model'] =selector.css('p.css-17wwe8r.e89szto5  ::text').get(),
        rolex_item['price'] =response.css('p.css-2im8jf.css-1g545ff.e8rn6rx1 ::text').get(),
        rolex_item['reference_number'] =response.url.split('/')[-1],
        rolex_item['external_url'] =response.url,
        rolex_item['image_urls'] =selector.css('figure.wv_reveal img.css-fmei9v.er6nhxj0 ::attr(srcset)').get().split(',')[4],
        rolex_item['parent_model'] =' '.join([i.title() for i in str(response).split('/')[-2].split('-')]),  
        rolex_item['lug_to_lug']='',
        rolex_item['case_thickness'] = '',
        rolex_item['between_lugs'] = '',
        rolex_item['weight'] = '',
        rolex_item['description'] = '',
        rolex_item['short_description'] = response.css('div.css-1tggvg6.e1jcjnm81 h2 *::text').getall(),
        rolex_item['marketing_name'] ='',
        rolex_item['sku'] =response.url.split('/')[-1],
        rolex_item['style'] = '',
        rolex_item['brand'] = response.url.split('.')[1],
        rolex_item['year_model_introduced'] = '',
        rolex_item['bezel_material'] ='',
        rolex_item['bezel_color']='',
        rolex_item['numerals'] ='',
        rolex_item['frequency'] ='',
        rolex_item['bracelet_color']='',
        rolex_item['jewels']='',
        rolex_item['type']= response.meta['type'],
        rolex_item['features']= response.css('ul.css-1o13pd1.e1yf0wve5 ul:nth-child(2) li p::text').getall()[5] +", " ,response.css('ul.css-1o13pd1.e1yf0wve5 ul:nth-child(2) li p::text').getall()[19]
        rolex_item['listing_title']=response.url.split('/')[-1]
        rolex_item['group_reference']=selector.css('p.css-pzm8qd.e1yf0wve6 ::text').getall()[-1]

        yield rolex_item

        # with open("html.txt", "w") as text_file:
        #     text_file.write(content)

        # s3 = boto3.resource('s3')
        # BUCKET = 'wcc-library'
        # s3.Bucket(BUCKET).upload_file('html.txt','brand/rolex/HTML/'+folder_name+"/"+file_name+".txt")

        
        
        await page.close()

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()

  
