from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, portrait
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch

from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter

import os

def generate_waterMarkPDF(serial_number, file_path, size, start_position):
    # ユーザのデスクトップのディレクトリを取得
    file = "WaterMark.pdf"
    # file_path = os.path.expanduser("~") + "/Desktop/" + file

    # 新規PDFファイルを作成
    page = canvas.Canvas(file_path, pagesize=(size[0]*4, size[1]*4))

    # フォントの読み込み
    pdfmetrics.registerFont(TTFont("Arial", "C:/Windows/Fonts/arial.ttf"))

    # フォントの設定(第1引数：フォント、第2引数：サイズ)
    page.setFont("Arial", int(y/30))
    # 指定座標が左端となるように文字を挿入
    page.drawRightString(int(size[0]*0.97) + int(start_position[0]), int(size[1]*0.97) + int(start_position[1]), serial_number)


    # PDFファイルとして保存
    page.save()


if __name__ == "__main__":

    print('开始运行，请确保目标文件在同一目录下')
    target_folder = input('请输入目标文件夹名称')

    current_path = os.getcwd()

    #folder contains files without watermark
    current_folder_path = os.path.join(current_path, target_folder)
    #Judge if the file path exist, otherwise
    # if exist
    if (not os.path.exists(current_folder_path)):
        exit()

    #folder contains files with watermark
    target_folder_path = os.path.join(current_path, target_folder + '_WaterMark')
    if (not os.path.exists(target_folder_path)):
        os.mkdir(target_folder_path)

    # pdf_file = current_path + r'/Sample.pdf'
    # watermark = current_path + r'/WaterMark.pdf'
    # merged = current_path + r'/Merged.pdf'

    file_name_list = os.listdir(current_folder_path)

    for file_name in file_name_list:
        if file_name.endswith(".pdf"):
            current_pdf_path = os.path.join(current_folder_path, file_name)
            current_pdf = PdfFileReader(current_pdf_path)

            watermark_pdf_path = os.path.join(target_folder_path, 'WaterMark.pdf')
            merged_pdf_path = os.path.join(target_folder_path, file_name)
            
            output = PdfFileWriter()
            
            for i in range(current_pdf.getNumPages()):
                x = float(current_pdf.getPage(i).bleedBox.getUpperRight_x() - current_pdf.getPage(i).bleedBox.getLowerLeft_x())
                y = float(current_pdf.getPage(i).bleedBox.getUpperRight_y() - current_pdf.getPage(i).bleedBox.getLowerLeft_y())
                generate_waterMarkPDF(file_name.split('.pdf')[0], watermark_pdf_path, [x, y], [current_pdf.getPage(i).bleedBox.getLowerLeft_x(), current_pdf.getPage(i).bleedBox.getLowerLeft_y()])
                watermark_pdf = PdfFileReader(watermark_pdf_path)

                watermark_page = watermark_pdf.getPage(0)
                pdf_page = current_pdf.getPage(i)
                
                pdf_page.mergePage(watermark_page)
                #pdf_page.mergeScaledPage(current_pdf.getPage(i), 0.8)
                pdf_page.compressContentStreams()
                output.addPage(pdf_page)
            with open(merged_pdf_path, "wb") as merged_file:
                output.write(merged_file)
                print('成功为 %s 生成水印文件'%(file_name))
    
    print('运行结束，请确认在同一目录下的生成文件夹，名称为' + target_folder + '_WaterMark')

    if os.path.exists(watermark_pdf_path):
        os.remove(watermark_pdf_path)

    input('按任意键结束')

