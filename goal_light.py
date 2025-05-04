import time
import drivers.st7796 as st7796
import drivers.ft6336u as ft6336u
from PIL import Image,ImageDraw,ImageFont
import requests
from subprocess import call
from datetime import datetime, timezone

welcome = """
****************************************
NHL GOAL LIGHT

Created and programmed by Joseph (quixt)

Useable under MIT License
****************************************
"""

print(welcome)
print("System Timezone: ", time.tzname)
def utc_to_local(utc:datetime):
    if utc.tzinfo is None:
        # Assume input is UTC but naive, convert it to aware
        utc = utc.replace(tzinfo=timezone.utc)
    local_time = utc.astimezone()
    return local_time

def clean_datetime_str(hour, minute):
    if hour > 12:
        hour-=12
        pmAm = "PM"
    else:
        pmAm = "AM"
    if minute == 0:
        minuteString = "00"
    else:
        minuteString = str(minute)
    timeString = f"{hour}:{minuteString} {pmAm}"
    return timeString
    

class GoalLightGUI:
    def __init__(self):
        # Used to get the date for the request
        # Deprecated for now
        self.game={}
        self.gameNum = 0
        self.allGames = []
        self.buttons = []
        
        # Load the first game as default
        self.getGames()
        self.runLoop = True
        self.refreshInterval = 0.05
        self.requestInterval = 10
        self.requestPoint = (1/0.05)*self.requestInterval

        # Display Params
        self.display = st7796.st7796()
        self.touch = ft6336u.ft6336u()
        self.width = 480
        self.height = 320

        #Width, Height, X, Y, Margin, SRC, Screen Size
        self.prevGameButton = self.Button(24, 42, 50, 250, 10, "PrevGameButton.png", (self.width, self.height))
        self.registerButton(self.prevGameButton, self.handlePrevGame)
        self.nextGameButton = self.Button(24, 42, 406, 250, 10, "NextGameButton.png", (self.width, self.height))
        self.registerButton(self.nextGameButton, self.handleNextGame)
        self.closeScreenButton = self.Button(25,25, 445, 10, 0, "CloseScreen.png", (self.width, self.height))
        self.registerButton(self.closeScreenButton, self.killProgram)

        # GUI Params
        self.logoSize = (100,100)
        self.sideMargin = 20
        self.font = "NotoSans"
        # Used to account for width of text in early stages
        self.phaseConstant = 20
        self.chevronSize = (50,50)
        self.chevronMargin = (50,50)
        self.touchMargin = 25

        # Colors
        self.backgroundGreyCOLOR = (25,25,25)
        self.whiteCOLOR = (255,255,255)

        # Clear the display initially
        self.display.clear()
        
    def drawScreen(self):
        background = Image.new("RGB",(480,320), self.backgroundGreyCOLOR)
        logoAway = Image.open(f"./logos/{self.game['awayTeam']['abbrev']}.png")
        logoHome = Image.open(f"./logos/{self.game['homeTeam']['abbrev']}.png")
        logoAwayAspectRatio = logoAway.height/logoAway.width
        logoHomeAspectRatio = logoHome.height/logoHome.width
        resizedLogoAway = logoAway.resize((self.logoSize[0],int(logoAwayAspectRatio*self.logoSize[0])))
        resizedLogoHome = logoHome.resize((self.logoSize[0], int(logoHomeAspectRatio*self.logoSize[0])))
        
        # Paste Logos
        # Schema: X: Distance from the left of screen
        #         Y: Distance from top of screen
        background.paste(resizedLogoAway, (self.sideMargin,int((self.height-resizedLogoAway.size[1])/2)), mask=resizedLogoAway)
        background.paste(resizedLogoHome, (self.width-self.sideMargin-self.logoSize[0],int((self.height-resizedLogoHome.size[1])/2)), mask=resizedLogoHome)
        
        # Draw the score text
        backgroundTextDraw = ImageDraw.Draw(background)
        textColor = self.whiteCOLOR
        font = ImageFont.truetype(f"./static/{self.font}.ttf", 48)
        if self.game["gameState"] == "PRE" or self.game["gameState"] == "FUT":
            awayScore = "-"
            homeScore = "-"
            startTimeUTC = str(self.game["startTimeUTC"])
            startTimeUTC = startTimeUTC.replace("T"," ").replace("Z","")
            utc = datetime.strptime(startTimeUTC, '%Y-%m-%d %H:%M:%S')
            utc = utc.replace(tzinfo=timezone.utc)
            newTime = utc_to_local(utc)
            timeFont = ImageFont.truetype(f"./static/{self.font}.ttf", 18)
            backgroundTextDraw.text((20,20), clean_datetime_str(newTime.hour,newTime.minute), textColor, font=timeFont)

        else:
            awayScore = str(self.game["awayTeam"]["score"])
            homeScore = str(self.game["homeTeam"]["score"])
        backgroundTextDraw.text((self.sideMargin*2+self.logoSize[0], 120), awayScore, textColor, font=font)
        backgroundTextDraw.text((self.width-(self.sideMargin*2+self.logoSize[0])-self.phaseConstant, 120), homeScore, fill=textColor, font=font)
        # Display the number of games
        gameNumFont = ImageFont.truetype(f"./static/{self.font}.ttf",18)
        backgroundTextDraw.text((230,260), f"{self.gameNum+1}/{len(self.allGames)}", fill = textColor, font=gameNumFont)
        periodFont = ImageFont.truetype(f"./static/{self.font}.ttf", 18)

        for button in self.buttons:
            background = button[0].drawButton(background)
        if self.game["gameState"] == "OFF" or self.game["gameState"] == "FINAL":
            backgroundTextDraw.text((20,20),f"FINAL: {self.game['gameOutcome']['lastPeriodType']}",textColor, font=periodFont)
        elif "period" in self.game:
            if self.game["clock"]["inIntermission"]:
                backgroundTextDraw.text((20,20),f"Intermission {str(self.game['period'])}",textColor, font=periodFont)
            elif self.game["periodDescriptor"]["periodType"] == "REG":
                backgroundTextDraw.text((20,20),f"Period {str(self.game['periodDescriptor']['number'])}",textColor, font=periodFont)
            elif self.game["periodDescriptor"]["periodType"] == "OT":
                backgroundTextDraw.text((20,20),f"Overtime {str(self.game['periodDescriptor']['otPeriods'])}",textColor, font=periodFont)
        # Screen display is flipped-image must be flipped horizontally to display correctly
        flippedBackground = background.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

        # Switch display
        self.display.show_image(flippedBackground)
        
    def registerButton(self, button, callback):
        self.buttons.append([button, callback])
    
    def getGames(self):
        print("making request to NHL API")
        gamesNow = requests.get(f"https://api-web.nhle.com/v1/score/now")
        gamesJson = gamesNow.json()
        self.allGames = gamesJson["games"]
        # Checks if no game has been loaded
        if len(list(self.game.keys())) != 0:
            self.evalChange(self.allGames[self.gameNum])
        else:
            self.game = self.allGames[self.gameNum]
    
    def setGame(self, number=None):
        if number == None:
            self.game = self.allGames[self.gameNum]
        else:
            self.game = self.allGames[number]
    def stateChanged(self, newGameData):
        if newGameData["gameState"] != self.game["gameState"]:
            return True
        elif "period" in newGameData and not "period" in newGameData:
            return True
        elif "period" in newGameData:
            if newGameData["period"] != self.game["period"] or newGameData["clock"]["inIntermission"] != self.game["clock"]["inIntermission"]:
                return True
            else:
                return False
        else:
            return False

    
    def evalChange(self, newGameData):
        if self.game["gameState"] != "PRE" and self.game["gameState"] != "FUT":
            oldAwayScore = self.game["awayTeam"]["score"]
            oldHomeScore = self.game["homeTeam"]["score"]
            newAwayScore = newGameData["awayTeam"]["score"]
            newHomeScore = newGameData["homeTeam"]["score"]
            # If the score is different, update the game data and redraw the screen
            if newAwayScore != oldAwayScore or newHomeScore != oldHomeScore or self.stateChanged(newGameData):
                self.game = newGameData
                print("State Updated (Goal or game state change)")
                self.drawScreen()
        elif self.stateChanged(newGameData):
            self.game = newGameData
            print("Game State Changed")
            self.drawScreen()
            
            
    def handleTouch(self, coordinates):
        # The "y" measures from the right of the screen to the left
        # The "x" measures from the bottom of the screen to the top
        xCoord = coordinates[0]["y"]
        yCoord = coordinates[0]["x"]
        for button, callback in self.buttons:
            if button.screenSize[0] - button.x + button.margin >= xCoord >= button.screenSize[0]-button.x-button.width-button.margin and button.screenSize[1] - button.y + button.margin >= yCoord >= button.screenSize[1]-button.y-button.height-button.margin:
                callback()
    
    def handlePrevGame(self):
        if(self.gameNum != 0):
            self.gameNum -= 1
            self.setGame()
            self.drawScreen()

    def handleNextGame(self):
        if(self.gameNum < len(self.allGames)-1):
            self.gameNum += 1
            self.setGame()
            self.drawScreen()

    def killProgram(self):
        self.runLoop = False
        
        print("Closing Program")

    def startLoop(self):
        firstTouchSensed = False
        timeVar = 0
        self.drawScreen()
        while(self.runLoop):
            timeVar += 1
            self.touch.read_touch_data()
            point, coordinates = self.touch.get_touch_xy()
            if point != 0 and coordinates:
                if not firstTouchSensed:
                    self.handleTouch(coordinates)
                    firstTouchSensed = True
            else:
                firstTouchSensed = False
            if timeVar == self.requestPoint:
                self.getGames()
                timeVar = 0
            time.sleep(self.refreshInterval)
    class Button:
        def __init__(self, width, height, x, y, margin, src, screenSize):
            #From screen left
            self.x = x
            #From screen top
            self.y = y
            self.margin = margin
            self.src = src
            self.width = width
            self.height = height
            self.screenSize = screenSize
        def drawButton(self, img:Image):
            buttonImage = Image.open(f"./static/{self.src}")
            buttonImageResized = buttonImage.resize((self.width, self.height))
            img.paste(buttonImageResized,(self.x, self.y), mask=buttonImageResized)
            return img

if __name__=="__main__":
    gui = GoalLightGUI()
    gui.startLoop()
    call("sudo shutdown -h now", shell=True)