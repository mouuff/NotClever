import android, time
from chatterbotapi import ChatterBotFactory,ChatterBotType

droid = android.Android()

factory = ChatterBotFactory()

c=1

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

readSms = set()

while 1:
 time.sleep(10)
 msgIDs = droid.smsGetMessageIds(True, 'inbox').result
 if msgIDs:
  for msgID in msgIDs:
   if (msgID not in readSms):
    message = droid.smsGetMessageById(msgID, ['address','body']).result
    number = message['address'].encode('utf-8')
    body = message['body'].encode('utf-8')
    print("[*] Got sms: "+number+" >> "+body)
    reply = session.think(body)
    droid.smsSend(number, reply)
    print("[*] Sent sms: "+reply)
    readSms.add(msgID)
   #droid.smsMarkMessageRead(msgRead,1)



