import sleekxmpp
import logging
import sys
from chatterbotapi import ChatterBotFactory, ChatterBotType
import os
import getpass

#import dnspython
 
def session_start(event):
    chatbot.send_presence()
    print 'Session started'
    chatbot.get_roster()
 
def message(msg):
    if msg['type'] in ('chat','normal'):
        msg1 = msg['body']
        print("User\t - "+msg1)
        if msg1 == "close":
           sys.exit(0)
         
        reply = session.think(msg1).replace(".","").lower()
        print("Bot\t - "+reply)
        
        msg.reply(reply).send()
 
 

jid = raw_input("Enter your facebook id: ") + '@chat.facebook.com'
if any('SPYDER' in name for name in os.environ) \
   or 'pythonw.exe' in sys.executable:
    password = raw_input('WARNING: PASSWORD WILL BE SHOWN ON SCREEN\n\n' * 3
                         + 'Please enter your password: ')
else:        
    password = getpass.getpass("Please enter your password: ")

try:
	c = input("What would you use?\nPandorabot = 0\nJabberWacky = 1\nCleverbot = 2\n0/1/2: ")
except:
	c = 1

addr = ('chat.facebook.com', 5222)

factory = ChatterBotFactory()

if (not c):
	print("* PandoraBots selected *")
	bot = factory.create(ChatterBotType.PANDORABOTS, 'b0dafd24ee35a477')
	
elif(c==1):
	print("* JabberWacky selected *")
	bot = factory.create(ChatterBotType.JABBERWACKY)
else:
	print("* Clerverbot selected *")
	bot = factory.create(ChatterBotType.CLEVERBOT)


session = bot.create_session()


chatbot = sleekxmpp.ClientXMPP(jid,password)
chatbot.add_event_handler("session_start", session_start)
chatbot.add_event_handler("message", message)

chatbot.auto_reconnect = True
 
#logging.basicConfig(level=logging.DEBUG,
#                       format='%(levelname)-8s %(message)s')
 

chatbot.connect(addr)
chatbot.process(block=True)
