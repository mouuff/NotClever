import clientxmpp
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
        print "msg recieved"
        msg1 = msg['body']
        print msg1
        if msg1 == "close":
           sys.exit(0)
           
        #ici ca fonctionne si on ne met un texte simple
        msg.reply(bot1session.think(msg1)).send()
        #msg.reply("merd").send()
 
 

jid = raw_input("Enter your facebook id: ") + '@chat.facebook.com'
if any('SPYDER' in name for name in os.environ) \
   or 'pythonw.exe' in sys.executable:
    password = raw_input('WARNING: PASSWORD WILL BE SHOWN ON SCREEN\n\n' * 3
                         + 'Please enter your password: ')
else:        
    password = getpass.getpass("Please enter your password: ")

try:
	c = input("What would you use?\nPandorabot = 0 Cleverbot = 1\n0/1: ")
except:
	c = 1

addr = ('chat.facebook.com', 5222)

factory = ChatterBotFactory()

if (c):
	print("* Clerverbot selected *")
	bot1 = factory.create(ChatterBotType.CLEVERBOT)
else:
	print("* PandoraBots selected *")
	bot1 = factory.create(ChatterBotType.PANDORABOTS, 'b0dafd24ee35a477')


bot1session = bot1.create_session()


chatbot = clientxmpp.ClientXMPP(jid,password)
chatbot.add_event_handler("session_start", session_start)
chatbot.add_event_handler("message", message)

chatbot.auto_reconnect = True
 
#logging.basicConfig(level=logging.DEBUG,
#                       format='%(levelname)-8s %(message)s')
 

chatbot.connect(addr)
chatbot.process(block=True)
