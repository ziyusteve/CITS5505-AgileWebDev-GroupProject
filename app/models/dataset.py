from app.extensions import db
from datetime import datetime
from flask import current_app

class Dataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_uploaded = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    file_path = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    shares = db.relationship('Share', backref='dataset', lazy=True, cascade="all, delete")
    
    def __repr__(self):
        return f"Dataset('{self.title}', '{self.date_uploaded}')"
    
    def has_scout_analysis(self):
        """Check if this dataset has an associated scout report analysis"""
        if not current_app.config.get('ENABLE_SCOUT_ANALYSIS', False):
            return False
            
        try:
            from app.scout_analysis.models import ScoutReportAnalysis
            analysis = ScoutReportAnalysis.query.filter_by(dataset_id=self.id).first()
            return analysis is not None
        except ImportError:
            return False
    
    def get_scout_analysis(self):
        """Get the scout report analysis for this dataset if it exists"""
        if not self.has_scout_analysis():
            return None
            
        from app.scout_analysis.models import ScoutReportAnalysis
        return ScoutReportAnalysis.query.filter_by(dataset_id=self.id).first()
