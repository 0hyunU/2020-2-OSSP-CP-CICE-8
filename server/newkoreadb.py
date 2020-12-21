from urllib.request import urlopen
from urllib.parse import urlencode, unquote, quote_plus
import urllib
import requests
import pandas as pd
import xmltodict
import json
import datetime
import sqlite3
import os

DB_PATH = os.path.dirname(__file__) + '/CoronaBotDB'
days_num = 7 # 받아오는 날짜 수

def five_days_ago(today):
    five = (today-datetime.timedelta(days_num)).strftime("%Y%m%d")
    return five

def make_db():

    today = datetime.datetime.now()

    key = 'RI5ekmQZaQtJcWF%2BFp%2FjIPg3kaXeWQj0MfyFVPynolhE9rUNQjg%2FCdWF1GkZe0UWS63SVaRd26nbQxZMqWGfKQ%3D%3D'
    url = f'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19InfStateJson?serviceKey={key}&'
    queryParams = urlencode({ quote_plus('pageNo') : 1, quote_plus('numOfRows') : 10,quote_plus('startCreateDt') : five_days_ago(today),
                            quote_plus('endCreateDt') : today.strftime("%Y%m%d")})

    url2 = url + queryParams
    response = urlopen(url2)
    results = response.read().decode("utf-8")

    results_to_json = xmltodict.parse(results)
    data = json.loads(json.dumps(results_to_json))

    corona=data['response']['body']['items']['item']

    Date=[]
    Cnt=[]
    clear_cnt=[]
    care_cnt=[]
    death_cnt=[]
    for i in corona:
        Date.append(i['stateDt'])
        Cnt.append(i['decideCnt'])
        clear_cnt.append(i['clearCnt'])
        care_cnt.append(i['careCnt'])
        death_cnt.append(i['deathCnt'])

    df=pd.DataFrame([Date,Cnt,clear_cnt,care_cnt,death_cnt]).T
    df.columns=['Date','acc_cnt', 'clear_cnt', 'care_cnt', 'death_cnt']
    df=df.sort_values(by='Date', ascending=True)

    #날짜 별 확진자/사망자 수 구하기
    df['acc_cnt']=df['acc_cnt'].astype(int)
    df['death_cnt']=df['death_cnt'].astype(int)
    df['clear_cnt']=df['clear_cnt'].astype(int)
    df = df.drop_duplicates(['Date'], keep="last")

    df['확진자 수']=(df.acc_cnt-df.acc_cnt.shift()).fillna(0)
    df['사망자 수']=(df.death_cnt-df.death_cnt.shift()).fillna(0)
    df['완치자 수']=(df.clear_cnt-df.clear_cnt.shift()).fillna(0)
    df['acc_cnt']=df['acc_cnt'].astype(object)
    df['death_cnt']=df['death_cnt'].astype(object)
    df['clear_cnt']=df['clear_cnt'].astype(object)
    print(df)

    con = sqlite3.connect(DB_PATH + '/newkorea.db')
    cursor = con.cursor()
    length1 = df.shape[0]
    length2 = df.shape[1]
    for i in range(length1):
        row = []
        for j in range(length2):
            row.append(df.iloc[i, j])
        cursor.execute("INSERT INTO korea VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                       (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
    con.commit()
    con.close()

def create_db():
    con = sqlite3.connect(DB_PATH + '/newkorea.db')
    cursor = con.cursor()
    # Date 날짜 acc 누적확진자 clear_a 완치자 care_a 치료중 death_a 사망누적 con 확진자 death 사망
    cursor.execute("CREATE TABLE korea(Date text, acc text, clear_a int, care_a int, death_a text, con int, death int, clear int)")
    con.commit()
    con.close()

def krefresh_db():
    con = sqlite3.connect(DB_PATH+'/newkorea.db')
    # con.execute("DROP TABLE korea")
    con.execute("DELETE FROM korea").rowcount
    con.commit()
    con.close()

def newkupdater(): # 업데이트 함수
    #create_db()
    krefresh_db() # 디비 clean
    make_db() # 다시 8일치 데이터 넣기 (7일간의 확진자 추이를 보기위해)

# newkupdater()
