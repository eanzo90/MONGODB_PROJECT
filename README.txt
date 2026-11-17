NYUMBAFIND UGANDA — MongoDB + Python Desktop UI
================================================

WHAT THIS PROJECT DOES
NyumbaFind addresses the difficulty of finding affordable, available and trustworthy rental
accommodation. It stores users, rental properties, suspicious-property reports and viewing requests.

PROJECT STRUCTURE
- nyumbafind_mongodb.js : original MongoDB setup script (mongosh). Kept separate from Python.
- app.py                : Python desktop interface (Tkinter + PyMongo).
- requirements.txt      : Python package needed by the interface.

IMPORTANT DESIGN
The Python interface does NOT replace the MongoDB script. The JavaScript file still creates the
same database, nyumbaFindDB, and the same four collections:
users, properties, propertyReports, viewingRequests.
Python connects to those collections using PyMongo.

REQUIREMENTS
1. Install Python 3.
2. Install MongoDB Community Server and MongoDB Shell (mongosh).
3. Start the MongoDB server.
4. Open Command Prompt/PowerShell in this project folder.

SETUP
Run:
    py -m pip install -r requirements.txt

CREATE THE ORIGINAL DATABASE
Run the MongoDB JavaScript file using mongosh:
    mongosh < nyumbafind_mongodb.js

If the database already exists with the sample records, do not run the setup script again:
it will attempt to insert duplicate IDs. The script intentionally does not drop your database.

START THE PYTHON INTERFACE
Run:
    py app.py

FEATURES IN THIS VERSION
- Dashboard counts for properties, users, reports and viewing requests.
- View the four original MongoDB collections.
- Search available listings by district and maximum monthly rent.
- Add a new property listing. New listings are marked "pending" for verification.

NOTES
- Tkinter is included with most standard Windows Python installations.
- MongoDB must be running locally at mongodb://localhost:27017/.
- This is an educational desktop prototype, not yet a public production service.
- Before real deployment, add secure login, role-based permissions, input validation,
  property verification procedures, audit logs, backups and protected database credentials.
- Do not put real people's private information into a public demo database.
