from sqlalchemy import create_engine, func
from sqlalchemy import event
from sqlalchemy import text
from datetime import datetime
from sqlalchemy_utils import create_database, database_exists
from datetime import datetime
from flask import Flask, jsonify, request
from models import db, Device, SMS, Call, SIM, Status, Account, Authuser,InstalledApps
from flask_httpauth import HTTPBasicAuth
from flask_migrate import Migrate
import configparser
import ssl
from pprint import pprint
import json
import printr
#from app import app
from flask import Blueprint
import string
import random
from werkzeug.security import check_password_hash
rtand_bp = Blueprint('rtand', __name__)


#config = configparser.ConfigParser()
#config.read('config.ini')
#
#dbuser = config.get('ri', 'dbuser')
#dbpass = config.get('ri', 'dbpass')
#dbhost = config.get('ri', 'dbhost')
#dbname = config.get('ri', 'dbname')
#
#engine = create_engine('mysql+pymysql://' + dbuser + ':' + dbpass + '@' + dbhost + '/' + dbname)
#app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = engine.url
#db.init_app(app)
auth = HTTPBasicAuth()
#authuser = HTTPBasicAuth()
#
#app.config['SECRET_KEY'] = 'secret-key'
#
#if database_exists(engine.url):
#    print("Database already exists")
#    with app.app_context():
#        db.create_all()
#
#else:
#    if not create_database(engine.url):
#        print('Database created successfully.')
#        app.config['SQLALCHEMY_DATABASE_URI'] = engine.url
#    with app.app_context():
#        db.create_all()
#
#@app.route('/')
#def index():
#    return 'Hello World!'
#
#@authuser.verify_password
#def verify_password(username, password):
#    authuser = Authuser.query.filter_by(username=username,password=password).first()
#    if authuser and authuser.password == password:
#        return authuser
#
def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

@auth.verify_password
def verify_password(phone_number, password):
    sim = SIM.query.filter_by(phone_number=phone_number).first()
    if sim and sim.check_password(password):
        return sim

@rtand_bp.route('/register', methods=['POST'])
def register_sim():
    try:
        data = request.get_json()
        phone_number = data.get('phoneNumber')

        if not phone_number:
            return jsonify({"Success": False, "Message": "Phone number is required"}), 400

        # Find the SIM with the given phone number
        sim = SIM.query.filter_by(phone_number=phone_number).first()

        if not sim:
            return jsonify({"Success": False, "Message": "Phone number not found"}), 404

        # Check if register_time is None and set the register_time and password
        if sim.register_time is None:
            sim.register_time = datetime.utcnow()
        else:
            return jsonify({"Success": False, "Message": "SIM already registered"}), 400
        # Generate a new password and set it
        new_password = generate_random_password()
        sim.set_password(new_password)

        db.session.commit()

        return jsonify({
            "Success": True,
            "configuration": {
                "password": new_password
            }
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"Success": False, "Message": "Internal server error"}), 500

