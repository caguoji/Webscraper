# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
import numpy as np
import cv2
from io import BytesIO
from scrapy.utils.python import get_func_args, to_bytes
from PIL import Image

class CustomImagesPipeline(ImagesPipeline):

     def get_images(self, response, request, info, *, item=None):
        #local variables
        canvas_width=1000 
        canvas_height=1000 
        min_margin=10

        #filepath and original image
        path = self.file_path(request, response=response, info=info, item=item)
        orig_image = self._Image.open(BytesIO(response.body))

        width, height = orig_image.size
        if width < self.min_width or height < self.min_height:
            raise ImageException(
                "Image too small "
                f"({width}x{height} < "
                f"{self.min_width}x{self.min_height})"
            )

        if self._deprecated_convert_image is None:
            self._deprecated_convert_image = "response_body" not in get_func_args(
                self.convert_image
            )
            pass
            if self._deprecated_convert_image:
                warnings.warn(
                    f"{self.__class__.__name__}.convert_image() method overridden in a deprecated way, "
                    "overridden method does not accept response_body argument.",
                    category=ScrapyDeprecationWarning,
                )

        if self._deprecated_convert_image:
            image, buf = self.convert_image(orig_image)
        else:
            image, buf = self.convert_image(
                orig_image, response_body=BytesIO(response.body)
            )
        
        yield path, image, buf

        for thumb_id, size in self.thumbs.items():
            thumb_path = self.thumb_path(
                request, thumb_id, response=response, info=info, item=item
            )
           
            # if orig_image.format in ("PNG", "WEBP") and orig_image.mode == "RGBA":
            #     print('PNG')
            background = self._Image.new("RGBA", orig_image.size, (255, 255, 255,0))
            new_image = self._Image.blend(orig_image,background,alpha=0)
            #image = background.paste(image, image)
            #image = background.convert("RGB")

            # Convert PIL image to OpenCV format
            open_cv_image = cv2.cvtColor(np.array(new_image), cv2.COLOR_RGBA2BGRA)

            # Threshold image to binary
            _, thresh = cv2.threshold(cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY), 1, 255, cv2.THRESH_BINARY)

            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if not contours:
                return None

            # Find the largest contour
            largest_contour = max(contours, key=cv2.contourArea)

            # Find the bounding box of the largest contour
            x, y, w, h = cv2.boundingRect(largest_contour)

            # Add a buffer around the bounding box
            buffer = 10

            x = max(0, x - buffer)
            y = max(0, y - buffer)
            w = min(new_image.size[0], x + w + buffer) - x
            h = min(new_image.size[1], y + h + buffer) - y

            # Crop the image based on the bounding box
            image_cropped = new_image.crop((x, y, x + w, y + h))

            #thumb_buf = BytesIO()
            #image_cropped.save(thumb_buf, "png")
            

            # Aspect ratio
            aspect_ratio = image_cropped.width / image_cropped.height
            
            max_width = canvas_width - 2 * min_margin
            max_height = canvas_height - 2 * min_margin
            
            # Resize the image while maintaining aspect ratio
            if image_cropped.height > image_cropped.width:
                new_height = max_height  # You can also use max_height here
                new_width = int(new_height * aspect_ratio)
            else:
                new_width = max_width  # You can also use max_width here
                new_height = int(new_width / aspect_ratio)
            
            resized_image = image_cropped.resize((new_width, new_height), Image.LANCZOS)

             # Calculate where to paste the image on the canvas
            paste_x = (canvas_width - new_width) // 2
            paste_y = (canvas_height - new_height) // 2
            final_image = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
            final_image.paste(resized_image, (paste_x, paste_y), mask=resized_image.split()[3] if "A" in resized_image.getbands() else None)

            thumb_buf = BytesIO()
            final_image.save(thumb_buf, "png")
            

            thumb_image = resized_image

        yield thumb_path, thumb_image, thumb_buf



class QuotesJsScraperPipeline:
    def process_item(self, item, spider):

        #make changes to caliber field
        adapter = ItemAdapter(item)
        field_name = ['caliber']
        for field_name in field_name:
            value = adapter.get(field_name)
            adapter[field_name] = value[0].split(',')[0]

        
        #make changes to price field
        field_name = ['price']
        for field_name in field_name:
            value = adapter.get(field_name)
            adapter[field_name] = value[0].replace(',','').strip('$')


        #make changes to crystal field
        field_name = ['crystal']
        for field_name in field_name:
            value = adapter.get(field_name)
            adapter[field_name] = value[0].split(' ')[1].replace(',','').title().lstrip().rstrip()


        #make changes to power reserve field
        field_name = ['power_reserve']
        for field_name in field_name:
            value = adapter.get(field_name)
            adapter[field_name] = value[0].replace('Approximately','').rstrip().lstrip().title()

        
        #make changes to short_description field
        field_name = ['short_description']
        for field_name in field_name:
            value = adapter.get(field_name)
            sentence = ''
            for each in value[0]:
                sentence += each
            adapter[field_name] = sentence

        
        #make changes to skus field
        field_names = ['sku','reference_number']
        for field_name in field_names:
            value = adapter.get(field_name)
            adapter[field_name] = value[0].replace('\u00a0','')
        
        #make changes to water resistance field
        field_name = ['water_resistance']
        for field_name in field_name:
            num=0
            num_atm = 0
            value = adapter.get(field_name)
            num = value[0].split('/')[0].split(' ')[2].replace(',','')
            num_atm = int(num)/10
            adapter[field_name] = str(int(num_atm)) + ' ATM'


        #make changes to brand and parent_name field
        field_name = ['brand', 'parent_model']
        for field_name in field_name:
            value = adapter.get(field_name)
            adapter[field_name] = value[0].title()

        
        #make changes to type field
        field_name = ['type']
        for field_name in field_name:
            value = adapter.get(field_name)
            adapter[field_name] = value
            new_val = lambda x: "Men's Watches" if x[0] == "man" else  "Women's Watches" 
            adapter[field_name] = new_val(value)

    
        
        return item
