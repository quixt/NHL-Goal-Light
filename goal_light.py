import time
import drivers.st7796 as st7796
import drivers.ft6336u as ft6336u
from PIL import Image,ImageDraw,ImageFont
import requests
from subprocess import call
from datetime import datetime

class GoalLightGUI:
    def __init__(self):
        # Used to get the date for the request
        # Deprecated for now
        self.date = datetime.today().strftime('%Y-%m-%d')
        print(self.date)
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
        self.nextGameButton = self.Button(24, 42, 380, 250, 10, "NextGameButton.png", (self.width, self.height))
        self.registerButton(self.nextGameButton, self.handleNextGame)
        self.closeScreenButton = self.Button(40,40, 430, 10, 0, "CloseScreen.png", (self.width, self.height))
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
        else:
            awayScore = str(self.game["awayTeam"]["score"])
            homeScore = str(self.game["homeTeam"]["score"])
        backgroundTextDraw.text((self.sideMargin*2+self.logoSize[0], 120), awayScore, textColor, font=font)
        backgroundTextDraw.text((self.width-(self.sideMargin*2+self.logoSize[0])-self.phaseConstant, 120), homeScore, fill=textColor, font=font)

        # Create the chevrons to switch games
        # chevron = Image.open("./static/chevron.png")
        # chevronResized = chevron.resize(self.chevronSize)
        # background.paste(chevronResized,(self.width-self.chevronSize[0]-self.chevronMargin[0],self.height-self.chevronMargin[1]-self.chevronSize[1]),mask=chevronResized)
        # chevronFlipped = chevronResized.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        # background.paste(chevronFlipped,(self.chevronMargin[0],self.height-self.chevronMargin[1]-self.chevronSize[1]),mask=chevronFlipped)
        for button in self.buttons:
            background = button[0].drawButton(background)
        if self.game["gameState"] == "OFF" or self.game["gameState"] == "FINAL":
            finalScore = Image.open("./static/FinalScore.png")
            background.paste(finalScore, (int((self.width-finalScore.width)/2), 35), mask=finalScore)

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

    def evalChange(self, newGameData):
        if self.game["gameState"] != "PRE" and self.game["gameState"] != "FUT":
            oldAwayScore = self.game["awayTeam"]["score"]
            oldHomeScore = self.game["homeTeam"]["score"]
            newAwayScore = newGameData["awayTeam"]["score"]
            newHomeScore = newGameData["homeTeam"]["score"]
            # If the score is different, update the game data and redraw the screen
            if newAwayScore != oldAwayScore or newHomeScore != oldHomeScore or newGameData["gameState"] != self.game["gameState"]:
                self.game = newGameData
                print("State Updated (Goal or game state change)")
                self.drawScreen()
            
            
    def handleTouch(self, coordinates):
        # The "y" measures from the right of the screen to the left
        # The "x" measures from the bottom of the screen to the top
        xCoord = coordinates[0]["y"]
        yCoord = coordinates[0]["x"]
        for button, callback in self.buttons:
            if button.screenSize[0] - button.x + button.margin >= xCoord >= button.screenSize[0]-button.x-button.width-button.margin and button.screenSize[1] - button.y + button.margin >= yCoord >= button.screenSize[1]-button.y-button.height-button.margin:
                callback()
        # if self.chevronMargin[0]+self.chevronSize[0]+self.touchMargin >= coordinates[0]["y"] >= self.chevronMargin[0]-self.touchMargin and self.chevronMargin[1]+self.chevronSize[1]+self.touchMargin >= coordinates[0]["x"] >= self.chevronMargin[1]-self.touchMargin:
        #     self.handleNextGame()
        # elif self.width-(self.chevronMargin[0]-self.touchMargin) >= coordinates[0]["y"] >= self.width-(self.chevronMargin[0]+self.chevronSize[0]+self.touchMargin) and self.chevronMargin[1]+self.chevronSize[1]+self.touchMargin >= coordinates[0]["x"] >= self.chevronMargin[0]-self.touchMargin:
        #     self.handlePrevGame()
        # elif 50 >= coordinates[0]["y"] and self.height >= coordinates[0]["x"] >= self.height-50:
        #     self.killProgram()
    
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