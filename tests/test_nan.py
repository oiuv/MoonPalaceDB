#!/usr/bin/env python3
"""
测试NaN值处理
"""
import json
import math
import pandas as pd
import numpy as np

def clean_data_for_json(data):
    """清理数据中的NaN和无限值，使其可JSON序列化"""
    if isinstance(data, list):
        return [clean_data_for_json(item) for item in data]
    elif isinstance(data, dict):
        return {key: clean_data_for_json(value) for key, value in data.items()}
    elif isinstance(data, float):
        if math.isnan(data):
            return None
        elif math.isinf(data):
            return str(data)
        else:
            return data
    elif isinstance(data, (pd.Timestamp)):
        return str(data)
    elif data is None:
        return None
    else:
        return data

# 测试数据
test_data = [
    {'name': 'test1', 'value': 1.0, 'nan_value': float('nan')},
    {'name': 'test2', 'value': float('inf'), 'nan_value': None},
    {'name': 'test3', 'value': 3.14, 'nan_value': -float('inf')},
]

print("原始数据:")
print(test_data)

print("\n清理后的数据:")
cleaned = clean_data_for_json(test_data)
print(cleaned)

print("\nJSON序列化测试:")
try:
    json_str = json.dumps(cleaned, ensure_ascii=False, indent=2)
    print("成功序列化:")
    print(json_str)
except Exception as e:
    print(f"序列化失败: {e}")

# 测试pandas数据
print("\n测试pandas数据:")
df = pd.DataFrame({
    'col1': [1, 2, np.nan],
    'col2': [np.inf, -np.inf, 3.14],
    'col3': ['a', 'b', 'c']
})

print("原始DataFrame:")
print(df.to_dict('records'))

pandas_cleaned = clean_data_for_json(df.to_dict('records'))
print("\n清理后的数据:")
print(pandas_cleaned)

print("\nJSON序列化测试:")
try:
    json_str = json.dumps(pandas_cleaned, ensure_ascii=False, indent=2)
    print("成功序列化")
except Exception as e:
    print(f"序列化失败: {e}")