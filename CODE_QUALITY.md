# 代码质量指南

本项目使用以下工具来保证代码质量：

## 安装开发依赖

```bash
pip install -r dev-requirements.txt
```

## 代码格式化工具

### Black

运行以下命令格式化代码：

```bash
black app/
```

### Flake8

运行以下命令检查代码风格：

```bash
flake8 app/
```

## 预提交钩子

本项目使用 pre-commit 来自动运行格式化和代码检查。

安装预提交钩子：

```bash
pre-commit install
```

预提交钩子将在每次提交代码前自动运行，确保代码符合规范。

## 代码文档规范

请遵循以下文档规范：

1. 为所有函数和类添加符合 PEP 257 的文档字符串
2. 文档应包含：
   - 功能描述
   - 参数说明
   - 返回值说明
   - 异常说明（如适用）

例如：

```python
def calculate_average(numbers):
    """
    计算数字列表的平均值。

    Args:
        numbers (list): 数字列表

    Returns:
        float: 平均值

    Raises:
        ValueError: 如果列表为空
    """
    if not numbers:
        raise ValueError("数字列表不能为空")
    return sum(numbers) / len(numbers)
```
