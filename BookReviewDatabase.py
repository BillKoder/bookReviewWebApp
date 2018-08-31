from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
	__tablename__ = 'user'
	id = Column(Integer, primary_key = True)
	name = Column(String(80), nullable = False)
	email = Column(String(250))
	picture= Column(String(250))

class Book(Base):
	__tablename__ = 'book'
	id = Column(Integer, primary_key = True)
	title = Column(String(120), nullable = False)
	author = Column(String(120), nullable = False)
	subject = Column(String(120))
	category = Column(String(80))
	summary = Column(String(400))
	user_id = Column(Integer,ForeignKey('user.id'))
	user = relationship(User)

class Forum(Base):
	__tablename__ = 'forum'
	id = Column(Integer, primary_key = True)
	title = Column(String)
	book_id = Column(Integer, ForeignKey('book.id'))
	book = relationship(Book)

class ForumContent(Base):
	__tablename__ = 'ForumContent'
	id = Column(Integer, primary_key =True)
	content = Column(String)
	time = Column(String)
	forum_id = Column(Integer, ForeignKey('forum.id'))
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)



	@property
	def serialize(self):
		# Returns object data in easily serializable format
		return {
			'id' : self.id,
			'title' : self.title,
			'author' : self.author,
			'subject' : self.subject,
			'category' : self.category,
			'summary' : self.summary,
		}

engine = create_engine('sqlite:///bookreview.db')

Base.metadata.create_all(engine)