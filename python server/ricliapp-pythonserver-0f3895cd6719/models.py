from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
db = SQLAlchemy()

class Authuser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    contact_name = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(100), nullable=False)
    contact_handler_uri = db.Column(db.String(100), nullable=False)
    contact_timezone = db.Column(db.String(100), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=False)
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    contract_type = db.Column(db.String(100), nullable=False)

    # Relationships
    devices = db.relationship('Device', backref='account', cascade="all, delete-orphan")
    expenses = db.relationship('Expense', backref='account', cascade="all, delete-orphan")
    sim_cards = db.relationship('SIM', backref='account', cascade="all, delete-orphan")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Numeric(6, 2), nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    paid_date = db.Column(db.Date, nullable=True)
    paid_reference = db.Column(db.String(128), nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    payment_model = db.Column(db.String(64), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)

    # Relationships
    topups = db.relationship('Topups', backref='expense', cascade="all, delete-orphan")

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(100), nullable=False)
    manufacturer = db.Column(db.String(100), nullable=False)
    os = db.Column(db.String(100), nullable=False)
    os_version = db.Column(db.String(100), nullable=False)
    api_version = db.Column(db.String(100), nullable=False)
    multisim = db.Column(db.Boolean, nullable=False, default=False)
    in_use = db.Column(db.Boolean, nullable=False, default=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)

    # Relationships
    sim_cards = db.relationship('SIM', backref='device', cascade="all, delete-orphan")


class SIM(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=True)
    created_time = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    register_time = db.Column(db.DateTime, nullable=True)
    expire_date = db.Column(db.Date, nullable=True)
    in_use = db.Column(db.Boolean, nullable=True, default=False)
    purchase_price_usd = db.Column(db.Numeric(5, 2), nullable=True)  # Column to store grade
    topup_price_usd = db.Column(db.Numeric(5, 2), nullable=True)  # Column to store grade


    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=True)

    # Relationships
    smss = db.relationship('SMS', backref='sim', cascade="all, delete-orphan", uselist=False)
    calls = db.relationship('Call', backref='sim', cascade="all, delete-orphan", uselist=False)
    statuses = db.relationship('Status', backref='sim', cascade="all, delete-orphan", uselist=False)
    topups = db.relationship('Topups', backref='sim', cascade="all, delete-orphan", uselist=False)
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
   

class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    received_time = db.Column(db.DateTime, default=datetime.utcnow)
    device_brand = db.Column(db.String(100), nullable=True, default='Unknown')
    device_model = db.Column(db.String(100), nullable=True, default='Unknown')
    device_android_version = db.Column(db.String(100), nullable=True, default='Unknown')
    device_installe_apps= db.Column(db.String(100), nullable=True)
    device_charging = db.Column(db.Boolean, nullable=False, default=False)
    device_battery_level = db.Column(db.String(10), nullable=False, default='0%')
    device_access_wifi_state = db.Column(db.Boolean, nullable=False, default=False)
    device_access_location = db.Column(db.Boolean, nullable=False, default=False)
    device_access_phone_state = db.Column(db.Boolean, nullable=False, default=False)
    device_access_phone_numbers = db.Column(db.Boolean, nullable=False, default=False)
    device_access_phone_calls = db.Column(db.Boolean, nullable=False, default=False)
    device_access_contacts = db.Column(db.Boolean, nullable=False, default=False)
    device_access_sms = db.Column(db.Boolean, nullable=False, default=False)
    device_access_call_interception = db.Column(db.Boolean, nullable=False, default=False)
    gsm_signal_strength = db.Column(db.Integer, nullable=False, default=0)
    gsm_signal_level_description = db.Column(db.String(50), nullable=False, default='No Signal')
    gsm_units = db.Column(db.String(10), nullable=False, default='dBm')
    gsm_reachable_status = db.Column(db.Boolean, nullable=False, default=False)
    gsm_roaming_status = db.Column(db.Boolean, nullable=False, default=False)
    gsm_mcc = db.Column(db.String(10), nullable=False, default='000')
    gsm_mnc = db.Column(db.String(10), nullable=False, default='000')
    gsm_network_operator_name = db.Column(db.String(100), nullable=False, default='Unknown')
    gsm_phone_number = db.Column(db.String(20), nullable=False, default='0000000000')
    gsm_network_country_iso = db.Column(db.String(10), nullable=False, default='US')
    wifi_signal_strength = db.Column(db.Integer, nullable=False, default=0)
    wifi_signal_level_description = db.Column(db.String(50), nullable=False, default='No Signal')
    wifi_units = db.Column(db.String(10), nullable=False, default='dBm')
    location_latitude=db.Column(db.Double, nullable=True, default=None)
    location_longitude=db.Column(db.Double, nullable=True, default=None)
    ri_app_running_since = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ri_calls_received = db.Column(db.Integer, nullable=False, default=0)
    ri_last_call_received = db.Column(db.DateTime, nullable=True)
    sim_id = db.Column(db.Integer, db.ForeignKey('sim.id'), nullable=False)

class InstalledApps(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    app_name = db.Column(db.String(100), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=False)

    #def as_dict(self):
    #    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def as_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        # Format datetime fields
        if 'received_time' in result:
            result['received_time'] = result['received_time'].strftime('%Y-%m-%d %H:%M:%S')
        if 'ri_last_call_received' in result and result['ri_last_call_received'] is not None:
            result['ri_last_call_received'] = result['ri_last_call_received'].strftime('%Y-%m-%d %H:%M:%S')
        if 'ri_app_running_since' in result:
            result['ri_app_running_since'] = result['ri_app_running_since'].strftime('%Y-%m-%d %H:%M:%S')
        return result

class SMS(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20),nullable=True)
    sender_id = db.Column(db.String(100), default='0000000000')
    sms_content = db.Column(db.Text, default='No content')
    time_received = db.Column(db.DateTime, default=datetime.utcnow)
    sim_id = db.Column(db.Integer, db.ForeignKey('sim.id'), nullable=False)
    pdu = db.Column(db.Text, nullable=False)

class Call(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), default='0000000000')
    caller_id = db.Column(db.String(100), default='0000000000')
    caller_id = db.Column(db.String(100), default='0000000000')
    time_received = db.Column(db.DateTime, default=datetime.utcnow)
    sim_id = db.Column(db.Integer, db.ForeignKey('sim.id'), nullable=False)

class Topups(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sim_id = db.Column(db.Integer, db.ForeignKey('sim.id'), nullable=False)
    expense_id = db.Column(db.Integer, db.ForeignKey('expense.id'), nullable=False)
    topup_time = db.Column(db.DateTime, default=datetime.utcnow)
    cost_usd = db.Column(db.Numeric(5, 2), nullable=False)
    topup_type = db.Column(db.String(10), nullable=False)
    comment = db.Column(db.String(256), nullable=True)
