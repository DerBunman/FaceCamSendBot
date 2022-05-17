#!/usr/bin/env python
import sys
import os
import configparser
import tempfile

import face_recognition
from PIL import Image, ImageDraw

from telethon.sync import TelegramClient

# import logging
# logging.basicConfig(level=logging.INFO)

config = configparser.ConfigParser()
config.read('facecamsendbot.ini')

telegram_client = TelegramClient('bot',
                                 config['telegram']['api_id'],
                                 config['telegram']['api_hash']).start(
                                     bot_token=config['telegram']['token'])

# validate input file
if len(sys.argv) == 1:
    print("Usage:\npython3 {} file.jpg".format(os.path.basename(__file__)))
    exit(1)
if not os.path.exists(sys.argv[1]):
    print("Error: File does not exist: ", sys.argv[1])
    exit(1)

# Load the test image with unknown faces into a numpy array
test_image = face_recognition.load_image_file(sys.argv[1])

# Find all the faces in the test image using the default HOG-based model
face_locations = face_recognition.face_locations(test_image)

# Convert the image to a PIL-format image so that we can
# draw on top of it with the Pillow library
pil_image = Image.fromarray(test_image)

# Create a Pillow ImageDraw Draw instance to draw with
draw = ImageDraw.Draw(pil_image)

if not face_locations:
    print("There where no faces detected.\nExiting ...")
    exit()

for top, right, bottom, left in face_locations:
    # Draw a box around the face using the Pillow module
    draw.rectangle(((left - 2, top - 2), (right + 2, bottom + 2)),
                   outline=(0, 0, 255),
                   width=3)
del draw

# Display the resulting image
# pil_image.show()

picture_filehandle, picture_filename = tempfile.mkstemp(suffix=".jpg")
pil_image.save(picture_filename)

# send image via telegram
try:
    recipient = telegram_client.get_input_entity(
        int(config['telegram']['group_id']))
    telegram_client.send_message(recipient,
                                 "Number of faces: " + str(len(face_locations)),
                                 file=picture_filename)
except Exception as e:
    # there may be many error coming in while like peer
    # error, wrong access_hash, flood_error, etc
    print(e)

os.remove(picture_filename)

# disconnecting the telegram session
telegram_client.disconnect()
