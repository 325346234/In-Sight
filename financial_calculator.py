import numpy as np
import pandas as pd
from scipy.optimize import fsolve
import warnings
warnings.filterwarnings('ignore')

class FinancialCalculator:
    """
    Comprehensive financial calculator for investment analysis in steel industry projects.
    Provides NPV, IRR, payback period, and risk assessment calculations.
    """
    
    def __init__(self):
        self.precision = 1e-6
        self.max_iterations = 1000
    
    def calculate_npv(self, cash_flows, discount_rate, initial_investment):
        """
        Calculate Net Present Value (NPV) of an investment project.
        
        Args:
            cash_flows (list): Annual cash flows for each period
            discount_rate (float): Discount rate as decimal (e.g., 0.08 for 8%)
            initial_investment (float): Initial investment amount
            
        Returns:
            float: Net Present Value
        """
        if not cash_flows or discount_rate < 0:
            return 0.0
        
        try:
            npv = -initial_investment
            for i, cf in enumerate(cash_flows):
                npv += cf / ((1 + discount_rate) ** (i + 1))
            return npv
        except (ValueError, OverflowError):
            return 0.0
    
    def calculate_irr(self, cash_flows, initial_guess=0.1):
        """
        Calculate Internal Rate of Return (IRR) using iterative method.
        
        Args:
            cash_flows (list): Cash flows including initial investment as negative value
            initial_guess (float): Initial guess for IRR calculation
            
        Returns:
            float or None: IRR as decimal, None if calculation fails
        """
        if not cash_flows or len(cash_flows) < 2:
            return None
        
        try:
            def npv_function(rate):
                return sum(cf / ((1 + rate) ** i) for i, cf in enumerate(cash_flows))
            
            # Use scipy's fsolve for robust IRR calculation
            irr_solution = fsolve(npv_function, initial_guess, full_output=True)
            irr = irr_solution[0][0]
            
            # Validate the solution
            if abs(npv_function(irr)) < self.precision and -0.99 < irr < 10:
                return irr
            else:
                # Try alternative method if first attempt fails
                return self._calculate_irr_newton_raphson(cash_flows, initial_guess)
                
        except (ValueError, RuntimeError, OverflowError):
            return None
    
    def _calculate_irr_newton_raphson(self, cash_flows, initial_guess):
        """
        Alternative IRR calculation using Newton-Raphson method.
        """
        try:
            rate = initial_guess
            for _ in range(self.max_iterations):
                npv = sum(cf / ((1 + rate) ** i) for i, cf in enumerate(cash_flows))
                dnpv = sum(-i * cf / ((1 + rate) ** (i + 1)) for i, cf in enumerate(cash_flows))
                
                if abs(dnpv) < self.precision:
                    break
                    
                new_rate = rate - npv / dnpv
                
                if abs(new_rate - rate) < self.precision:
                    return new_rate
                    
                rate = new_rate
                
                # Safety bounds
                if rate < -0.99 or rate > 10:
                    return None
            
            return rate if abs(sum(cf / ((1 + rate) ** i) for i, cf in enumerate(cash_flows))) < self.precision else None
            
        except (ValueError, ZeroDivisionError, OverflowError):
            return None
    
    def calculate_payback_period(self, cash_flows, initial_investment):
        """
        Calculate payback period for the investment.
        
        Args:
            cash_flows (list): Annual cash flows
            initial_investment (float): Initial investment amount
            
        Returns:
            float or None: Payback period in years, None if not achieved
        """
        if not cash_flows or initial_investment <= 0:
            return None
        
        cumulative_cf = 0
        for i, cf in enumerate(cash_flows):
            cumulative_cf += cf
            if cumulative_cf >= initial_investment:
                # Linear interpolation for more precise payback period
                if i == 0:
                    return initial_investment / cf if cf > 0 else None
                else:
                    previous_cumulative = cumulative_cf - cf
                    return i + (initial_investment - previous_cumulative) / cf
        
        return None  # Payback not achieved within project duration
    
    def calculate_profitability_index(self, cash_flows, discount_rate, initial_investment):
        """
        Calculate Profitability Index (PI).
        
        Args:
            cash_flows (list): Annual cash flows
            discount_rate (float): Discount rate as decimal
            initial_investment (float): Initial investment amount
            
        Returns:
            float: Profitability Index
        """
        if initial_investment <= 0:
            return 0
        
        pv_inflows = sum(cf / ((1 + discount_rate) ** (i + 1)) for i, cf in enumerate(cash_flows))
        return pv_inflows / initial_investment
    
    def calculate_modified_irr(self, cash_flows, finance_rate, reinvest_rate):
        """
        Calculate Modified Internal Rate of Return (MIRR).
        
        Args:
            cash_flows (list): Cash flows including initial investment as negative
            finance_rate (float): Financing rate for negative cash flows
            reinvest_rate (float): Reinvestment rate for positive cash flows
            
        Returns:
            float or None: MIRR as decimal
        """
        if not cash_flows or len(cash_flows) < 2:
            return None
        
        try:
            n = len(cash_flows) - 1
            
            # Present value of negative cash flows
            pv_negative = sum(cf / ((1 + finance_rate) ** i) 
                            for i, cf in enumerate(cash_flows) if cf < 0)
            
            # Future value of positive cash flows
            fv_positive = sum(cf * ((1 + reinvest_rate) ** (n - i)) 
                            for i, cf in enumerate(cash_flows) if cf > 0)
            
            if pv_negative >= 0 or fv_positive <= 0:
                return None
            
            mirr = (fv_positive / abs(pv_negative)) ** (1/n) - 1
            return mirr
            
        except (ValueError, ZeroDivisionError, OverflowError):
            return None
    
    def calculate_risk_metrics(self, cash_flows, discount_rate, volatility):
        """
        Calculate risk metrics for the investment including VaR and expected shortfall.
        
        Args:
            cash_flows (list): Annual cash flows
            discount_rate (float): Discount rate
            volatility (float): Cash flow volatility as decimal
            
        Returns:
            dict: Dictionary containing various risk metrics
        """
        if not cash_flows or volatility < 0:
            return {
                'var_95': 0,
                'var_99': 0,
                'expected_shortfall': 0,
                'std_dev': 0,
                'coeff_variation': 0
            }
        
        try:
            # Calculate base NPV
            base_npv = sum(cf / ((1 + discount_rate) ** (i + 1)) for i, cf in enumerate(cash_flows))
            
            # Simulate cash flow scenarios using Monte Carlo
            num_simulations = 10000
            np.random.seed(42)  # For reproducible results
            
            npv_scenarios = []
            for _ in range(num_simulations):
                # Apply volatility to cash flows
                adjusted_cfs = [cf * (1 + np.random.normal(0, volatility)) for cf in cash_flows]
                scenario_npv = sum(cf / ((1 + discount_rate) ** (i + 1)) for i, cf in enumerate(adjusted_cfs))
                npv_scenarios.append(scenario_npv)
            
            npv_scenarios = np.array(npv_scenarios)
            
            # Calculate risk metrics
            var_95 = np.percentile(npv_scenarios, 5)  # 5th percentile for 95% VaR
            var_99 = np.percentile(npv_scenarios, 1)  # 1st percentile for 99% VaR
            
            # Expected shortfall (average of losses beyond VaR)
            losses_beyond_var = npv_scenarios[npv_scenarios <= var_95]
            expected_shortfall = np.mean(losses_beyond_var) if len(losses_beyond_var) > 0 else var_95
            
            std_dev = np.std(npv_scenarios)
            coeff_variation = std_dev / abs(base_npv) if base_npv != 0 else float('inf')
            
            return {
                'var_95': abs(base_npv - var_95),
                'var_99': abs(base_npv - var_99),
                'expected_shortfall': abs(expected_shortfall),
                'std_dev': std_dev,
                'coeff_variation': coeff_variation,
                'base_npv': base_npv
            }
            
        except Exception:
            return {
                'var_95': 0,
                'var_99': 0,
                'expected_shortfall': 0,
                'std_dev': 0,
                'coeff_variation': 0
            }
    
    def sensitivity_analysis(self, cash_flows, initial_investment, discount_rate, 
                           change_range=0.3, num_points=11):
        """
        Perform sensitivity analysis on key parameters.
        
        Args:
            cash_flows (list): Base case cash flows
            initial_investment (float): Base case initial investment
            discount_rate (float): Base case discount rate
            change_range (float): Range of parameter changes (e.g., 0.3 for ±30%)
            num_points (int): Number of sensitivity points to calculate
            
        Returns:
            dict: Sensitivity analysis results for each parameter
        """
        if not cash_flows:
            return {}
        
        try:
            base_npv = self.calculate_npv(cash_flows, discount_rate, initial_investment)
            
            # Create parameter change array
            changes = np.linspace(-change_range, change_range, num_points)
            
            sensitivity_results = {}
            
            # Cash flow sensitivity
            cf_npvs = []
            for change in changes:
                adjusted_cfs = [cf * (1 + change) for cf in cash_flows]
                npv = self.calculate_npv(adjusted_cfs, discount_rate, initial_investment)
                cf_npvs.append(npv)
            sensitivity_results['cash_flows'] = {
                'changes': (changes * 100).tolist(),
                'npv_changes': [(npv - base_npv) for npv in cf_npvs]
            }
            
            # Initial investment sensitivity
            inv_npvs = []
            for change in changes:
                adjusted_inv = initial_investment * (1 + change)
                npv = self.calculate_npv(cash_flows, discount_rate, adjusted_inv)
                inv_npvs.append(npv)
            sensitivity_results['initial_investment'] = {
                'changes': (changes * 100).tolist(),
                'npv_changes': [(npv - base_npv) for npv in inv_npvs]
            }
            
            # Discount rate sensitivity
            dr_npvs = []
            for change in changes:
                adjusted_dr = max(0.001, discount_rate * (1 + change))  # Prevent negative rates
                npv = self.calculate_npv(cash_flows, adjusted_dr, initial_investment)
                dr_npvs.append(npv)
            sensitivity_results['discount_rate'] = {
                'changes': (changes * 100).tolist(),
                'npv_changes': [(npv - base_npv) for npv in dr_npvs]
            }
            
            return sensitivity_results
            
        except Exception:
            return {}
    
    def calculate_break_even_analysis(self, fixed_costs, variable_cost_per_unit, 
                                    price_per_unit, production_capacity):
        """
        Calculate break-even analysis for steel production.
        
        Args:
            fixed_costs (float): Annual fixed costs
            variable_cost_per_unit (float): Variable cost per ton
            price_per_unit (float): Price per ton
            production_capacity (float): Maximum production capacity
            
        Returns:
            dict: Break-even analysis results
        """
        if price_per_unit <= variable_cost_per_unit:
            return {
                'break_even_units': float('inf'),
                'break_even_revenue': float('inf'),
                'margin_of_safety': 0,
                'feasible': False
            }
        
        try:
            contribution_margin = price_per_unit - variable_cost_per_unit
            break_even_units = fixed_costs / contribution_margin
            break_even_revenue = break_even_units * price_per_unit
            
            margin_of_safety = max(0, (production_capacity - break_even_units) / production_capacity)
            
            return {
                'break_even_units': break_even_units,
                'break_even_revenue': break_even_revenue,
                'contribution_margin': contribution_margin,
                'margin_of_safety': margin_of_safety,
                'feasible': break_even_units <= production_capacity
            }
            
        except (ValueError, ZeroDivisionError):
            return {
                'break_even_units': 0,
                'break_even_revenue': 0,
                'contribution_margin': 0,
                'margin_of_safety': 0,
                'feasible': False
            }
    
    def calculate_steel_industry_ratios(self, revenue, ebitda, total_assets, 
                                      debt, equity, production_tons):
        """
        Calculate steel industry specific financial ratios.
        
        Args:
            revenue (float): Annual revenue
            ebitda (float): EBITDA
            total_assets (float): Total assets
            debt (float): Total debt
            equity (float): Total equity
            production_tons (float): Annual production in tons
            
        Returns:
            dict: Steel industry financial ratios
        """
        try:
            ratios = {}
            
            # Profitability ratios
            ratios['ebitda_margin'] = ebitda / revenue if revenue > 0 else 0
            ratios['revenue_per_ton'] = revenue / production_tons if production_tons > 0 else 0
            ratios['ebitda_per_ton'] = ebitda / production_tons if production_tons > 0 else 0
            
            # Efficiency ratios
            ratios['asset_turnover'] = revenue / total_assets if total_assets > 0 else 0
            ratios['capacity_utilization'] = 1.0  # Would need actual vs capacity data
            
            # Leverage ratios
            total_capital = debt + equity
            ratios['debt_to_equity'] = debt / equity if equity > 0 else float('inf')
            ratios['debt_to_capital'] = debt / total_capital if total_capital > 0 else 0
            
            # Coverage ratios
            ratios['ebitda_to_interest'] = float('inf')  # Would need interest expense data
            
            return ratios
            
        except (ValueError, ZeroDivisionError):
            return {
                'ebitda_margin': 0,
                'revenue_per_ton': 0,
                'ebitda_per_ton': 0,
                'asset_turnover': 0,
                'capacity_utilization': 0,
                'debt_to_equity': 0,
                'debt_to_capital': 0,
                'ebitda_to_interest': 0
            }
