"""
Mock Scout Report Analysis Service
Used to generate fake data when API calls fail
"""


class MockAnalysisService:
    """Mock Scout Report Analysis Service"""

    @staticmethod
    def analyze_text(text_content):
        """Analyze text and generate mock scout report analysis data"""
        # Extract some keywords to generate relevant analysis
        text_lower = text_content.lower()
        name = "Unknown Player"

        # Try to extract player name
        if "lebron" in text_lower:
            name = "LeBron James"
        elif "curry" in text_lower:
            name = "Stephen Curry"
        elif "durant" in text_lower:
            name = "Kevin Durant"
        elif "giannis" in text_lower:
            name = "Giannis Antetokounmpo"
        elif "jokic" in text_lower:
            name = "Nikola Jokic"
        elif "doncic" in text_lower:
            name = "Luka Doncic"

        # Generate analysis based on extracted keywords
        strengths = [
            "Excellent court vision",
            "High basketball IQ",
            "Strong offensive skills"
        ]
        weaknesses = [
            "Needs improvement on defense",
            "Inconsistent three-point shooting"
        ]
        development_areas = [
            "Focus on defensive positioning",
            "Develop leadership skills"
        ]

        if "shoot" in text_lower or "shooter" in text_lower or "shooting" in text_lower:
            strengths.append("Great shooting ability")
            offensive_rating = 88
        else:
            offensive_rating = 80

        if "defend" in text_lower or "defense" in text_lower or "defensive" in text_lower:
            strengths.append("Solid defensive skills")
            defensive_rating = 85
        else:
            defensive_rating = 75

        if "athletic" in text_lower or "jump" in text_lower or "speed" in text_lower:
            strengths.append("Exceptional athleticism")
            physical_rating = 90
        else:
            physical_rating = 78

        # Generate analysis summary
        summary = (
            f"Based on the provided text, {name} appears to be a talented basketball player with significant potential. "
            "The player shows strong offensive capabilities and court awareness. "
            "Further development in defensive positioning and consistency would elevate their game to the next level."
        )

        # Return mock analysis data
        return {
            "processing_status": "completed",
            "player_info": {
                "name": name,
                "position": "Forward",
                "team": "All-Stars"
            },
            "strengths": strengths,
            "weaknesses": weaknesses,
            "development_areas": development_areas,
            "summary": summary,
            "offensive_rating": offensive_rating,
            "defensive_rating": defensive_rating,
            "physical_rating": physical_rating,
            "technical_rating": 82,
            "potential_rating": 87,
            "overall_rating": 83
        }
