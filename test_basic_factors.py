# /Applications/tradingagent/test_basic_factors.py
"""
�������Ӳ��Խű� - ������ʼ������Ч����
ʹ������tushare token: b34d8920b99b43d48df7e792a4708a29f868feeee30d9c84b54bf065
"""

import sys
import os
sys.path.append('/Applications/tradingagent')

import pandas as pd
import numpy as np
import tushare as ts
import warnings
warnings.filterwarnings('ignore')

# ����tushare token
TUSHARE_TOKEN = "b34d8920b99b43d48df7e792a4708a29f868feeee30d9c84b54bf065"

class BasicFactorTester:
    """
    �������Ӳ����� - �������а汾
    """
    
    def __init__(self, tushare_token: str = TUSHARE_TOKEN):
        self.ts_pro = ts.pro_api(tushare_token)
        print(f"? Tushare API ��ʼ���ɹ�")
    
    def get_stock_data(self, stock_code: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        ��ȡ��Ʊ����
        """
        if start_date is None:
            start_date = (pd.Timestamp.now() - pd.Timedelta(days=365)).strftime('%Y%m%d')
        if end_date is None:
            end_date = pd.Timestamp.now().strftime('%Y%m%d')
        
        try:
            print(f"? ���ڻ�ȡ {stock_code} ������...")
            data = self.ts_pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
            
            if data.empty:
                print(f"? �޷���ȡ {stock_code} ������")
                return pd.DataFrame()
            
            data['trade_date'] = pd.to_datetime(data['trade_date'])
            data = data.set_index('trade_date').sort_index()
            
            # ��׼������
            data.columns = [col.lower() for col in data.columns]
            
            print(f"? �ɹ���ȡ {len(data)} �������յ�����")
            print(f"? ���ݷ�Χ: {data.index[0].strftime('%Y-%m-%d')} �� {data.index[-1].strftime('%Y-%m-%d')}")
            
            return data
            
        except Exception as e:
            print(f"? ���ݻ�ȡʧ��: {e}")
            return pd.DataFrame()
    
    def generate_basic_factors(self, stock_data: pd.DataFrame) -> pd.DataFrame:
        """
        ���ɻ�����������
        """
        print(f"? �������ɻ�������...")
        
        factors = pd.DataFrame(index=stock_data.index)
        
        # �۸�ͳɽ�������
        price = stock_data['close']
        volume = stock_data.get('vol', pd.Series(index=stock_data.index))
        high = stock_data.get('high', price)
        low = stock_data.get('low', price)
        open_price = stock_data.get('open', price)
        
        try:
            # === �������� ===
            print("  ? ���ɶ�������...")
            factors['momentum_5'] = price.pct_change(5)      # 5�ն���
            factors['momentum_20'] = price.pct_change(20)    # 20�ն���
            factors['momentum_60'] = price.pct_change(60)    # 60�ն���
            
            # ���յ�������
            returns = price.pct_change()
            vol_20 = returns.rolling(20).std()
            factors['momentum_risk_adj'] = factors['momentum_20'] / vol_20
            
            # === ��ת���� ===
            print("  ? ���ɷ�ת����...")
            factors['reversal_1'] = -price.pct_change(1)    # ���ڷ�ת
            factors['reversal_5'] = -price.pct_change(5)    # ���ڷ�ת
            
            # === ���������� ===
            print("  ? ���ɲ���������...")
            factors['volatility_20'] = vol_20               # 20�ղ�����
            factors['volatility_60'] = returns.rolling(60).std()  # 60�ղ�����
            factors['volatility_ratio'] = factors['volatility_20'] / factors['volatility_60']
            
            # === �ɽ������� ===
            if not volume.isna().all():
                print("  ? ���ɳɽ�������...")
                factors['volume_ratio'] = volume / volume.rolling(20).mean()
                factors['volume_price_corr'] = returns.rolling(20).corr(volume.pct_change())
                
                # �ɽ�������
                vol_ma = volume.rolling(20).mean()
                vol_std = volume.rolling(20).std()
                factors['volume_surge'] = (volume - vol_ma) / vol_std
            
            # === �۸���̬���� ===
            print("  ? ���ɼ۸���̬����...")
            factors['high_low_ratio'] = (high - low) / price
            factors['gap_ratio'] = (open_price - price.shift(1)) / price.shift(1)
            
            # === �߼����� ===
            print("  ? ���ɸ߼�����...")
            # �۸�λ��
            price_min_20 = price.rolling(20).min()
            price_max_20 = price.rolling(20).max()
            factors['price_position'] = (price - price_min_20) / (price_max_20 - price_min_20)
            
            # ����ǿ��
            factors['momentum_strength'] = returns.rolling(10).sum() / returns.rolling(10).std()
            
            # ��������
            factors = factors.replace([np.inf, -np.inf], np.nan)
            factors = factors.dropna()
            
            print(f"? �ɹ����� {len(factors.columns)} �����ӣ���Ч���� {len(factors)} ��")
            
            return factors
            
        except Exception as e:
            print(f"? ��������ʧ��: {e}")
            return pd.DataFrame()
    
    def test_factor_effectiveness(self, factors: pd.DataFrame, stock_data: pd.DataFrame, 
                                forward_days: int = 10) -> dict:
        """
        ����������Ч��
        """
        print(f"? ���ڲ���������Ч�� (ǰհ{forward_days}��������)...")
        
        if factors.empty:
            return {"error": "��������Ϊ��"}
        
        price = stock_data['close']
        returns = price.pct_change()
        forward_returns = returns.shift(-forward_days)
        
        results = {}
        
        for i, factor_name in enumerate(factors.columns, 1):
            print(f"  �������� {i}/{len(factors.columns)}: {factor_name}")
            
            factor_values = factors[factor_name].dropna()
            
            if len(factor_values) < 50:
                print(f"    ?? ���ݵ㲻��: {len(factor_values)}")
                continue
            
            # ��������
            aligned_data = pd.concat([factor_values, forward_returns], axis=1).dropna()
            
            if len(aligned_data) < 30:
                print(f"    ?? ��������ݲ���: {len(aligned_data)}")
                continue
            
            factor_col = aligned_data.iloc[:, 0]
            return_col = aligned_data.iloc[:, 1]
            
            # ����ICָ��
            ic = factor_col.corr(return_col)
            rank_ic = factor_col.rank().corr(return_col.rank())
            
            # �������
            try:
                quantiles = pd.qcut(factor_col, q=5, labels=False, duplicates='drop')
                group_returns = pd.DataFrame({
                    'factor_group': quantiles,
                    'returns': return_col
                }).groupby('factor_group')['returns'].mean()
                
                # ������
                if len(group_returns) >= 3:
                    diffs = group_returns.diff().dropna()
                    if len(diffs) > 0:
                        positive_diffs = (diffs > 0).sum()
                        negative_diffs = (diffs < 0).sum()
                        monotonicity = max(positive_diffs, negative_diffs) / len(diffs)
                    else:
                        monotonicity = 0.5
                else:
                    monotonicity = 0.5
                
                spread = group_returns.max() - group_returns.min()
                
            except Exception as e:
                print(f"    ?? �������ʧ��: {e}")
                monotonicity = 0.5
                spread = 0
            
            # �ȶ��Է���
            stability = self._calculate_stability(factor_col, return_col)
            
            # �ۺ�����
            ic_score = abs(ic) * 0.4
            monotonicity_score = monotonicity * 0.3
            spread_score = min(abs(spread) * 100, 1.0) * 0.2
            stability_score = stability * 0.1
            
            final_score = ic_score + monotonicity_score + spread_score + stability_score
            
            results[factor_name] = {
                'IC': ic,
                'Rank_IC': rank_ic,
                'IC_abs': abs(ic),
                'monotonicity': monotonicity,
                'spread': spread,
                'stability': stability,
                'sample_size': len(aligned_data),
                'final_score': final_score
            }
            
            # ʵʱ��ʾ���
            if abs(ic) > 0.03:  # ������IC
                print(f"    ? IC: {ic:.4f}, ����: {final_score:.4f}")
            else:
                print(f"    ? IC: {ic:.4f}, ����: {final_score:.4f}")
        
        # ����������
        sorted_results = dict(sorted(results.items(), key=lambda x: x[1]['final_score'], reverse=True))
        
        print(f"? ������Ч�Բ�����ɣ������� {len(results)} ������")
        
        return sorted_results
    
    def _calculate_stability(self, factor_values: pd.Series, returns: pd.Series, window: int = 60) -> float:
        """
        ���������ȶ���
        """
        try:
            rolling_ic = []
            for i in range(window, len(factor_values)):
                window_factor = factor_values.iloc[i-window:i]
                window_returns = returns.iloc[i-window:i]
                ic = window_factor.corr(window_returns)
                if not np.isnan(ic):
                    rolling_ic.append(ic)
            
            if len(rolling_ic) > 5:
                ic_mean = np.mean(rolling_ic)
                ic_std = np.std(rolling_ic)
                stability = 1 - ic_std / (abs(ic_mean) + 0.001)
                return max(0, min(1, stability))
            else:
                return 0.5
        except:
            return 0.5
    
    def run_complete_test(self, stock_code: str, start_date: str = None, end_date: str = None):
        """
        �������������Ӳ�������
        """
        print(f"? ��ʼ�� {stock_code} �����������Ӳ���")
        print("="*60)
        
        # 1. ��ȡ����
        stock_data = self.get_stock_data(stock_code, start_date, end_date)
        if stock_data.empty:
            print("? ����ʧ�ܣ��޷���ȡ��Ʊ����")
            return
        
        # 2. ��������
        factors = self.generate_basic_factors(stock_data)
        if factors.empty:
            print("? ����ʧ�ܣ��޷���������")
            return
        
        # 3. ����������Ч��
        factor_results = self.test_factor_effectiveness(factors, stock_data)
        if not factor_results or 'error' in factor_results:
            print("? ����ʧ�ܣ�������Ч�Բ���ʧ��")
            return
        
        # 4. ���ɼ򻯱���
        print(f"""
? {stock_code} ���Ӳ��Խ��
==============================

? ���ݸſ�:
- ���ݷ�Χ: {stock_data.index[0].strftime('%Y-%m-%d')} �� {stock_data.index[-1].strftime('%Y-%m-%d')}
- ����������: {len(stock_data)} ��
- ������������: {len(factors.columns)} ��
- ��Ч��������: {len(factor_results)} ��

? Top 5 ����Ч����:""")
        
        if factor_results:
            for i, (factor_name, metrics) in enumerate(list(factor_results.items())[:5], 1):
                ic = metrics['IC']
                final_score = metrics['final_score']
                
                # ����
                if abs(ic) > 0.05:
                    grade = "? ����"
                elif abs(ic) > 0.03:
                    grade = "? ����"
                elif abs(ic) > 0.01:
                    grade = "? һ��"
                else:
                    grade = "? �ϲ�"
                
                print(f"""{i}. {factor_name} {grade}
   - ICϵ��: {ic:.4f}
   - Rank IC: {metrics['Rank_IC']:.4f}
   - ������: {metrics['monotonicity']:.3f}
   - �ȶ���: {metrics['stability']:.3f}
   - �ۺ�����: {final_score:.4f}
""")
            
            # Ͷ�ʽ���
            top_factor = list(factor_results.keys())[0]
            top_ic = factor_results[top_factor]['IC']
            
            print("? Ͷ�ʽ���:")
            if abs(top_ic) > 0.05:
                suggestion = "? ǿ���Ƽ�ʹ�ö�����ѡ�ɲ���"
            elif abs(top_ic) > 0.03:
                suggestion = "? �Ƽ�ʹ������ѡ�ɣ�ע����տ���"
            elif abs(top_ic) > 0.01:
                suggestion = "?? ����Ч��һ�㣬������������������"
            else:
                suggestion = "? ����Ч���ϲ�����鵥��ʹ��"
            
            print(f"""{suggestion}

? �Ƽ�����:
- ��������: {top_factor} (IC: {top_ic:.4f})
- ����ʹ�ö�������϶��ǵ�һ����
- ����(3-6����)��������������Ч��

==============================
�������ʱ��: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
==============================""")
        
        return {
            'stock_data': stock_data,
            'factors': factors,
            'factor_results': factor_results
        }


def main():
    """
    ������ - ��ʾ���ʹ��
    """
    print("? �������Ӳ���ϵͳ����")
    print("ʹ������Tushare Token���в���")
    print("="*60)
    
    # ��ʼ��������
    tester = BasicFactorTester()
    
    # ���Թ�Ʊ�б� (�������޸�����)
    test_stocks = [
        "000001.SZ",  # ƽ������
        "000002.SZ",  # ���A  
        "600000.SH",  # �ַ�����
        "600036.SH",  # ��������
        "000858.SZ"   # ����Һ
    ]
    
    print(f"? ���Թ�Ʊ�б�: {test_stocks}")
    
    # ѡ��Ҫ���ԵĹ�Ʊ
    while True:
        print("\n" + "="*40)
        print("��ѡ��Ҫ���ԵĹ�Ʊ:")
        for i, stock in enumerate(test_stocks, 1):
            print(f"{i}. {stock}")
        print("0. �˳�")
        
        try:
            choice = input("\n������ѡ�� (0-5): ").strip()
            
            if choice == '0':
                print("? ���Խ���")
                break
            elif choice in ['1', '2', '3', '4', '5']:
                stock_code = test_stocks[int(choice) - 1]
                print(f"\n? ��ʼ���� {stock_code}")
                
                # ������������
                results = tester.run_complete_test(stock_code)
                
                if results:
                    print(f"\n? {stock_code} �������!")
                    
                    # ѯ���Ƿ����
                    continue_test = input("\n�Ƿ��������������Ʊ? (y/n): ").strip().lower()
                    if continue_test != 'y':
                        print("? ���Խ���")
                        break
                else:
                    print(f"\n? {stock_code} ����ʧ��")
                    
            else:
                print("?? ��Чѡ������������")
                
        except KeyboardInterrupt:
            print("\n\n? �û�ȡ�������Խ���")
            break
        except Exception as e:
            print(f"\n? ���Թ����г��ִ���: {e}")
            continue


if __name__ == "__main__":
    main()