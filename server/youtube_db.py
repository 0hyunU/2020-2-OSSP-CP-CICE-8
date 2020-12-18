import sqlite3
import requests
import html
import os

DB_PATH = os.path.dirname(__file__) + '/CoronaBotDB'
# con = sqlite3.connect(DB_PATH + '/tube.db')
# cursor = con.cursor()
# cursor.execute("CREATE TABLE NEWS(CATEGORY text, TITLE text, DESC text, IMG text, LINK text)")

def insert_db(data):
    con = sqlite3.connect(DB_PATH + '/tube.db')
    cursor = con.cursor()
    for row in data:
        cursor.execute("INSERT INTO NEWS VALUES(?, ?, ?, ?, ?)", (row[0], row[1], row[2], row[3], row[4]))
        con.commit()
    con.close()


def yrefresh_db():
    con = sqlite3.connect(DB_PATH+'/tube.db')
    con.execute("DELETE FROM NEWS").rowcount
    con.commit()
    con.close()


# 키는 보안을 위해 지움
def crawl_tube():
    youtube_key = "AIzaSyDgTuKL86WcF3uS6b6gBWEUoaUdd_cAOOA"
    news_num = 5
    add_list = [] # 저장할 아이템들
    search_list = ['코로나 확진자', '코로나 백신', '코로나 후유증']

    for i in search_list:
        r = requests.get(
            f"https://www.googleapis.com/youtube/v3/search?part=snippet&key={youtube_key}&q={i.replace(' ', '+') + '+뉴스'}19&maxResults={news_num}")
        j = r.json()

        for item in j['items']:
            title = html.unescape(item['snippet']['title'])
            desc = html.unescape(item['snippet']['description'])
            r_img = item['snippet']['thumbnails']['high']['url']
            j_img = f"https://www.youtube.com/watch?v={item['id']['videoId']}"

            add_list.append([i, title, desc, r_img, j_img])

    insert_db(add_list)
