# 크롤링에 필요한 library
import requests
import time
import pandas as pd
from bs4 import BeautifulSoup
import selenium
from selenium import webdriver as wd
from tqdm import tqdm
import lxml.html
import os
import re
import logging.config

def dart_crawling(my_driver_path, url):
    """
    다트 사이트에서 html을 이용하여 공시 table 가지고 오는 함수

    params:
        driver : chromedriver가 있는 경로를 넣어주세요.
        url : 공시 url을 넣어주세요

    return:
        DART_df : 공시 table 내용을 가지고 옴
    """
    try :
        # 크롬드라이버 경로 설정
        current_path = os.getcwd()                          #현재 경로 저장
        os.chdir(my_driver_path)                            #chromedriver가 있는 경로로 바꿔줌

        driver = wd.Chrome(r'chromedriver')                 #chromedriver 불러오기
        os.chdir(current_path)                              # 원래 경로로 다시 바꾸기
        time.sleep(2)
        driver.get(url)

        # iframe 바꿔주기
        driver.switch_to_default_content                    #iframe 안 내용으로 바꿔줌.
        driver.switch_to.frame('ifrm')

        # html에서 table html 추출하기
        html = driver.page_source

        # table 시작 index
        p = re.compile("<table")
        m = p.search(html)
        start_idx= m.start()

        #table 끝 index
        p = re.compile("</table>")
        m = p.search(html)
        end_idx= m.end()

        #table html 불러오기
        table_html = html[start_idx: end_idx]
        html_df = pd.read_html(table_html)
        DART_df = html_df[0]

    except WebDriverException:
        logging.warning("Message: 'chromedriver.exe' executable needs to be in PATH. Please see https://sites.google.com/a/chromium.org/chromedriver/home")
        exit()


    return DART_df


def dart_preprocess(DART_df):
    """
    가지고온 table에서 필요한 정보만 추출해내는 함수

    params:
        DART_df: 크롤링하여 가지고온 데이터프레임 형식의 공시

    return:
        DART_preprocess_df : 공시 table 중 필요한 내용만 시리즈 형식으로 추출.
    """
    if DART_df.shape[1] > 2 :
        #공시 소제목과 공시 내용만 추출함.
        DART_df.columns = ['공시대제목', '공시소제목', '공시내용', '공시내용2(같은내용)']
        idx= DART_df[DART_df['공시소제목'].str.contains("종료일")].index[0]  # 종료일 이후는 안 쓴다.
        DART_preprocess_df = DART_df.iloc[:idx+1,  1:3]
        DART_preprocess_df.set_index('공시소제목', inplace= True)

        #series로 바꾸기
        DART_preprocess_df = pd.Series(DART_preprocess_df['공시내용'])

    else:
        logging.warning("Fetching Wrong Table")
        return None

    return DART_preprocess_df
