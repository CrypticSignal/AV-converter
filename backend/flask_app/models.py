from flask_app import db


# Defining a ConverterDB table in the database.
class ConverterDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(20), unique=True, nullable=False)
    times_used = db.Column(db.Integer, default=0)

    def __init__(self, ip, times_used):
        self.ip = ip
        self.times_used= times_used