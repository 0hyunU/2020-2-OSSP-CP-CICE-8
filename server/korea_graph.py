import sqlite3
import os
import numpy as np
import matplotlib.pyplot as plt

import matplotlib.font_manager as fm
font_text = 13
font_leg = 15
font_title = 30
linewidth_size = 5
Date_idx = 0
con_idx = 1
clear_idx = 2

font_path = r'./경기천년바탕_Regular.ttf'   # plot할때 한국어로 하기 위해 폰트 지정
fontprop = fm.FontProperties(fname=font_path, size= font_leg)  # plot 할 때 font size : 15

Path = os.path.dirname(__file__) + '/CoronaBotDB/newkorea.db'
#Path = os.path.dirname(__file__) + 'newkorea.db'
conn = sqlite3.connect(Path)
cur = conn.cursor()
try:
    cur.execute("SELECT Date, con, clear FROM korea")  # DB에서 날짜, 확진자 증가된 수치, 완치자 증가된 수치 가져옴
    rows = cur.fetchall()
    #print(rows)

    day_list=[]
    con_list=[]
    clear_list =[]
    for i in range(1, len(rows)):  # 총 8개 데이터 중 최근 7일치 데이터를 가져옴 (제일 처음 데이터는 증가된 수치 계산이 안되므로)
        row = rows[i]
        day = row[Date_idx][4:6] + "/" + str(int(row[Date_idx][6:])-1)    # 날짜 mm/dd 형식으로 표시, 12월 18일 00시 기준이면 12/17 로 표시
        day_list.append(day)
        con_list.append(row[con_idx])    # 증가된 확진자 수치
        clear_list.append(row[clear_idx])    # 증가된 완치자 수치

    plt.rc('axes', unicode_minus=False)

    for i, v in enumerate(day_list):
        plt.text(v, con_list[i], str(con_list[i])+'명',
                 fontproperties=fontprop,
                 color='red',
                 fontsize = font_text, # plot 할 때 font 사이즈 : 13
                 horizontalalignment='center',  # horizontalalignment (left, center, right)
                 verticalalignment='bottom')    # verticalalignment (top, center, bottom)

    plt.title('[대한민국 코로나 19 확진자 추이 그래프]\n',fontproperties=fontprop, fontsize= font_title) # plot 할 때 font 사이즈 : 30
    plt.plot(day_list, con_list, marker = 'o', color = 'lightcoral', linewidth = linewidth_size, label='Confirmed')  # plot 할 때 linewidth : 5

    plt.plot(day_list, clear_list, marker='o', color='cornflowerblue', linewidth=linewidth_size, label='Recovered')  # plot 할 때 linewidth : 5
    plt.rc('font')
    for i, v in enumerate(day_list):
        plt.text(v, clear_list[i], str(clear_list[i]) + '명',
                 fontproperties=fontprop,
                 color='blue',
                 fontsize= font_text,  # plot할때 font 사이즈 : 13
                 horizontalalignment='center',  # horizontalalignment (left, center, right)
                 verticalalignment='bottom')  # verticalalignment (top, center, bottom).

    plt.xlabel('(날짜)', fontproperties=fontprop, fontsize = font_leg)  # plot 할 때 font 사이즈 : 15
    plt.ylabel('(명)', fontproperties=fontprop, fontsize = font_leg)  # plot할 때 font 사이즈 : 15

    plt.legend(loc='center right', bbox_to_anchor=(1.45, 0.5), shadow = True, fontsize = font_text)    # 범례 위치 : 박스옆으로 (1.45, 0.5) 떨어지게
                                                                                                     # plot 할 때 font 사이즈 : 13
    #font_name = fm.FontProperties(fname = font_path).get_name()
    #plt.legend(prop = {'family' : font_name, 'size':15})
    plt.grid(True)  # 격자선 추가
    #plt.savefig('CoronaBotDB/1.png', facecolor='#eeeeee', bbox_inches='tight')
    plt.savefig('./static/korea_graph.jpg', facecolor = '#eeeeee', bbox_inches='tight')

finally:
    cur.close()
    conn.close()
