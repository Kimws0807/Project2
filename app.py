import os
import pymysql
from flask import Flask, render_template
from flask import request, redirect, abort, session
app = Flask(__name__, 
            static_folder="static",
            template_folder="views")

app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.secret_key = 'project_2'

db = pymysql.connect(
    user='root',
    passwd='123456',
    host='localhost',
    db='web',
    charset='utf8',
    cursorclass=pymysql.cursors.DictCursor
)

members = [
    {"id": "wansoo", "pw": "111111"},
    {"id": "changmin", "pw": "222222"}    
]

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
    
    title = 'Welcome ' + id
    content = 'Welcome Python Class...'
    menu = get_menu()
    return template.format(title, content, menu)

@app.route("/create", methods=['GET', 'POST'])
def create():
    template = get_template('create.html')
    menu = get_menu()
    
    if request.method == 'GET':
        return template.format('', menu)
    
    elif request.method == 'POST':
        # request.form['title'], request.form['desc']
        with open(f'content/{request.form["title"]}', 'w') as f:
            f.write(request.form['desc'])
        return redirect('/')

    
@app.route("/login", methods=['GET', 'POST'])
def login():
    template = get_template('login.html')
    
    if request.method == 'GET':
        return render_template('login.html', 
                               message="",)
        # return template.format("", menu)
    
    elif request.method == 'POST':
        # 만약 회원이 아니면, "회원이 아닙니다."라고 알려주자
        m = [e for e in members if e['id'] == request.form['id']]
        if len(m) == 0:
            return render_template('login.html', 
                                   message="<p>회원이 아닙니다.</p>")
        
        # 만약 패스워드가 다르면, "패스워드를 확인해 주세요"라고 알려주자
        if request.form['pw'] != m[0]['pw']:
            return render_template('login.html', 
                                   message="<p>패스워드를 확인해 주세요.</p>")

        # 로그인 성공에는 메인으로
        session['user'] = m[0]
        return redirect("template/base2.html")

@app.route("/favicon.ico")
def favicon():
    return abort(404)

app.run(port=8005)