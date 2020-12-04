import sqlite3
import os

item_list = []

DB_PATH = os.path.dirname(__file__) + '/CoronaBotDB'

def tube_get(param = '코로나 확진자'):
    con = sqlite3.connect(DB_PATH+"/tube.db")
    res = con.cursor().execute("""SELECT * from NEWS WHERE CATEGORY='%s' """ % (param)).fetchall()
    for i in res:
        item_list.append({
            "title": i[1],
            "description": i[2],
            "thumbnail": {
                "imageUrl": i[3]},
            "buttons": [
                {
                    "action": "webLink",
                    "label": "뉴스 보러가기",
                    "webLinkUrl": i[4]
                }
            ]
        })
    send = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "carousel": {
                        "type": "basicCard",
                        "items": item_list}}]}}
    return send