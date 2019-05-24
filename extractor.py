# coding: utf-8
import os
import re
import time
import codecs
import shutil
import chardet
import copy
import traceback
import pymysql.cursors
from w3lib.html import remove_tags
from lxml.html import fromstring
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class ExtractorQCC():

    def __init__(self):
        self.data_path = r'./data/'
        self.backup_path = './backup_data/'
        self.connection = pymysql.connect(host='localhost', user='root', password='123456', db='spider_data',charset='utf8mb4')
        # self.file = self.get_files()
        # self.file_path = self.all_files_path(self.file)


    def get_files(self):
        '''获取需要解析的文档'''
        files = os.listdir(self.data_path)
        if files:
            return files[0]
        return None


    def extractor(self, file):
        '''解析'''
        with codecs.open(file, 'r', 'utf-8') as f:
            html = f.read()
        if not html:
            return
        tree = fromstring(html)
        com_items = tree.cssselect('table.m_srchList tr')
        if not com_items:
            return
        index = 0
        for item in com_items:
            com_id = com_name = legal_man = more_tel = registered_money = found_time = telephone = email = addr = business_scope = '-'

            # com_id  公司id
            c_item = item.cssselect('label input')
            if c_item:
                com_id = c_item[0].get('value')

            # com_name  公司名
            n_item = item.cssselect('td a.ma_h1')
            if n_item:
                com_name_str = n_item[0].get('onclick')
                t_com_name = re.findall(u"{'企业名称':'(.*?)'}", com_name_str.replace('\\',''), re.S)
                if t_com_name:
                    com_name = remove_tags(t_com_name[0])

            # legal_man / more_tel  法定人 / 更多号码
            l_item = item.cssselect('p.m-t-xs a.text-primary')
            if l_item:
                if l_item[0].text:
                    legal_man = l_item[0].text
                if len(l_item) == 2:
                    if u'更多号码' == l_item[1].text:
                        more_tel_str = l_item[1].get('onclick')
                        more_tel = ' '.join(re.findall('{"t":"(.*?)"', more_tel_str)[1:])

            # registered_money/found_time/telephone  注册资本/成立时间/电话
            r_item = item.cssselect('p.m-t-xs span.m-l')
            if r_item:
                for _ in r_item:
                    if u'注册资本' in _.text:
                        registered_money = re.findall(u'注册资本：(.*)', _.text)[0]
                    elif u'成立时间' in _.text:
                        found_time = re.findall(u'成立时间：(.*)', _.text)[0]
                    elif u'电话' in _.text:
                        telephone = re.findall(u'电话：(.*)', _.text)[0]

            # email/addr  邮箱/地址
            e_item = item.cssselect('p.m-t-xs')
            if e_item:
                for _ in e_item:
                    if u'邮箱' in _.text:
                        email = re.findall(u'邮箱：(.*)', _.text)[0]
                    elif u'地址' in _.text:
                        addr = re.findall(u'地址：(.*)', _.text)[0]

            # business_scope 经营范围
            b_item = item.cssselect('p i.i')
            if b_item:
                for _ in b_item:
                    if u'经营范围' in _.tail:
                        business_scope = re.findall(u'经营范围：(.*)', _.tail)[0]
                        if not business_scope:
                            business_scope = '-'
            index += 1
            print(index)
            print(com_id, com_name, legal_man, registered_money, found_time, email, telephone, more_tel, addr, business_scope)
            self.insert_mysql(com_id, com_name, legal_man, registered_money, found_time, email, telephone, more_tel, addr, business_scope)



    def insert_mysql(self, com_id, com_name, legal_man, registered_money, found_time, email, telephone,more_tel, addr, business_scope):
        '''向mysql数据库插入数据'''
        try:
            with self.connection.cursor() as c:
                c.execute("insert into qichacha_data_2(com_id, com_name, legal_man, registered_money, found_time, email, telephone, more_tel, addr, business_scope) values('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(com_id.strip().encode('utf8'), com_name.strip().encode('utf8'), legal_man.strip().encode('utf8'), registered_money.strip().encode('utf8'), found_time.strip().encode('utf8'), email.strip().encode('utf8'), telephone.strip().encode('utf8'), more_tel.strip().encode('utf8'), addr.strip().encode('utf8'), business_scope.strip().encode('utf8')))
            self.connection.commit()
        except Exception as e:
            print('insert into mysql error')
            traceback.print_exc()


    def run(self):
        while True:
            file = self.get_files()
            if not file:
                continue
            file = self.data_path + file
            self.extractor(file)
            try:
                shutil.move(file, self.backup_path)
            except:
                time.sleep(2)
                try:
                    shutil.move(file, self.backup_path)
                except:
                    pass
                    # traceback.print_exc()



if __name__ == '__main__':
    extractor = ExtractorQCC()
    extractor.run()
    # extractor.extractor(r'./data/data/4e968080-3b1c-11e9-bae4-5cea1da2a168.txt')