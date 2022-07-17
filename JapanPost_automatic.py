import requests
from bs4 import BeautifulSoup


import os

import datetime
import chardet
from sqlalchemy import desc
import xlrd
import xlwt
from tqdm import tqdm

now = datetime.datetime.now()
url_list = []
current_path = os.getcwd()
jpn_url = 'http://tracking.post.japanpost.jp/service/singleSearch.do?org.apache.struts.taglib.html.TOKEN=&searchKind=S002&locale=ja&SVID=&reqCodeNo1='


# def parse_title_link(url):

#     page_response = requests.get(url)

#     if page_response.status_code == 200:
#         try:
#             page_data = page_response.text.lstrip('getNewsContentOnlyOutput(').rstrip(')')
#             page_json = json.loads(page_data)
#         except Exception as e:
#             print('error occured', e, 'when getting this page', url)
#     else:
#         print ("Can't get the page", url, "go to the next page")
#         return

def preprocess(inputHTML):
    try:
        charset = chardet.detect(inputHTML)
        inputHTML = inputHTML.decode(charset['encoding'], 'ignore')
    except UnicodeDecodeError as e:
        print(e)
    else:
        return inputHTML

def parse_content(link):
    try:
        r = requests.get(link)
        r.encoding = 'utf-8'
        data = r.text
        soup = BeautifulSoup(data)
        paras_table = soup.find(attrs= {'summary': '履歴情報'})
        row = paras_table.findChildren('tr')[-2]
        cell = row.findChildren('td')[1]
        status = cell.text
        #print(status)
        if len(status) > 1:
            return status
        else:
            return 'no status'

        # paras_more = soup.find(attrs={'id': 'news_textmore'}).get_text()
        # paras = paras_body+paras_more
        # return paras
    except Exception as ex:
        #print('link has skip, regenerate url')
        return 'no status'
    

def Generate_Link_list(url, file_name):

    number_list = []
    file_path = current_path + file_name
    wb = xlrd.open_workbook(file_path)
    sheet = wb.sheet_by_index(0)
    number_list = sheet.col_values(0)[1:]
    for i in tqdm(range(len(number_list))):
        if len(str(int(number_list[i]))) > 1:
           url_list.append(url + str(int(number_list[i])))
    return number_list, url_list

def Generate_status_list(url_list):
    status_list = []
    for i in tqdm(range(len(url_list)), desc = "生成Excel"):
        status_list.append(parse_content(url_list[i]))
    return status_list

def Generate_Excel(number_list, status_list):
    wb = xlwt.Workbook(encoding='ascii')
    sheet = wb.add_sheet("result")
    sheet.write(0, 0, "number")
    sheet.write(0, 1, "status")
    if (len(number_list) == len(status_list)):
        for i in range(len(number_list)):
            sheet.write(1+i, 0, number_list[i])
            sheet.write(1+i, 1, status_list[i])
    wb.save('郵便局問合せ結果.xls')

################################################
if __name__ == "__main__":

    print('开始运行，请确保文件名在同一目录下，名称为 邮局单号.xlsx')
    number_list = []
    url_list = []
    status_list = []

    number_list, url_list  = Generate_Link_list(jpn_url, "/邮局单号.xlsx")
    status_list = Generate_status_list(url_list)
    Generate_Excel(number_list, status_list)
    print('运行结束，请确认在同一目录下的生成结果，名称为 郵便局問合せ結果.xls')