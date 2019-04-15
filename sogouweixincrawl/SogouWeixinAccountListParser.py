
from lxml import etree

class SogouWeixinAccountParser(object):

    __content = None

    def __init__(self, content):
        self.__content = content

    def parser(self):
        accountListHtml = etree.HTML(self.__content, etree.HTMLParser())

        accountList = {}
        if accountListHtml is not None:

            accountElements = accountListHtml.xpath(".//li[starts-with(@id,'sogou_vr_')]")

            for element in accountElements:
                accountInfo = dict()
                accountInfo['appid'] = element.attrib["d"]
                accountInfo['logo'] = element.find(".//div[@class='img-box']//img").attrib["src"]
                nameLink = element.find(".//div[@class='txt-box']//a")
                accountInfo['name'] = nameLink.xpath("string(.)")
                accountInfo['nameUigs'] = nameLink.attrib['uigs']
                accountInfo['weixinhao'] = element.find(".//label[@name='em_weixinhao']").text
                introductionElement = element.find(".//dl[1]/dd")
                if introductionElement is not None:
                    accountInfo['introduction'] = introductionElement.text
                companyElement = element.find(".//dl[2]/dd")
                if companyElement is not None:
                    accountInfo['company'] = companyElement.text
                recentArticleTitle = element.find(".//dl[3]/dd/a")
                if recentArticleTitle is not None:
                    accountInfo['recentArticleTitle'] = recentArticleTitle.text
                    accountInfo['recentArticleLink'] = recentArticleTitle.attrib['href']
                    accountInfo['recentArticleUigs'] = recentArticleTitle.attrib['uigs']
                accountList[accountInfo['appid']] = accountInfo

        return accountList