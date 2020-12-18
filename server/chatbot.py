from flask import Flask, jsonify, request , render_template

#-*- coding:utf-8 -*-
from urllib.parse import urlencode, quote_plus
from urllib.request import urlopen , Request
import json
import requests
import re #계산을 위한 특수문자 제거

SECURE_SSL_REDIRECT = False

# 스케줄링에 필요한 모듈
from apscheduler.schedulers.background import BackgroundScheduler

# 카카오 챗봇 기능별 메소드
#from KoreaAPIData import KoreaCorona, update_KoreaDB  # 국내 현황, 국내 확진자 추이 시각화, api 오후 2시 업데이트
from globalData import globalData # 전세계 데이터
from emergency_service import * # 재난 문자 현황
from hospital_pharmacy import hospital_info # 근처 병원 및 약국 안내
from triage_center import triage # 선별진료소 안내
from hotKeyword import * # 인기 키워드
from GlobalDB import update_GlobalDB # 전세계 현황 디비 업데이트
from Sociallev import level # 사회적 거리두기 단계
from Self_diag import self_diagnosis # 자가 진단
from mask import * # 마스크
from newkoreadb import newkupdater
from korea_response import KoreaCorona
from ConstVar import CurrentPath

# 유튜브 뉴스 리스트 카드 버전
from Tube import tube_get
# 네이버 뉴스 리스트 카드 버전
from Naver import naver_get
# 뉴스 9시, 13시, 18시 update
from news_updater import news_update
# from distance_txt import distance_update

# db 업데이트
def update_db():
    print("GlobalDB 업데이트 진행중")
    update_GlobalDB()
    print("GlobalDB 업데이트 완료")

def update_msg():
    print("재난문자 업데이트 진행중")
    import disaster_msg
    print("재난문자 업데이트 완료")

#update_GlobalDB()
sched = BackgroundScheduler({'apscheduler.timezone': 'Asia/Seoul'})
#sched.add_job(update_db, 'cron', hours=24)

def update_korea():
    print("koreadb 업데이트 진행중")
    newkupdater()  # 국내 코로나 정보 업데이트
    import korea_graph  # 국내 코로나 추이 그래프 업데이트
    print("koreadb 업데이트 완료")

sched.add_job(update_db,'cron', day_of_week='0-6', hour=10)  # 전세계 현황 매일 오전 10시 업데이트
sched.add_job(news_update, 'interval', hours=2)  # 뉴스 2시간마다 업데이트
sched.add_job(update_msg,'cron', day_of_week='0-6', hours = 12)  # 재난문자 매일 오후 12시 업데이트


#sched.add_job(update_KoreaDB, 'cron', day_of_week='0-6', hour=13) # KoreaDB 오후 1시 업데이트
sched.add_job(update_korea, 'cron', day_of_week='0-6', hour=13)  # 국내 현황 매일 오후 1시 업데이트

sched.start()

app = Flask(__name__)

# api Test
@app.route('/keyboard')
def Keyboard():
    dataSend = {
      "user" : "corona_chatbot",
      "Subject" : "OSSP",
    }
    return jsonify(dataSend)

@app.route('/korea_graph')
def KoreaGraph():
    return render_template('graph.html')

# 긴급 재난문자
@app.route('/city_info', methods=['POST'])
def CityInfo():
    body = json.loads(request.data)
    print("긴급 재난문자 call")
    print("blockId : "+body['userRequest']['block']['id'])
    # req = request.get_json()
    params = body["action"]["params"]
    return emergency_alerts(params)

# 전세계 현황 데이터
@app.route('/globalData',methods = ['POST'])
def Global():
    print("전세계 현황 call")
    # get request and return json message for global
    dataSend = globalData(request.get_json())
    return jsonify(dataSend)

# 네이버 뉴스
@app.route('/naver_news', methods=['POST'])
def Naver_news():
    print("네이버 뉴스 call")
    body = request.get_json()
    print("blockId : "+body['userRequest']['block']['id'])
    content = body["action"]["detailParams"]["corona_topic"]["origin"]
    dataSend = naver_get(content)
    return jsonify(dataSend)

# 유튜브 뉴스
@app.route('/Youtube', methods=['POST'])
def Youtube():
    print("유튜브 뉴스 call")
    body = request.get_json()
    print("blockId : "+body['userRequest']['block']['id'])
    content = body["action"]["detailParams"]["youtube_corona"]["origin"]
    dataSend = tube_get(content)
    return jsonify(dataSend)

# 국내 코로나 현황
@app.route('/KoreaData',methods = ['GET','POST'])
def KoreaData():
    body = request.get_json() # 되묻기 질문용도
    print("blockId : "+body['userRequest']['block']['id'])
    # print(body)
    print("국내 코로나 현황 call")
    content = body["action"]["detailParams"]["select"]["origin"]
    KoreaResult = KoreaCorona(content)
    #KoreaResult = KoreaCorona()
    hotKeyword('국내 현황')
    return jsonify(KoreaResult)


# 선별진료소 안내
@app.route('/triagecenter_info', methods=['POST'])
def Triage():
    print("선별진료소 call")
    body = request.get_json()
    print("blockId : "+body['userRequest']['block']['id'])
    return jsonify(triage(body))


# 병원및약국 안내
@app.route('/hospital_info', methods=['POST'])
def Hospital():
    print("병원및약국 call")
    body = request.get_json()
    print("blockId : "+body['userRequest']['block']['id'])
    return jsonify(hospital_info(body))

# 인기 키워드 검색기능
@app.route('/hotKeyword' , methods = ['POST'])
def HotKeyword():
    print("인기 키워드 call")
    body = request.get_json()
    print("blockId : "+body['userRequest']['block']['id'])
    return jsonify(searchHotKeyword(body))

# 자가진단 테스트
@app.route('/self_diagnosis', methods = ['POST'])
def Diagnosis():
    print("자가진단 테스트 call")
    body = request.get_json()
    print("blockId : "+body['userRequest']['block']['id'])
    return jsonify(self_diagnosis(body))

# 사회적 거리두기
@app.route('/distance_level', methods = ['POST'])
def Distance():
    print("사회적 거리두기 call")
    body = request.get_json()
    print("blockId : "+body['userRequest']['block']['id'])
    content = body["action"]["detailParams"]["lev"]["origin"]
    a = level(content)
    return jsonify(a)

# 마스크
@app.route('/mask_info', methods=['POST'])
def Mask():
    print("마스크 call")
    body = request.get_json()
    print("blockId : "+body['userRequest']['block']['id'])
    return jsonify(hospital_info(body))

# 서버 테스트 ( 카카오 오픈빌더 return format )
@app.route('/message', methods=['POST'])
def Message():
    content = request.get_json()
    print(content)
    content = content['userRequest']
    content = content['utterance']

    if content.rstrip() == "안녕":
        dataSend = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "carousel": {
                            "type" : "basicCard",
                            "items": [
                                {
                                    "title" : "",
                                    "description" : "서버테스트"
                                }
                            ]
                        }
                    }
                ]
            }
        }
    else :
        dataSend = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText":{
                            "text" : "질문을 이해하지 못했습니다."
                        }
                    }
                ]
            }
        }
    return dataSend

if __name__ == "__main__":
    app.run(host='0.0.0.0') # default Flask port : 5000
