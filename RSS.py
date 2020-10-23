import feedparser
from dateutil.parser import parse
from datetime import datetime, timedelta
import pandas as pd


def new_rss(date_tracker):
    """
    다트 RSS를 통해 새로 올라온 공시를 가져오고, 공시의 제목, 링크, 날짜, 작성기업을 반환한다.

    params:
        date_tracker : 지금까지 확인한 날짜/시각 datetime

    return:
        ret : 공시 table 내용을 가지고 옴
        date_tracker : 확인한 가장 최근공시의 날짜/시각 datetime
    """

    url = "http://dart.fss.or.kr/api/todayRSS.xml"
    fp = feedparser.parse(url)
    ret = []

    ret.append(('단일판매ㆍ공급계약체결','http://dart.fss.or.kr/dsaf001/main.do?rcpNo=20201013900126', datetime.today(),'우원개발'))

    # entry 가장 최근 공시가 위, 내림차순
    for e in fp.entries:
        if(parse(e.published) <= date_tracker):         # compare date to get new feed
            break
        entry_tuple = (e.title, e.link, parse(e.published),e.author)
        ret.append(entry_tuple)


    #  TEST
    print("Checking RSS - new feed(s) : " + str(len(ret)))
    #ret.append(('단일판매ㆍ공급계약체결','http://dart.fss.or.kr/dsaf001/main.do?rcpNo=20201013900126',datetime.today(),'엔씨소프트'))
    #ret.append(('단일판매ㆍ공급계약체결','https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20201020900377',datetime.today(),'엔씨소프트'))
    # TEST

    return ret, parse(fp.entries[0].published)


def corp_to_code(corpname):
    """
    기업명이 주어지면, 기업 종목 코드를 반환한다

    params:
        corpname : 공시 기업명

    return:
        code : 공시기업 코드
    """

    corporation = pd.read_csv('data/corporation_code.csv')
    code = str(corporation[corporation['회사명']==corpname]['종목코드'].values[0].item())
    code = '0'*(6-len(code)) + code
    return code
