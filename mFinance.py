import pandas as pd
import requests
from bs4 import BeautifulSoup
import traceback
from datetime import datetime, timedelta
import mLog
import logging.config

def parse_naver_page(code, page):
    """
    네이버 페이지 주식 데이터 파싱

    params:
        code : 종목 코드
        page : 종목 주식 페이지

    return:
        table_df : 페이지 나온 종목 주가들 df
    """

    # Go to naver finance for corp stock data
    url = 'http://finance.naver.com/item/sise_day.nhn?code={code}&page={page}'.format(code=code, page=page)
    res = requests.get(url)

    # TODO: 반환된 status에 문제가 있다면 해결방안
    mLog.status_checker(__name__, res.status_code)

    soup = BeautifulSoup(res.text, 'lxml')
    df = pd.read_html(str(soup.find("table")), header=0)[0]
    df = df.dropna()
    return df


def get_pg_last(soup):
    """
    주어진 페이지에서 navigator로 마지막 페이지를 찾는다.

    params:
        soup: 파싱한 html 정보

    return:
        pg_last : 마지막 페이지 넘버
    """

    el_table_navi = soup.find("table", class_="Nnavi")
    el_td_last = el_table_navi.find("td", class_="pgRR")
    pg_last = el_td_last.a.get('href').rsplit('&')[1]
    pg_last = pg_last.split('=')[1]
    pg_last = int(pg_last)

    return pg_last


def crawl_stock(corporation_code):
    """
    네이버 증권에서 종목의 주가 데이터를 가지고 온다.

    params:
        corporation_code : 종목 코드

    return:
        df : 90일간 종목 주가 데이터
    """

    url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=corporation_code)
    res = requests.get(url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'lxml')
    logger = logging.getLogger(__name__)

    mLog.status_checker(__name__, res.status_code)

    # get date range for 3 months
    minus_90_days = datetime.today() - timedelta(days=90)
    str_datefrom = datetime.strftime(minus_90_days, '%Y.%m.%d')
    df = None
    try:
        pg_last = get_pg_last(soup)

    except AttributeError:
        logger = logging.getLogger(__name__)
        logger.warning(
            "Cannot find stock information for corporation code {} from NAVER Finance".format(corporation_code))
        return

    # traverse through needed pages to collect data
    for page in range(1, pg_last+1):
        _df = parse_naver_page(corporation_code, page)
        _df_filtered = _df[_df['날짜'] > str_datefrom]
        if df is None:
            df = _df_filtered
        else:
            df = pd.concat([df, _df_filtered])
        if len(_df) > len(_df_filtered):
            break

    return df.set_index('날짜')
