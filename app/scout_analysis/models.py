from app.extensions import db
from datetime import datetime
import json


class ScoutReportAnalysis(db.Model):
    """Scout Report Analysis Result Model"""

    __tablename__ = "scout_report_analyses"

    id = db.Column(db.Integer, primary_key=True)

    # Relationship to existing Dataset model
    dataset_id = db.Column(db.Integer, db.ForeignKey("datasets.id"), nullable=False)
    dataset = db.relationship(
        "Dataset", backref=db.backref("scout_analyses", lazy=True)
    )

    # Analysis results
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)
    analysis_result = db.Column(
        db.Text, nullable=True
    )  # Store analysis results in JSON format
    processing_status = db.Column(
        db.String(20), default="pending"
    )  # pending, processing, completed, failed

    # Player information
    player_name = db.Column(db.String(100), nullable=True)
    position = db.Column(db.String(50), nullable=True)
    team = db.Column(db.String(100), nullable=True)

    # Ratings
    offensive_rating = db.Column(db.Float, nullable=True)
    defensive_rating = db.Column(db.Float, nullable=True)
    physical_rating = db.Column(db.Float, nullable=True)
    technical_rating = db.Column(db.Float, nullable=True)
    potential_rating = db.Column(db.Float, nullable=True)
    overall_rating = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f"<ScoutReportAnalysis {self.id} for dataset {self.dataset_id}>"

    def to_dict(self):
        """Convert analysis result to dictionary"""
        return {
            "id": self.id,
            "dataset_id": self.dataset_id,
            "analysis_date": self.analysis_date.isoformat()
            if self.analysis_date
            else None,
            "processing_status": self.processing_status,
            "player_info": {
                "name": self.player_name,
                "position": self.position,
                "team": self.team,
            },
            "ratings": {
                "offensive": self.offensive_rating,
                "defensive": self.defensive_rating,
                "physical": self.physical_rating,
                "technical": self.technical_rating,
                "potential": self.potential_rating,
                "overall": self.overall_rating,
            },
            "analysis": json.loads(self.analysis_result)
            if self.analysis_result
            else {},
        }

    def update_from_analysis_result(self, analysis_result):
        """Update model fields from analysis result, compatible with various AI API return formats, ensuring content for display"""
        if not analysis_result:
            self.analysis_result = json.dumps(
                {"raw": "API returned no content"}, ensure_ascii=False
            )
            self.processing_status = "completed"
            return
        # Handle player_info compatibility
        player_info = (
            analysis_result.get("player_info", {})
            if isinstance(analysis_result, dict)
            else {}
        )
        self.player_name = player_info.get("name") or (
            analysis_result.get("player_name")
            if isinstance(analysis_result, dict)
            else None
        )
        self.position = player_info.get("position") or (
            analysis_result.get("position")
            if isinstance(analysis_result, dict)
            else None
        )
        self.team = player_info.get("team") or (
            analysis_result.get("team") if isinstance(analysis_result, dict) else None
        )
        # Handle ratings compatibility
        ratings = (
            analysis_result.get("ratings", {})
            if isinstance(analysis_result, dict)
            else {}
        )
        self.offensive_rating = ratings.get("offensive") or (
            analysis_result.get("offensive_rating")
            if isinstance(analysis_result, dict)
            else None
        )
        self.defensive_rating = ratings.get("defensive") or (
            analysis_result.get("defensive_rating")
            if isinstance(analysis_result, dict)
            else None
        )
        self.physical_rating = ratings.get("physical") or (
            analysis_result.get("physical_rating")
            if isinstance(analysis_result, dict)
            else None
        )
        self.technical_rating = ratings.get("technical") or (
            analysis_result.get("technical_rating")
            if isinstance(analysis_result, dict)
            else None
        )
        self.potential_rating = ratings.get("potential") or (
            analysis_result.get("potential_rating")
            if isinstance(analysis_result, dict)
            else None
        )
        self.overall_rating = ratings.get("overall") or (
            analysis_result.get("overall_rating")
            if isinstance(analysis_result, dict)
            else None
        )
        # Store complete analysis result, fallback to string
        try:
            self.analysis_result = json.dumps(analysis_result, ensure_ascii=False)
        except Exception:
            self.analysis_result = json.dumps(
                {"raw": str(analysis_result)}, ensure_ascii=False
            )
        self.processing_status = "completed"
