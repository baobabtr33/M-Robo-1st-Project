import time
import RSS
import pandas as pd
import naver_finance
import DART_crawling_preprocessing
import make_chart
import write_article
import sending_email
import sys
import argparse
import logging

from dateutil.parser import parse


def main(argv):
    # get Arguments
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('path', type=str,
                            help="Chrome Driver Path must be given")
    arg_parser.add_argument('state', type=str,
                            help="Need to choose \"test\" or  \"service\" for the project")
    args = arg_parser.parse_args()

    global project_logger
    project_logger = logging.getLogger("proj1")
    project_logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    project_logger.addHandler(stream_hander)

    file_handler = logging.FileHandler('proj1.log')
    project_logger.addHandler(file_handler)

    project_logger.info("server start!!!")






    if args.state == "test":
        test_ver(args.path)
    elif args.state == "service":
        service_ver(args.path)
    else:
        print("Please choose which version to use (\"test\" or  \"service\")")




def service_ver(my_driver_path):
    # initial Settings
    date_tracker = parse("Mon, 1 Jan 1000 00:00:01 GMT")

    while 1:
        new_feed, date_tracker = RSS.new_rss(date_tracker)
        for RSS_info in new_feed:
            # 정정은 다루지 않는다
            if "단일판매ㆍ공급계약체결" in RSS_info[0] and not "정정" in RSS_info[0]:
                # RSS_info composition
                # 0. title 1. link 2. datetime 3. creator

                corp_code = RSS.corp_to_code(RSS_info[3])
                print("Converting corporation name to code: COMPLETE")

                feed_num = RSS_info[1].split('rcpNo=')[1]
                stock_df = naver_finance.crawl_stock(str(corp_code))
                print("Fetching stock data from NAVER finance: COMPLETE")

                DART_df = DART_crawling_preprocessing.dart_crawling(my_driver_path, RSS_info[1])
                DART_preprocess_df = DART_crawling_preprocessing.dart_preprocess(DART_df)
                print("Fetching DART filing data from DART: COMPLETE")


                chart_file = []
                chart_file.append(make_chart.draw_stock_chart(stock_df, RSS_info[3], feed_num))
                chart_file.append(make_chart.draw_comparison_chart("계약 규모", feed_num, "최근 매출액", "이번계약",
                                                                   DART_preprocess_df[
                                                                       DART_preprocess_df.index.str.contains('최근')][0],
                                                                   DART_preprocess_df[
                                                                       DART_preprocess_df.index.str.contains('계약금액')][
                                                                       0]))
                print("Making charts: COMPLETE")

                title, first_sen, second_sen, third_sen, final_sen = write_article.write_title_article(
                    DART_preprocess_df, RSS_info, stock_df)
                print("Composing sentence for new article: COMPLETE")

                str_from_email_addr = 'tndhks3837@gmail.com'  # 발신자
                str_to_email_addrs = ['tndhks3837@gmail.com', 'stevekim0131@naver.com']  # 수신자리스트
                sending_email.Sending_Final_Email(RSS_info[1], title, first_sen, second_sen, third_sen, final_sen,
                                                  chart_file,
                                                  str_from_email_addr, str_to_email_addrs)
                print("Sending e-mail to recipient: COMPLETE")
                print("=====================================")
                print("==========PROCESS COMPLETE ==========")
                print("=====================================")

        print("WAITING RSS feed ...")
        time.sleep(60)


def test_ver(my_driver_path):
    # initial Settings
    date_tracker = parse("Mon, 1 Jan 1000 00:00:01 GMT")

    # switch on and off 0 /1
    while 1:
        new_feed, date_tracker = RSS.new_rss(date_tracker)
        for RSS_info in new_feed:
            # 정정은 다루지 않는다
            if "단일판매ㆍ공급계약체결" in RSS_info[0] and not "정정" in RSS_info[0]:

                # RSS_info composition
                # 0. title 1. link 2. datetime 3. creator
                print(RSS_info[0])
                print(RSS_info[1])
                print(RSS_info[2])
                print(RSS_info[3])

                corp_code = RSS.corp_to_code(RSS_info[3])
                print(str(corp_code))

                feed_num = RSS_info[1].split('rcpNo=')[1]
                print("FEED NUm" + feed_num)
                stock_df = naver_finance.crawl_stock(str(corp_code))
                print(stock_df)

                print("+++++++++++++++ WEB CRAWL +++++++++++++++")
                DART_df = DART_crawling_preprocessing.dart_crawling(my_driver_path, RSS_info[1])
                DART_preprocess_df = DART_crawling_preprocessing.dart_preprocess(DART_df)
                print(DART_preprocess_df)
                print("+++++++++++++++++Write Article++++++++++++++++++++")

                chart_file = []
                chart_file.append(make_chart.draw_stock_chart(stock_df, RSS_info[3], feed_num))
                chart_file.append(make_chart.draw_comparison_chart("계약 규모", feed_num, "최근 매출액", "이번계약",
                                                                   DART_preprocess_df[
                                                                       DART_preprocess_df.index.str.contains('최근')][0],
                                                                   DART_preprocess_df[
                                                                       DART_preprocess_df.index.str.contains('계약금액')][
                                                                       0]))

                title, first_sen, second_sen, third_sen, final_sen = write_article.write_title_article(
                    DART_preprocess_df, RSS_info, stock_df)

                print("+++++++++++++++++Sending Email++++++++++++++++++++")
                str_from_email_addr = 'tndhks3837@gmail.com'  # 발신자
                str_to_email_addrs = ['tndhks3837@gmail.com', 'stevekim0131@naver.com']  # 수신자리스트
                sending_email.Sending_Final_Email(RSS_info[1], title, first_sen, second_sen, third_sen, final_sen,
                                                  chart_file,
                                                  str_from_email_addr, str_to_email_addrs)

                print()
                print("=========================END=========================")
        print("WAITING...")
        time.sleep(60)


if __name__ == "__main__":
    main(sys.argv[1:])
