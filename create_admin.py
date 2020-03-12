from app.db import db
import os
from werkzeug.security import generate_password_hash, check_password_hash
from getpass import getpass
from dotenv import load_dotenv
load_dotenv()

db.init(os.getenv("MONGO_URI"))
username = input("Give name: ")
password = getpass("Give pass: ")
hashedpwd = generate_password_hash(password)

document = {"username": username, "password": hashedpwd}
res = db._users.insert_one(document)
print(res.inserted_id if res.acknowledged else "Error.")
print("check...", check_password_hash(hashedpwd, password))