#!/usr/bin/env python
import sys, os
import configparser
import tempfile

import face_recognition
from PIL import Image, ImageDraw

from telethon.sync import TelegramClient

config = configparser.ConfigParser()
config.read('facecamsendbot.ini')

telegram_client = TelegramClient('session',
                                 config['telegram']['api_id'],
                                 config['telegram']['api_hash'])
telegram_client.connect()

# in case of script ran first time it will
# ask either to input token or otp sent to
# number or sent or your telegram id
if not telegram_client.is_user_authorized():
    print('This bot is not yet authorized.\nRequesting code for {}'.format(config['telegram']['phone']))
    telegram_client.send_code_request(config['telegram']['phone'])
    # signing in the telegram_client
    telegram_client.sign_in(config['telegram']['phone'], input('Enter the code: '))

# validate input file
if len(sys.argv) == 1:
    print("Usage:\npython3 {} file.jpg".format(os.path.basename(__file__)) )
    exit(1)
if not os.path.exists(sys.argv[1]):
    print("Error: File does not exist: ",sys.argv[1] )
    exit(1)

# Load the test image with unknown faces into a numpy array
test_image = face_recognition.load_image_file(sys.argv[1])

# Find all the faces in the test image using the default HOG-based model
face_locations = face_recognition.face_locations(test_image)

# Convert the image to a PIL-format image so that we can draw on top of it with the Pillow library
# See http://pillow.readthedocs.io/ for more about PIL/Pillow
pil_image = Image.fromarray(test_image)

# Create a Pillow ImageDraw Draw instance to draw with
draw = ImageDraw.Draw(pil_image)

number_of_faces = len(face_locations)
if number_of_faces < 1:
    print("There where no faces detected.\nExiting ...")
    exit()

for i in range(number_of_faces):
    # get face location
    top, right, bottom, left = face_locations[i]
    # Draw a box around the face using the Pillow module
    draw.rectangle(((left -2, top -2), (right +2, bottom +2)),
                   outline=(0, 0, 255),
                   width=3)
# Remove the drawing library from memory as per the Pillow docs
del draw

# Display the resulting image
#pil_image.show()

picture_filehandle, picture_filename = tempfile.mkstemp(suffix=".jpg")
pil_image.save(picture_filename)

# send image via telegram
try:
    recipient = telegram_client.get_input_entity(int(config['telegram']['group_id']))
    telegram_client.send_message(recipient,
                        "Number of faces detected: "+ str(number_of_faces),
                        file=picture_filename)
except Exception as e:
    # there may be many error coming in while like peer
    # error, wrong access_hash, flood_error, etc
    print(e);

os.remove(picture_filename)

# disconnecting the telegram session
telegram_client.disconnect()
