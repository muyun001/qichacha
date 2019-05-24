# encoding=utf-8
__author__ = 'zhuming'

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import uuid
import requests

class SpiderQCC(object):

    def __init__(self):
        options = ChromeOptions()
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36')
        self.driver = webdriver.Chrome(chrome_options=options)

    def open(self, word, province, start_date):
        self.driver.get("https://www.qichacha.com/")
        locator = (By.ID, 'searchkey')
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(locator))
        self.driver.delete_cookie("QCCSESSID")
        self.driver.add_cookie({'name':'QCCSESSID', 'value':'8m6kegjp03th6229it1pcunit4'})
        self.driver.get("https://www.qichacha.com/search?key={}#p:1&phone:MN&statusCode:10&registfund:0-500&province:{}&startDate:{}&".format(word, province, start_date))
        # self.driver.get('https://www.qichacha.com/search?key=%E7%BD%91%E7%BB%9C%E8%90%A5%E9%94%80#p:1&phone:MN&statusCode:10&registfund:0-500&startDate:2001&')
        # self.driver.get("https://www.qichacha.com/search?key=%E7%BD%91%E7%BB%9C%E8%90%A5%E9%94%80#p:1&phone:MN&statusCode:10&registfund:0-500&province:BJ&startDate:0-2000&")
        locator = (By.CSS_SELECTOR, 'span.text-danger')
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(locator))
        time.sleep(5)

        if self.get_num():
            self.get_list()

    def get_prov(self):
        html = self.driver.execute_script("return document.documentElement.outerHTML")
        html = html.encode('utf-8')

        pass

    def get_num(self):
        num = 0
        try:
            num_ele = self.driver.find_element(By.CSS_SELECTOR, '#countOld > span.text-danger')
            return int(num_ele.text)
        except:
            return num

    def get_list(self, page=1):
        # tr_list = self.driver.find_elements(By.CSS_SELECTOR, "#search-result > tr")
        # if len(tr_list):
        #     for item in tr_list:
        #         company_id = self.get_company_id(item)
        #         company = self.get_company_name(item)
        #         print(company_id, company)
        html = self.driver.execute_script("return document.documentElement.outerHTML")
        html = html.encode('utf-8')
        self.write_txt(html)

        pages = self.driver.find_elements(By.ID, "ajaxpage")
        page_link = None
        if len(pages):
            for item in pages:
                if item.text == ">":
                    page_link  = item
                    break
        if page_link:
            page_link.click()
            time.sleep(10)
            page = page+1
            self.get_list(page)


    def get_company_id(self, item):
        inputs = item.find_elements(By.TAG_NAME, "input")
        if len(inputs):
            ele = inputs[0]
            return ele.get_attribute("value")

    def get_company_name(self, item):
        links = item.find_elements(By.TAG_NAME, "a")
        if len(links):
            ele = links[0]
            return ele.text

    def write_txt(self, body):
        with open(r"data\{}.txt".format(str(uuid.uuid1())), 'ab+') as f:
            f.write(body)

if __name__ == "__main__":

    dates = ["0-2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012",
             "2013", "2014", "2015", "2016", "2017", "2018", "2019"]
    provinces = ["AH", "BJ", "CQ", "FJ", "GD", "GS", "GX", "GZ", "HAIN", "HB", "HEN", "HK", "HLJ", "HUB", "HUN", "JL",
                 "JS", "JX", "LN", "NMG", "NX", "QH", "SAX", "SC", "SD", "SH", "SX", "TJ", "XJ", "XZ", "YN", "ZJ", "CN"]

    provinces_dict = {'安徽': 'AH', '北京': 'BJ', '重庆': 'CQ', '福建': 'FJ', '广东': 'GD', '甘肃': 'GS', '广西': 'GX', '贵州': 'GZ', '海南': 'HAIN', '河北': 'HB', '河南': 'HEN', '香港特别行政区': 'HK', '黑龙江': 'HLJ', '湖北': 'HUB', '湖南': 'HUN', '吉林': 'JL', '江苏': 'JS', '江西': 'JX', '辽宁': 'LN', '内蒙古': 'NMG', '宁夏': 'NX', '青海': 'QH', '陕西': 'SAX', '四川': 'SC', '山东': 'SD', '上海': 'SH', '山西': 'SX', '天津': 'TJ', '新疆': 'XJ', '西藏': 'XZ', '云南': 'YN', '浙江': 'ZJ', '总局': 'CN'}


    words = ['网络营销']
    spider = SpiderQCC()

    for word in words:
        for date in dates:
            for prov in provinces:
                spider.open(word, prov, date)
                time.sleep(5)
