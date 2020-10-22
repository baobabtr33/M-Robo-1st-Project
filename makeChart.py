import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import pandas as pd
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

    plt.plot(series_df.index, series_df['종가'])
    plt.xlabel("날짜(일)",fontproperties=fontprop, loc = "right")
    plt.ylabel("주가(원)",fontproperties=fontprop, rotation = "horizontal", loc = "top")
    plt.title(corpname + ", 최근 3개월",fontproperties=fontprop, loc = "right")
    plt.grid(True) # 그리드
    plt.xticks(series_df.index[::7],series_df.index[::7], rotation=45, ha="right")  #ha 로 tick에 맞춘다. / 7일에 한 번 tick label
    file_save = 'db/chart/'+ filing_num
    plt.savefig(file_save, bbox_inches='tight')

    return file_save





## make bottom chart
## f(X)compare chart horizontal


## make chart
# def create_horizontal_compare(계약)
