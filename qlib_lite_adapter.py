
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
