import re
import math

import pandas as pd
import numpy as np

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from datetime import datetime


def draw_stock_chart(df, corpname, filing_num):
    """
    3달 주가를 df로 받으면, 3달 주가 차트를 그린다.

    params:
        df : 주식 종가, 날짜를 포함한 df
        corpname : 차트에 들어갈 기업명
        filing_num : 공시고유번호
    return:
        file_save : 저장한 위치와 파일명을 반환
    """

    # Change df to descending
    series_df = df.iloc[::-1]
    font_path = 'data/kor_font/NanumBarunGothic.ttf'
    fontprop = fm.FontProperties(fname=font_path, size=10)

    # make plot
    plt.plot(series_df.index, series_df['종가'])
    plt.xlabel("날짜(일)",fontproperties=fontprop, loc = "right")
    plt.ylabel("주가(원)",fontproperties=fontprop, rotation = "horizontal", loc = "top")
    plt.title(corpname + ", 최근 3개월",fontproperties=fontprop, loc = "right")
    plt.grid(True) # 그리드
    plt.xticks(series_df.index[::7],series_df.index[::7], rotation=45, ha="right")  #ha 로 tick에 맞춘다. / 7일에 한 번 tick label
    file_save = 'db/chart/'+ filing_num + '-chart.png'
    plt.savefig(file_save, bbox_inches='tight')

    #erase
    plt.clf()

    return file_save

def draw_comparison_chart(chart_title, filing_num, comp1_name, comp2_name, comp1_num, comp2_num):
    """
    비교 차트 생성, 비교 차트 주소 반환.

    params:
        chart_title : 차트에 들어갈 title
        filing_num : 공시 보고서 고유 번호
        comp1_name : 라벨1 이름
        comp2_name : 라벨2 이름
        comp1_num : 라벨1 값
        comp2_num : 라벨2 값

    return:
        file_save : 저장한 위치, 파일명을 반환
    """

    # set data for plot
    comp1_num = int(re.search(r'\d+', comp1_num).group()) # to int
    comp2_num = int(re.search(r'\d+', comp2_num).group())
    comp1_num = comp1_num / math.pow(10,8) # 억단위로
    comp2_num = comp2_num / math.pow(10,8)

    # define axis and labels
    y_axis = [str(comp1_name), str(comp2_name)]
    x_axis = [float("{:.2f}".format(comp1_num)),float("{:.2f}".format(comp2_num))]
    y_pos = np.arange(len(y_axis))

    # Create horizontal bar plot
    bars = plt.barh(y_pos, x_axis, height = 0.5)
    font_path = 'data/kor_font/NanumBarunGothic.ttf'
    fontprop = fm.FontProperties(fname=font_path, size=10)
    plt.title('단위 : 억 원', loc='right', fontsize = 10, fontproperties = fontprop)
    plt.title(chart_title, fontproperties = fontprop, fontsize = 15)

    # Create labels on the y-axis
    plt.yticks(y_pos, y_axis)
    locs, labels = plt.yticks()
    for label in labels:
        label.set_fontproperties(fontprop)

    # save plot
    file_save = 'db/chart/'+ filing_num + '-bar.png'
    plt.savefig(file_save, bbox_inches='tight')
    
    # clear data
    plt.clf()

    return file_save
