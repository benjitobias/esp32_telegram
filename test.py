import random
import string
import time
from utelegram import ubot
from config import utelegram_config

BOT_TOKEN = utelegram_config['token']
CHAT_ID = utelegram_config['chat_id']


bot = ubot(BOT_TOKEN)

def test_get_updates():
	print('Please send a message')
	incoming_text = input("Sent text: ")
	latest_message = bot.get_latest_message()
	assert latest_message['message']['text'] == incoming_text, "Fetched message text doesn't match"

def test_send():
	print('Sending random string')
	sent_string = (''.join(random.choice(string.ascii_lowercase) for i in range(5)))
	bot.send(CHAT_ID, sent_string)
	recv_string = input('String received: ')
	assert recv_string == sent_string, "Sent message text doesn't match"


def test_register_handler():	
	def test_handler(message):
		msg_text = message.message_text
		cmd = message.cmd		
		args = message.args		
		
		response_text = " ".join(args)[::-1]		
		bot.send(CHAT_ID, response_text)
		return response_text

	bot.register_handler('/test_handler', test_handler)

	handler_output = None
	while not handler_output:
		print('Please send "/test_handler [string]"')
		time.sleep(3)
		handler_output = bot.check_commands()
		
	recv = input('Response: ')
	assert handler_output == recv, 'Handler output does not match expected'


# test_get_updates()
# test_send()
test_register_handler()