@rtand_bp.route('/sms', methods=['POST'])
@auth.login_required
def put_sms():
    data = request.get_json()
    current_sim = auth.current_user()
    if not data:
        return jsonify(message="No SMS data provided"), 400

    for sms_data in data:
        phone_number = sms_data.get('phone_number')
        sender_id = sms_data.get('sender_id')
        sms_content = sms_data.get('sms_content')
        time_received_str = sms_data.get('time_received')
        pdu = sms_data.get('pdu')

        try:
            time_received = datetime.strptime(time_received_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return jsonify(message="Invalid time format"), 400

        # Assuming you have a current_user variable representing the authenticated user
 # Check if an SMS with the same user ID and phone number exists


            # Create a new SMS entry
        new_sms = SMS(
            phone_number=phone_number,
            sender_id=sender_id,
            sms_content=sms_content,
            time_received=time_received,
            sim_id=current_sim.id,
            pdu=pdu
            )
        db.session.add(new_sms)

    db.session.commit()

    return jsonify(message="SMS data processed successfully"), 200

@rtand_bp.route('/call', methods=['POST'])
@auth.login_required
def put_call():
    data = request.get_json()
    current_sim = auth.current_user()
    #rtand_bp.logger.log(10, data)
    if not data:
        return jsonify(message="No call data provided"), 400

    for call_data in data:
        phone_number = call_data.get('phone_number')
        caller_id = call_data.get('caller_id')
        time_received_str = call_data.get('time_received')

        try:
            time_received = datetime.strptime(time_received_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return jsonify(message="Invalid time format"), 400

        # Assuming you have a current_user variable representing the authenticated user

        new_call = Call(
            phone_number=phone_number,
            caller_id=caller_id,
            time_received=time_received,
            sim_id=current_sim.id
        )
        db.session.add(new_call)

    db.session.commit()

    return jsonify(message="Call data processed successfully"), 200


@rtand_bp.route('/status', methods=['POST'])
@auth.login_required
def put_data():
    try:
        current_sim = auth.current_user()  # Extract user from authentication (simulated)
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400

        # Extract nested data
        ri_data = data.get('RI', {})
        wifi_data = data.get('WiFi', {})
        gsm_data = data.get('GSM', {})
        device_data = data.get('Device', {})
        location_data = data.get('location', {})

        # Create the status entry
        create_status(current_sim.id, ri_data, wifi_data, gsm_data, device_data, location_data)

        # Commit the transaction to the database
        db.session.commit()

        return jsonify({"message": "Data added successfully"}), 200

    except Exception as e:
        db.session.rollback()  # Rollback transaction in case of error
        return jsonify({"message": "Error adding data", "error": str(e)}), 500

def create_status(sim_id, ri_data, wifi_data, gsm_data, device_data, location_data):
    if ri_data.get('lastCallReceived') is None or ri_data.get('lastCallReceived') == "":
        ri_data['lastCallReceived'] = None

    if not location_data:
        location_data = {'latitude': None, 'longitude': None}

    status = Status(
        received_time=datetime.utcnow(),
        device_brand=device_data.get('brand', 'Unknown'),
        device_model=device_data.get('model', 'Unknown'),
        device_android_version=device_data.get('android_version', 'Unknown'),
        device_charging=device_data.get('charging', False),
        device_battery_level=device_data.get('batteryLevel', '0%'),
        device_access_wifi_state=device_data.get('access_wifi_state', False),
        device_access_location=device_data.get('access_location', False),
        device_access_phone_state=device_data.get('access_phone_state', False),
        device_access_phone_numbers=device_data.get('access_phone_numbders', False),
        device_access_phone_calls=device_data.get('access_phone_calls', False),
        device_access_contacts=device_data.get('access_contacts', False),
        device_access_sms=device_data.get('access_sms', False),
        device_access_call_interception=device_data.get('access_call_interception', False),
        gsm_signal_strength=gsm_data.get('signalStrength', 0),
        gsm_signal_level_description=gsm_data.get('signalLevelDescription', 'No Signal'),
        gsm_units=gsm_data.get('units', 'dBm'),
        gsm_reachable_status=gsm_data.get('reachableStatus', False),
        gsm_roaming_status=gsm_data.get('roamingStatus', False),
        gsm_mcc=gsm_data.get('MCC', '000'),
        gsm_mnc=gsm_data.get('MNC', '000'),
        gsm_network_operator_name=gsm_data.get('networkOperatorName', 'Unknown'),
        gsm_phone_number=gsm_data.get('phoneNumber', '0000000000'),
        gsm_network_country_iso=gsm_data.get('networkCountryISO', 'US'),
        wifi_signal_strength=wifi_data.get('signalStrength', 0),
        wifi_signal_level_description=wifi_data.get('signalLevelDescription', 'No Signal'),
        wifi_units=wifi_data.get('units', 'dBm'),
        location_latitude=location_data.get('latitude'),
        location_longitude=location_data.get('longitude'),
        ri_app_running_since=datetime.strptime(ri_data.get('appRunningSince'), '%Y-%m-%d %H:%M:%S') if ri_data.get('appRunningSince') else datetime.utcnow(),
        ri_calls_received=ri_data.get('callsReceived', 0),
        ri_last_call_received=datetime.strptime(ri_data.get('lastCallReceived'), '%Y-%m-%d %H:%M:%S') if ri_data.get('lastCallReceived') else None,
        sim_id=sim_id
    )
    db.session.add(status)
    db.session.flush()  
    installed_apps = device_data.get('installed_apps', [])
    if installed_apps:  
        for app in installed_apps:
            installed_app = InstalledApps(app_name=app, status_id=status.id)
            db.session.add(installed_app)

