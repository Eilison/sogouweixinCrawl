
from lxml import etree
from PIL import Image

class SogouWeixinVerify(object):

    def check(self, crawl=None, sogouVerifyFunc=None, weixinVerifyFunc=None):
        if crawl is None:
            return
        
        pageHtml = etree.HTML(crawl.page_source, etree.HTMLParser())

        sogouVerifyElement = pageHtml.xpath('//*[@id="seccodeImage"]')
        
        if sogouVerifyElement:
            
            if callable(sogouVerifyFunc):
                sogouVerifyFunc(crawl, self.getVerifyImg(crawl, sogouVerifyElement))
            return
        
        weixinVerifyElement = pageHtml.xpath('//*[@class="weui_input"]')
        
        if weixinVerifyElement:
            
            if callable(weixinVerifyFunc):
                weixinVerifyFunc(crawl, self.getVerifyImg(crawl, weixinVerifyElement))
            return

    def getVerifyImg(self, crawl, element):
        location = element.location
        size = element.size

        crawl.getBrowser().save_screenshot("screenimg.png")

        x = location['x']
        y = location['y']
        width = location['x']+size['width']
        height = location['y']+size['height']

        im = Image.open('screenimg.png')
        im = im.crop((int(x), int(y), int(width), int(height)))
        im.save('verifyimg.png')
        return im