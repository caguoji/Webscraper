import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

rolex_url = 'https://www.rolex.com'

class RolexspiderSpider(scrapy.Spider):
    name = "rolexspider"
    #allowed_domains = ["www.rolex.com"]
    #start_urls = ["https://www.rolex.com/en-us/watches"]
    
    
    
    def start_requests(self):
        url = 'https://www.rolex.com/en-us/watches'
        yield SeleniumRequest(
                    url=url, 
                    callback=self.parse, 
                    wait_time=2
                    )

    def parse(self, response):
        
        
        model_types = response.css('div.dark-theme.css-1bss45e.e1y25pk71') + response.css('div.light-theme.css-1bss45e.e1y25pk71')
        
        for model in model_types:   
            link_suffix = model.css('a.inline.reverseIcon.css-17wfajn.eob9b3y0').attrib['href']+'/all-models'

            if 'air-king' in link_suffix:
                link_suffix = model.css('a.inline.reverseIcon.css-17wfajn.eob9b3y0').attrib['href']
             
            link_suffix = link_suffix.lower().replace(" ","-")
            model_link = rolex_url+link_suffix

            yield response.follow(model_link,callback=self.parse_models_page)

    def parse_models_page(self,response):
        
        watches = response.css('div.css-hfsu5e.eyz9ve26').css('ul li a::attr(href)').getall()
       

        for watch in watches:
            watch_link_suffix = watch.replace("'",'')
            watch_model_link = rolex_url + watch_link_suffix
           
            yield SeleniumRequest(url=watch_model_link,callback=self.parse_watch_model,script="document.querySelector('.css-1tg8aam e1yf0wve3').click()")

    
    def parse_watch_model(self,response):
        
        keys = response.css('ul.css-1pwmb5z.e1yf0wve2 h5::text').getall()
        values = response.css('ul.css-1pwmb5z.e1yf0wve2 p::text').getall()

        #tabular data
        specs = dict(zip(keys,values))
     

        other_data = {
        
        'Model' : response.css('section.css-1vaz9md.e11axyq41 h2::text').get(),
        'Model Case' : response.css('ul.css-1pwmb5z.e1yf0wve2 li p::text').get(),
        'Price' : response.css('p.css-2im8jf.css-1g545ff.e8rn6rx1 span::text').get(),
        'Reference_Number': response.css('p.css-pzm8qd.e1yf0wve6 ::text').getall()[2]

        }
        
        yield {**specs, **other_data}

               
       
    


       
