import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
	__tablename__ = 'user'
	id = Column(Integer, primary_key = True)
	name = Column(String(80), nullable = False)

class Book(Base):
	__tablename__ = 'book'
	id = Column(Integer, primary_key = True)
	title = Column(String(120), nullable = False)
	author = Column(String(120), nullable = False)
	subject = Column(String(120))
	category = Column(String(80))
	summary = Column(String(400))

	@property
	def serialize(self):
		# Returns object data in easily serializable format
		return {
			'title' : self.title,
			'author' : self.author,
			'subject' : self.subject,
			'category' : self.category,
			'summary' : self.summary,
		}

engine = create_engine('sqlite:///bookreview.db')

Base.metadata.create_all(engine)