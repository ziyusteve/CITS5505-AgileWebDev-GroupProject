import requests
import json
import logging
import threading
import re
from flask import current_app
from datetime import datetime

class ScoutAnalysisService:
    """Scout Report Analysis Service"""
    # Class variables for model caching
    _nlp_model = None
    _model_lock = threading.Lock()
    
    @classmethod
    def get_nlp_model(cls):
        """Lazy load NLP model, only when needed to save resources"""
        if cls._nlp_model is None:
            with cls._model_lock:  # Prevent multiple threads from loading simultaneously
                if cls._nlp_model is None:
                    try:
                        # Only load model when deep analysis is enabled in config
                        if current_app.config.get('ENABLE_SCOUT_DEEP_ANALYSIS', False):
                            current_app.logger.info("Loading NLP models for scout analysis...")
                            # Load different model sizes based on configuration
                            try:
                                from transformers import pipeline
                                # Use lightweight model for sentiment analysis
                                cls._nlp_model = {
                                    'sentiment': pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english'),
                                    'type': 'transformer'
                                }
                                current_app.logger.info("NLP models loaded successfully")
                            except ImportError:
                                current_app.logger.warning("Transformers library not available, using rule-based analysis only")
                                cls._nlp_model = {'type': 'rule_engine'}
                        else:
                            current_app.logger.info("Deep analysis disabled, using rule-based analysis only")
                            cls._nlp_model = {'type': 'rule_engine'}
                    except Exception as e:
                        current_app.logger.error(f"Error loading NLP model: {str(e)}")                        # Provide a fallback rule engine
                        cls._nlp_model = {'type': 'rule_engine'}
        return cls._nlp_model

    @staticmethod
    def analyze_report(text_content, use_deep_analysis=False):
        # Log file path to debug loaded module
        current_app.logger.warning(f"[DEBUG] services module path: {__file__}")
        """Analyze scout report text, ensuring strict adherence to Gemini API format"""
        try:            # Log initial analysis request
            current_app.logger.info(f"Starting text analysis, length={len(text_content)}")
            
            # Get API key from configuration, without default value
            api_key = current_app.config.get('GEMINI_API_KEY')
            
            # Verify if API key exists
            if not api_key:
                current_app.logger.error("Missing GEMINI_API_KEY configuration, unable to perform text analysis")
                return ScoutAnalysisService.generate_mock_analysis(text_content)
                
            # Set API URL
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
            current_app.logger.warning(f"[DEBUG] Using config API key: {api_key[:5]}...{api_key[-5:]}")

            current_app.logger.warning(f"[DEBUG] Using API service: {api_url}")
            current_app.logger.warning(f"[DEBUG] Using Gemini API key: {api_key[:5]}...{api_key[-5:]}")
            
            # Build standard headers
            headers = {
                "Content-Type": "application/json"
            }
            
            # Build standard prompt
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

            # Build API request body for Gemini
            prompt_with_instruction = f"{system_instruction}\n\n{user_prompt}"
            
            # Build API request body for Gemini
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "text": prompt_with_instruction
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 2000
                }
            }
              # Print detailed request information for debugging
            current_app.logger.warning(f"[DEBUG] Gemini API request URL: {api_url}")
            current_app.logger.warning(f"[DEBUG] Gemini API request headers: {headers}")
            current_app.logger.warning(f"[DEBUG] Gemini API request body: {payload}")
            
            try:
                # Execute API call to Gemini
                resp = requests.post(api_url, json=payload, headers=headers, timeout=60)
                
                # Log response status
                current_app.logger.warning(f"[DEBUG] Gemini API response status: {resp.status_code}")
                
                # If response unsuccessful, log more information
                if resp.status_code != 200:
                    current_app.logger.error(f"Gemini API call failed: {resp.status_code} - {resp.text}")
                    # Use built-in mock service as fallback
                    return ScoutAnalysisService.generate_mock_analysis(text_content)
                  # Parse response result from Gemini API
                result = resp.json()
                current_app.logger.warning(f"[DEBUG] API response: {result}")
                
                # Extract content from Gemini API format
                # Gemini returns content in candidates[0].content.parts[0].text
                content = ""
                candidates = result.get("candidates", [])
                if candidates and len(candidates) > 0:
                    candidate = candidates[0]
                    if "content" in candidate and "parts" in candidate["content"] and len(candidate["content"]["parts"]) > 0:
                        content = candidate["content"]["parts"][0].get("text", "")
                
                current_app.logger.warning(f"[DEBUG] Analysis content: {content}")
                
                # Try to parse as JSON
                try:
                    # Clean content (remove potential ```json and ``` markers)
                    content = content.replace("```json", "").replace("```", "").strip()
                    analysis_result = json.loads(content)
                    current_app.logger.warning(f"[DEBUG] Parsed JSON: {analysis_result}")
                except Exception as e:
                    current_app.logger.error(f"JSON parsing failed: {str(e)}")
                    # If JSON parsing fails, use raw content as summary
                    analysis_result = {"summary": content}
                
                return analysis_result
                
            except Exception as e:
                current_app.logger.error(f"API request failed: {str(e)}")
                return ScoutAnalysisService.generate_mock_analysis(text_content)
                
        except Exception as e:
            current_app.logger.error(f"Error during API call process: {str(e)}")
            # Use built-in mock data on error
            return ScoutAnalysisService.generate_mock_analysis(text_content)
    
    @staticmethod
    def generate_mock_analysis(text_content):
        """Generate mock scout report analysis data"""
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
        strengths = ["Excellent court vision", "High basketball IQ", "Strong offensive skills"]
        weaknesses = ["Needs improvement on defense", "Inconsistent three-point shooting"]
        development_areas = ["Focus on defensive positioning", "Develop leadership skills"]
        
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
        summary = f"Based on the provided text, {name} appears to be a talented basketball player with significant potential. "
        summary += "The player shows strong offensive capabilities and court awareness. "
        summary += "Further development in defensive positioning and consistency would elevate their game to the next level."
        
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
