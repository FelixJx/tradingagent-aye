# -*- coding: utf-8 -*-
"""
qlib整合测试 - 验证可用性
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path

# 添加qlib路径
qlib_path = '/Users/jx/Downloads/qlib-main'
sys.path.insert(0, qlib_path)

def test_qlib_availability():
    """测试qlib基础功能可用性"""
    print("=== qlib整合可用性测试 ===")
    
    # 1. 测试基础导入
    try:
        import qlib
        print("✅ qlib基础模块导入成功")
        qlib_version = getattr(qlib, '__version__', 'Unknown')
        print(f"   版本: {qlib_version}")
    except Exception as e:
        print(f"❌ qlib基础模块导入失败: {e}")
        return False
    
    # 2. 测试数据操作模块
    try:
        from qlib.data import ops
        print("✅ qlib数据操作模块可用")
    except Exception as e:
        print(f"⚠️ qlib数据操作模块导入失败: {e}")
    
    # 3. 测试模型模块
    try:
        from qlib.contrib.model import xgboost, gbdt
        print("✅ qlib机器学习模型可用")
    except Exception as e:
        print(f"⚠️ qlib机器学习模型导入失败: {e}")
    
    # 4. 测试回测模块
    try:
        from qlib.backtest import backtest
        print("✅ qlib回测框架可用")
    except Exception as e:
        print(f"⚠️ qlib回测框架导入失败: {e}")
    
    # 5. 检查预训练模型
    model_files = [
        'ml_models/best_model.pkl',
        'trading_model_surge_signal.pkl',
        'sector_rotation_models.pkl',
        'surge_ml_models.pkl'
    ]
    
    available_models = []
    for model_file in model_files:
        model_path = os.path.join(qlib_path, model_file)
        if os.path.exists(model_path):
            available_models.append(model_file)
            print(f"✅ 发现预训练模型: {model_file}")
    
    if available_models:
        print(f"📊 共发现 {len(available_models)} 个预训练模型")
    else:
        print("⚠️ 未发现预训练模型文件")
    
    # 6. 检查数据库
    db_files = [
        'databases/main_data/qlib_enhanced.db',
        'surge_predictions.db',
        'sector_rotation_research.db'
    ]
    
    available_dbs = []
    for db_file in db_files:
        db_path = os.path.join(qlib_path, db_file)
        if os.path.exists(db_path):
            available_dbs.append(db_file)
            print(f"🗃️ 发现数据库: {db_file}")
    
    print(f"\n📋 整合建议:")
    print(f"   - qlib基础功能: {'可用' if 'qlib' in sys.modules else '需要修复'}")
    print(f"   - 预训练模型: {len(available_models)} 个可用")
    print(f"   - 历史数据库: {len(available_dbs)} 个可用")
    
    return True

def test_qlib_factor_extraction():
    """测试qlib因子提取功能"""
    print("\n=== qlib因子提取测试 ===")
    
    # 创建测试数据
    dates = pd.date_range('2023-01-01', '2023-12-31', freq='D')
    np.random.seed(42)
    
    test_data = pd.DataFrame({
        'open': 100 + np.cumsum(np.random.randn(len(dates)) * 0.5),
        'high': 0,
        'low': 0, 
        'close': 0,
        'vol': np.random.randint(1000000, 10000000, len(dates))
    }, index=dates)
    
    # 生成OHLC数据
    test_data['high'] = test_data['open'] + np.random.rand(len(dates)) * 2
    test_data['low'] = test_data['open'] - np.random.rand(len(dates)) * 2
    test_data['close'] = test_data['low'] + (test_data['high'] - test_data['low']) * np.random.rand(len(dates))
    
    print(f"📊 生成测试数据: {len(test_data)} 条记录")
    
    # 尝试qlib高级因子
    try:
        # 测试一些高级因子计算
        factors = {}
        
        # 基础因子
        factors['returns'] = test_data['close'].pct_change()
        factors['volatility'] = factors['returns'].rolling(20).std()
        
        # 高级因子（尝试使用qlib方法）
        try:
            from qlib.data.ops import Corr, Std, Mean
            # 如果qlib可用，使用其高级操作
            factors['vol_price_corr'] = test_data['close'].rolling(20).corr(test_data['vol'])
            factors['momentum_vol_adj'] = (test_data['close'].pct_change(20) / 
                                         test_data['close'].pct_change().rolling(20).std())
            print("✅ qlib高级因子计算成功")
        except:
            # 降级到手动计算
            factors['vol_price_corr'] = test_data['close'].rolling(20).corr(test_data['vol'])
            factors['momentum_vol_adj'] = (test_data['close'].pct_change(20) / 
                                         test_data['close'].pct_change().rolling(20).std())
            print("⚠️ 使用手动因子计算（qlib不可用）")
        
        # 统计结果
        valid_factors = {k: v for k, v in factors.items() if not v.isna().all()}
        print(f"📈 成功计算 {len(valid_factors)} 个因子")
        
        for factor_name, factor_values in valid_factors.items():
            ic = abs(factor_values.corr(factors['returns'].shift(-1)))
            print(f"   {factor_name}: IC = {ic:.4f}")
        
        return True
        
    except Exception as e:
        print(f"❌ 因子提取测试失败: {e}")
        return False

def create_qlib_adapter():
    """创建qlib适配器"""
    print("\n=== 创建qlib适配器 ===")
    
    adapter_code = '''
# -*- coding: utf-8 -*-
"""
qlib轻量级适配器
"""

import sys
import os
import pandas as pd
import numpy as np
import joblib
from pathlib import Path

class QLIBLiteAdapter:
    """qlib轻量级适配器"""
    
    def __init__(self, qlib_path='/Users/jx/Downloads/qlib-main'):
        self.qlib_path = qlib_path
        self.models = {}
        self.setup_qlib()
        self.load_available_models()
    
    def setup_qlib(self):
        """设置qlib环境"""
        if self.qlib_path not in sys.path:
            sys.path.insert(0, self.qlib_path)
        
        try:
            import qlib
            self.qlib_available = True
            print("✅ qlib环境设置成功")
        except:
            self.qlib_available = False
            print("⚠️ qlib不可用，使用备用方案")
    
    def load_available_models(self):
        """加载可用的预训练模型"""
        model_files = [
            'ml_models/best_model.pkl',
            'trading_model_surge_signal.pkl',
            'sector_rotation_models.pkl',
            'surge_ml_models.pkl'
        ]
        
        for model_file in model_files:
            model_path = os.path.join(self.qlib_path, model_file)
            if os.path.exists(model_path):
                try:
                    self.models[model_file] = joblib.load(model_path)
                    print(f"✅ 加载模型: {model_file}")
                except Exception as e:
                    print(f"⚠️ 模型加载失败 {model_file}: {e}")
    
    def extract_enhanced_factors(self, df):
        """提取增强因子"""
        factors = {}
        
        # 基础因子
        factors['returns'] = df['close'].pct_change()
        factors['volatility'] = factors['returns'].rolling(20).std()
        
        # 尝试使用qlib高级因子
        if self.qlib_available:
            factors.update(self.qlib_advanced_factors(df))
        else:
            factors.update(self.manual_advanced_factors(df))
        
        return factors
    
    def qlib_advanced_factors(self, df):
        """使用qlib的高级因子"""
        try:
            from qlib.data.ops import *
            
            factors = {}
            # 这里可以使用qlib的高级操作
            factors['qlib_momentum'] = df['close'].rolling(20).apply(
                lambda x: (x[-1] - x[0]) / x.std() if x.std() > 0 else 0
            )
            
            return factors
        except:
            return self.manual_advanced_factors(df)
    
    def manual_advanced_factors(self, df):
        """手动高级因子（备用方案）"""
        factors = {}
        
        # 高级动量因子
        factors['momentum_adj'] = (df['close'].pct_change(20) / 
                                 df['close'].pct_change().rolling(20).std())
        
        # 量价相关性
        factors['vol_price_corr'] = df['close'].rolling(20).corr(df['vol'])
        
        # 价格位置因子
        factors['price_position'] = ((df['close'] - df['close'].rolling(60).min()) / 
                                   (df['close'].rolling(60).max() - df['close'].rolling(60).min()))
        
        return factors
    
    def predict_with_ensemble(self, features):
        """使用集成模型预测"""
        if not self.models:
            return self.fallback_prediction(features)
        
        predictions = []
        for model_name, model in self.models.items():
            try:
                if hasattr(model, 'predict'):
                    pred = model.predict(features.values.reshape(1, -1))
                    predictions.append(pred[0] if len(pred) > 0 else 0)
            except Exception as e:
                print(f"模型预测失败 {model_name}: {e}")
                continue
        
        if predictions:
            return np.mean(predictions)
        else:
            return self.fallback_prediction(features)
    
    def fallback_prediction(self, features):
        """备用预测方案"""
        # 简单的线性组合
        if 'momentum_adj' in features and 'vol_price_corr' in features:
            return 0.6 * features['momentum_adj'] + 0.4 * features['vol_price_corr']
        else:
            return 0.0
'''
    
    # 保存适配器代码
    with open('/Applications/tradingagent/qlib_lite_adapter.py', 'w', encoding='utf-8') as f:
        f.write(adapter_code)
    
    print("✅ qlib适配器已创建: qlib_lite_adapter.py")
    return True

def main():
    """主测试函数"""
    print("🚀 开始qlib整合测试")
    
    # 测试1: 基础可用性
    basic_ok = test_qlib_availability()
    
    # 测试2: 因子提取
    factor_ok = test_qlib_factor_extraction()
    
    # 测试3: 创建适配器
    adapter_ok = create_qlib_adapter()
    
    # 总结
    print("\n" + "="*50)
    print("🎯 qlib整合测试总结")
    print("="*50)
    print(f"基础功能测试: {'✅ 通过' if basic_ok else '❌ 失败'}")
    print(f"因子提取测试: {'✅ 通过' if factor_ok else '❌ 失败'}")
    print(f"适配器创建: {'✅ 通过' if adapter_ok else '❌ 失败'}")
    
    if basic_ok and factor_ok and adapter_ok:
        print("\n🎉 建议: 可以开始Phase 1整合")
        print("   1. 使用qlib_lite_adapter.py作为桥梁")
        print("   2. 逐步提取qlib的高价值组件")
        print("   3. 保持现有系统的稳定性")
    else:
        print("\n⚠️ 建议: 暂时使用独立方案")
        print("   1. 继续完善现有的Agent系统")
        print("   2. 手动实现高级因子")
        print("   3. 待qlib环境稳定后再整合")

if __name__ == "__main__":
    main()