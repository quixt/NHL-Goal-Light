from PIL import Image,ImageDraw,ImageFont
import time
background = Image.new("RGB", (480,320), (25,25,25))
logo = Image.open("./logos/kraken.png")
logo_resized = logo.resize((100,100))
background.paste(logo_resized, (360, 110), mask=logo_resized)
background.paste(logo_resized, (20, 110), mask=logo_resized)
textDraw = ImageDraw.Draw(background)
textDraw.text((360, 110), "1", fill=(255,255,255), font=ImageFont.truetype("./NotoSans.ttf", 24))
fl_bg = background.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
fl_bg.show()
time.sleep(30)