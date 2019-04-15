#encoding:utf-8
from netcrawl.CreateCrawl import getBaseCrawler
from selenium.webdriver.common.by import By
from lxml import etree
from selenium.webdriver.support import expected_conditions as EC
import re
import json
from SogouWeixinAccountListParser import SogouWeixinAccountParser
from SogouWeixinVerify import SogouWeixinVerify

class SogouWeixinCrawl(object):
    __crawl = None

    __verifyFunc = None
    __parserFunc = None

    __keyword = ""
    __accountList = dict()

    __sogouVerifyFunc = None
    __weixinVerifyFunc = None

    def __init__(self, sogouVerifyFunc=None, weixinVerifyFunc=None):
        self.__sogouVerifyFunc = sogouVerifyFunc
        self.__weixinVerifyFunc = weixinVerifyFunc
        self.__crawl = getBaseCrawler()

    def getAccountList(self, keyword):

        if len(self.__accountList) > 0:
            return

        self.__keyword = keyword
        self.keywordUrl = "http://weixin.sogou.com/weixin?type=1&query=%s&ie=utf8&s_from=input&_sug_=y&_sug_type_="%(self.__keyword)

        self.__crawl.getContent(self.keywordUrl)

        accountListElement = self.__crawl.findElement(By.CLASS_NAME, 'news-list2')

        if accountListElement is None:
            SogouWeixinVerify().check(self.__crawl, self.__sogouVerifyFunc, self.__weixinVerifyFunc)
            return

        listHtml = accountListElement.get_attribute("innerHTML")
        
        self.__accountList = SogouWeixinAccountParser(listHtml).parser()

        return self.__accountList
    
    def getArticleList(self, key):

        if len(self.__accountList) == 0:
            self.getAccountList(key)

        nameUigs = None
        for account in self.__accountList:
            if key in self.__accountList[account]['name']:
                nameUigs = self.__accountList[account]['nameUigs']
                break
        
        if nameUigs:
            self.__crawl.clickElement(self.__crawl.findElement(By.XPATH, '//a[@uigs="%s"]'%(nameUigs)), 
                1, 30)

            pageContent = self.__crawl.getBrowser().page_source

            pattern = re.compile(r"var\s{1}msgList\s?=\s?[^\<\>]+};", re.I | re.M)
            jsonValue = pattern.findall(pageContent)

            if len(jsonValue) > 0:
                jsonValue = jsonValue[0].replace("var msgList","",1).replace("=","",1).strip()
                return json.loads(jsonValue[:-1])
        return []

    def getArticleContent(self, url, func):
        self.__crawl.getContent(url)

        if callable(func):
            func(self.__crawl.findElement(By.XPATH, "//div[@id='img-content']/descendant::img"))

    def getFirstArticleFromAccountList(self, key):

        if len(self.__accountList) == 0:
            self.getAccountList(key)

        articleUigs = None
        for account in self.__accountList:
            if key in self.__accountList[account]['name']:
                articleUigs = self.__accountList[account]['recentArticleUigs']
                break

        if articleUigs:
            self.__crawl.clickElement(self.__crawl.findElement(By.XPATH, '//a[@uigs="%s"]'%(articleUigs)), 
                1, 30)

        return self.__crawl.getBrowser().page_source