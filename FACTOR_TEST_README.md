# ? �������Ӳ���ϵͳʹ��ָ��

## ? ϵͳ����

����tradingagent��Ŀ�����Ѿ������˻������Ӳ���ϵͳ�����ԣ�
- ? ���ֹ�Ʊ����Чѡ������
- ? ����������δ�������ʵ������
- ? �ṩ��������Ͻ���
- ? ������֤������Ч��

## ? ���ٿ�ʼ

### ����1�������п��ٲ���
```bash
cd /Applications/tradingagent
python3 quick_factor_test.py
```

### ����2����������ϵͳ
```bash
cd /Applications/tradingagent
python3 test_basic_factors.py
```

### ����3��Python�������
```python
from test_basic_factors import BasicFactorTester

# ��ʼ��������
tester = BasicFactorTester()

# ���Ե�ֻ��Ʊ
results = tester.run_complete_test("000001.SZ")
```

## ? ���ɵ���������

### ��������
- `momentum_5`: 5�ռ۸���
- `momentum_20`: 20�ռ۸���  
- `momentum_60`: 60�ռ۸���
- `momentum_risk_adj`: ���յ�������

### ��ת����
- `reversal_1`: ���ڼ۸�ת
- `reversal_5`: ���ڼ۸�ת

### ����������
- `volatility_20`: 20����ʷ������
- `volatility_ratio`: �������ƶ��л�

### �ɽ�������
- `volume_ratio`: �ɽ�����ֵ
- `volume_price_corr`: ���������
- `volume_surge`: �ɽ�������

### �۸���̬����
- `high_low_ratio`: �����
- `gap_ratio`: ���ձ�
- `price_position`: �۸�λ��
- `momentum_strength`: ����ǿ��

## ? ����ָ��˵��

### IC (Information Coefficient)
- **����**: ����ֵ��δ�������ʵ����������
- **��׼**: |IC| > 0.03 Ϊ�����壬|IC| > 0.05 Ϊ����
- **����**: ICԽ������Ԥ������Խǿ

### Rank IC
- **����**: ��������������������������
- **����**: ���Ƚ������ܼ�ֵӰ��
- **��׼**: ��IC���ƣ������ɿ�

### ������ (Monotonicity)
- **����**: ���ӷ���������ʵĵ�������
- **��׼**: >0.6 Ϊ���õ�����
- **��Ҫ��**: ȷ�������߼�һ��

### �ȶ��� (Stability)
- **����**: �����ڲ�ͬʱ�ڵı���һ����
- **����**: 1 - IC��׼��/IC��ֵ
- **��׼**: >0.5 Ϊ�ȶ�

## ? ������

### ? �������� (|IC| > 0.05)
- ǿ���Ƽ�ʹ��
- ����Ϊ����ѡ������
- ������������

### ? �������� (0.03 < |IC| �� 0.05)
- �Ƽ�ʹ��
- ע����տ���
- �����������������

### ? һ������ (0.01 < |IC| �� 0.03)
- ����ʹ��
- �����ϻ��������
- ����Ϊ��������

### ? �ϲ����� (|IC| �� 0.01)
- �����鵥��ʹ��
- ���ܴ�����������
- �����������

## ? ʹ�ý���

### 1. ����ѡ�����
```python
# ѡ�����ʾ��
def select_factors(factor_results):
    selected = []
    
    # ��ѡ��IC > 0.05 ����������
    for factor, metrics in factor_results.items():
        if abs(metrics['IC']) > 0.05:
            selected.append(factor)
    
    # ��ѡ��IC > 0.03 ���ȶ��Ժõ�����
    for factor, metrics in factor_results.items():
        if 0.03 < abs(metrics['IC']) <= 0.05 and metrics['stability'] > 0.6:
            selected.append(factor)
    
    return selected[:8]  # ���8������
```

### 2. ���տ���
- **��ɢ��**: ʹ�ö�����������
- **���ڸ���**: ÿ3-6�������²���
- **ֹ������**: ����ʧЧʱ��ʱֹͣʹ��
- **��������֤**: ����������֤����Ч��

### 3. ʵ��Ӧ��
```python
# ����ѡ���ź�
def generate_signals(stock_data, selected_factors):
    signals = {}
    
    for factor_name in selected_factors:
        factor_value = calculate_factor(stock_data, factor_name)
        signals[factor_name] = factor_value
    
    # �ۺ��ź�
    composite_signal = sum(signals.values()) / len(signals)
    
    return composite_signal
```

## ?? ��Ҫ����

### ��������
- ȷ�����������Ժ�׼ȷ��
- ����ȱʧֵ���쳣ֵ
- ע�⸴Ȩ���ݵ�ʹ��

### ����˥��
- ������Ч�Ի���ʱ��˥��
- �г������仯Ӱ�����ӱ���
- ��Ҫ������غ͸���

### ���������
- ��ʷ��Ч����֤δ����Ч
- ����������������֤
- ���ú����Ԥ������

### ���չ���
- �����ӷ��գ��������������һ����
- �����ھ���գ�������������ʷ����
- �г����գ�ע���г������ı仯

## ?? ��չ����

### 1. ���������
```python
def add_custom_factor(stock_data):
    # �� generate_basic_factors �����������������
    custom_factor = your_calculation(stock_data)
    return custom_factor
```

### 2. �������Բ���
```python
# �޸�ǰհ��
forward_days = 20  # ��10�ո�Ϊ20��

# �޸���������
window = 40  # ��20�ո�Ϊ40��
```

### 3. ���ɵ�����ϵͳ
```python
# �����Ľ���ϵͳ�м���
from test_basic_factors import BasicFactorTester

class TradingSystem:
    def __init__(self):
        self.factor_tester = BasicFactorTester()
    
    def update_factors(self, stock_code):
        results = self.factor_tester.run_complete_test(stock_code)
        self.current_factors = results['factor_results']
```

## ? ����֧��

����������⣺
1. ����������Ӻ�tushareȨ��
2. ȷ�Ϲ�Ʊ�����ʽ��ȷ
3. ���Python�������Ƿ�����
4. �鿴������־��ȡ��ϸ��Ϣ

## ? ��һ���ж�

1. **��������**: ���п��ٲ�����֤ϵͳ����
2. **��������**: ������ע�Ĺ�Ʊ�ؽ�����������
3. **���Ӽ��**: �������ڵ�������Ч�Լ��
4. **���Լ���**: ����Ч���Ӽ��ɵ����Ľ��ײ�����

---
*ϵͳ����ʱ��: 2025-07-31*  
*Tokenʹ��: b34d8920b99b43d48df7e792a4708a29f868feeee30d9c84b54bf065*