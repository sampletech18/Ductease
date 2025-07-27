from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

# Create upload folder if not exists
UPLOAD_FOLDER = os.path.join("static", "uploads")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# Import routes at the end to avoid circular imports
from routes import *


if __name__ == "__main__":
    app.run()
