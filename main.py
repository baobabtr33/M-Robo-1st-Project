import feedparser
import time
import pandas as pd
import naverFinance
import DART_Crawling_Preprocessing
import makeChart
import Write_Article
from dateutil.parser import parse
from datetime import datetime, timedelta



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
    #
    # ret.append(('단일판매ㆍ공급계약체결','http://dart.fss.or.kr/dsaf001/main.do?rcpNo=20201020800165', datetime.today(),'우원개발'))

    # entry 가장 최근 공시가 위, 내림차순
    for e in fp.entries:
        if(parse(e.published) <= date_tracker):         # compare date to get new feed
            break
        entry_tuple = (e.title, e.link, parse(e.published),e.author)
        ret.append(entry_tuple)


    #  TEST
    print("Checking RSS: new feed : " + str(len(ret)))
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



# initial Settings
date_tracker = parse("Mon, 1 Jan 1000 00:00:01 GMT")
my_driver_path = "/Users/KimJungHwan/Desktop/m-Robo/proj1"


# TEST DART Crawling
#DART_df = DART_Crawling_Preprocessing.dart_crawling(my_driver_path, "http://dart.fss.or.kr/dsaf001/main.do?rcpNo=20201013900126")
#DART_preprocess_df = DART_Crawling_Preprocessing.dart_preprocess(DART_df)
#print(DART_preprocess_df)

# switch on and off 0 /1
while(1):
    new_feed, date_tracker = new_rss(date_tracker)
    for RSS_info in new_feed:
        # 정정은 다루지 않는다, 자회사의 도, 자율공시도
        if("단일판매ㆍ공급계약체결" in RSS_info[0] and not "정정" in RSS_info[0]):
            # new feed tuple
            # 0. title 1. link 2. datetime 3. creator
            print(RSS_info[0])
            print(RSS_info[1])
            print(RSS_info[2])
            print(RSS_info[3])

            corpCode = corp_to_code(RSS_info[3])
            print(str(corpCode))

            feed_num = RSS_info[1].split('rcpNo=')[1]
            print("FEED NUm" + feed_num)
            stock_df = naverFinance.crawlStock(str(corpCode))
            print(stock_df)
            
            print("+++++++++++++++ WEB CRAWL +++++++++++++++")
            DART_df = DART_Crawling_Preprocessing.dart_crawling(my_driver_path, RSS_info[1])
            DART_preprocess_df = DART_Crawling_Preprocessing.dart_preprocess(DART_df)
            print(DART_preprocess_df)
            print("+++++++++++++++++Write Article++++++++++++++++++++")
            
            chart_file = []
            chart_file.append(makeChart.draw_stock_chart(stock_df,RSS_info[3],feed_num))
            chart_file.append(makeChart.draw_comparison_chart("계약 규모", feed_num, "최근 매출액", "이번계약",
                                                        DART_preprocess_df[DART_preprocess_df.index.str.contains('최근')][0],
                                                        DART_preprocess_df[DART_preprocess_df.index.str.contains('계약금액')][0]))


            # 제목
            title = Write_Article.Title(DART_preprocess_df, RSS_info)
            print(title)
            # 기사 생성
            first_sen, third_sen = Write_Article.first_third_sentence(DART_preprocess_df, RSS_info)
            print(first_sen)
            second_sen = Write_Article.second_sentence(DART_preprocess_df)
            print(second_sen)
            final_sen = Write_Article.final_sentence(RSS_info, stock_df)
            print(final_sen)
            final_article = Write_Article.Article(first_sen, second_sen, third_sen, final_sen)
            print()
            print(final_article)


            print()
            print("=========================END=========================")
    print("WAITING...")
    time.sleep(60)
