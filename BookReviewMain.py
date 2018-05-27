from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from BookReviewDatabase import Base, User, Book

app = Flask(__name__)

engine = create_engine('sqlite:///bookreview.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()

@app.route('/')
@app.route('/books/')
def bookList():
	books = session.query(Book)
	output = ''
	output += '<h1>Books</h1>'
	for book in books:
		output += book.title
		output += '</br>'
	return output

	

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)