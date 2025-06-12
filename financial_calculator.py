import numpy as np
import pandas as pd
from scipy.optimize import fsolve

class FinancialCalculator:
    def __init__(self, params, cost_data, sales_data):
        self.params = params
        self.cost_data = cost_data
        self.sales_data = sales_data
        self.total_years = params['business_period'] + params['construction_period']
        
        # Calculate unit price and costs from data
        self.unit_price = self._calculate_unit_price()
        self.material_cost_per_unit = self._calculate_material_cost_per_unit()
        self.processing_cost_per_unit = self._calculate_processing_cost_per_unit()
    
    def _calculate_unit_price(self):
        """단위당판매가격 = 판매실적 시트에서 매출액의 합계 / 판매량의 합계"""
        # Use the correct column names from the uploaded Excel file
        if '총 매출액' in self.sales_data.columns and '판매량' in self.sales_data.columns:
            total_sales = self.sales_data['총 매출액'].sum()
            total_volume = self.sales_data['판매량'].sum()
        else:
            # Fallback to default column names
            total_sales = self.sales_data['매출액'].sum()
            total_volume = self.sales_data['판매량'].sum()
        return total_sales / total_volume if total_volume > 0 else 0
    
    def _calculate_material_cost_per_unit(self):
        """소재가격 평균"""
        return self.cost_data['소재가격'].mean()
    
    def _calculate_processing_cost_per_unit(self):
        """가공비 평균"""
        return self.cost_data['가공비'].mean()
    
    def get_sales_volume(self, year):
        """연도별 판매량 계산"""
        if year <= self.params['construction_period']:
            return 0
        elif year == self.params['construction_period'] + 1:  # Year 5
            return self.params['sales_volumes'].get(5, 0)
        elif year == self.params['construction_period'] + 2:  # Year 6
            return self.params['sales_volumes'].get(6, 0)
        else:  # Year 7 이후
            return self.params['sales_volumes'].get('after_7', 0)
    
    def calculate_total_revenue(self, year):
        """총매출액 = 단위당판매가격 * 판매량"""
        sales_volume = self.get_sales_volume(year)
        return self.unit_price * sales_volume
    
    def calculate_material_cost(self, year):
        """소재가격 = 원가실적 시트에서 소재가격의 평균 * 판매량"""
        sales_volume = self.get_sales_volume(year)
        return self.material_cost_per_unit * sales_volume
    
    def calculate_processing_cost(self, year):
        """가공비 = 원가실적 시트에서 가공비의 평균 * 판매량"""
        sales_volume = self.get_sales_volume(year)
        return self.processing_cost_per_unit * sales_volume
    
    def calculate_machinery_depreciation(self, year):
        """기계설비 = 총투자비 * 기계설비투자비비율 / 15, Year(공사기간+1)부터 반영"""
        if year <= self.params['construction_period']:
            return 0
        machinery_investment = self.params['total_investment'] * self.params['machinery_ratio']
        return machinery_investment / self.params['machinery_depreciation_years']
    
    def calculate_building_depreciation(self, year):
        """건축물 = 총투자비 * 건축물투자비비율 / 20, Year(공사기간+1)부터 반영"""
        if year <= self.params['construction_period']:
            return 0
        building_investment = self.params['total_investment'] * self.params['building_ratio']
        return building_investment / self.params['building_depreciation_years']
    
    def calculate_depreciation(self, year):
        """감가상각 = 감가상각기계설비 + 감가상각건축물"""
        return self.calculate_machinery_depreciation(year) + self.calculate_building_depreciation(year)
    
    def calculate_manufacturing_cost(self, year):
        """제조원가 = 소재가격 + 가공비 + 감가상각"""
        material_cost = self.calculate_material_cost(year)
        processing_cost = self.calculate_processing_cost(year)
        depreciation = self.calculate_depreciation(year)
        return material_cost + processing_cost + depreciation
    
    def calculate_investment(self, year):
        """투자비 = 총투자비 * 투자비집행YearX, 투자비집행YearX가 없으면 0으로 적용"""
        execution_ratio = self.params['investment_execution'].get(year, 0)
        return self.params['total_investment'] * execution_ratio
    
    def calculate_equity(self, year):
        """자본 = 투자비 * 자본비율"""
        investment = self.calculate_investment(year)
        return investment * self.params['equity_ratio']
    
    def calculate_debt_borrowing(self, year):
        """차입 = 투자비 * 차입비율, Year (장기차입 거치기간 + 1) 부터는 0으로 적용"""
        if year > self.params['loan_grace_period']:
            return 0
        investment = self.calculate_investment(year)
        return investment * self.params['debt_ratio']
    
    def calculate_debt_increase(self, year):
        """장기차입증가 = 차입"""
        return self.calculate_debt_borrowing(year)
    
    def calculate_debt_decrease(self, year):
        """장기차입감소 = (총투자비 * 차입비율)을 (Year (장기차입 거치기간 + 1)) 부터 (장기차입 상환기간)동안 정액 균등"""
        start_year = self.params['loan_grace_period'] + 1
        end_year = start_year + self.params['loan_repayment_period'] - 1
        
        if year < start_year or year > end_year:
            return 0
        
        total_debt = self.params['total_investment'] * self.params['debt_ratio']
        return total_debt / self.params['loan_repayment_period']
    
    def calculate_debt_balance(self, year, debt_balances):
        """기말잔액 = 기초잔액 + (장기차입 증가) - (장기차입 감소)"""
        if year == 1:
            beginning_balance = 0
        else:
            beginning_balance = debt_balances.get(year - 1, 0)
        
        debt_increase = self.calculate_debt_increase(year)
        debt_decrease = self.calculate_debt_decrease(year)
        
        return beginning_balance + debt_increase - debt_decrease
    
    def calculate_financial_cost(self, year, debt_balances):
        """금융비용 = 기말잔액 * 장기차입금리"""
        debt_balance = debt_balances.get(year, 0)
        return debt_balance * self.params['loan_interest_rate']
    
    def calculate_receivables(self, year):
        """매출채권 = 총매출액/365 * 매출채권일수, 총 매출액이 없는 경우 0으로 적용"""
        total_revenue = self.calculate_total_revenue(year)
        if total_revenue == 0:
            return 0
        return total_revenue / 365 * self.params['working_capital_days']['receivables']
    
    def calculate_payables(self, year):
        """매입채무 = 소재가격/365 * 매입채무일수, 소재가격이 없는 경우 0으로 적용"""
        material_cost = self.calculate_material_cost(year)
        if material_cost == 0:
            return 0
        return material_cost / 365 * self.params['working_capital_days']['payables']
    
    def calculate_product_inventory(self, year):
        """제품재고 = 총매출액 * 제품재고일수 / 365, 총매출액이 없는 경우 0으로 적용"""
        total_revenue = self.calculate_total_revenue(year)
        if total_revenue == 0:
            return 0
        return total_revenue * self.params['working_capital_days']['product_inventory'] / 365
    
    def calculate_material_inventory(self, year):
        """소재재고 = 소재가격 * 소재재고일수 / 365, 소재가격이 없는 경우 0으로 적용"""
        material_cost = self.calculate_material_cost(year)
        if material_cost == 0:
            return 0
        return material_cost * self.params['working_capital_days']['material_inventory'] / 365
    
    def calculate_inventory(self, year):
        """재고자산 = 제품재고 + 소재재고"""
        return self.calculate_product_inventory(year) + self.calculate_material_inventory(year)
    
    def calculate_working_capital(self, year):
        """운전자금 = 매출채권 - 매입채무 + 재고자산"""
        receivables = self.calculate_receivables(year)
        payables = self.calculate_payables(year)
        inventory = self.calculate_inventory(year)
        return receivables - payables + inventory
    
    def calculate_working_capital_increase(self, year, working_capitals):
        """운전자금증가분 = Year(공사기간+1) 부터, (YearX 운전자금) - (Year (X-1) 운전자금), Year 1부터 Year (공사기간) 까지는 0"""
        # Year 1부터 Year (공사기간) 까지는 0
        if year <= self.params['construction_period']:
            return 0
        
        # Year(공사기간+1) 부터 계산: (YearX 운전자금) - (Year (X-1) 운전자금)
        current_wc = working_capitals.get(year, 0)
        previous_wc = working_capitals.get(year - 1, 0)
        increase = current_wc - previous_wc
        
        return increase
    
    def calculate_sales_admin_expense(self, year):
        """판매관리비 = 총매출액 * 판매관리비비율, 총매출액이 없는 경우 0으로 적용"""
        total_revenue = self.calculate_total_revenue(year)
        if total_revenue == 0:
            return 0
        return total_revenue * self.params['sales_admin_ratio']
    
    def calculate_ebit(self, year):
        """EBIT = 손익계산 매출액 - 손익계산 제조원가 - 손익계산 판매관리비"""
        revenue = self.calculate_total_revenue(year)
        manufacturing_cost = self.calculate_manufacturing_cost(year)
        sales_admin = self.calculate_sales_admin_expense(year)
        return revenue - manufacturing_cost - sales_admin
    
    def calculate_pretax_income(self, year, financial_costs):
        """세전이익 = EBIT - (손익계산 금융비용)"""
        ebit = self.calculate_ebit(year)
        financial_cost = financial_costs.get(year, 0)
        return ebit - financial_cost
    
    def calculate_corporate_tax(self, pretax_income):
        """법인세 = 세전이익 * 법인세율, 세전이익<=0 인 경우 0으로 적용"""
        if pretax_income <= 0:
            return 0
        return pretax_income * self.params['corporate_tax_rate']
    
    def calculate_net_income(self, pretax_income, corporate_tax):
        """순이익 = 세전이익 - 법인세"""
        return pretax_income - corporate_tax
    
    def calculate_residual_value(self, year, total_depreciation):
        """잔존가치 = Year1부터 Year(사업기간+공사기간-1)은 0, Year(사업기간+공사기간)에 총 투자비 - (Year(공사기간+1) 부터 Year(사업기간+공사기간) 까지의 감가상각 합)"""
        if year < self.total_years:
            return 0
        return self.params['total_investment'] - total_depreciation
    
    def calculate_working_capital_inflow(self, year, working_capitals):
        """운전자금유입 = Year1부터 Year(사업기간+공사기간-1)은 0, Year (사업기간+공사기간)의 운전자금"""
        if year < self.total_years:
            return 0
        return working_capitals.get(year, 0)
    
    def calculate_cash_inflow(self, year, net_income, financial_cost, depreciation, residual_value, working_capital_inflow):
        """현금유입 = 순이익 + 금융비용 + 감가상각 + 잔존가치 + 운전자금유입"""
        return net_income + financial_cost + depreciation + residual_value + working_capital_inflow
    
    def calculate_cash_outflow(self, year, investment, working_capital_increase):
        """현금유출 = 투자비 + 운전자금유출
        운전자금유출 = 운전자금증가분"""
        working_capital_outflow = working_capital_increase
        return investment + working_capital_outflow
    
    def calculate_net_cash_flow(self, cash_inflow, cash_outflow):
        """NetCashFlow = 현금유입 - 현금유출"""
        return cash_inflow - cash_outflow
    
    def calculate_irr(self, net_cash_flows):
        """IRR = Year 1부터 Year (사업기간 + 공사기간) 동안의 Net Cash Flow의 NPV를 0으로 만드는 할인율"""
        cash_flows = [net_cash_flows.get(year, 0) for year in range(1, self.total_years + 1)]
        
        def npv(rate):
            return sum(cf / (1 + rate) ** i for i, cf in enumerate(cash_flows, 1))
        
        try:
            # Initial guess for IRR
            result = fsolve(npv, 0.1)
            if len(result) > 0:
                irr = float(result[0])
                # Validate IRR is reasonable (-100% to 500%)
                if -1.0 <= irr <= 5.0 and not (np.isnan(irr) or np.isinf(irr)):
                    return irr
            return 0.0
        except:
            return 0.0
    
    def calculate_all_metrics(self):
        """모든 재무지표 계산"""
        # Initialize results with proper typing
        results = {}
        
        # Initialize year-based dictionaries
        for key in ['total_revenue', 'manufacturing_cost', 'investment', 'depreciation', 
                   'working_capital', 'working_capital_increase', 'debt_balance', 'financial_cost',
                   'sales_admin_expense', 'ebit', 'pretax_income', 'corporate_tax', 'net_income',
                   'residual_value', 'working_capital_inflow', 'cash_inflow', 'cash_outflow', 'net_cash_flow']:
            results[key] = {}
        
        # Initialize scalar value
        results['irr'] = 0.0
        
        # First pass: calculate basic metrics
        for year in range(1, self.total_years + 1):
            results['total_revenue'][year] = self.calculate_total_revenue(year)
            results['manufacturing_cost'][year] = self.calculate_manufacturing_cost(year)
            results['investment'][year] = self.calculate_investment(year)
            results['depreciation'][year] = self.calculate_depreciation(year)
            results['working_capital'][year] = self.calculate_working_capital(year)
            results['sales_admin_expense'][year] = self.calculate_sales_admin_expense(year)
            results['ebit'][year] = self.calculate_ebit(year)
        
        # Second pass: calculate debt balances and financial costs
        for year in range(1, self.total_years + 1):
            results['debt_balance'][year] = self.calculate_debt_balance(year, results['debt_balance'])
            results['financial_cost'][year] = self.calculate_financial_cost(year, results['debt_balance'])
        
        # Third pass: calculate working capital increases
        for year in range(1, self.total_years + 1):
            results['working_capital_increase'][year] = self.calculate_working_capital_increase(year, results['working_capital'])
        
        # Fourth pass: calculate income statement items
        total_depreciation = 0
        for year in range(1, self.total_years + 1):
            results['pretax_income'][year] = self.calculate_pretax_income(year, results['financial_cost'])
            results['corporate_tax'][year] = self.calculate_corporate_tax(results['pretax_income'][year])
            results['net_income'][year] = self.calculate_net_income(results['pretax_income'][year], results['corporate_tax'][year])
            
            # Calculate cumulative depreciation for residual value
            if year > self.params['construction_period']:
                total_depreciation += results['depreciation'][year]
        
        # Fifth pass: calculate cash flows
        for year in range(1, self.total_years + 1):
            results['residual_value'][year] = self.calculate_residual_value(year, total_depreciation)
            results['working_capital_inflow'][year] = self.calculate_working_capital_inflow(year, results['working_capital'])
            
            results['cash_inflow'][year] = self.calculate_cash_inflow(
                year,
                results['net_income'][year],
                results['financial_cost'][year],
                results['depreciation'][year],
                results['residual_value'][year],
                results['working_capital_inflow'][year]
            )
            
            results['cash_outflow'][year] = self.calculate_cash_outflow(
                year,
                results['investment'][year],
                results['working_capital_increase'][year]
            )
            
            results['net_cash_flow'][year] = self.calculate_net_cash_flow(
                results['cash_inflow'][year],
                results['cash_outflow'][year]
            )
        
        # Calculate IRR
        results['irr'] = self.calculate_irr(results['net_cash_flow'])
        
        return results
