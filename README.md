# NHL-Goal-Light
This is a light that flashes and plays a goal horn and song when a hockey team scores.  The score is displayed on a small touchscreen.<br>
The CAD can be found [here](https://cad.onshape.com/documents/c55c02e04e703cfe27a60e14/w/b4b5bbc7188e16cf4a296082/e/4daa85a60760a7a30a035af4?renderMode=0&uiState=682fcc6b14300841d701ed5a).

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
- USB-C Power Dummy Board
- MAX98357A Class D Amplifier Breakout Board
- 5W 4Ohm Speaker
## GPIO Pinouts
### Capacitive Touch LCD
| Device Pin | Raspberry Pi Pin |
|------------|------------------|
| 3.3V       | 3.3V             |
| GND        | GND              |
| MISO       | GPIO 9           |
| MOSI       | GPIO 10          |
| SCLK       | GPIO 11          |
| LCD_CS     | GPIO 8           |
| LCD_DC     | GPIO 25          |
| LCD_RST    | GPIO 27          |
| TP_SDA     | GPIO 2           |
| TP_SCL     | GPIO 3           |
| TP_INT     | GPIO 4           |
| TP_RST     | GPIO 17          |
Unused Pins: VCC, SD
### MAX98357A Amplifier Board
| Device Pin | Raspberry Pi Pin |
|------------|------------------|
| GND        | GND              |
| DIN        | GPIO 21          |
| BCLK       | GPIO 18          |
| LRCLK      | GPIO 19          |
Vin to USB-C Breakout Vout
### USB-C Power Dummy:
| Device Pin | Raspberry Pi Pin |
|------------|------------------|
| Vout       | 5V               |
| GND        | GND              |
