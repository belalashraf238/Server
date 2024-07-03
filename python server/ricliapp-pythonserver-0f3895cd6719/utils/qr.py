#!/usr/bin/python3
import json
import random
import string
import qrcode
from PIL import Image

# Function to generate a random and complex password
def generate_password(length=16):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password

# Generate password
password = generate_password()

# Create JSON object
data = {
    "configuration": {
        "password": password
    }
}

# Convert JSON object to string
json_data = json.dumps(data, indent=4)

# Write JSON string to a text file
with open('password_config.json', 'w') as json_file:
    json_file.write(json_data)

# Generate QR code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(json_data)
qr.make(fit=True)

# Create an image from the QR code instance
img = qr.make_image(fill='black', back_color='white')

# Save the image to a file
img.save('password_config_qr.png')

print("Password, JSON file, and QR code image have been generated successfully.")

