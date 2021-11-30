#encoding:utf-8
from netcrawl.CreateCrawl import getBaseCrawler
from selenium.webdriver.common.by import By
from lxml import etree
from selenium.webdriver.support import expected_conditions as EC
import re
import json
from sogouweixincrawl.SogouWeixinVerify import SogouWeixinVerify
from sogouweixincrawl.SogouWeixinAccountListParser import SogouWeixinAccountParser
import time

class SogouWeixinCrawl(object):
    __crawl = None

    __verifyFunc = None
    __parserFunc = None

    __keyword = ""
    __accountList = dict()

    __verifyHandler = None

    def __init__(self, sogouVerifyFunc=None, 
        weixinVerifyFunc=None, 
        screenSavePath="verifyscreenimg.png", 
        verifyCodeSavePath="verifyimg.png",
        netAddress="127.0.0.1:4444"):
        
        self.__crawl = getBaseCrawler(netAddress)

        self.__verifyHandler = SogouWeixinVerify(self.__crawl,sogouVerifyFunc, weixinVerifyFunc, screenSavePath, verifyCodeSavePath)

    def getAccountList(self, keyword):

        if len(self.__accountList) > 0:
            return

        mainUrl = "https://weixin.sogou.com/"
        self.__crawl.getContent(mainUrl)
        self.__crawl.waitLast(30)
        self.__keyword = keyword

        queryElement = self.__crawl.findElement(By.ID, "query")
        if queryElement:
            queryElement.send_keys(self.__keyword)
            self.__crawl.findElement(By.XPATH, "//*[@uigs='search_account']").click()
            self.__crawl.waitLast(30)

            # self.keywordUrl = "http://weixin.sogou.com/weixin?type=1&query=%s&ie=utf8&s_from=input&_sug_=y&_sug_type_="%(self.__keyword)

            # self.__crawl.getContent(self.keywordUrl)

            accountListElement = self.__crawl.findElement(By.CLASS_NAME, 'news-list2')

            if accountListElement is None:
                if not self.__verifyHandler.checkSogouVerify():
                    return
                accountListElement = self.__crawl.findElement(By.CLASS_NAME, 'news-list2')

            if accountListElement is not None:
                listHtml = accountListElement.get_attribute("innerHTML")
            
                self.__accountList = SogouWeixinAccountParser(listHtml).parser()

        return self.__accountList
    
    def getArticleList(self, keyword):

        if len(self.__accountList) == 0:
            self.getAccountList(keyword)

        nameUigs = self.getUigsByKey(keyword)

        if nameUigs:
            self.__crawl.clickElement(self.__crawl.findElement(By.XPATH, '//a[@uigs="%s"]'%(nameUigs['nameUigs'])), 
                1, 30)

            if not self.__verifyHandler.checkWeixinVerify():
                return

            pageContent = self.__crawl.getBrowser().page_source

            pattern = re.compile(r"var\s{1}msgList\s?=\s?[^\<\>]+};", re.I | re.M)
            jsonValue = pattern.findall(pageContent)

            if len(jsonValue) > 0:
                jsonValue = jsonValue[0].replace("var msgList","",1).replace("=","",1).strip()
                return json.loads(jsonValue[:-1])
        return []

    def getArticleContent(self, url):
        self.__crawl.getContent(url)
        time.sleep(2)

        if not self.__verifyHandler.checkWeixinVerify():
                return

        contentElement = self.__crawl.findElement(By.XPATH, "//div[@id='img-content']")
        if contentElement:
            return contentElement.get_attribute("outerHTML")
        else:
            return ""

    def getFirstArticleFromAccountList(self, keyword, parserfunc=None):

        if len(self.__accountList) == 0:
            self.getAccountList(keyword)

        articleUigs = self.getUigsByKey(keyword)

        if articleUigs:
            self.__crawl.clickElement(self.__crawl.findElement(By.XPATH, '//a[@uigs="%s"]'%(articleUigs['recentArticleUigs'])), 
                1, 30)
            time.sleep(2)

            if not self.__verifyHandler.checkWeixinVerify():
                return

        if parserfunc:
            return parserfunc(self.__crawl)
        else:
            return self.__crawl.getBrowser().page_source

    def getUigsByKey(self, keyword = None):
        '''

        根据key获取页面对应的点击元素

        '''
        
        if keyword is None:
            return None

        for account in self.__accountList:
            if keyword == self.__accountList[account]['weixinhao'] or keyword == self.__accountList[account]['name']:
                return self.__accountList[account]
        
        return None

    def saveScreen(self, path):
        self.__crawl.getBrowser().save_screenshot(path)

    def reset(self):
        self.__accountList = dict()