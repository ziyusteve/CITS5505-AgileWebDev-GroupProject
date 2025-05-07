import requests
import json
import threading
from flask import current_app


class ScoutAnalysisService:
    """Scout Report Analysis Service"""

    # Class variables for model caching
    _nlp_model = None
    _model_lock = threading.Lock()

    @classmethod
    def get_nlp_model(cls):
        """Lazy load NLP model, only when needed to save resources"""
        if cls._nlp_model is None:
            with cls._model_lock:
                if cls._nlp_model is None:
                    try:
                        if current_app.config.get("ENABLE_SCOUT_DEEP_ANALYSIS", False):
                            current_app.logger.info(
                                "Loading NLP models for scout analysis..."
                            )
                            try:
                                from transformers import pipeline

                                cls._nlp_model = {
                                    "sentiment": pipeline(
                                        "sentiment-analysis",
                                        model="distilbert-base-uncased-finetuned-sst-2-english",
                                    ),
                                    "type": "transformer",
                                }
                                current_app.logger.info(
                                    "NLP models loaded successfully"
                                )
                            except ImportError:
                                current_app.logger.warning(
                                    "Transformers library not available, using rule-based analysis only"
                                )
                                cls._nlp_model = {"type": "rule_engine"}
                        else:
                            current_app.logger.info(
                                "Deep analysis disabled, using rule-based analysis only"
                            )
                            cls._nlp_model = {"type": "rule_engine"}
                    except Exception as e:
                        current_app.logger.error(f"Error loading NLP model: {str(e)}")
                        cls._nlp_model = {"type": "rule_engine"}
        return cls._nlp_model

    @staticmethod
    def analyze_report(text_content, use_deep_analysis=False):
        current_app.logger.warning(f"[DEBUG] services module path: {__file__}")
        """Analyze scout report text, ensuring strict adherence to Gemini API format"""
        try:
            current_app.logger.info(
                f"Starting text analysis, length={len(text_content)}"
            )
            api_key = current_app.config.get("GEMINI_API_KEY")
            if not api_key:
                current_app.logger.error(
                    "Missing GEMINI_API_KEY configuration, unable to perform text analysis"
                )
                return ScoutAnalysisService.generate_mock_analysis(text_content)
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
            current_app.logger.warning(
                f"[DEBUG] Using config API key: {api_key[:5]}...{api_key[-5:]}"
            )
            current_app.logger.warning(f"[DEBUG] Using API service: {api_url}")
            current_app.logger.warning(
                f"[DEBUG] Using Gemini API key: {api_key[:5]}...{api_key[-5:]}"
            )

            headers = {"Content-Type": "application/json"}

            system_instruction = "You are a professional basketball scout. You analyze player information and generate detailed scouting reports."
            user_prompt = f"""Given the following basketball player information, generate a detailed scouting report.

Include:
1. Player Name (string, key: player_name)
2. Player Position (string, key: position)
3. Player Team (string, if available, key: team)
4. Strengths (list of strings, at least 3, key: strengths)
5. Weaknesses (list of strings, at least 2, key: weaknesses)
6. Development areas (list of strings, at least 2, key: development_areas)
7. A detailed summary (string, 2-3 paragraphs, key: summary)
8. Numerical ratings from 0-100 for: offensive_rating, defensive_rating, physical_rating, technical_rating, potential_rating, overall_rating (keys: offensive_rating, defensive_rating, physical_rating, technical_rating, potential_rating, overall_rating)

Format your response as valid JSON with these exact keys: player_name, position, team, strengths, weaknesses, development_areas, summary, offensive_rating, defensive_rating, physical_rating, technical_rating, potential_rating, overall_rating

Player information:
{text_content[:1000]}"""

            prompt_with_instruction = f"{system_instruction}\n\n{user_prompt}"

            payload = {
                "contents": [
                    {"role": "user", "parts": [{"text": prompt_with_instruction}]}
                ],
                "generationConfig": {"temperature": 0.3, "maxOutputTokens": 2000},
            }

            current_app.logger.warning(f"[DEBUG] Gemini API request URL: {api_url}")
            current_app.logger.warning(f"[DEBUG] Gemini API request headers: {headers}")
            current_app.logger.warning(f"[DEBUG] Gemini API request body: {payload}")

            try:
                resp = requests.post(api_url, json=payload, headers=headers, timeout=60)
                current_app.logger.warning(
                    f"[DEBUG] Gemini API response status: {resp.status_code}"
                )
                if resp.status_code != 200:
                    current_app.logger.error(
                        f"Gemini API call failed: {resp.status_code} - {resp.text}"
                    )
                    return ScoutAnalysisService.generate_mock_analysis(text_content)
                result = resp.json()
                current_app.logger.warning(f"[DEBUG] API response: {result}")

                content = ""
                candidates = result.get("candidates", [])
                if candidates and len(candidates) > 0:
                    candidate = candidates[0]
                    if (
                        "content" in candidate
                        and "parts" in candidate["content"]
                        and len(candidate["content"]["parts"]) > 0
                    ):
                        content = candidate["content"]["parts"][0].get("text", "")

                current_app.logger.warning(f"[DEBUG] Analysis content: {content}")

                try:
                    content = content.replace("```json", "").replace("```", "").strip()
                    analysis_result = json.loads(content)
                    current_app.logger.warning(
                        f"[DEBUG] Parsed JSON: {analysis_result}"
                    )
                except Exception as e:
                    current_app.logger.error(f"JSON parsing failed: {str(e)}")
                    analysis_result = {"summary": content}

                return analysis_result

            except Exception as e:
                current_app.logger.error(f"API request failed: {str(e)}")
                return ScoutAnalysisService.generate_mock_analysis(text_content)

        except Exception as e:
            current_app.logger.error(f"Error during API call process: {str(e)}")
            return ScoutAnalysisService.generate_mock_analysis(text_content)

    @staticmethod
    def generate_mock_analysis(text_content):
        """Generate mock scout report analysis data"""
        text_lower = text_content.lower()
        name = "Unknown Player"

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

        strengths = [
            "Excellent court vision",
            "High basketball IQ",
            "Strong offensive skills",
        ]
        weaknesses = [
            "Needs improvement on defense",
            "Inconsistent three-point shooting",
        ]
        development_areas = [
            "Focus on defensive positioning",
            "Develop leadership skills",
        ]

        if "shoot" in text_lower or "shooter" in text_lower or "shooting" in text_lower:
            strengths.append("Great shooting ability")
            offensive_rating = 88
        else:
            offensive_rating = 80

        if (
            "defend" in text_lower
            or "defense" in text_lower
            or "defensive" in text_lower
        ):
            strengths.append("Solid defensive skills")
            defensive_rating = 85
        else:
            defensive_rating = 75

        if "athletic" in text_lower or "jump" in text_lower or "speed" in text_lower:
            strengths.append("Exceptional athleticism")
            physical_rating = 90
        else:
            physical_rating = 78

        summary = (
            f"Based on the provided text, {name} appears to be a talented basketball player with significant potential. "
            "The player shows strong offensive capabilities and court awareness. "
            "Further development in defensive positioning and consistency would elevate their game to the next level."
        )

        return {
            "processing_status": "completed",
            "player_info": {"name": name, "position": "Forward", "team": "All-Stars"},
            "strengths": strengths,
            "weaknesses": weaknesses,
            "development_areas": development_areas,
            "summary": summary,
            "offensive_rating": offensive_rating,
            "defensive_rating": defensive_rating,
            "physical_rating": physical_rating,
            "technical_rating": 82,
            "potential_rating": 87,
            "overall_rating": 83,
        }
