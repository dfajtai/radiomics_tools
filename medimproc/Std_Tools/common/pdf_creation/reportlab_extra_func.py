#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import six
import os, sys
from functools import partial


from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Image, PageBreak, Paragraph, Table, TableStyle, Frame, PageTemplate, BaseDocTemplate
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_JUSTIFY,TA_LEFT,TA_CENTER,TA_RIGHT
from reportlab.lib import utils
from reportlab.lib.units import cm
from reportlab.lib import colors

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

styles = getSampleStyleSheet()
styleN = styles['Normal']
styleH = styles['Heading1']

pdfmetrics.registerFont((TTFont("Times","/home/fajtai/py/Std_Tools/common/pdf_creation/TIMES.ttf")))
pdfmetrics.registerFont((TTFont("Times-Bold","/home/fajtai/py/Std_Tools/common/pdf_creation/TIMES-BOLD.ttf")))

def footer(canvas, doc,content):
    canvas.saveState()
    w, h = content.wrap(doc.width, doc.bottomMargin)
    content.drawOn(canvas, doc.leftMargin, h)
    canvas.restoreState()

def header(canvas, doc, content):
    canvas.saveState()
    w, h = content.wrap(doc.width, doc.topMargin)
    content.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)
    canvas.restoreState()

def header_and_footer(canvas, doc, header_content,footer_content):
    header(canvas,doc,header_content)
    footer(canvas,doc,footer_content)

def get_image(path, width=1*cm):
    img = utils.ImageReader(path)
    iw, ih = img.getSize()
    aspect = ih / float(iw)
    return Image(path, width=width, height=(width * aspect))

def horizontal_line():
    style = TableStyle([
     ("LINEBELOW", (0,0), (-1,-1), 1, colors.black), ])
    t = Table([[""]],colWidths="*")
    t.setStyle(style)
    return t

def add_dataframe(df, simple_font = "Times",bold_font = "Times-Bold"):
    GRID_STYLE = TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                             ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                             ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                             ('BOX', (0,0), (-1,-1), 2, colors.black),
                             ('BOX',(0,0),(-1,0),2,colors.black),
                             ('FONTNAME',(0,1),(-1,-1),simple_font), # additional rows
                             ('FONTNAME',(0,0),(-1,0),bold_font)]) # first row

    df_data = [df.columns.to_list()]
    df_data.extend(np.array(df).tolist())

    t1 = Table(df_data,style=GRID_STYLE)
    return t1

def add_data_array(array, simple_font = "Courier",bold_font = "Courier-Bold"):
    GRID_STYLE = TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                             ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                             ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                             ('BOX', (0,0), (-1,-1), 2, colors.black),
                             ('BOX',(0,0),(-1,0),2,colors.black),
                             ('FONTNAME',(0,1),(-1,-1),simple_font), # additional rows
                             ('FONTNAME',(0,0),(-1,0),bold_font)]) # first row


    t1 = Table(array.tolist(),style=GRID_STYLE)
    return t1

def image_row(img_path_list,img_width,caption_list = None):
    imgs = []
    captions = []

    chart_style = TableStyle([('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                              ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
                              ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                              ('VALIGN', (0, 1), (-1, -1), 'MIDDLE')
                              ])


    if isinstance(caption_list,list):
        for i,c in zip(img_path_list,caption_list):
            try:
                imgs.append(get_image(i,img_width))
                captions.append(c)
            except:
                continue

    else:
        for i in img_path_list:
            try:
                imgs.append(get_image(i,img_width))
            except:
                continue

    if len(captions)>0:
        return Table([imgs,captions], colWidths=[img_width] * len(imgs), style=chart_style)
    else:
        return Table([imgs],colWidths=[img_width]*len(imgs),style= chart_style)

def main():
    pdf_path = "test.pdf"
    doc = BaseDocTemplate(pdf_path,pagesize = A4,rightMargin=24,leftMargin=24,topMargin=24,bottomMargin=24)
    doc_content = []

    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
               id='normal')

    header_content = Paragraph("Header text")
    footer_content = Paragraph("<b>Some fancy bold footer</b>")

    template = PageTemplate(id='test', frames=frame, onPage=partial(header_and_footer,header_content = header_content, footer_content = footer_content))
    doc.addPageTemplates(template)

    info_style = ParagraphStyle( name='Normal',fontName='Courier',fontSize=8)
    caption_style = ParagraphStyle( name='Normal',fontName='Courier',fontSize=16, alignment = TA_CENTER, spaceAfter = 12)


    page = []
    page.append(Paragraph("<b>{0}</b>".format("Some bold bullshit"),style=caption_style))
    page.append(Paragraph("{0}".format("and some not bolt stuff"), style= info_style))
    page.append(add_dataframe(pd.DataFrame({"A":[1,3,4,5],"B":["asd","qwe","sdfsdfad","A"],"C":[0,0,1,3]})))

    doc_content.extend(page)

    doc_content.append(PageBreak())
    doc_content.append(horizontal_line())
    doc_content.append(Paragraph("asdasd"))

    doc.build(doc_content)


if __name__ == '__main__':
    main()
