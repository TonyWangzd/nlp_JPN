#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from optparse import OptionParser
import re
import json
import os
import time
import datetime
import chardet
import sys
import random

reload(sys)
sys.setdefaultencoding('utf-8')

now = datetime.datetime.now()
file_name_list = []

##################################################################

def parse_blanklist(item, title_name, title_content):
    number = random.randint(0,1000)
    initial_file_name = "nhk_" + item + str(number) + "JPN.txt"
    #generate file path
    path = options.dest+'/'+item+'/'
    if not os.path.exists(path):
        os.makedirs(path)
    #file_name_list.append(path + initial_file_name)
    print("start scrape " + title_name)

    try:
        # write the content to the file
        if len(title_content):
            with open(path + initial_file_name, 'a') as write_file:
                write_file.write(title_name + '\n')
                write_file.write(title_content)
    except Exception as ex:
        print(ex)

    print(title_name + "successfully scraped")


def parse_content(link):
    try:
        r = requests.get(link)
        r.encoding = 'utf-8'
        data = r.text
        soup = BeautifulSoup(data)
        paras_body = soup.find(attrs={'id': 'news_textbody'}).get_text()
        paras_more = soup.find(attrs={'id': 'news_textmore'}).get_text()
        paras = paras_body+paras_more
        return paras
    except Exception as ex:
        print('link has skip, regenerate url')

def parse_json(domain):
    if domain == 'social':
        url = "https://www3.nhk.or.jp/news/json16/cat01_00"
    if domain == 'weather':
        url = "https://www3.nhk.or.jp/news/json16/cat08_00"
    if domain == 'culture':
        url = "https://www3.nhk.or.jp/news/json16/cat03_00"
    if domain == 'politics':
        url = "https://www3.nhk.or.jp/news/json16/cat04_00"
    if domain == 'sports':
        url = "https://www3.nhk.or.jp/news/json16/cat07_00"
    for i in range(1,9):
        tar_url = url+str(i)+'.json'
        parse_title_link(domain, tar_url)
        print('finish page'+str(i))


def parse_title_link(domain, url):

    page_response = requests.get(url)

    if page_response.status_code == 200:
        try:
            page_data = page_response.text.lstrip('getNewsContentOnlyOutput(').rstrip(')')
            page_json = json.loads(page_data)
        except Exception as e:
            print('error occured', e, 'when getting this page', url)
    else:
        print ("Can't get the page", url, "go to the next page")
        return

    if page_json['channel']:
        page_result = page_json['channel']
        for line in page_result['item']:
            home_link = 'https://www3.nhk.or.jp/news/'
            url_link = home_link+line.get('link')
            datestring = url_link.split('/')[-2]
            if currentdate_compare(datestring):
                title_name = line.get('title')
                title_content = parse_content(url_link)
                parse_blanklist(domain, title_name, title_content)
                # write the content to the file
                print('finish parse'+url_link)

def filter_content(content):
    try:
        content = content.split('\n')
        filter_pool = ['<br>']
        delete_line = []
        for line in content:
            content[content.index(line)] = re.sub('["■▲▼○△→●]', '', line)
            for word in filter_pool:
                if word in line:
                    delete_line.append(line)
                    break
            continue
        for item in delete_line:
            content.remove(item)

        # delete the repeated line
        news_content = list(set(content))
        news_content.sort(key=content.index)
        return news_content
    except Exception as e:
        print(e)

def preprocess(inputHTML):
    try:
        charset = chardet.detect(inputHTML)
        inputHTML = inputHTML.decode(charset['encoding'], 'ignore')
    except UnicodeDecodeError as e:
        print(e)
    else:
        return inputHTML
def generate_path(initial_path):
    return os.path.join(initial_path, year4FsMonth2FsDay2())

def year4FsMonth2FsDay2():
    return (time.strftime("%Y/%m/%d/", time.gmtime()))

def currentdate_compare(date):
    return (time.strftime("%Y%m%d", time.gmtime())) == date

#################################################
usage = '''
 python2.7 %prog [--debug]

 <<NOTE>>
'''
################################################
if __name__ == "__main__":

    parser = OptionParser(usage=usage)

    parser.add_option('--dest', dest='dest',
                      #default='/Users/wangzhaodong/code/JPN_classification/data/text-train.inc')
                        default = '/Users/wangzhaodong/PycharmProjects/nlp_JPN/nhk_news')
    parser.add_option('--debug', action='store_true', dest='debug', default=False,
                      help='print status messages to stdout')

    options, args = parser.parse_args()


    try:
        print("start scraping")
        number = 1
        domains = ['social', 'weather', 'culture', 'politics', 'sports']
        for item in domains:
            print('scraping', item)
            parse_json(item)

        print('Program Complete')
    except Exception as e:
        print(e)



