from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import plotly.utils
import json
import os
import base64
from datetime import datetime
from sqlalchemy import create_engine
from scipy.optimize import fsolve
from ai_analyzer import AIAnalyzer
from financial_calculator import FinancialCalculator
from steel_industry_data import SteelIndustryData

app = Flask(__name__)
app.secret_key = 'steel_investment_analysis_secret_key'
CORS(app)

# Initialize components
ai_analyzer = AIAnalyzer()
financial_calc = FinancialCalculator()
steel_data = SteelIndustryData()

def get_company_logo():
    """Get POSCO Holdings logo as base64"""
    try:
        logo_path = "attached_assets/POSCO Holdings_eng_1749727332592.png"
        with open(logo_path, "rb") as f:
            img_bytes = f.read()
            img_base64 = base64.b64encode(img_bytes).decode()
        return img_base64
    except:
        return None

def load_data_from_db():
    """Load sales and cost data from database"""
    try:
        DATABASE_URL = os.environ.get('DATABASE_URL')
        if DATABASE_URL:
            engine = create_engine(DATABASE_URL)
            sales_df = pd.read_sql('SELECT * FROM sales_data', engine)
            cost_df = pd.read_sql('SELECT * FROM cost_data', engine)
            return sales_df, cost_df
        else:
            return None, None
    except Exception as e:
        print(f"Database connection error: {e}")
        return None, None

def calculate_detailed_analysis(params):
    """Perform detailed financial analysis"""
    # Load data from database
    sales_data, cost_data = load_data_from_db()
    if sales_data is None or cost_data is None:
        return None
    
    # Basic calculations
    total_revenue = sales_data['total_revenue'].sum()
    total_quantity = sales_data['sales_volume'].sum()
    unit_selling_price = total_revenue / total_quantity
    avg_material_cost = cost_data['material_cost'].mean()
    avg_processing_cost = cost_data['processing_cost'].mean()
    
    # Parameters
    business_period = params.get('business_period', 15)
    construction_period = params.get('construction_period', 4)
    total_period = business_period + construction_period
    total_investment = params.get('total_investment', 400e6)
    debt_ratio = params.get('debt_ratio', 50.0)
    machinery_ratio = params.get('machinery_ratio', 80.0)
    building_ratio = params.get('building_ratio', 20.0)
    long_term_rate = params.get('long_term_rate', 3.7)
    grace_period = params.get('grace_period', 4)
    repayment_period = params.get('repayment_period', 8)
    tax_rate = params.get('tax_rate', 25.0)
    sales_admin_ratio = params.get('sales_admin_ratio', 4.0)
    receivables_days = params.get('receivables_days', 30)
    payables_days = params.get('payables_days', 50)
    product_inventory_days = params.get('product_inventory_days', 30)
    material_inventory_days = params.get('material_inventory_days', 40)
    discount_rate = params.get('discount_rate', 6.92) / 100
    
    # Sales volumes
    year5_volume = params.get('year5_volume', 70000)
    year6_volume = params.get('year6_volume', 80000)
    year7_plus_volume = params.get('year7_plus_volume', 100000)
    
    sales_volumes = [0, 0, 0, 0, year5_volume, year6_volume] + [year7_plus_volume] * (total_period - 6)
    
    # Detailed financial model calculation
    cash_flows = []
    debt_balance = 0
    previous_working_capital = 0
    total_debt_principal = total_investment * (debt_ratio / 100)
    annual_repayment = total_debt_principal / repayment_period
    investment_execution = [0.3, 0.3, 0.3, 0.1] + [0] * (total_period - 4)
    
    yearly_details = []
    
    for year in range(1, total_period + 1):
        # Basic values
        sales_volume = sales_volumes[year-1] if year <= len(sales_volumes) else sales_volumes[-1]
        total_revenue_year = unit_selling_price * sales_volume
        material_cost = avg_material_cost * sales_volume
        processing_cost = avg_processing_cost * sales_volume
        
        # Depreciation
        if year > construction_period:
            machinery_depreciation = (total_investment * machinery_ratio / 100) / 15
            building_depreciation = (total_investment * building_ratio / 100) / 20
            depreciation = machinery_depreciation + building_depreciation
        else:
            depreciation = 0
        
        manufacturing_cost = material_cost + processing_cost + depreciation
        
        # Investment
        investment = total_investment * investment_execution[year - 1] if year <= len(investment_execution) else 0
        
        # Debt management
        debt_increase = investment * (debt_ratio / 100)
        if year > grace_period and year <= grace_period + repayment_period:
            debt_decrease = annual_repayment
        else:
            debt_decrease = 0
        
        debt_balance = debt_balance + debt_increase - debt_decrease
        financial_cost = debt_balance * (long_term_rate / 100)
        
        # Working capital calculation
        if total_revenue_year > 0:
            receivables = (total_revenue_year / 365) * receivables_days
            product_inventory = (total_revenue_year * product_inventory_days) / 365
            material_inventory = (material_cost * material_inventory_days) / 365 if material_cost > 0 else 0
            payables = (material_cost / 365) * payables_days if material_cost > 0 else 0
            working_capital = receivables + product_inventory + material_inventory - payables
        else:
            working_capital = 0
        
        working_capital_increase = 0
        if year > construction_period:
            working_capital_increase = working_capital - previous_working_capital
        previous_working_capital = working_capital
        
        # Income statement
        sales_admin_cost = total_revenue_year * (sales_admin_ratio / 100)
        ebit = total_revenue_year - manufacturing_cost - sales_admin_cost
        pretax_income = ebit - financial_cost
        corporate_tax = max(0, pretax_income * (tax_rate / 100))
        net_income = pretax_income - corporate_tax
        
        # Residual value (last year)
        if year == total_period:
            total_depreciation_sum = depreciation * (total_period - construction_period)
            residual_value = total_investment - total_depreciation_sum
            working_capital_recovery = working_capital
        else:
            residual_value = 0
            working_capital_recovery = 0
        
        # Cash flow
        cash_inflow = net_income + financial_cost + depreciation + residual_value + working_capital_recovery
        cash_outflow = investment + working_capital_increase
        cash_flow = cash_inflow - cash_outflow
        
        cash_flows.append(cash_flow)
        
        yearly_details.append({
            'year': year,
            'sales_volume': sales_volume,
            'revenue': total_revenue_year,
            'cash_flow': cash_flow,
            'net_income': net_income,
            'debt_balance': debt_balance
        })
    
    # IRR calculation
    def npv_func(rate):
        return sum(cf / (1 + rate) ** i for i, cf in enumerate(cash_flows))
    
    try:
        irr = fsolve(npv_func, 0.1)[0]
        if abs(npv_func(irr)) > 1e-6 or irr < -0.99 or irr > 10:
            irr = None
    except:
        irr = None
    
    npv = sum(cf / (1 + discount_rate) ** i for i, cf in enumerate(cash_flows))
    
    return {
        'irr': irr,
        'npv': npv,
        'cash_flows': cash_flows,
        'yearly_details': yearly_details,
        'unit_selling_price': unit_selling_price,
        'avg_material_cost': avg_material_cost,
        'avg_processing_cost': avg_processing_cost,
        'total_investment': total_investment,
        'discount_rate': discount_rate
    }

