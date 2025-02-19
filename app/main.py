from flask import Flask, render_template, request, redirect, url_for
from app.models import db, Schedule, Holiday_change
from dotenv import load_dotenv
import os
from uuid import UUID
import calendar
from datetime import datetime, timedelta

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

#第何何曜日かを受け取り、その年の日付を返す。
def get_nth_weekday(year, month, weekday, n):
	cal = calendar.Calendar(firstweekday=6)
	month_days = cal.monthdayscalendar(year, month)
	count = 0
	for week in month_days:
		if week[weekday] != 0:
			count += 1
			if count == n:
				return datetime(year, month, week[weekday])
	return None

# 月別カレンダー一覧を表示
@app.route('/')
def index():
	schedules = Schedule.query.order_by(Schedule.created_at.desc()).all()#スケジュールデータの取得
	holiday_changes = Holiday_change.query.order_by(Holiday_change.created_at.desc()).all()#スケジュールデータの取得
	holidays = []# 祝日の計算
	for holiday in holiday_changes:
		holiday_date = get_nth_weekday(year, holiday.month, holiday.weekday, holiday.week)
		if holiday_date:
			holidays.append({"title": holiday.title, "date": holiday_date})

	cal = calendar.Calendar(firstweekday=6)
	month_days = cal.monthdayscalendar(year, month)
	return render_template('index.html', year=year, month=month, month_days=month_days, schedules=schedules, holidays=holidays, now_year=now.year, now_month=now.month, now_day=now.day)

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
	schedules = Schedule.query.order_by(Schedule.created_at.desc()).all()#スケジュールデータの取得
	holiday_changes = Holiday_change.query.order_by(Holiday_change.created_at.desc()).all()#スケジュールデータの取得
	holidays = []# 祝日の計算
	for holiday in holiday_changes:
		holiday_date = get_nth_weekday(year, holiday.month, holiday.weekday, holiday.week)
		if holiday_date:
			holidays.append({"title": holiday.title, "date": holiday_date})

	cal = calendar.Calendar(firstweekday=6)
	month_days = cal.monthdayscalendar(year, month)
	return render_template('index.html',schedule=schedule, year=year, month=month, month_days=month_days, schedules=schedules, holidays=holidays, now_year=now.year, now_month=now.month, now_day=now.day)

# 新しい予定の作成フォームを表示
@app.route('/create', methods=['GET'])
def show_create_schedule():
	return render_template('create_schedule.html')

# 新しい予定を作成
@app.route('/create', methods=['POST'])
def create_schedule():
	title = request.form['title']
	startdate = request.form['startdate']
	if 'finishdate' in request.form and request.form['finishdate']:  # 終了日の入力が空白でない場合
		finishdate = request.form['finishdate']
		if finishdate < startdate:# 終了日が開始日より前の場合、開始日と終了日を入れ替える
			startdate, finishdate = finishdate, startdate
	else:# 終了日の入力が空白の場合、開始日と同じ日にする
		finishdate = startdate
	category = request.form['category']
	location = request.form['location']
	url_link = request.form['url_link']
	content = request.form['content']
	new_schedule = Schedule(title=title, startdate=startdate, finishdate=finishdate, category=category, location=location, url_link=url_link, content=content)
	db.session.add(new_schedule)
	db.session.commit()

	return redirect(url_for('index'))

# 予定編集ページを表示
@app.route('/schedule/<uuid:schedule_id>', methods=['GET','POST'])
def edit_schedule(schedule_id):
	schedule = Schedule.query.get_or_404(str(schedule_id))
	if request.method == 'POST':
		schedule.title = request.form['title']
		schedule.startdate = request.form['startdate']
		if 'finishdate' in request.form and request.form['finishdate']:  # 終了日の入力が空白でない場合
			schedule.finishdate = request.form['finishdate']
			if schedule.finishdate < schedule.startdate:# 終了日が開始日より前の場合、開始日と終了日を入れ替える
				schedule.startdate, schedule.finishdate = schedule.finishdate, schedule.startdate
		else:# 終了日の入力が空白の場合、開始日と同じ日にする
			schedule.finishdate = schedule.startdate
		schedule.category = request.form['category']
		schedule.location = request.form['location']
		schedule.url_link = request.form['url_link']
		schedule.content = request.form['content']
		db.session.commit()
		return redirect(url_for('index'))
	return render_template('edit_schedule.html', schedule=schedule)

# 予定を削除
@app.route('/schedule/<uuid:schedule_id>/delete', methods=['POST'])
def delete_schedule(schedule_id):
	schedule = Schedule.query.get_or_404(str(schedule_id))
	db.session.delete(schedule)
	db.session.commit()
	return redirect(url_for('index'))

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)
