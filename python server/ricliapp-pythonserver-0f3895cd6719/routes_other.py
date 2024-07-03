from sqlalchemy import create_engine, func
from sqlalchemy import event
from sqlalchemy import text
from datetime import datetime
from sqlalchemy_utils import create_database, database_exists
from datetime import datetime
from flask import Flask, jsonify, request
from models import db, Device, SMS, Call, SIM, Status, Account, Authuser
from flask_httpauth import HTTPBasicAuth
from flask_migrate import Migrate
import configparser
import ssl
from pprint import pprint
import json
import printr
from flask import Blueprint

rtoth_bp = Blueprint('rtoth', __name__)

authuser = HTTPBasicAuth()

@rtoth_bp.route('/authuser', methods=['POST'])
@authuser.login_required
def create_authuser():
    data = request.get_json()

    print(data)
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    try:
        new_authuser = Authuser(
            username=data['username'],
            password=data['password'],
            description=data['description']
        )

        db.session.add(new_authuser)
        db.session.commit()

        return jsonify({'message': 'Authuser created successfully', 'authuser_id': new_authuser.id}), 201

    except KeyError as e:
        return jsonify({'error': f'Missing key: {e.args[0]}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rtoth_bp.route('/accounts', methods=['GET'])
@authuser.login_required
def get_accounts():
    accounts = Account.query.all()
    return jsonify([account.as_dict() for account in accounts])

@rtoth_bp.route('/accounts/<int:id>', methods=['GET'])
@authuser.login_required
def get_account(id):
    account = Account.query.get(id)
    if account is None:
        return jsonify({'error': 'Account not found'}), 404
    return jsonify(account.as_dict())

@rtoth_bp.route('/createaccount', methods=['POST'])
@authuser.login_required
def create_account():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    try:
        new_account = Account(
            username=data['username'],
            password=data['password'],
            contact_name=data['contact_name'],
            contact_email=data['contact_email'],
            contact_phone=data['contact_phone'],
            contact_handler_uri=data['contact_handler_uri'],
            contact_timezone=data['contact_timezone'],
            active=data.get('active', False),
            contract_type=data['contract_type']
        )

        db.session.add(new_account)
        db.session.commit()

        return jsonify({'message': 'Account created successfully', 'account_id': new_account.id}), 201

    except KeyError as e:
        return jsonify({'error': f'Missing key: {e.args[0]}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rtoth_bp.route('/allsimstatuses', methods=['GET'])
@authuser.login_required
def get_all():
    subquery = db.session.query(
        Status.sim_id,
        func.max(Status.id).label('max_id')
    ).group_by(Status.sim_id).subquery()

    query = db.session.query(Status).join(
        subquery,
        (Status.sim_id == subquery.c.sim_id) & (Status.id == subquery.c.max_id)
    )

    latest_status = query.all()
    all_statuses_dict = [status.as_dict() for status in latest_status]
    return jsonify(all_statuses_dict)


@authuser.verify_password
def verify_password(username, password):
    authuser = Authuser.query.filter_by(username=username,password=password).first()
    if authuser and authuser.password == password:
        return authuser

@rtoth_bp.route('/getstatus', methods=['GET'])
@authuser.login_required
def get_status():
    query = Status.query
    for key, value in request.args.items():
        if '__' in key:
            column, op = key.split('__')
            if op == 'eq':
                query = query.filter(getattr(Status, column) == value)
            elif op == 'gt':
                query = query.filter(getattr(Status, column) > value)
            elif op == 'lt':
                query = query.filter(getattr(Status, column) < value)
    
    results = query.all()
    return jsonify([status.as_dict() for status in results])

@rtoth_bp.route('/getstatus/latest', methods=['GET'])
@authuser.login_required
def get_latest_status():
    subquery = db.session.query(
        Status.sim_id,
        db.func.max(Status.received_time).label('max_received_time')
    ).group_by(Status.sim_id).subquery()

    query = db.session.query(Status).join(
        subquery,
        (Status.sim_id == subquery.c.sim_id) & 
        (Status.received_time == subquery.c.max_received_time)
    )

    for key, value in request.args.items():
        if '__' in key:
            column, op = key.split('__')
            if op == 'eq':
                query = query.filter(getattr(Status, column) == value)
            elif op == 'gt':
                query = query.filter(getattr(Status, column) > value)
            elif op == 'lt':
                query = query.filter(getattr(Status, column) < value)

    results = query.all()
    return jsonify([status.as_dict() for status in results])

