#!/bin/python3

from telegram.ext import Updater, jobqueue, MessageHandler, CommandHandler, CallbackQueryHandler, Handler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from base import db_session, User, Parametr
import datetime, logging, traceback, sys


# нужно поменять
PROXY = {'proxy_url': 'socks5://t1.learn.python.ru:1080',
         'urllib3_proxy_kwargs': {'username': 'learn', 'password': 'python'}} 

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log')

def start(bot, update):
	id = update.message.chat.id
	if id > 0: # groups ignored
		keyboard = [['Status', 'Media'], 
			        ['Settings', 'Chat'], 
			        ['Referral link']]
		reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
		welcome_text = '''Welcome to the AIRDROP CTLgroup bot!
						To get 25 CTLcoin please do the following:
						- specify in the bot settings the links to your reposts from our Facebook and Twitter pages
						- subscribe to our telegram channel @CryptoTradeLine and go to chat
						To get additional tokens invite your friends to the bot and get 1 CTLcoin for each one connected to the bot'''
		bot.send_message(chat_id=id, text=welcome_text, reply_markup=reply_markup)
		msg = update.message.text.replace('/start', '').strip()
		entered_user = User.query.filter(User.id==id).first()
		if entered_user == None:

			db_session.add(User(id=id, name=update.message.chat.username, inviter=msg))
			db_session.commit()
			print('commited')
			if msg != '' and msg != str(id):
				bonus = 1
				inviter = User.query.filter(User.id==msg).first()
				inviter.tokens_acc += bonus
				inviter.refs += 1
				tokens_left = Parametr.query.filter(Parametr.parametr=='Tokens_left').first()
				tokens_left.value_flt -= bonus
				db_session.commit()
				bot.send_message(chat_id=msg, text='+ %s tokens for friend inviting ' % bonus + update.message.chat.first_name)
			elif msg == str(id):
				update.message.text_reply('You have received a link to yourself, do /start')
		elif msg == str(id):
			bot.send_message(chat_id=id, text='You invited yourself')

def set_email(bot, update):
	cur_id = update.callback_query.message.chat.id
	bot.send_message(chat_id=cur_id, text='Enter your mail')
	usr = User.query.filter(User.id==cur_id).first()
	usr.cmd = 'email'
	db_session.commit()
def set_wallet(bot, update):
	cur_id = update.callback_query.message.chat.id
	bot.send_message(chat_id=cur_id, text='Enter your ETH wallet(ERC 20)')
	usr = User.query.filter(User.id==cur_id).first()
	usr.cmd = 'wallet'
	db_session.commit()
def set_fb(bot, update):
	cur_id = update.callback_query.message.chat.id
	bot.send_message(chat_id=cur_id, text='Enter your facebook link')
	usr = User.query.filter(User.id==cur_id).first()
	usr.cmd = 'fb'
	db_session.commit()
def set_twit(bot, update):
	cur_id = update.callback_query.message.chat.id
	bot.send_message(chat_id=cur_id, text='Enter your twitter link')
	usr = User.query.filter(User.id==cur_id).first()
	usr.cmd = 'twit'
	db_session.commit()

def msg_handler(bot, update):
	try:
		id = update.message.chat.id
		print('Chat ID', id)
	except:
		id = update.channel_post.chat.id
		print('Channel ID', id)
	if id < 0:
		return
	usr = User.query.filter(User.id==id).first()
	if usr == None: 
		update.message.reply_text('Account not found, do /start')
		return
	msg = update.message.text
	if msg == 'Settings':
		keyboard = [[InlineKeyboardButton("Email",    	callback_data='set_email')],
					[InlineKeyboardButton("ETH Wallet", callback_data='set_wallet')],
					[InlineKeyboardButton("Facebook", 	callback_data='set_fb')],
					[InlineKeyboardButton("Twitter",  	callback_data='set_twit')]]
		markup = InlineKeyboardMarkup(keyboard)
		bot.send_message(chat_id=id, reply_markup=markup, text='Set:')
		usr.cmd = ''
		db_session.commit()
	elif msg == 'Status':
		res_left = Parametr.query.filter(Parametr.parametr=='Tokens_left').first().value_flt
		res = 'Amount: ' + str(usr.tokens_acc) + '\nAvailable: ' + str(res_left) + '\n'
		res += 20 * '-'
		res += '\nEmail: ' + usr.email + '\nETH wallet (ERC 20): ' + usr.vallet + '\nFacebook: ' + usr.facebook + '\nTwitter: ' + usr.twitter
		update.message.reply_text(res)
		usr.cmd = ''
		db_session.commit()
	elif msg == 'Referral link':
		url = 'https://t.me/Airdrop_Coin_bot?start=' + str(id)
		text = 'Invite your friends by link: '
		update.message.reply_text(text)
		update.message.reply_text(url)
		usr.cmd = ''
		db_session.commit()
	elif msg == 'Media':
		text = '''Website:\nhttps://cryptotradeline.org/\n\nTelegram channel:\nhttps://t.me/CryptoTradeLine\nFacebook:\nhttps://www.facebook.com/Cryptotradeline/\nTwitter:\nhttps://twitter.com/cryptotradeline\nReddit:\nhttps://www.reddit.com/user/cryptotradeline\nMedium:\nhttps://medium.com/@cryptotradeline\nBitcointalk:\nhttps://bitcointalk.org/index.php?topic=4609704.new#new\nYoutube:\nhttps://www.youtube.com/channel/UC0THTvP7FzJIuSrFoGZV8Dw'''
		update.message.reply_text(text=text)
		usr.cmd = ''
		db_session.commit()
	elif msg == 'Chat':
		text  = 'En chat: ' + 'https://t.me/joinchat/G_IwyRIqIyZPdYSudBbhcw' + ' \n'
		text += 'Ru chat: ' + 'https://t.me/joinchat/G_IwyRG5Xa0C-N7l9N8vcQ'
		update.message.reply_text(text=text)
		usr.cmd = ''
		db_session.commit()		
	else:
		if   usr.cmd == 'email':  usr.email = msg
		elif usr.cmd == 'wallet': usr.vallet = msg
		elif usr.cmd == 'fb':     usr.facebook = msg
		elif usr.cmd == 'twit':   usr.twitter = msg			
		else:
			usr.cmd = ''
			db_session.commit()
			update.message.reply_text('Unknown command')
			return 0
		usr.cmd = ''
		db_session.commit()
		update.message.reply_text('Done')
		check_bonus(usr, bot)
		
