from flask import Flask, render_template, request, redirect, url_for#python組はこのファイル+(models.py)をメインに触る予定
from app.models import db, Schedule	#ここでsqlファイルを宣言
from dotenv import load_dotenv
import os
from uuid import UUID
import calendar
from datetime import datetime

# .envファイルを読み込む
load_dotenv()

# 環境変数からデータベース接続情報を取得
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')

app = Flask(__name__)

# SQLAlchemy設定
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.before_request
def create_tables():
	db.create_all()

# 現在の年と月を取得
now = datetime.now()
year = now.year
month = now.month
day = now.day

# 月別カレンダー一覧を表示
@app.route('/')
def index():
	schedules = Schedule.query.order_by(Schedule.created_at.desc()).all()#スケジュールデータの取得
	cal = calendar.Calendar(firstweekday=6)#カレンダーの生成
	month_days = cal.monthdayscalendar(year, month)

	return render_template('index.html', year=year, month=month, month_days=month_days, schedules=schedules, now_year = now.year, now_month=now.month, now_day=now.day )

# 次の月に遷移
@app.route('/next_month')
def next_month():
	global month, year
	if month == 12:
		month = 1
		year += 1
	else:
		month += 1
	return redirect(url_for('index'))

# 今月に遷移
@app.route('/now_month')
def now_month():
	global month, year
	year = now.year
	month = now.month
	return redirect(url_for('index'))

# 前の月に遷移
@app.route('/previous_month')
def previous_month():
	global month, year
	if month == 1:
		month = 12
		year -= 1
	else:
		month -= 1
	return redirect(url_for('index'))

# 予定詳細ページの展開
@app.route('/view_schedule/<uuid:schedule_id>')
def view_schedule(schedule_id):
	schedule = Schedule.query.get_or_404(str(schedule_id))
	schedules = Schedule.query.order_by(Schedule.created_at.desc()).all()
	cal = calendar.Calendar(firstweekday=6)
	month_days = cal.monthdayscalendar(year, month)
	return render_template('index.html', schedule=schedule, year=year, month=month, month_days=month_days, schedules=schedules, now_year=now.year, now_month=now.month, now_day=now.day)

###########################################
# 予定編集ページを表示
#@app.route('/schedule/<uuid:schedule_id>',methods=['GET,POST'])
#def show_edit_schedule(schedule_id):
#	schedule = Schedule.query.get_or_404(str(schedule_id))

@app.route('/schedule/<uuid:schedule_id>', methods=['GET','POST'])
def edit_schedule(schedule_id):
	schedule = Schedule.query.get_or_404(str(schedule_id))
	if request.method == 'POST':
		schedule.title = request.form['title']
		schedule.startdate = request.form['startdate']
		schedule.finishdate = request.form['finishdate']
		schedule.category = request.form['category']
		schedule.location = request.form['location']
		schedule.url_link = request.form['url_link']
		schedule.content = request.form['content']
		db.session.commit()
		return redirect(url_for('index'))
	return render_template('edit_schedule.html', schedule=schedule)
###########################################

# 新しい予定の作成フォームを表示
@app.route('/create', methods=['GET'])
def show_create_schedule():
	return render_template('create_schedule.html')

# 新しい予定を作成
@app.route('/create', methods=['POST'])
def create_schedule():
	title = request.form['title']
	startdate = request.form['startdate']
	if request.form['finishdate']:
		finishdate = request.form['finishdate']	
	else:
		finishdate = request.form['startdate']

	category = request.form['category']
	location = request.form['location']
	url_link = request.form['url_link']
	content = request.form['content']
	new_schedule = Schedule(title=title, startdate=startdate, finishdate=finishdate, category=category, location=location,url_link=url_link, content=content)#新たにカラム追加予定
	db.session.add(new_schedule)
	db.session.commit()
	return redirect(url_for('index'))

# 予定を削除
@app.route('/schedule/<uuid:schedule_id>/delete', methods=['POST'])
def delete_schedule(schedule_id):
	schedule = Schedule.query.get_or_404(str(schedule_id))
	db.session.delete(schedule)
	db.session.commit()
	return redirect(url_for('index'))

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)
