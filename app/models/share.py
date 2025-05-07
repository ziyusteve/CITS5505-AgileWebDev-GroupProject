from app.extensions import db
from datetime import datetime


class Share(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey("datasets.id"), nullable=False)
    shared_with_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    date_shared = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    shared_with = db.relationship("User", foreign_keys=[shared_with_id])

    def __repr__(self):
        return f"Share(Dataset: {self.dataset_id}, Shared with: {self.shared_with_id})"
