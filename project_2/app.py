import os
import json 
import requests
import re
from bs4 import BeautifulSoup
import pymysql
from flask import Flask, render_template
from flask import request, redirect, abort, session
from datetime import date, timedelta

app = Flask(__name__, 
            static_folder="static",
            template_folder="template")

app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.secret_key = 'project_2'

db = pymysql.connect(
    user='root',
    passwd='123456',
    host='localhost',
    db='project_2',
    charset='utf8',
    cursorclass=pymysql.cursors.DictCursor
)
def get_movie():
    movie_temp = "<li><a href='ticket?name=0{0}'>{0}</a></li>"
    movie = [e for e in os.listdir('movies') if e[0]!='.']
    return "\n".join([movie_temp.format(m) for m in movie])

def get_musical():
    musical_temp = "<li><a href='ticket?name=1{0}'>{0}</a></li>"
    musical = [e for e in os.listdir('musicals') if e[0]!='.']
    return "\n".join([musical_temp.format(m) for m in musical])

def get_menu():
    menu_temp = "<li><a href='/{0}'>{0}</a></li>"
    menu = [e for e in os.listdir('views') if e[0] != '.']
    return "\n".join([menu_temp.format(m) for m in menu])

def get_template(filename):
    with open(filename, 'r', encoding="utf-8") as f:
        template = f.read()
    return template

@app.route("/")
def index():
    with open('template/base1.html', 'r', encoding="utf-8") as f:
        default = f.read()
    return default

@app.route("/template/base2.html")
def index2():
    id = request.args.get('id', '')
    template = get_template('template/base2.html')
    
    if 'user' in session:
        title = 'Welcome ' + session['user']['id']
    else:
        title = 'Welcome'

    content = 'Welcome Movie Reservation Page with NAVER & DAUM'
    menu = get_menu()
    return template.format(title, content, menu)
#     return render_template('template/base2.html',
#                            title=title,
#                            message=message,
#                            menu=menu)

@app.route("/create", methods=['GET', 'POST'])
def create():
    message = ""
    if request.method == 'POST':
        cursor = db.cursor()
        cursor.execute(f"""
            insert into members (id, name, mail, password)
                        values ('{request.form['id']}', '{request.form['name']}', '{request.form['mail']}', SHA2('{request.form['pw']}', 256))""")
        db.commit()
        return redirect("/")

    return render_template('create.html', message=message, menu=get_menu())
                       
    
@app.route("/login", methods=['GET', 'POST'])
def login():
    message = ""
    if request.method == 'POST':
        cursor = db.cursor()
        cursor.execute(f"""
            select id, name, mail, password from members
            where id = '{request.form['id']}'""")
        user = cursor.fetchone()

        if user is None:
            message="<p>회원이 아닙니다.</p>"

        else:
            cursor.execute(f"""
            select id, name, mail, password from members
            where id = '{request.form['id']}' and password = SHA2('{request.form['pw']}', 256)""")
            user = cursor.fetchone()
            
            if user is None:
                message = "<p>패스워드를 확인해 주세요</p>"
            else:
                session['user'] = user
                return redirect("main")

    return render_template('login.html', 
                               message=message, 
                               menu=get_menu())


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect("template/base1.html")

@app.route("/favicon.ico")
def favicon():
    return abort(404)


###############################################################################33

@app.route("/main")
def main():
    
    d_res = requests.get("https://movie.daum.net/premovie/released")
    m_res = requests.get(f"http://ticket.interpark.com/contents/Ranking/RankList?pKind=01009&pCate=&pType=D&pDate={date.today().strftime('%Y%m%d')}")
    
    d_soup = BeautifulSoup(d_res.content, 'html.parser')
    m_soup = BeautifulSoup(m_res.content, 'html.parser')

    movies = list(d_soup.select('.movie_join li'))
    musicals = list(m_soup.select('.rankBody'))
   
    regex = re.compile("예매율 (.+)\ ")
    
    dm_sum = []
    count = 1  ## 8번만 돌게 하기

#     for tag in d_soup.select('.movie_join li'):
#         d_movies.append({"제목" : tag.div.strong.get_text(), "이미지" :                                    tag.a.img['src']})
#         count += 1
#         if count == 8:
#                 count = 1
#                 break
    
#     for tag in m_soup.select('.prds'):
#         m_movies.append({"제목" : tag.b.get_text(), "이미지" : tag.img['src']})
#         count += 1
#         if count == 8:
#                 break
       
    for d, m in zip(movies, musicals):
        
        reser = d.dl.get_text() # 예매율 가져오기
        ####################################################################
     
        dm_sum.append({"영화제목" : d.div.strong.get_text(), "영화이미지" : d.a.img['src'], "영화예매율" : re.findall(regex, reser)[0],
                    "연극제목" : m.b.get_text() , "연극이미지" : m.img['src'], "연극예매율" : m.find_all('b')[1].text})
        
        count += 1
        if count == 10:
                break
    
    return render_template("sample.html", 
                           dm_sum = dm_sum)

#############################################################################
@app.route("/ticket", methods=['GET', 'POST'])
def reservation():
    
 print("test")
 if request.method == 'GET':
    title = request.args.get('name', '')
    print(title)
    if title[0] == '0':
        title = title[1:]
        movie = get_movie()
        with open(f'movies/{title}', 'r', encoding="utf-8") as f:
            content = f.read()
         
        with open(f'moviestime/{title}', 'r', encoding="utf-8") as f:
            time = f.read()
            
        return render_template("sample2.html",
                               kind = '영화',
                               name = title,
                               numbers = movie,
                               theater = content,
                               time = time )  
    elif title[0] == '1':
        title = title[1:]
        musical = get_musical()
        with open(f'musicals/{title}', 'r', encoding="utf-8") as f:
            content = f.read()
            
        with open(f'musicalstime/{title}', 'r', encoding="utf-8") as f:
            time = f.read()
        return render_template("sample2.html", 
                               kind = '연극',
                               name = title,
                               numbers = musical,
                               theater = content,
                               time = time)  
   
    else:
        return redirect("/main")
    
app.run(port=8005)