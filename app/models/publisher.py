"""Publisher (login) model. Owner: Aariz."""
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db, utcnow


class Publisher(UserMixin, db.Model):
    __tablename__ = "publishers"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    announcements = db.relationship("Announcement", back_populates="author")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
