from flask import current_app
import json

def analyze_sentiment(text):
    """
    分析文本情感
    
    Args:
        text (str): 需要分析的文本内容
        
    Returns:
        dict: 包含情感分析结果的字典
    """
    gemini = current_app.config.get('GEMINI_INSTANCE')
    if not gemini:
        return {"error": "Gemini API实例未初始化"}
    
    try:
        result = gemini.analyze_text(text)
        # 直接返回API结果，不使用硬编码默认值
        if isinstance(result, dict) and "error" in result:
            return result
        return result
    except Exception as e:
        current_app.logger.error(f"分析情感时出错: {str(e)}")
        return {"error": str(e)}

def extract_keywords(text):
    """
    从文本中提取关键词
    
    Args:
        text (str): 需要分析的文本内容
        
    Returns:
        dict: 包含关键词提取结果的字典
    """
    gemini = current_app.config.get('GEMINI_INSTANCE')
    if not gemini:
        return {"error": "Gemini API实例未初始化"}
    
    try:
        result = gemini.analyze_text(text)
        # 直接返回API结果，不使用硬编码默认值
        if isinstance(result, dict) and "error" in result:
            return result
        return result
    except Exception as e:
        current_app.logger.error(f"提取关键词时出错: {str(e)}")
        return {"error": str(e)}

def summarize_text(text, max_words=50):
    """
    对文本进行摘要
    
    Args:
        text (str): 需要摘要的文本内容
        max_words (int): 摘要的最大字数
        
    Returns:
        dict: 包含文本摘要结果的字典
    """
    gemini = current_app.config.get('GEMINI_INSTANCE')
    if not gemini:
        return {"error": "Gemini API实例未初始化"}
    
    try:
        # 在请求中加入max_words参数
        prompt = f"请将以下文本总结为不超过{max_words}个字的摘要:\n\n{text}"
        result = gemini.analyze_text(prompt)
        # 直接返回API结果，不使用硬编码默认值
        if isinstance(result, dict) and "error" in result:
            return result
        return result
    except Exception as e:
        current_app.logger.error(f"生成摘要时出错: {str(e)}")
        return {"error": str(e)}

def classify_text(text, categories=None):
    """
    对文本进行分类
    
    Args:
        text (str): 需要分类的文本内容
        categories (list): 可选的分类类别列表
        
    Returns:
        dict: 包含文本分类结果的字典
    """
    gemini = current_app.config.get('GEMINI_INSTANCE')
    if not gemini:
        return {"error": "Gemini API实例未初始化"}
    
    try:
        # 如果提供了类别，则在提示中包含这些类别
        prompt = text
        if categories:
            category_list = ", ".join(categories)
            prompt = f"请将以下文本分类为以下类别之一: {category_list}\n\n{text}"
        
        result = gemini.analyze_text(prompt)
        # 直接返回API结果，不使用硬编码默认值
        if isinstance(result, dict) and "error" in result:
            return result
        return result
    except Exception as e:
        current_app.logger.error(f"文本分类时出错: {str(e)}")
        return {"error": str(e)} 