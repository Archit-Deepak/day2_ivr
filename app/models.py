from datetime import datetime
from app.extensions import db


class CallLog(db.Model):
    __tablename__ = "call_logs"

    id = db.Column(db.Integer, primary_key=True)
    call_uuid = db.Column(db.String, nullable=False)
    from_number = db.Column(db.String, nullable=False)
    to_number = db.Column(db.String, nullable=False)
    menu_selection = db.Column(db.String, nullable=False)
    call_status = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "call_uuid": self.call_uuid,
            "from_number": self.from_number,
            "to_number": self.to_number,
            "menu_selection": self.menu_selection,
            "call_status": self.call_status,
            "created_at": self.created_at.isoformat(),
        }
