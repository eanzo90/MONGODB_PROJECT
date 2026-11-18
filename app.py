import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient, DESCENDING
from pymongo.errors import PyMongoError
from bson.json_util import dumps

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "nyumbafind-demo-change-this")

MONGO_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
DATABASE_NAME = "nyumbaFindDB"
COLLECTIONS = {
    "users": ["_id", "fullName", "phone", "role", "district"],
    "propertyReports": ["_id", "propertyId", "reportedBy", "reason", "status"],
    "viewingRequests": ["_id", "propertyId", "tenantId", "requestedDate", "status"],
}
client = None
db = None
connection_error = None

def get_db():
    global client, db, connection_error
    if db is not None:
        return db
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        db = client[DATABASE_NAME]
        connection_error = None
        return db
    except Exception as exc:
        connection_error = str(exc)
        client = None
        db = None
        return None

def safe_count(database, collection):
    try:
        return database[collection].count_documents({})
    except Exception:
        return 0

def display_value(value):
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    if isinstance(value, dict):
        return str(value)
    return value if value is not None else ""

@app.route("/")
def index():
    database = get_db()
    stats = {"properties": 0, "users": 0, "reports": 0, "views": 0}
    properties = []
    connected = database is not None
    if connected:
        stats = {
            "properties": safe_count(database, "properties"),
            "users": safe_count(database, "users"),
            "reports": safe_count(database, "propertyReports"),
            "views": safe_count(database, "viewingRequests"),
        }
        query = {"available": True}
        district = request.args.get("district", "").strip()
        maximum = request.args.get("max_rent", "").strip()
        if district:
            query["district"] = {"$regex": district, "$options": "i"}
        if maximum:
            try:
                query["monthlyRentUGX"] = {"$lte": int(maximum)}
            except ValueError:
                flash("Maximum rent must be a whole number, for example 300000.", "error")
        properties = list(database.properties.find(query).sort("monthlyRentUGX", 1).limit(100))
    return render_template("index.html", stats=stats, properties=properties,
                           connected=connected, connection_error=connection_error,
                           district=request.args.get("district", ""),
                           max_rent=request.args.get("max_rent", ""))

@app.route("/add-property", methods=["POST"])
def add_property():
    database = get_db()
    if database is None:
        flash("Database is unavailable. Please try again later.", "error")
        return redirect(url_for("index"))
    try:
        doc = {
            "_id": request.form.get("property_id", "").strip(),
            "title": request.form.get("title", "").strip(),
            "district": request.form.get("district", "").strip(),
            "area": request.form.get("area", "").strip(),
            "propertyType": request.form.get("property_type", "").strip(),
            "bedrooms": int(request.form.get("bedrooms", "0")),
            "monthlyRentUGX": int(request.form.get("rent", "0")),
            "depositUGX": int(request.form.get("deposit", "0")),
            "available": True,
            "verificationStatus": "pending",
            "advertiserId": request.form.get("advertiser_id", "").strip(),
        }
        if not all([doc["_id"], doc["title"], doc["district"], doc["advertiserId"]]):
            raise ValueError("Complete all required fields.")
        if doc["bedrooms"] < 0 or doc["monthlyRentUGX"] < 0 or doc["depositUGX"] < 0:
            raise ValueError("Bedrooms, rent and deposit cannot be negative.")
        database.properties.insert_one(doc)
        flash("Property added successfully. Its verification status is PENDING.", "success")
    except ValueError as exc:
        flash(str(exc), "error")
    except PyMongoError as exc:
        flash(f"Could not save property: {exc}", "error")
    return redirect(url_for("index"))

@app.route("/records/<collection>")
def records(collection):
    if collection not in COLLECTIONS and collection != "properties":
        return "Collection not found", 404
    database = get_db()
    if database is None:
        flash("MongoDB is not connected. Configure MONGODB_URI.", "error")
        return redirect(url_for("index"))
    columns = (["_id", "title", "district", "area", "bedrooms", "monthlyRentUGX",
                "depositUGX", "available", "verificationStatus"]
               if collection == "properties" else COLLECTIONS[collection])
    docs = list(database[collection].find().sort("_id", DESCENDING).limit(200))
    rows = [{col: display_value(doc.get(col, "")) for col in columns} for doc in docs]
    return render_template("records.html", collection=collection, columns=columns, rows=rows)

@app.route("/health")
def health():
    database = get_db()
    return {"status": "ok" if database is not None else "database_unavailable",
            "database": DATABASE_NAME}, (200 if database is not None else 503)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
