import time
import RSS
import pandas as pd
import mFinance
import mDART
import mChart
import mArticle
import mEmail
import sys
import argparse
import logging
import logging.config
from datetime import datetime
from dateutil.parser import parse


def main(argv):
    # get Arguments
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('path', type=str,
                            help="Chrome Driver Path must be given")
    arg_parser.add_argument('state', type=str,
                            help="Need to choose \"test\" or  \"service\" for the project")
    args = arg_parser.parse_args()

    if args.state == "test" or args.state == "service":
        logger.info("Starting program: service")
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
                logger.debug("Title : {} Link : {} Datetime : {} Creator : {}".format(RSS_info[0], RSS_info[1],
                                                                                      RSS_info[2], RSS_info[3]))
                logger.info("Target Filing: " + RSS_info[3] + " " + RSS_info[0])

                corp_code = RSS.corp_to_code(RSS_info[3])
                if corp_code != "":
                    logger.info("Converting corporation name to code: COMPLETE")
                else:
                    continue

                feed_num = RSS_info[1].split('rcpNo=')[1]
                stock_df = mFinance.crawl_stock(str(corp_code))
                if stock_df is not None:
                    logger.info("Fetching stock data from NAVER finance: COMPLETE")
                else:
                    continue

                DART_df = mDART.dart_crawling(my_driver_path, RSS_info[1])
                DART_preprocess_df = mDART.dart_preprocess(DART_df)
                if DART_preprocess_df is not None:
                    logger.info("Fetching DART filing data from DART: COMPLETE")
                else:
                    continue


                chart_file = []
                chart_file.append(mChart.draw_stock_chart(stock_df, RSS_info[3], feed_num))
                chart_file.append(mChart.draw_comparison_chart("계약 규모", feed_num, "최근 매출액", "이번계약",
                                                               DART_preprocess_df[DART_preprocess_df.index.str.contains('최근')][0],
                                                               DART_preprocess_df[ DART_preprocess_df.index.str.contains('계약금액')][0]))
                logger.info("Making charts: COMPLETE")

                title, first_sen, second_sen, third_sen, final_sen = mArticle.write_title_article(
                    DART_preprocess_df, RSS_info, stock_df)
                logger.info("Composing sentence for new article: COMPLETE")

                str_from_email_addr = 'tndhks3837@gmail.com'  # 발신자
                str_to_email_addrs = ['tndhks3837@gmail.com', 'stevekim0131@naver.com']  # 수신자리스트
                mEmail.Sending_Final_Email(RSS_info[1], title, first_sen, second_sen, third_sen, final_sen,
                                           chart_file,
                                           str_from_email_addr, str_to_email_addrs)
                logger.info("Sending e-mail to recipient: COMPLETE")
                logger.info("TASK COMPLETE!!")

        logger.info("WAITING for RSS feed ...")
        time.sleep(60)

if __name__ == "__main__":
    # 로그 생성
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger(__name__)

    # 'application' code
    logger.debug('debug message')
    logger.info('info message')
    logger.warning('warn message')
    logger.error('error message')
    logger.critical('critical message')

    main(sys.argv[1:])
