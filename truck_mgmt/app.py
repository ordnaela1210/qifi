from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    plate_number = db.Column(db.String(50), nullable=False, unique=True)

class MaintenanceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    vehicle = db.relationship('Vehicle', backref=db.backref('maintenance_records', lazy=True))

class SparePart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    quantity = db.Column(db.Integer, default=1)

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Integer, default=0)

class ToolUsage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tool_name = db.Column(db.String(120), nullable=False)
    used_by = db.Column(db.String(120))
    date = db.Column(db.DateTime, default=datetime.utcnow)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/vehicles', methods=['GET', 'POST'])
def vehicles():
    if request.method == 'POST':
        data = request.json
        vehicle = Vehicle(name=data['name'], plate_number=data['plate_number'])
        db.session.add(vehicle)
        db.session.commit()
        return jsonify({'id': vehicle.id}), 201
    all_vehicles = Vehicle.query.all()
    return jsonify([{'id': v.id, 'name': v.name, 'plate_number': v.plate_number} for v in all_vehicles])

@app.route('/maintenance', methods=['GET', 'POST'])
def maintenance():
    if request.method == 'POST':
        data = request.json
        rec = MaintenanceRecord(vehicle_id=data['vehicle_id'], description=data.get('description', ''))
        db.session.add(rec)
        db.session.commit()
        return jsonify({'id': rec.id}), 201
    records = MaintenanceRecord.query.all()
    return jsonify([{'id': r.id, 'vehicle_id': r.vehicle_id, 'description': r.description, 'date': r.date.isoformat()} for r in records])

@app.route('/parts', methods=['GET', 'POST'])
def parts():
    if request.method == 'POST':
        data = request.json
        part = SparePart(name=data['name'], quantity=data.get('quantity',1))
        db.session.add(part)
        db.session.commit()
        return jsonify({'id': part.id}), 201
    parts = SparePart.query.all()
    return jsonify([{'id': p.id, 'name': p.name, 'quantity': p.quantity, 'purchase_date': p.purchase_date.isoformat()} for p in parts])

@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    if request.method == 'POST':
        data = request.json
        item = InventoryItem(name=data['name'], quantity=data.get('quantity', 0))
        db.session.add(item)
        db.session.commit()
        return jsonify({'id': item.id}), 201
    items = InventoryItem.query.all()
    return jsonify([{'id': i.id, 'name': i.name, 'quantity': i.quantity} for i in items])

@app.route('/tools', methods=['GET', 'POST'])
def tools():
    if request.method == 'POST':
        data = request.json
        usage = ToolUsage(tool_name=data['tool_name'], used_by=data.get('used_by'))
        db.session.add(usage)
        db.session.commit()
        return jsonify({'id': usage.id}), 201
    usages = ToolUsage.query.all()
    return jsonify([{'id': u.id, 'tool_name': u.tool_name, 'used_by': u.used_by, 'date': u.date.isoformat()} for u in usages])

if __name__ == '__main__':
    app.run(debug=True)
