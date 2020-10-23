import hgtk
import datetime


# 숫자 단위 변환 함수
def convert_number(num):
    """
    계약규모나 최근 매출액 등 큰 숫자값을 조/억/만 단위의 숫자로 변환해주는 함수
    
    params :
        num : 숫자값(str)
    
    return :
        result : 문자값(str)
    """
    result = ""
    
    num = int(num)

    if num >= 1000000000000: # 1조
        result = f"{int(num // 1000000000000):,}조"
    elif num >= 100000000: # 1억
        result = f"{int(num // 100000000):,}억"
    elif num >= 10000: # 1만
        result = f" {int(num // 10000):,}만"
    elif num >= 1: # 1
        result = f" {int(num):,}"

    return result


#제목 함수
# 기업명 계약상대명과(와) 계약규모원 계약체결

def Title(DART_preprocess_df, RSS_info):
    """
    단일 공급 계약 체결 기사의 제목
    params :
        DART_preprocess_df : 공시 내용 table  (series)
        RSS_info : RSS에서 가져온 tuble 형식 데이터
    return :
        title : 기사 제목
    """
    corp = RSS_info[3] #회사명
    print(DART_preprocess_df)
    partner = DART_preprocess_df[DART_preprocess_df.index.str.contains('계약상대')][0] #계약상대 회사명
    bf_contract_price = DART_preprocess_df[DART_preprocess_df.index.str.contains('계약금액')][0] #공시, 자율공시 둘다 첫번째 인덱스가 계약금액을 가지고 있다.
    contract_price = convert_number(bf_contract_price) #계약금액 변환

    title = corp + ' ' + hgtk.josa.attach(partner, hgtk.josa.GWA_WA) + ' ' +  contract_price +'원' + ' 계약체결'

    return title

#문장 생성
# 1, 3번째 문장
def first_third_sentence(DART_preprocess_df, RSS_info):
    """
    1st, 3rd 문장 생성

    params:
        DART_preprocess_df : 공시 내용 table  (series)
        RSS_info : RSS에서 가져온 tuple 형식 데이터

    return :
        first_sen, thrid_sen : 각각 첫번째, 세번째 문장
    """
    # 필요한 내용
    corp = RSS_info[3] #기업명
    partner = DART_preprocess_df[DART_preprocess_df.index.str.contains('계약상대')][0] #계약상대 회사명
    bf_contract_price = DART_preprocess_df[DART_preprocess_df.index.str.contains('계약금액')][0] #공시, 자율공시 둘다 첫번째 인덱스가 계약금액을 가지고 있다.
    contract_price = convert_number(bf_contract_price) #계약금액 변환
    recent_sales = convert_number(DART_preprocess_df[DART_preprocess_df.index.str.contains('최근')][0]) #최근 매출액
    diff = DART_preprocess_df[DART_preprocess_df.index.str.contains('대비')][0] # 매출액 대비

    #첫번째 문장
    first_sen = hgtk.josa.attach(corp, hgtk.josa.EUN_NEUN) + ' ' + hgtk.josa.attach(partner, hgtk.josa.GWA_WA) + ' ' + contract_price+'원' + ' 규모의 계약을 체결했다고 ' + str(RSS_info[2].day) + '일에 공시했다.'

    #세번쨰 문장
    third_sen = '계약규모는 ' + contract_price+'원으로 최근 매출액인 ' + recent_sales + ' 대비 ' + diff + '% 수준이다'

    return first_sen, third_sen

#두번째 문장
def second_sentence(DART_preprocess_df):
    """
    두번째 문장 생성 함수
        *시작일, 종료일 유무에 따라 달라짐
    params:
        DART_preprocess_df : 공시 내용 table  (series)

    return :
        second_sen : 두번째 문장
    """
    # 필요한 내용
    contract_content = DART_preprocess_df[0] # 계약 내용
    start_date = DART_preprocess_df['시작일'] ; end_date = DART_preprocess_df['종료일']

    start_date_year = start_date[0:4] ; start_date_month = start_date[5:7] ; start_date_day = start_date[8:10]
    end_date_year = end_date[0:4] ; end_date_month = end_date[5:7] ; end_date_date = end_date[8:10]

    # 상황에 따라 문장 생성
    second_sen_both = '이번 계약은 ' + contract_content+'이고 계약기간은 ' + start_date_year +'년 ' +  start_date_month + '월 ' + start_date_day + '일부터 ' + end_date_year +'년 ' +  end_date_month + '월 ' + end_date_date + '일까지이다.'

    second_sen_none = '이번 계약은 ' + contract_content+'이다.'

    second_sen_first = '이번 계약은 ' + contract_content+'이고 계약기간은 ' + start_date_year +'년 ' +  start_date_month + '월 ' + start_date_day + '일부터이다.'

    second_sen_end = '이번 계약은 ' + contract_content+'이고 계약기간은 ' + end_date_year +'년 ' +  end_date_month + '월 ' + end_date_date + '일까지이다.'

    # if 문
    second_sen = ''
    if (start_date == '-') & (end_date == '-') :
        second_sen = second_sen_none
    elif (start_date != '-') & (end_date == '-') :
        second_sen = second_sen_first
        second_sen = second_sen_none
    elif (start_date == '-') & (end_date != '-') :
        second_sen = second_sen_end
    elif (start_date != '-') & (end_date != '-') :
        second_sen = second_sen_both

    return second_sen

