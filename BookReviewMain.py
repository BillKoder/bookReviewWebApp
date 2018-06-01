from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from BookReviewDatabase import Base, User, Book

app = Flask(__name__)

engine = create_engine('sqlite:///bookreview.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()

# Main page for Website, Shows all the book
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

# Route for individual book information
@app.route('/books/<int:book_id>/')
def bookInformaion(book_id):
	books = session.query(Book).filter_by(id = book_id)
	output = ''
	for book in books:
		output += '<h1>'
		output += book.title
		output += '</h1>'
		output += 'Author: ' + str(book.author)
		if book.subject is not None:
			output += 'Subject: ' + str(book.subject)
		if book.category is not None:
			output += 'Category: ' + str(book.category)
		if book.summary is not None:
			output += 'Summary; ' + str(book.summary)
		output += '</br>'
	return output


# Route for adding a new book
@app.route('/books/new', methods = ['GET', 'POST'])
def newBook():
	output = ''
	output += 'Page for adding a new book'
	return output

# Route for editing book information
@app.route('/books/<int:book_id>/edit', methods = ['GET', 'POST'])
def editBook(book_id):
	editBook = session.query(Book).filter_by(id = book_id).one()
	output = ''
	output += 'Page for editing information of ' + str(editBook.title)
	return output

# Route for deleting book information
@app.route('/books/<int:book_id>/delete', methods = ['GET', 'POST'])
def deleteBook(book_id):
	deleteBook = session.query(Book).filter_by(id = book_id).one()
	output = ''
	output += 'Page for deleting ' + str(deleteBook.title)
	return output

	

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)