from flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass

db = SQLAlchemy()


@dataclass
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False)  # Assuming email is a string
    name = db.Column(db.String(100), nullable=False)   # Increased length for name
    password = db.Column(db.String(100), nullable=True) # Password can be nullable
    auth_type = db.Column(db.String(50), nullable=False, default='local')  # New field for authentication type
    oath_token = db.Column(db.String(100), nullable=True) # Oath token can also be nullable

    def __repr__(self):
        return f"<User {self.id}: {self.username}>"