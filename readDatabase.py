from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from BookReviewDatabase import Base, User, Book, Forum, BookForumConnect
engine = create_engine('sqlite:///bookreview.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()
books = session.query(Book).all()
print "Books:"
for book in books:
	print book.title
	print book.user
	print book.id
print
users = session.query(User).all()
print ""
print "Users:"
for user in users:
	print user.email
	print user.id
print
forums = session.query(Forum).all()
print "Forums:"
for forum in forums:
	print forum.id
	print forum.title
connects = session.query(BookForumConnect).all()
print "Connects:"
for connect in connects:
	print connect.book_id
	print connect.forum_id