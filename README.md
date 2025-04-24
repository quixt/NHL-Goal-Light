# NHL-Goal-Light
This is a physical light that flashes and plays a goal horn and song when a hockey team scores.
## How It Works
The program starts by writing to a capacitive touch screen powered off of the GPIO pins on a Raspberry Pi 4B.
A simple screen is displayed: Two teams (corresponding to the teams in a game), their respective scores, and two arrows.
The arrows allow the user to switch between games to "subscribe" to.
The NHL API is polled every 10 seconds and the game "subscribed" to (in focus on touchscreen) is obtained.
The program checks if a goal has been scored.  If so, it plays the light and audio program.
This is all run in a synchronous loop, handling both display and touch capability.
The program uses the basic drivers provided by Waveshare.
## Materials
- Waveshare 3.5" Capacitive Touch LCD with board
- Raspberry Pi 4B
- USB-C Breakout Board
- Class D Amplifier Breakout Board
- 5W 4Ohm Speaker