# 마지막 문
## 직전일 대비 변화량 : 상승, 하락, 변동 x 함수 만들기
def inc_dec_ing(x):
    """
    장 진행 중일 때 변화량에 따라 달라지는 함수

    params :
        x: 직전거래일 대비 변화량 (%) (str)

    return :
        result :
            1) 상승일 경우 : 변화량%) 상승이며
            2) 하락일 경우 : 변화량%) 하락이며
            3) 변동 없음 : 변동이 없으며
    """
    result = ''
    if float(x) > 0 :
        result = x + '%) 상승이며'
    elif float(x)  < 0:
        result = x + '%) 하락이며'
    elif float(x)  == 0:
        result = '변동이 없으며'
    return result


def inc_dec_done(x):
    """
    장 마감일 때 변화량에 따라 달라지는 함수

    params :
        x: 직전거래일 대비 변화량 (%)

    return :
        result :
            1) 상승일 경우 : 변화량%) 상승했다.
            2) 하락일 경우 : 변화량%) 하락했다.
            3) 변동 없음 : 변동이 없다.
    """
    result = ''
    if float(x)  > 0 :
        result = x + '%) 상승했다.'
    elif float(x)  < 0:
        result = x + '%) 하락했다.'
    elif float(x)  == 0:
        result = '변동이 없다.'
    return result

# 마지막 문장
def final_sentence(RSS_info, stack_df):
    """
    마지막 문장 생성 함수
        *장 마감 이전, 이후 / 직전거래일 대비 상승 하락 구분하여 생성

    params :
        RSS_info : RSS에서 가져온 tuple 형식 데이터
        stack_df : 주가 데이터
    return :
        final_sen : 마지막 문장 return
    """
    #필요한 내용
    corp = RSS_info[3] #기업명

    #장마감 전
    stock_price = str(stack_df['종가'][0])
    stock_diff_won = str(stack_df['전일비'][0])
    stock_diff_per = str(round((stack_df["종가"][0] - stack_df["종가"][1]) / stack_df["종가"][1], 2) )
    stock_vol = str(stack_df['거래량'][0])

    #상황에 따른 문장 생성

    # 장 진행 중
    final_sen_ing = '한편 ' + corp + '의 ' + str(RSS_info[2].hour) + '시' + str(RSS_info[2].minute) + '분 현재주가는 '  + stock_price +'원으로 직전 거래일 대비 ' + stock_diff_won +'원(' + inc_dec_ing(stock_diff_per) + ', 거래량은 ' + stock_vol + '주이다.'

    # 장마감 후 - 당일 (15시 ~ 18시)
    final_sen_day = '한편 ' + corp + '은 장마감 이후 해당 기업공시를 발표했으며, 오늘 종가가 ' + stock_price +'원, 거래량은 ' + stock_vol + '주로, 직전 거래일 대비 ' + stock_diff_won + '원(' + inc_dec_done(stock_diff_per)

    # 장 마감 후 _ 다음날
    final_sen_dayafter = '한편 ' + corp + '은 장시작 전에 해당 기업공시를 발표했으며, 전날 종가는 ' + stock_price +'원, 거래량은 ' + stock_vol + '주로, 직전 거래일 대비 ' + stock_diff_won + '원(' + inc_dec_done(stock_diff_per)


    # if 문

    final_sen = ''
    current_hour = datetime.datetime.now().hour
    if (current_hour >= 10) and (current_hour < 15): # 장 진행 중
        final_sen = final_sen_ing
    elif (current_hour >= 15) and (current_hour < 18) : # 장 마감 당일
        final_sen = final_sen_day
    elif ((current_hour >= 7) and (current_hour < 10))  : # 6시 이후에 올린 공시는 다음날 7시 30분에 공시처리 됨.
        final_sen = final_sen_dayafter
    elif ((current_hour >= 18) and (current_hour < 19)):
        final_sen = final_sen_dayafter

    return final_sen


# 최종 기사 생성
def Article(first_sen, second_sen, third_sen, final_sen):
    """
    기사를 합쳐서 완성하는 함수

    params :
        first_sen, second_sen, third_sen, fianl_sen : 각각 1, 2, 3, 4번째 문장(str)

    return :
        final_article : 최종 기사
    """

    final_article = print(first_sen + '\n\n' + second_sen + '\n\n' + third_sen + '\n\n' + final_sen + '\n')

    return final_article
