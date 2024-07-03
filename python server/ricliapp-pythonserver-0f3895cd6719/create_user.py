import json
import random
import string
import qrcode
from PIL import Image
from sqlalchemy import create_engine, MetaData, Table
import random
import string

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

DATABASE_URL = 'mysql+pymysql://callreporter:ricli123@localhost/ricli'

# Create engine
engine = create_engine(DATABASE_URL, echo=True)


metadata = MetaData()



user=Table('user', metadata,autoload_with=engine)
username=input("enter username :")
passowrd=generate_random_password()

with engine.connect() as connection:

    connection.execute(user.insert(), {'username': username, 'password':passowrd })

    connection.commit()
print(username)
print(passowrd)

engine.dispose()

data = {
    "configuration": {
        "password": passowrd,
        "username": username
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
