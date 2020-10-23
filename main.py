import time
import RSS
import pandas as pd
import naverFinance
import DART_Crawling_Preprocessing
import makeChart
import Write_Article
import Sending_Email
import sys
import argparse


from dateutil.parser import parse



def main (argv):
    # initial Settings



    date_tracker = parse("Mon, 1 Jan 1000 00:00:01 GMT")

    argsparser = argparse.ArgumentParser()
    argsparser.add_argument('path', type=str,
                help="Chrome Driver Path must be given")

    args = argsparser.parse_args()
    my_driver_path = args.path



    # TEST DART Crawling
    #DART_df = DART_Crawling_Preprocessing.dart_crawling(my_driver_path, "http://dart.fss.or.kr/dsaf001/main.do?rcpNo=20201013900126")
    #DART_preprocess_df = DART_Crawling_Preprocessing.dart_preprocess(DART_df)
    #print(DART_preprocess_df)

    # switch on and off 0 /1
    while(1):
        new_feed, date_tracker = RSS.new_rss(date_tracker)
        for RSS_info in new_feed:
            # 정정은 다루지 않는다, 자회사의 도, 자율공시도
            if("단일판매ㆍ공급계약체결" in RSS_info[0] and not "정정" in RSS_info[0]):
                # new feed tuple
                # 0. title 1. link 2. datetime 3. creator
                print(RSS_info[0])
                print(RSS_info[1])
                print(RSS_info[2])
                print(RSS_info[3])

                corpCode = RSS.corp_to_code(RSS_info[3])
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

                Sending_Email.sendMail('tndhks3837@gmail.com','stevekim0131@naver.com',title,final_article, chart_file)

                print()
                print("=========================END=========================")
        print("WAITING...")
        time.sleep(60)

if __name__ == "__main__":
   main(sys.argv[1:])