def check_bonus(usr, bot):
	bonus = 25
	prm = Parametr.query.filter(Parametr.parametr=='Tokens_left').first()
	if usr.vallet != '' and usr.facebook != '' and usr.twitter != '' and usr.email != '' and usr.channel:
		print(usr.id, 'Bonus!')
		if not usr.bonus:
			usr.tokens_acc += bonus
			prm.value_flt -= bonus
			usr.bonus = True
			bot.send_message(chat_id=usr.id, text='+ %s tokens for settings ' % bonus)
			db_session.commit()
	else:
		if usr.bonus:
			usr.tokens_acc -= bonus
			prm.value_flt += bonus
			usr.bonus = False	
			bot.send_message(chat_id=usr.id, text='+ %s tokens for settings ' % bonus)
			db_session.commit()

def check_group(bot, update, new, left):
	id  = left.id if left != None else new[0].id
	opr = 'out'   if left != None else 'in'
	usr = User.query.filter(User.id==id).first()
	if usr == None: 
		return
	#prm = Parametr.query.filter(Parametr.parametr=='Tokens_left').first()
	usr.group = True if opr=='in' else False
	#usr.tokens_acc = usr.tokens_acc+1 if opr=='in' else usr.tokens_acc-1
	#prm.value_flt  = prm.value_flt-1  if opr=='in' else prm.value_flt+1
	db_session.commit()
	text = 'You entered to the chat' if opr=='in' else 'You left the chat'
	bot.send_message(chat_id=id, text=text)
	check_bonus(usr, bot)

def check_channel(bot, job):
	allusers = User.query.filter().all()
	#prm = Parametr.query.filter(Parametr.parametr=='Tokens_left').first()
	for usr in allusers:
		usr_tele = bot.get_chat_member(-1001325975220, user_id=usr.id, timeout=10)
		if usr_tele.status == 'left' and usr.channel:
			#usr.tokens_acc -= 1
			#prm.value_flt += 1
			usr.channel = False
			bot.send_message(chat_id=usr.id, text='you unsubscribed from the channel')
			db_session.commit()
			check_bonus(usr, bot)
		elif usr_tele.status != 'left' and not usr.channel:
			#usr.tokens_acc += 1
			#prm.value_flt -= 1
			usr.channel = True
			bot.send_message(chat_id=usr.id, text='you subscribed to the channel')
			db_session.commit()
			check_bonus(usr, bot)
	
class UpdHandler(Handler):
	def check_update(self, update):
		return True
	def handle_update(self, update, dispatcher):
		new = update.message.new_chat_members
		left = update.message.left_chat_member
		self.callback(dispatcher.bot, update, new, left)
		return True

def main():
	token = sys.argv[1]
	
	updater = Updater(token, request_kwargs=PROXY)
	dp  = updater.dispatcher
	dp.add_handler(MessageHandler(Filters.text, msg_handler))
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CallbackQueryHandler(set_email, 	pattern='^set_email$'))
	dp.add_handler(CallbackQueryHandler(set_wallet, pattern='^set_wallet$'))
	dp.add_handler(CallbackQueryHandler(set_fb, 	pattern='^set_fb$'))
	dp.add_handler(CallbackQueryHandler(set_twit, 	pattern='^set_twit$'))
	dp.add_handler(UpdHandler(callback=check_group, ))
	job = jobqueue.JobQueue(dp.bot)
	job.run_repeating(callback=check_channel, interval=120)
	job.start()

	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
	main()
