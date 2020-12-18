import sqlite3
import os
DB_PATH = os.path.dirname(__file__) + '/CoronaBotDB'

Date_idx = 0
acc_idx = 1
clear_a_idx = 2
care_a_idx = 3
death_a_idx = 4
con_idx = 5
death_idx = 6
clear_idx = 7
to_percent = 100

def KoreaCorona(param):
    con = sqlite3.connect(DB_PATH + '/newkorea.db')
    cur = con.cursor()
    cur.execute("select * from korea where rowid = 8")  # 최신 데이터 가져오기 (8번째 행에 해당하는 데이터가 최신 데이터)
    # 데이터 Fetch
    rows = cur.fetchall()
    row = rows[0]  # 해당행의 전체 열 가져오기
    row = list(row)  # 딕셔너리를 리스트로 변환
    row[Date_idx] = row[Date_idx][:4]+'.'+row[Date_idx][4:6]+'.'+row[Date_idx][6:]  # 날짜 표시형식 20201210 -> 2020.12.10식으로 표시
    for i in range(1, len(row)):  # DB에서 날짜(index:0)를 제외한 모든 데이터 int형으로 바꾸고 콤마찍기
        row[i] = int(row[i])
        row[i] = format(row[i], ',')  # 숫자 표시형식 지정
    messages = """(%s 00시 기준)
확진자 %s(+%s)명
완치자 %s(+%s)명
사망자 %s(+%s)명
격리해제 %s명
치명률 %.2f%%""" % (row[Date_idx],
                 row[acc_idx], row[con_idx],
                 row[clear_a_idx], row[clear_idx],
                 row[death_a_idx], row[death_idx],
                 row[care_a_idx],
                 int(row[death_a_idx].replace(",","")) / int(row[acc_idx].replace(",","")) * to_percent)  # 치명률: (사망자/ 확진자)*100
    #print(messages)

    cur.close()
    con.close()
    if param == "현황 보기":
        return KoreadataSendCard(messages,
                                 imageUrl="https://user-images.githubusercontent.com/71917474/101284898-d39a9200-3825-11eb-9474-44084a8631de.jpg")
    elif param == "추이 그래프":
        dataSend = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleImage": {
                            "imageUrl": "http://3.223.84.68:5000/static/korea_graph.jpg",
                            # 직접 만든 시각화 이미지의 URL
                            "altText": "국내 코로나 확진자 추이입니다."
                        }
                    }
                ]
            }
        }
    else:  # 현황보기/ 추이 그래프가 입력되지 않은 경우.
        dataSend = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "다시 입력해주세요."
                        }
                    }
                ]
            }
        }

    return dataSend


def KoreadataSendCard(message, imageUrl):
    dataSend = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "carousel": {
                        "type": "basicCard",
                        "items": [
                            {
                                "title": "국내 코로나 현황",
                                "description": message,
                                "thumbnail": {
                                    "imageUrl": imageUrl},
                                "buttons": [
                                    {
                                        "action": "share",
                                        "label": "공유하기"}
                                ]
                            }
                        ]
                    }
                }
            ]
        }
    }
    return dataSend
KoreaCorona('현황보기')
