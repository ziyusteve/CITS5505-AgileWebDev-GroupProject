from app import create_app
from app.scout_analysis.services import ScoutAnalysisService
import json

app = create_app()

def test_scout_analysis_api():
    print("测试球探分析API连接...")
    # 测试文本
    test_text = "测试DeepSeek API连接。这是一个NBA球员：Lebron James，他是一位全明星球员。"
    
    with app.app_context():
        try:
            # 获取API密钥信息
            api_key = app.config.get('DEEPSEEK_API_KEY')
            print(f"API密钥: {api_key[:5]}...{api_key[-5:]}")
            print(f"球探分析开启状态: {app.config.get('ENABLE_SCOUT_ANALYSIS', False)}")
            
            # 调用分析服务
            result = ScoutAnalysisService.analyze_report(test_text)
            
            # 输出结果
            print("\n分析结果:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return True
        except Exception as e:
            print(f"测试失败: {e}")
            return False

if __name__ == "__main__":
    success = test_scout_analysis_api()
    print(f"\n测试结果: {'成功' if success else '失败'}") 