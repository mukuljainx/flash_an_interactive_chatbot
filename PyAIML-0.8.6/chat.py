import aiml
import os
import subprocess
import time

k = aiml.Kernel()
k.learn("Science.aiml")

while True:
	os.chdir('/home/hodor/Desktop/flash/LiSpeak-master') # used for changing directory
	print "Flash is listening to you" 
	subprocess.call("./hotkey") #to run any process, hotkey is recording trigger
	time.sleep(3) #creates delay
	subprocess.call("./hotkey") #stops recording after 3 sec and sends voice to google
	print "Give him some time"
	f= open('data', 'r') 
	rec = f.read() # reads what we said from a file kept in pwd
	print rec
	reply = k.respond(rec) #to get reply
	print reply
	r= open('ans','w')
	r.write(reply) # reply printed in a txt file
	f.close()
	r.close()
	os.system("cat ans | festival --tts") # using terminal commands, yes terminal commands can be used for chaging directory.
	x = raw_input('Press y to continue') 
	if x == "y" :
		continue
	else :
		break
