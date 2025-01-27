import uuid
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Schedule(db.Model):
	id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
	title = db.Column(db.String(100), nullable=False)
	startdate = db.Column(db.DateTime, nullable=False)
	finishdate = db.Column(db.DateTime, nullable=True) 
	category = db.Column(db.String(10), nullable=True)
	location = db.Column(db.String(50), nullable=True)
	url_link = db.Column(db.String(100), nullable=True)
	content = db.Column(db.Text, nullable=False)
	created_at = db.Column(db.DateTime, server_default=db.func.now())
	updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
