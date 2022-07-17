
import requests
from bs4 import BeautifulSoup
import os
import datetime
import xlrd
import xlwt
from tqdm import tqdm

now = datetime.datetime.now()
url_list = []
current_path = os.getcwd()
jpn_url = "https://toi.kuronekoyamato.co.jp/cgi-bin/tneko" 

def parse_content(trackcode, url):
    try:
        r = requests.post(url, {"number01":str(trackcode), "number00":1})
        soup = BeautifulSoup(r.text, "html.parser")
        rs = soup.find("div", class_="tracking-invoice-block-detail")
        if rs == None:
            #print("追跡番号の情報がありません。")
            return '情報なし'
        else:
            rs = [i for i in rs.text.splitlines()]
            rs = [rs[3:][idx:idx + 5] for idx in range(0,len(rs[3:]), 5)] 
            ds = rs[-1][0]
            #print(ds)
            return ds
        # paras_more = soup.find(attrs={'id': 'news_textmore'}).get_text()
        # paras = paras_body+paras_more
        # return paras
    except Exception as ex:
        print('link has skip, regenerate url')
        return 'no status'
    

def Generate_Link_list(url, file_name):

    number_list = []
    file_path = current_path + file_name
    wb = xlrd.open_workbook(file_path)
    sheet = wb.sheet_by_index(0)
    number_list = sheet.col_values(0)[1:]
    return number_list

def Generate_status_list(number_list):
    status_list = []
    for i in tqdm(range(len(number_list)), desc='查询单号状态'):
        status_list.append(parse_content(str(int(number_list[i])), jpn_url))
    return status_list

def Generate_Excel(number_list, status_list):
    wb = xlwt.Workbook(encoding='ascii')
    sheet = wb.add_sheet("ressult")
    sheet.write(0, 0, "number")
    sheet.write(0, 1, "status")
    if (len(number_list) == len(status_list)):
        for i in range(len(number_list)):
            sheet.write(1+i, 0, number_list[i])
            sheet.write(1+i, 1, status_list[i])
    wb.save('yamato問合せ結果.xls')

################################################
if __name__ == "__main__":

    print('开始运行，请确保文件名在同一目录下，名称为 yamato单号.xlsx')
    number_list = []
    status_list = []

    parse_content('624234637073', jpn_url)

    number_list  = Generate_Link_list(jpn_url, "/yamato单号.xlsx")
    status_list = Generate_status_list(number_list)
    Generate_Excel(number_list, status_list)
    print('运行结束，请确认在同一目录下的生成结果，名称为 yamato問合せ結果.xls')

    