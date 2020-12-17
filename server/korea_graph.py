import sqlite3
import os
import numpy as np
import matplotlib.pyplot as plt

import matplotlib.font_manager as fm

font_path = r'./경기천년바탕_Regular.ttf'   # plot할때 한국어로 하기 위해
fontprop = fm.FontProperties(fname=font_path, size=15)

Path = os.path.dirname(__file__) + '/CoronaBotDB/newkorea.db'
#Path = os.path.dirname(__file__) + 'newkorea.db'
conn = sqlite3.connect(Path)
cur = conn.cursor()
try:
    cur.execute("SELECT Date, con, clear FROM korea")
    rows = cur.fetchall()
    #print(rows)

    day_list=[]
    con_list=[]
    clear_list =[]
    for i in range(1, len(rows)):
        row = rows[i]
        day = row[0][4:6] + "/" + row[0][6:]    # 날짜 mm/dd 형식으로 표시
        day_list.append(day)
        con_list.append(row[1])    # 증가된 확진자 수치
        clear_list.append(row[2])    # 증가된 완치자 수치

    plt.rc('axes', unicode_minus=False)

    for i, v in enumerate(day_list):
        plt.text(v, con_list[i], str(con_list[i])+'명',
                 fontproperties=fontprop,
                 color='red',
                 fontsize = 13,
                 horizontalalignment='center',  # horizontalalignment (left, center, right)
                 verticalalignment='bottom')    # verticalalignment (top, center, bottom)

    plt.title('[대한민국 코로나 19 확진자 추이 그래프]\n',fontproperties=fontprop, fontsize=30)
    plt.plot(day_list, con_list, marker = 'o', color = 'lightcoral', linewidth = 5, label='Confirmed')

    plt.plot(day_list, clear_list, marker='o', color='cornflowerblue', linewidth=5, label='Recovered')
    plt.rc('font')
    for i, v in enumerate(day_list):
        plt.text(v, clear_list[i], str(clear_list[i]) + '명',
                 fontproperties=fontprop,
                 color='blue',
                 fontsize=13,
                 horizontalalignment='center',  # horizontalalignment (left, center, right)
                 verticalalignment='bottom')  # verticalalignment (top, center, bottom).

    plt.xlabel('(날짜)', fontproperties=fontprop, fontsize = 15)
    plt.ylabel('(명)', fontproperties=fontprop, fontsize = 15)
    #plt.ylim(0,1300)
    plt.legend(loc='center right', bbox_to_anchor=(1.45, 0.5), shadow = True, fontsize = 13)
    #font_name = fm.FontProperties(fname = font_path).get_name()
    #plt.legend(prop = {'family' : font_name, 'size':15})
    plt.grid(True)
    #plt.savefig('CoronaBotDB/1.png', facecolor='#eeeeee', bbox_inches='tight')
    plt.savefig('./static/korea_graph.jpg', facecolot = '#eeeeee', bbox_inches='tight')

finally:
    cur.close()
    conn.close()
