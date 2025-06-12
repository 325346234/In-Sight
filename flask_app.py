from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from financial_calculator import FinancialCalculator
from data_loader import DataLoader
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/auth_management')
def auth_management():
    return render_template('auth_management.html')

@app.route('/auth_request')
def auth_request():
    return render_template('auth_request.html')

@app.route('/auth_received')
def auth_received():
    return render_template('auth_received.html')

@app.route('/approval_status')
def approval_status():
    return render_template('approval_status.html')

@app.route('/api/calculate', methods=['POST'])
def calculate_economics():
    try:
        data = request.get_json()
        
        # Extract parameters from request
        params = data.get('params', {})
        
        # Load data
        data_loader = DataLoader()
        cost_data = data_loader.load_cost_data()
        sales_data = data_loader.load_sales_data()
        
        # Calculate financial metrics
        calculator = FinancialCalculator(params, cost_data, sales_data)
        results = calculator.calculate_all_metrics()
        
        return jsonify({
            'success': True,
            'results': results
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)