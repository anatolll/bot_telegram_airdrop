from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///bot_users.sqlite')
db_session = scoped_session(sessionmaker(bind=engine)) # связь сессии с базой
Base = declarative_base() # создание декларативно, при помощи классов
Base.query = db_session.query_property() # подключаем возможность делать запросы

class User(Base):
	__tablename__ = 'bot_users'
	id = Column(String(100), primary_key=True)
	name = Column(String(50))
	email = Column(String(100))
	vallet = Column(String(100))
	facebook = Column(String(100))
	twitter = Column(String(100))
	tokens_acc = Column(Float())
	inviter = Column(String(100))
	cmd = Column(String(20))
	refs = Column(Integer())
	group = Column(Boolean())
	channel = Column(Boolean())
	bonus = Column(Boolean())

	def __init__(self, id=None, name='', email='', vallet='', 
				facebook='', twitter='', tokens_acc=0, tokens_left=1000000, 
	            cmd='', refs=0, inviter='', group=False, channel=False, bonus=False):
		self.id = id
		self.name = name
		self.email = email
		self.vallet = vallet
		self.facebook = facebook
		self.twitter = twitter
		self.tokens_acc = tokens_acc
		self.inviter = inviter
		self.cmd = cmd
		self.refs = refs
		self.group = group
		self.channel = channel
		self.bonus = bonus

class Parametr(Base):
	__tablename__ = 'parameters'
	parametr = Column(String(50), primary_key=True)
	value_str = Column(String(50))
	value_flt = Column(Float())
	
	def __init__(self, parametr='', value_str='', value_flt=0):
		self.parametr = parametr
		self.value_str = value_str
		self.value_flt = value_flt

def init():
	coins_left = Parametr(parametr='Tokens_left', value_flt=1323000)
	db_session.add(coins_left)
	db_session.commit()

if __name__ == '__main__':
	Base.metadata.create_all(bind=engine) # существующие таблицы не пересоздаются
	init()
