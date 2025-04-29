def fix_file():
    """Fix indentation in the file"""
    with open("app/scout_analysis/services.py", "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Fix the specific lines
    if len(lines) >= 55:
        lines[51] = "            gemini = current_app.config.get('GEMINI_INSTANCE')\n"
        lines[52] = "            if not gemini:\n"
        lines[53] = "                current_app.logger.error(\"Gemini API instance not found in app.config! Cannot proceed with analysis.\")\n"
        lines[54] = "                return ScoutAnalysisService.generate_error_analysis(\"Gemini API instance not initialized\")\n"
    
    with open("app/scout_analysis/services.py", "w", encoding="utf-8") as f:
        f.writelines(lines)
    
    print("File fixed successfully!")

if __name__ == "__main__":
    fix_file() 