from subprocess import call
print("Starting")
call(["aplay","-D","hw:3,0","./static/SEA.wav"])

print("End")