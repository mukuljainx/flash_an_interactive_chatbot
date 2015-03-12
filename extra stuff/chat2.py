import aiml
k = aiml.learn()
k.learn("Default.aiml")

while True:
	rec = raw_input(rec)
	reply = k.respond(rec)
	print reply
