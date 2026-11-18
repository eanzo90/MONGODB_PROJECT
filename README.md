# NyumbaFind Uganda — Web Application

A browser-based version of the original NyumbaFind MongoDB + Python desktop prototype.

## Features
- Dashboard counts for properties, users, reports and viewing requests.
- Search available rentals by district and maximum monthly rent.
- Register a property; new listings are marked `pending`.
- Browse the original MongoDB collections: `properties`, `users`, `propertyReports`, `viewingRequests`.
- Flask backend and responsive HTML/CSS interface.

## Database compatibility
Uses the original database name `nyumbaFindDB` and the same four collection names and field names as `nyumbafind_mongodb.js`.

## Original MongoDB setup script
The included `nyumbafind_mongodb.js` creates the same database (`nyumbaFindDB`), four original collections and sample records. Run it only once against an empty database: `mongosh < nyumbafind_mongodb.js`. Do not rerun it after the sample records have been inserted, because the document IDs are unique.

## Run locally
1. Install Python 3.11 or 3.12.
2. Install dependencies: `python -m pip install -r requirements.txt`
3. Ensure MongoDB is running locally, or set `MONGODB_URI` to a MongoDB connection string.
4. Start: `python app.py`
5. Open `http://127.0.0.1:5000`

## Deploy on Render
1. Push this folder to a GitHub repository.
2. Create a MongoDB Atlas database and allow the Render service to connect to it. Use a strong database user and restrict network access where practical.
3. In Render, choose **New + → Web Service**, connect the GitHub repository, and use:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
4. Add environment variable `MONGODB_URI` with the Atlas connection string. Add `SECRET_KEY` with a long random value.
5. Deploy. Render will provide the public hosted URL.

## Important demo/security note
This is an educational demonstration, not a production rental marketplace. The current prototype has no login or role-based access control. Anyone who can access the public URL can view the records and submit property listings. Use synthetic/sample data only; do not connect private user information or a production database until authentication, authorization, validation, moderation and privacy protections are implemented.