@app.route('/')
def index():
    """Main page with YouTube video"""
    logo_base64 = get_company_logo()
    return render_template('index.html', logo_base64=logo_base64)

@app.route('/analysis')
def analysis():
    """AI Economic Analysis page"""
    logo_base64 = get_company_logo()
    sales_data, cost_data = load_data_from_db()
    
    if sales_data is not None and cost_data is not None:
        # Calculate basic values
        total_revenue = sales_data['total_revenue'].sum()
        total_quantity = sales_data['sales_volume'].sum()
        unit_selling_price = total_revenue / total_quantity
        avg_material_cost = cost_data['material_cost'].mean()
        avg_processing_cost = cost_data['processing_cost'].mean()
        
        return render_template('analysis.html', 
                             logo_base64=logo_base64,
                             unit_selling_price=unit_selling_price,
                             avg_material_cost=avg_material_cost,
                             avg_processing_cost=avg_processing_cost)
    else:
        return render_template('analysis.html', 
                             logo_base64=logo_base64,
                             error="Database connection failed")

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for financial analysis"""
    try:
        data = request.get_json()
        
        # Perform analysis
        results = calculate_detailed_analysis(data)
        
        if results is None:
            return jsonify({'error': 'Analysis failed - database connection error'}), 500
        
        # Generate chart data
        years = list(range(1, len(results['cash_flows']) + 1))
        cash_flows_million = [cf / 1e6 for cf in results['cash_flows']]
        cumulative_cf = np.cumsum(cash_flows_million).tolist()
        
        # Create chart
        fig = go.Figure()
        
        # Annual cash flows
        colors = ['red' if cf < 0 else 'green' for cf in cash_flows_million]
        fig.add_trace(go.Bar(
            x=years, 
            y=cash_flows_million, 
            name='Annual Cash Flow',
            marker_color=colors
        ))
        
        # Cumulative cash flows
        fig.add_trace(go.Scatter(
            x=years, 
            y=cumulative_cf, 
            mode='lines+markers',
            name='Cumulative Cash Flow',
            line=dict(color='blue', width=3),
            yaxis='y2'
        ))
        
        # Layout
        fig.update_layout(
            title="Cash Flow Analysis",
            xaxis_title="Year",
            yaxis=dict(title="Annual Cash Flow (Million USD)", side="left"),
            yaxis2=dict(title="Cumulative Cash Flow (Million USD)", side="right", overlaying="y"),
            height=500,
            hovermode='x unified'
        )
        
        chart_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        # AI Analysis
        financial_data = {
            'npv': results['npv'],
            'irr': results['irr'],
            'cash_flows': results['cash_flows'],
            'investment_amount': results['total_investment'],
            'discount_rate': results['discount_rate'],
            'project_duration': len(results['cash_flows'])
        }
        
        ai_analysis = ai_analyzer.analyze_investment(financial_data)
        
        return jsonify({
            'success': True,
            'results': {
                'irr': results['irr'] * 100 if results['irr'] else None,
                'npv': results['npv'] / 1e6,  # Convert to millions
                'total_investment': results['total_investment'] / 1e6,
                'discount_rate': results['discount_rate'] * 100,
                'chart': chart_json,
                'ai_analysis': ai_analysis,
                'yearly_details': results['yearly_details']
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)