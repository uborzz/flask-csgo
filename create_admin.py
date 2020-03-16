import os
from getpass import getpass

from werkzeug.security import check_password_hash, generate_password_hash

from app.db import db
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
