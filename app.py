import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
from financial_calculator import FinancialCalculator
from data_loader import DataLoader
from scipy import stats

def perform_single_variable_monte_carlo(base_params, base_cost_data, base_sales_data, variable_type, n_simulations=500):
    """
    Perform Monte Carlo analysis on IRR sensitivity for a single variable
    """
    
    # Define variation ranges for each variable
    variations = {
        'price': 0.20,      # ±20%
        'cost': 0.15,       # ±15%
        'investment': 0.25  # ±25%
    }
    
    variation = variations[variable_type]
    
    # Store results
    irr_results = []
    factor_values = []
    
    # Base case calculation
    base_calculator = FinancialCalculator(base_params, base_cost_data, base_sales_data)
    base_results = base_calculator.calculate_all_metrics()
    base_irr = base_results['irr']
    
    # Run Monte Carlo simulations
    for i in range(n_simulations):
        # Generate random variation (normal distribution)
        factor = 1 + np.random.normal(0, variation/2)  # 95% within specified range
        factor = max(0.5, min(2.0, factor))  # Reasonable bounds
        
        # Create modified data based on variable type
        modified_params = base_params.copy()
        modified_cost_data = base_cost_data.copy()
        modified_sales_data = base_sales_data.copy()
        
        if variable_type == 'price':
            # Modify sales price by changing unit price (총매출액/판매량)
            # This effectively changes the unit price while keeping volume constant
            if '매출액' in modified_sales_data.columns:
                modified_sales_data['매출액'] = modified_sales_data['매출액'] * factor
            if '총 매출액' in modified_sales_data.columns:
                modified_sales_data['총 매출액'] = modified_sales_data['총 매출액'] * factor
            # Keep volume unchanged to simulate pure price effect
        elif variable_type == 'cost':
            # Modify cost performance
            if '소재가격' in modified_cost_data.columns:
                modified_cost_data['소재가격'] = modified_cost_data['소재가격'] * factor
            if '가공비' in modified_cost_data.columns:
                modified_cost_data['가공비'] = modified_cost_data['가공비'] * factor
        elif variable_type == 'investment':
            # Modify total investment
            modified_params['total_investment'] = base_params['total_investment'] * factor
        
        try:
            # Calculate IRR for this scenario
            calculator = FinancialCalculator(modified_params, modified_cost_data, modified_sales_data)
            results = calculator.calculate_all_metrics()
            scenario_irr = results['irr']
            
            # Validate IRR result
            if scenario_irr is not None:
                try:
                    irr_value = float(scenario_irr)
                    # Check for reasonable IRR bounds and validity
                    if -1.0 <= irr_value <= 5.0 and not (np.isnan(irr_value) or np.isinf(irr_value)):
                        irr_results.append(irr_value)
                        factor_values.append(factor)
                except (TypeError, ValueError, OverflowError):
                    # Skip invalid IRR values
                    continue
            
        except Exception as e:
            # Skip failed calculations - continue silently
            continue
    
    # Calculate statistics
    irr_array = np.array(irr_results)
    
    if len(irr_array) == 0:
        return None
        
    stats_dict = {
        'base_irr': base_irr,
        'mean_irr': np.mean(irr_array),
        'std_irr': np.std(irr_array),
        'min_irr': np.min(irr_array),
        'max_irr': np.max(irr_array),
        'p5_irr': np.percentile(irr_array, 5),
        'p25_irr': np.percentile(irr_array, 25),
        'p75_irr': np.percentile(irr_array, 75),
        'p95_irr': np.percentile(irr_array, 95),
        'irr_results': irr_results,
        'factor_values': factor_values,
        'variable_type': variable_type
    }
    
    return stats_dict

def show_progress_page():
    """Show analysis progress page with animation - completely separate page"""
    
    # Custom CSS for progress page only - hide all streamlit elements
    st.markdown("""
    <style>
    /* Hide sidebar completely */
    .css-1d391kg, .css-1rs6os, .css-17eq0hr, .stSidebar {
        display: none !important;
    }
    
    /* Hide header */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    /* Full width main content */
    .main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
    
    /* Progress page specific styling */
    .progress-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        background: linear-gradient(135deg, #000000 0%, #004488 100%);
        color: white;
        text-align: center;
        padding: 2rem;
    }
    
    .spinner {
        font-size: 5rem;
        margin-bottom: 2rem;
        animation: spin 2s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .progress-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #FFFFFF !important;
        margin-bottom: 1rem;
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    .progress-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 3rem;
        font-family: 'Noto Sans KR', sans-serif;
        color: #FFFFFF !important;
    }
    
    .progress-status {
        font-size: 1.1rem;
        margin: 1rem 0;
        font-family: 'Noto Sans KR', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Full screen progress layout
    st.markdown("""
    <div class="progress-container">
        <div class="spinner">⚙️</div>
        <h1 class="progress-title">경제성 분석 진행 중</h1>
        <p class="progress-subtitle">Steel Industry Economic Analysis in Progress</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress tracking in a container
    container = st.container()
    with container:
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Analysis steps
        steps = [
            "데이터 로딩 중...",
            "재무지표 계산 중...", 
            "현금흐름 분석 중...",
            "IRR 계산 중...",
            "Monte Carlo 분석 준비 중...",
            "분석 완료!"
        ]
        
        # Simulate analysis with progress
        for i, step in enumerate(steps):
            status_text.markdown(f'<div class="progress-status">📊 {step}</div>', unsafe_allow_html=True)
            progress_bar.progress((i + 1) / len(steps))
            time.sleep(1.2)
        
        # Show completion
        st.success("경제성 분석이 완료되었습니다!")
        time.sleep(2)
        
        # Navigate to results page
        st.session_state['current_page'] = 'results'
        st.rerun()

def main():
    st.set_page_config(
        page_title="철강사업 프로젝트 경제성 분석",
        page_icon="🏭",
        layout="wide"
    )
    
    # Custom CSS styling inspired by POSCO design principles
    st.markdown("""
    <style>
/* 모든 요소, 가상요소, 인라인 스타일까지 강제 덮어쓰기 */
*, *::before, *::after {
    transition: none !important;
    animation: none !important;
}
[style*="transition"], [style*="animation"] {
    transition: none !important;
    animation: none !important;
}
.stButton > button,
.stSlider,
.stAlert,
.stDataFrame,
.block-container,
.section-header {
    transition: none !important;
    animation: none !important;
}
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
    
    /* Main background and text */
    .stApp {
        background: #ffffff;
        font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #333333;
    }
    
/* Header styling - POSCO Blue Solid + Rounded + Compact */
.main-header {
    background-color: #FFFFFF;
    border: 3px solid #000000;
    padding: 1rem 1rem;
    border-radius: 0.75rem;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 2px 16px rgba(0, 87, 139, 0.15);
}

.main-header h1 {
    font-weight: 700;
    font-size: 2.5rem;
    color: #000000;
    margin-bottom: 0.5rem;
    letter-spacing: -0.5px;
}

.main-header p {
    font-weight: 300;
    font-size: 1.2rem;
    color: #000000;
    opacity: 0.9;
    margin: 0;
}

    
    /* Typography improvements */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Noto Sans KR', sans-serif;
        color: #000000;
        font-weight: 500;
        line-height: 1.4;
    }
    
    /* All text elements */
    p, div, span, label, .stMarkdown {
        color: #000000;
    }
    
    /* Cards and containers */
    .stContainer > div {
        background: #ffffff;
        border: 1px solid #e8eaf0;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    /* Buttons - POSCO style */
    .stButton > button {
        background: #000000;
        color: white !important;
        border: none;
        border-radius: 4px;
        padding: 0.75rem 2rem;
        font-weight: 500;
        font-family: 'Noto Sans KR', sans-serif;
        box-shadow: 0 2px 4px rgba(0, 51, 102, 0.2);
        font-size: 1rem;
    }
    
    .stButton > button:hover {
        background: #004488;
        color: white !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 51, 102, 0.3);
    }
    
    /* Input fields */
    .stNumberInput > div > div > input {
        border: 1px solid #b3d9ff;
        border-radius: 4px;
        background: #f0f8ff;
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 0.95rem;
        padding: 0.75rem;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: #000000;
        background: #e6f3ff;
        box-shadow: 0 0 0 3px rgba(179, 217, 255, 0.3);
        outline: none;
    }
    
    .stNumberInput > div > div > input:hover {
        border-color: #66b3ff;
        background: #e6f3ff;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #000000, #004488);
    }
    
    /* Metrics - Clean POSCO style */
    .metric-container {
        background: #ffffff;
        border: 1px solid #e8eaf0;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 0.5rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .metric-container:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }
    
    .metric-container h4 {
        color: #666666;
        font-size: 0.9rem;
        font-weight: 400;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-container h2 {
        color: #000000;
        font-weight: 700;
        font-size: 1.8rem;
        margin: 0;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background: white;
        border: 1px solid #e8eaf0;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    /* Success/Info messages */
    .stSuccess {
        background: #FFFFFF;
        border-left: 4px solid #000000;
        border-radius: 4px;
        color: #155724;
    }
    
    .stInfo {
        background: #e6f3ff;
        border-left: 4px solid #000000;
        border-radius: 4px;
        color: #000000;
    }
    
    /* Section headers - Professional style */
    .section-header {
        background: #fbfcfb;
        border-left: 4px solid #000000;
        padding: 1rem;
        border-radius: 4px;
        margin: 2rem 0 1rem 0;
    }
    
    .section-header h2 {
        color: #000000;
        font-weight: 600;
        font-size: 1.5rem;
        margin-left: 0.5rem;
    }
    
    .section-header h3 {
        color: #000000;
        font-weight: 500;
        font-size: 1.2rem;
        
    }
    
    .section-header p {
        color: #666666;
        font-size: 1rem;
        margin: 0;
        font-weight: 300;
        margin-left:0.5rem;
    }
    
    /* Label styling */
    .stNumberInput label {
        font-weight: 500;
        color: #000000;
        font-size: 0.9rem;
    }
    
    /* Sidebar removal */
    .css-1d391kg {
        display: none;
    }

.stButton > button, .stButton > button * {
    background: #000 !important;
    color: #fff !important;
    border-radius: 16px !important;
}
    
                
/* Navigation elements - White Text & Rounded */
.nav-button {
    background: #FFFFFF;
    border: 2px solid #000000;
    color: #fff;
    border-radius: 16px;
    padding: 0.5rem 1.5rem;
    font-weight: 500;
    font-family: 'Noto Sans KR', sans-serif;
}

.nav-button:hover {
    background: ;
    color: #fff !important;
    border-radius: 16px;
}
                
    """, unsafe_allow_html=True)
    
    # Main header with new styling
    st.markdown("""
    <div class="main-header">
        <h1>In-Sight, Insight to Your Investment</h1>
        <p>Steel Industry Project Economic Feasibility Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation menu
    create_navigation_menu()
    
    # Initialize session state variables
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'input'
    
    # Page routing
    if st.session_state.get('current_page') == 'progress':
        show_progress_page()
    elif st.session_state.get('current_page') == 'results':
        show_results_page()
    elif st.session_state.get('current_page') == 'analysis':
        show_analysis_page()
    else:
        # Default to input page
        st.session_state['current_page'] = 'input'
        show_input_page()

def create_navigation_menu():
    """Create top navigation menu"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("전제사항 입력", key="nav_input", use_container_width=True):
            st.session_state['current_page'] = 'input'
            st.rerun()
    
    with col2:
        if st.button("경제성 분석 결과", key="nav_results", use_container_width=True):
            if 'analysis_results' in st.session_state and st.session_state['analysis_results'] is not None:
                st.session_state['current_page'] = 'results'
                st.rerun()
            else:
                st.warning("먼저 전제사항을 입력하고 분석을 실행해주세요.")
    
    with col3:
        if st.button("심화 분석", key="nav_advanced", use_container_width=True):
            if 'analysis_results' in st.session_state and st.session_state['analysis_results'] is not None:
                st.session_state['current_page'] = 'analysis'
                st.rerun()
            else:
                st.warning("먼저 전제사항을 입력하고 분석을 실행해주세요.")
    
    with col4:
        if st.button("철강사 투자동향", key="nav_insights", use_container_width=True):
            st.session_state['current_page'] = 'insights'
            st.rerun()
    
    st.markdown("---")

def show_results_page():
    """Display economic analysis results"""
    st.markdown("""
    <div class="section-header">
        <h2> 경제성 분석 결과</h2>
        <p>Steel Industry Project Economic Analysis Results</p>
    </div>
    """, unsafe_allow_html=True)
    
    if 'project_params' not in st.session_state:
        st.warning("먼저 전제사항을 입력하고 분석을 실행해주세요.")
        st.session_state['current_page'] = 'input'
        st.rerun()
        return
    
    params = st.session_state['project_params']
    
    # Load data from Excel files
    data_loader = DataLoader()
    
    try:
        # Try to load Excel files
        cost_data = data_loader.load_cost_data()
        sales_data = data_loader.load_sales_data()
        
        # Store data in session state for advanced analysis
        st.session_state['cost_data'] = cost_data
        st.session_state['sales_data'] = sales_data
        
        # Initialize calculator
        calculator = FinancialCalculator(params, cost_data, sales_data)
        
        # Calculate financial metrics
        results = calculator.calculate_all_metrics()
        
        # Store results for advanced analysis
        st.session_state['analysis_results'] = results
        st.session_state['params'] = params
        
        # Display results
        display_results(results, params)
        
    except Exception as e:
        st.error(f"데이터 로딩 또는 계산 중 오류가 발생했습니다: {str(e)}")
        st.info("Excel 파일이 없는 경우 기본 데이터로 계산을 진행합니다.")
        
        # Use default data for demonstration
        cost_data = data_loader.get_default_cost_data()
        sales_data = data_loader.get_default_sales_data()
        
        # Store data in session state for advanced analysis
        st.session_state['cost_data'] = cost_data
        st.session_state['sales_data'] = sales_data
        
        calculator = FinancialCalculator(params, cost_data, sales_data)
        results = calculator.calculate_all_metrics()
        
        # Store results for advanced analysis
        st.session_state['analysis_results'] = results
        st.session_state['params'] = params
        
        display_results(results, params)

def show_input_page():
    st.markdown("""
    <div class="section-header">
        <h2>프로젝트 파라미터 입력</h2>
        <p>각 항목의 값을 입력하세요. 기본값이 사전 설정되어 있습니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create columns for better layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="section-header">
            <h3>기본 프로젝트 정보</h3>
        </div>
        """, unsafe_allow_html=True)
        business_period = st.number_input("사업기간 (년)", min_value=1, max_value=50, value=15)
        construction_period = st.number_input("공사기간 (년)", min_value=1, max_value=10, value=4)
        interest_rate = st.number_input("할인율 (%)", min_value=0.0, max_value=50.0, value=6.92, step=0.01)
    
    with col2:
        st.markdown("""
        <div class="section-header">
            <h3>투자비 정보</h3>
        </div>
        """, unsafe_allow_html=True)
        total_investment = st.number_input("총투자비 ($)", min_value=0, value=400000000, step=1000000)
        machinery_ratio = st.number_input("기계설비투자비비율 (%)", min_value=0.0, max_value=100.0, value=80.0, step=0.1)
        building_ratio = st.number_input("건축물투자비비율 (%)", min_value=0.0, max_value=100.0, value=20.0, step=0.1)
    
    with col3:
        st.markdown("""
        <div class="section-header">
            <h3>투자비 집행률</h3>
        </div>
        """, unsafe_allow_html=True)
        investment_year1 = st.number_input("투자비집행Year1 (%)", min_value=0.0, max_value=100.0, value=30.0, step=0.1)
        investment_year2 = st.number_input("투자비집행Year2 (%)", min_value=0.0, max_value=100.0, value=30.0, step=0.1)
        investment_year3 = st.number_input("투자비집행Year3 (%)", min_value=0.0, max_value=100.0, value=30.0, step=0.1)
        investment_year4 = st.number_input("투자비집행Year4 (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.1)
        

    col4, col5, col6 = st.columns(3)
    with col4:

        st.markdown("""
        <div class="section-header">
            <h3>자금조달</h3>
        </div>
        """, unsafe_allow_html=True)
        equity_ratio = st.number_input("자본비율 (%)", min_value=0.0, max_value=100.0, value=50.0, step=0.1)
        debt_ratio = st.number_input("차입비율 (%)", min_value=0.0, max_value=100.0, value=50.0, step=0.1)
    
    with col5:
        st.markdown("""
        <div class="section-header">
            <h3>차입금 조건</h3>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            grace_period = st.number_input("감가상각기계설비 (년)", min_value=1, value=15)
        with col2:
            building_depreciation = st.number_input("감가상각건축물 (년)", min_value=1, value=20)
        col1, col2 = st.columns(2)
        with col1:
            loan_grace_period = st.number_input("장기차입거치기간 (년)", min_value=0, value=4)
        with col2:
            loan_repayment_period = st.number_input("장기차입상환기간 (년)", min_value=1, value=8)
        col1, col2 = st.columns(2)
        with col1:
            loan_interest_rate = st.number_input("장기차입금리 (%)", min_value=0.0, max_value=50.0, value=3.7, step=0.01)
        with col2:
            short_term_interest_rate = st.number_input("단기차입금리 (%)", min_value=0.0, max_value=50.0, value=4.8, step=0.01)
    
    with col6:
        st.markdown("""
        <div class="section-header">
            <h3>기타 비율</h3>
        </div>
        """, unsafe_allow_html=True)
        corporate_tax_rate = st.number_input("법인세율 (%)", min_value=0.0, max_value=100.0, value=25.0, step=0.1)
        sales_admin_ratio = st.number_input("판매관리비비율 (%)", min_value=0.0, max_value=100.0, value=4.0, step=0.1)
    
    col1, col2 = st.columns(2)
    with col1:
    # Sales volume inputs
        st.markdown("""
    <div class="section-header">
        <h3>판매량 정보</h3>
        <p>연도별 판매량 (톤단위)</p>
    </div>
    """, unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    
    with col3:
        sales_year1to4 = st.number_input("Year1-4 (톤)", min_value=0, value=0)
        sales_year5 = st.number_input("판매량Year5 (톤)", min_value=0, value=70000)
        sales_year6 = st.number_input("판매량Year6 (톤)", min_value=0, value=80000)
    
    with col4:
        receivables_days = st.number_input("매출채권일수 (일)", min_value=0, value=50)
        payables_days = st.number_input("매입채무일수 (일)", min_value=0, value=30)
        product_inventory_days = st.number_input("제품재고일수 (일)", min_value=0, value=50)
       

    col5, col6 = st.columns(2)
    
    with col5:
        sales_after_year7 = st.number_input("판매량AfterYear7 (톤)", min_value=0, value=100000)
       
    
    with col6:    
        material_inventory_days = st.number_input("소재재고일수 (일)", min_value=0, value=40)





    
    with col2:
    # Working capital days
        st.markdown("""
    <div class="section-header">
        <h3>운전자금 관련 일수</h3>
    </div>
    """, unsafe_allow_html=True)
  
    
    # Store parameters in session state
    if st.button("분석 시작", type="primary"):
        params = {
            'business_period': business_period,
            'construction_period': construction_period,
            'interest_rate': interest_rate / 100,
            'total_investment': total_investment,
            'machinery_ratio': machinery_ratio / 100,
            'building_ratio': building_ratio / 100,
            'equity_ratio': equity_ratio / 100,
            'debt_ratio': debt_ratio / 100,
            'investment_execution': {
                1: investment_year1 / 100,
                2: investment_year2 / 100,
                3: investment_year3 / 100,
                4: investment_year4 / 100
            },
            'machinery_depreciation_years': grace_period,
            'building_depreciation_years': building_depreciation,
            'loan_grace_period': loan_grace_period,
            'loan_repayment_period': loan_repayment_period,
            'loan_interest_rate': loan_interest_rate / 100,
            'short_term_interest_rate': short_term_interest_rate / 100,
            'corporate_tax_rate': corporate_tax_rate / 100,
            'sales_admin_ratio': sales_admin_ratio / 100,
            'sales_volumes': {
                5: sales_year5,
                6: sales_year6,
                'after_7': sales_after_year7
            },
            'working_capital_days': {
                'receivables': receivables_days,
                'payables': payables_days,
                'product_inventory': product_inventory_days,
                'material_inventory': material_inventory_days
            }
        }
        st.session_state['project_params'] = params
        st.session_state['current_page'] = 'progress'
        st.rerun()

def show_analysis_page():
    """Advanced analysis page with Monte Carlo analysis"""
    st.markdown("""
    <div class="section-header">
        <h2> 심화 분석</h2>
        <p>Advanced Economic Analysis and Risk Assessment</p>
    </div>
    """, unsafe_allow_html=True)
    if 'analysis_results' not in st.session_state or st.session_state['analysis_results'] is None:
        st.warning("먼저 전제사항을 입력하고 경제성 분석을 실행해주세요.")
        return
    results = st.session_state['analysis_results']
    params = st.session_state['params']
    # 변수별 영향도 영역
    st.markdown("### 📈 IRR 민감도 분석")
    st.markdown(f"기준 IRR: **{results['irr']:.2%}**")
    st.markdown("#### 변수별 영향도")
    sensitivity_data = {
        '변수': ['판매가격', '제조원가', '총투자비'],
        '기준값 대비 ±10% 변동시 예상 IRR 변화': ['±2.5%p', '±1.8%p', '±1.2%p'],
        '위험도': ['높음', '중간', '낮음']
    }
    sensitivity_df = pd.DataFrame(sensitivity_data)
    st.dataframe(sensitivity_df, use_container_width=True, hide_index=True)
 
    st.markdown("""
    <div class="section-header">
        <h2> Monte Carlo 위험 분석</h2>
        <p>판매가격, 원가실적, 총투자비 개별 변동에 따른 IRR 민감도 분석</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get the original data from session state
    cost_data = st.session_state.get('cost_data', pd.DataFrame())
    sales_data = st.session_state.get('sales_data', pd.DataFrame())
    
    # Perform separate Monte Carlo analysis for each variable
    variable_names = {
        'price': '판매가격 (±20%)',
        'cost': '원가실적 (±15%)', 
        'investment': '총투자비 (±25%)'
    }
    
    variable_colors = {
        'price': '#000000',
        'cost': '#dc3545',
        'investment': '#6c757d'
    }
    
    monte_carlo_results = {}
    with st.spinner("Monte Carlo 시뮬레이션 실행 중..."):
        for var_type in ['price', 'cost', 'investment']:
            with st.expander(f"{variable_names[var_type]} 분석 진행 중...", expanded=False):
                result = perform_single_variable_monte_carlo(params, cost_data, sales_data, var_type, n_simulations=300)
                if result:
                    monte_carlo_results[var_type] = result
                    st.success(f"{variable_names[var_type]} 분석 완료: {len(result['irr_results'])}개 시나리오")
                else:
                    st.warning(f"{variable_names[var_type]} 분석 실패")
    if not monte_carlo_results:
        st.error("Monte Carlo 분석을 수행할 수 없습니다.")
        return
    for var_type, result in monte_carlo_results.items():
        st.markdown(f"### {variable_names[var_type]} 민감도 분석")
        
        # Metrics for this variable
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <h4>기본 IRR</h4>
                <h2>{result['base_irr']:.2%}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-container">
                <h4>평균 IRR</h4>
                <h2>{result['mean_irr']:.2%}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-container">
                <h4>5% 하위 IRR</h4>
                <h2 style="color: #dc3545;">{result['p5_irr']:.2%}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-container">
                <h4>95% 상위 IRR</h4>
                <h2 style="color: #28a745;">{result['p95_irr']:.2%}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Charts for this variable
        col1, col2 = st.columns(2)
        
        with col1:
            # IRR Distribution Histogram
            fig_hist = go.Figure()
            fig_hist.add_trace(go.Histogram(
                x=result['irr_results'],
                nbinsx=30,
                marker_color=variable_colors[var_type],
                opacity=0.7,
                name=f'IRR 분포 ({variable_names[var_type]})'
            ))
            
            # Add vertical lines for key statistics
            fig_hist.add_vline(x=result['base_irr'], line_dash="dash", line_color="red", 
                               annotation_text="기본", annotation_position="top")
            fig_hist.add_vline(x=result['mean_irr'], line_dash="dash", line_color="blue", 
                               annotation_text="평균", annotation_position="top")
            
            fig_hist.update_layout(
                title={
                    'text': f"IRR 분포 - {variable_names[var_type]}",
                    'x': 0.5,
                    'font': {'color': '#333333', 'size': 14, 'family': 'Noto Sans KR'}
                },
                xaxis_title="IRR (%)",
                yaxis_title="빈도",
                plot_bgcolor='white',
                paper_bgcolor='white',
                font={'color': '#333333', 'family': 'Noto Sans KR'},
                showlegend=False,
                height=300,
                xaxis=dict(
                    gridcolor='#f0f0f0',
                    linecolor='#e0e0e0',
                    tickformat='.1%'
                ),
                yaxis=dict(
                    gridcolor='#f0f0f0',
                    linecolor='#e0e0e0'
                )
            )
            
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # Scatter plot: Variable vs IRR
            fig_scatter = go.Figure()
            fig_scatter.add_trace(go.Scatter(
                x=(np.array(result['factor_values']) - 1) * 100,
                y=np.array(result['irr_results']) * 100,
                mode='markers',
                marker=dict(color=variable_colors[var_type], opacity=0.6, size=4),
                name=f'{variable_names[var_type]} vs IRR'
            ))
            
            fig_scatter.update_layout(
                title={
                    'text': f"{variable_names[var_type]} 변동 vs IRR",
                    'x': 0.5,
                    'font': {'color': '#333333', 'size': 14, 'family': 'Noto Sans KR'}
                },
                xaxis_title=f"{variable_names[var_type]} 변동 (%)",
                yaxis_title="IRR (%)",
                plot_bgcolor='white',
                paper_bgcolor='white',
                font={'color': '#333333', 'family': 'Noto Sans KR'},
                showlegend=False,
                height=300,
                xaxis=dict(
                    gridcolor='#f0f0f0',
                    linecolor='#e0e0e0'
                ),
                yaxis=dict(
                    gridcolor='#f0f0f0',
                    linecolor='#e0e0e0'
                )
            )
            
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Risk Statistics for this variable
        risk_stats = pd.DataFrame({
            '통계량': ['최솟값', '5%ile', '25%ile', '평균', '75%ile', '95%ile', '최댓값', '표준편차'],
            f'{variable_names[var_type]} IRR (%)': [
                f"{result['min_irr']:.2%}",
                f"{result['p5_irr']:.2%}",
                f"{result['p25_irr']:.2%}",
                f"{result['mean_irr']:.2%}",
                f"{result['p75_irr']:.2%}",
                f"{result['p95_irr']:.2%}",
                f"{result['max_irr']:.2%}",
                f"{result['std_irr']:.2%}"
            ]
        })
        
        st.dataframe(risk_stats, use_container_width=True)
        
        # Calculate correlation
        correlation = np.corrcoef(result['factor_values'], result['irr_results'])[0,1]
        
        st.markdown(f"""
        <div style="background: #ffffff; border: 1px solid #e8eaf0; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
            <p><strong>{variable_names[var_type]} 상관계수:</strong> {correlation:.3f}</p>
            <p><strong>위험도 (표준편차):</strong> {result['std_irr']:.2%}</p>
            <p><strong>하방위험 (VaR 5%):</strong> {result['p5_irr']:.2%}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
    
    # Interactive Dashboard Section
    st.markdown("""
    <div class="section-header">
        <h2> 실시간 민감도 대시보드</h2>
        <p>슬라이드바를 조정하여 실시간으로 IRR 변화를 확인하세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get base values for sliders
    base_investment = params['total_investment']
    base_unit_price = FinancialCalculator(params, cost_data, sales_data).unit_price
    base_material_cost = FinancialCalculator(params, cost_data, sales_data).material_cost_per_unit
    base_processing_cost = FinancialCalculator(params, cost_data, sales_data).processing_cost_per_unit
    base_manufacturing_cost = base_material_cost + base_processing_cost
    
    # Enhanced CSS for styled sliders with dynamic coloring
    st.markdown("""
    <style>
    .slider-container {
        background: #ffffff;
        border: 1px solid #e8eaf0;
        border-radius: 16px; /* 더 둥글게 */
        padding: 1.5rem;
        margin-bottom: 1rem;
        position: relative;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .slider-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #fff; /* 흰색 텍스트 */
        margin-bottom: 0.5rem;
    }
    .base-line {
        position: absolute;
        left: 50%;
        top: 60px;
        bottom: 80px;
        width: 3px;
        border-left: 3px dotted #6c757d;
        z-index: 1;
        opacity: 0.7;
    }
    .value-display {
        background: #000000;
        border-radius: 16px; /* 더 둥글게 */
        padding: 0.75rem;
        margin-top: 0.5rem;
        font-size: 0.9rem;
        border-left: 4px solid #dee2e6;
        color: #fff; /* 흰색 텍스트 */
    }
    .value-display.low-impact {
        border-left-color: #000000;
        background: #FFFFFF;
        color: #000000;
    }
    .value-display.medium-impact {
        border: 3px solid #000000;
        background: #FFFFFF;
        color: #000000;
    }
    .value-display.high-impact {
        border-left-color: #000000;
        background: #FFFFFF;
        color: #000000;
    }
    .positive-change { color: #28a745; font-weight: 600; }
    .negative-change { color: #dc3545; font-weight: 600; }
    .no-change { color: #fff; font-weight: 600; }
    .impact-indicator {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #fff;
        background: #000000;
    }
    .impact-low { background: #28a745; color: #fff; }
    .impact-medium { background: #ffc107; color: #000000; }
    .impact-high { background: #dc3545; color: #fff; }
    /* Custom slider styling */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #dc3545 0%, #ffc107 50%, #28a745 100%);
        border-radius: 16px;
    }
    /* 컨테이너, 회귀분석 등 주요 박스 둥글게, 텍스트 흰색 */
    .metric-container {
        background: #FFFFFF;
        border: 3px solid #000000;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.5rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        color: #000000;
    }
    .metric-container h4 {
        color: #000000;
        font-size: 2rem;
    }
    
    .metric-container h2 {
        color: #000000;
    }
    .section-header {
        background: #fbfcfb;
        border-left: 4px solid #000000;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 2rem 0 1rem 0;
        color: #fff;
    }
    .section-header h2, .section-header h3, .section-header p {
        color: #000000;
    }
    /* 회귀분석 공식 등 주요 박스 */
    .regression-box {
        background: #000000;
        border-radius: 16px;
        color: #fff;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create layout with sliders on left and IRR display on right
    col_sliders, col_irr = st.columns([2, 1])
    
    with col_sliders:
        # Enhanced Investment slider
        st.markdown("""
        <div class="slider-container">
            <div class="slider-title" style="color: #000000;">총투자비 조정</div>
            <div class="base-line"></div>
        </div>
        """, unsafe_allow_html=True)
        
        investment_change = st.slider(
            "투자비 변화율",
            min_value=-100,
            max_value=100,
            value=0,
            step=5,
            key="investment_slider",
            format="%d%%"
        )
        investment_multiplier = 1 + (investment_change / 100)
        adjusted_investment = base_investment * investment_multiplier
        
        # Dynamic value display with color coding and impact indicator
        abs_change = abs(investment_change)
        impact_class = "low-impact" if abs_change <= 20 else "medium-impact" if abs_change <= 50 else "high-impact"
        impact_label = "낮음" if abs_change <= 20 else "보통" if abs_change <= 50 else "높음"
        impact_badge_class = "impact-low" if abs_change <= 20 else "impact-medium" if abs_change <= 50 else "impact-high"
        change_class = "negative-change" if investment_change > 0 else "positive-change" if investment_change < 0 else "no-change"
        
        st.markdown(f"""
        <div class="value-display {impact_class}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <strong>투자비 영향도</strong>
                <span class="impact-indicator {impact_badge_class}">{impact_label}</span>
            </div>
            <strong>기준값:</strong> ${base_investment:,.0f}<br>
            <strong>조정값:</strong> ${adjusted_investment:,.0f}<br>
            <strong>변화:</strong> <span class="{change_class}">{investment_change:+d}%</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced Price slider
        st.markdown("""
        <div class="slider-container">
            <div class="slider-title" style="color: #000000;">판매가격 조정</div>
            <div class="base-line"></div>
        </div>
        """, unsafe_allow_html=True)
        
        price_change = st.slider(
            "판매가격 변화율",
            min_value=-100,
            max_value=100,
            value=0,
            step=5,
            key="price_slider",
            format="%d%%"
        )
        price_multiplier = 1 + (price_change / 100)
        adjusted_price = base_unit_price * price_multiplier
        
        abs_change = abs(price_change)
        impact_class = "low-impact" if abs_change <= 20 else "medium-impact" if abs_change <= 50 else "high-impact"
        impact_label = "낮음" if abs_change <= 20 else "보통" if abs_change <= 50 else "높음"
        impact_badge_class = "impact-low" if abs_change <= 20 else "impact-medium" if abs_change <= 50 else "impact-high"
        change_class = "positive-change" if price_change > 0 else "negative-change" if price_change < 0 else "no-change"
        
        st.markdown(f"""
        <div class="value-display {impact_class}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <strong>판매가격 영향도</strong>
                <span class="impact-indicator {impact_badge_class}">{impact_label}</span>
            </div>
            <strong>기준값:</strong> ${base_unit_price:,.0f}/톤<br>
            <strong>조정값:</strong> ${adjusted_price:,.0f}/톤<br>
            <strong>변화:</strong> <span class="{change_class}">{price_change:+d}%</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced Cost slider
        st.markdown("""
        <div class="slider-container">
            <div class="slider-title" style="color: #000000;">제조원가 조정</div>
            <div class="base-line"></div>
        </div>
        """, unsafe_allow_html=True)
        
        cost_change = st.slider(
            "제조원가 변화율",
            min_value=-100,
            max_value=100,
            value=0,
            step=5,
            key="cost_slider",
            format="%d%%"
        )
        cost_multiplier = 1 + (cost_change / 100)
        adjusted_manufacturing_cost = base_manufacturing_cost * cost_multiplier
        
        abs_change = abs(cost_change)
        impact_class = "low-impact" if abs_change <= 20 else "medium-impact" if abs_change <= 50 else "high-impact"
        impact_label = "낮음" if abs_change <= 20 else "보통" if abs_change <= 50 else "높음"
        impact_badge_class = "impact-low" if abs_change <= 20 else "impact-medium" if abs_change <= 50 else "impact-high"
        change_class = "positive-change" if cost_change < 0 else "negative-change" if cost_change > 0 else "no-change"
        
        st.markdown(f"""
        <div class="value-display {impact_class}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <strong>제조원가 영향도</strong>
                <span class="impact-indicator {impact_badge_class}">{impact_label}</span>
            </div>
            <strong>기준값:</strong> ${base_manufacturing_cost:,.0f}/톤<br>
            <strong>조정값:</strong> ${adjusted_manufacturing_cost:,.0f}/톤<br>
            <strong>변화:</strong> <span class="{change_class}">{cost_change:+d}%</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col_irr:
        st.markdown("#### 실시간 IRR 계산")
        
        # Calculate IRR with adjusted parameters automatically
        try:
            # Create modified parameters and data
            modified_params = params.copy()
            modified_params['total_investment'] = adjusted_investment
            
            modified_sales_data = sales_data.copy()
            if '매출액' in sales_data.columns:
                modified_sales_data['매출액'] = sales_data['매출액'] * price_multiplier
            if '총 매출액' in sales_data.columns:
                modified_sales_data['총 매출액'] = sales_data['총 매출액'] * price_multiplier
            
            modified_cost_data = cost_data.copy()
            if '소재가격' in cost_data.columns:
                modified_cost_data['소재가격'] = cost_data['소재가격'] * cost_multiplier
            if '가공비' in cost_data.columns:
                modified_cost_data['가공비'] = cost_data['가공비'] * cost_multiplier
            
            # Calculate new IRR
            dashboard_calculator = FinancialCalculator(modified_params, modified_cost_data, modified_sales_data)
            dashboard_results = dashboard_calculator.calculate_all_metrics()
            new_irr = dashboard_results['irr']
            
            # Display IRR metrics in vertical layout
            st.markdown(f"""
            <div class="metric-container">
                <h4>기준 IRR</h4>
                <h2>{results['irr']:.2%}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            irr_change = new_irr - results['irr']
            color = "#28a745" if irr_change >= 0 else "#dc3545"
            
            st.markdown(f"""
            <div class="metric-container">
                <h4>조정된 IRR</h4>
                <h2 style="color: {color};">{new_irr:.2%}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-container">
                <h4>IRR 변화</h4>
                <h2 style="color: {color};">{irr_change:+.2%}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            irr_change_pct = (new_irr / results['irr'] - 1) * 100 if results['irr'] != 0 else 0
            st.markdown(f"""
            <div class="metric-container">
                <h4>IRR 변화율</h4>
                <h2 style="color: {color};">{irr_change_pct:+.1f}%</h2>
            </div>
            """, unsafe_allow_html=True)
            
            # IRR sensitivity gauge
            st.markdown("#### 민감도 지표")
            
            # Create a simple visual indicator
            sensitivity_score = abs(irr_change) / abs(results['irr']) * 100 if results['irr'] != 0 else 0
            
            if sensitivity_score < 5:
                sensitivity_level = "낮음"
                sensitivity_color = "#28a745"
            elif sensitivity_score < 15:
                sensitivity_level = "보통"
                sensitivity_color = "#ffc107"
            else:
                sensitivity_level = "높음"
                sensitivity_color = "#dc3545"
            
            st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e8eaf0; padding: 1rem; border-radius: 8px; text-align: center;">
                <p><strong>민감도:</strong> <span style="color: {sensitivity_color};">{sensitivity_level}</span></p>
                <p><strong>영향도:</strong> {sensitivity_score:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error("IRR 계산 중 오류가 발생했습니다.")
            st.info("파라미터 조정값이 너무 극단적일 수 있습니다. 슬라이더를 조정해 보세요.")
    
    # Summary chart showing current adjustments
    st.markdown("---")
    st.markdown("####  현재 조정 상태")
    
    # Real-time sensitivity chart
    fig_sensitivity = go.Figure()
    
    # Add bars for each adjustment
    adjustments = [investment_change, price_change, cost_change]
    colors = ['#6c757d', '#000000', '#dc3545']
    
    fig_sensitivity.add_trace(go.Bar(
        x=['투자비', '판매가격', '제조원가'],
        y=adjustments,
        marker_color=colors,
        name='조정 비율',
        text=[f"{adj:+.0f}%" for adj in adjustments],
        textposition='auto'
    ))
    
    fig_sensitivity.update_layout(
        title={
            'text': "파라미터 조정 현황",
            'x': 0.5,
            'font': {'color': '#333333', 'size': 16, 'family': 'Noto Sans KR'}
        },
        xaxis_title="조정 항목",
        yaxis_title="조정 비율 (%)",
        plot_bgcolor='white',
        paper_bgcolor='white',
        font={'color': '#333333', 'family': 'Noto Sans KR'},
        showlegend=False,
        height=220,
        yaxis=dict(
            gridcolor='#f0f0f0',
            linecolor='#e0e0e0',
            zeroline=True,
            zerolinecolor='#333333',
            range=[-100, 100]
        )
    )
    
    st.plotly_chart(fig_sensitivity, use_container_width=True)
    
    # Regression Analysis Section
    st.markdown("---")
    st.markdown("""
    <div class="section-header">
        <h2> IRR 회귀분석 공식</h2>
        <p>주요 변수들의 IRR에 대한 영향도를 수학적 공식으로 표현</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("회귀분석 계산 중..."):
        # Generate data points for regression analysis
        sample_points = []
        sample_irrs = []
        
        # Create a grid of sample points around the base values
        investment_variations = [-50, -25, -10, 0, 10, 25, 50]
        price_variations = [-30, -15, -5, 0, 5, 15, 30]
        cost_variations = [-30, -15, -5, 0, 5, 15, 30]
        
        try:
            for inv_change in investment_variations:
                for price_change in price_variations:
                    for cost_change in cost_variations:
                        # Calculate IRR for this combination
                        modified_params = params.copy()
                        modified_params['total_investment'] = base_investment * (1 + inv_change/100)
                        
                        modified_sales_data = sales_data.copy()
                        if '매출액' in sales_data.columns:
                            modified_sales_data['매출액'] = sales_data['매출액'] * (1 + price_change/100)
                        if '총 매출액' in sales_data.columns:
                            modified_sales_data['총 매출액'] = sales_data['총 매출액'] * (1 + price_change/100)
                        
                        modified_cost_data = cost_data.copy()
                        if '소재가격' in cost_data.columns:
                            modified_cost_data['소재가격'] = cost_data['소재가격'] * (1 + cost_change/100)
                        if '가공비' in cost_data.columns:
                            modified_cost_data['가공비'] = cost_data['가공비'] * (1 + cost_change/100)
                        
                        try:
                            regression_calculator = FinancialCalculator(modified_params, modified_cost_data, modified_sales_data)
                            regression_results = regression_calculator.calculate_all_metrics()
                            
                            if regression_results['irr'] is not None and not np.isnan(regression_results['irr']) and np.isfinite(regression_results['irr']):
                                sample_points.append([inv_change, price_change, cost_change])
                                sample_irrs.append(regression_results['irr'])
                        except:
                            continue
            
            if len(sample_irrs) >= 10:  # Need sufficient data points
                # Perform multiple linear regression
                from sklearn.linear_model import LinearRegression
                from sklearn.metrics import r2_score
                
                X = np.array(sample_points)
                y = np.array(sample_irrs)
                
                # Fit the regression model
                model = LinearRegression()
                model.fit(X, y)
                
                # Get coefficients
                intercept = model.intercept_
                coef_investment = model.coef_[0]
                coef_price = model.coef_[1]
                coef_cost = model.coef_[2]
                
                # Calculate R-squared
                y_pred = model.predict(X)
                r2 = r2_score(y, y_pred)
                
                # Display regression results
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("#### 📊 회귀분석 공식")
                    
                    # Format the regression equation
                    st.markdown(f"""
                    <div class="regression-box">
                        <h4 style="color: #fff;">IRR 예측 공식</h4>
                        <div style="font-family: 'Courier New', monospace; font-size: 1.1rem; background: white; padding: 1rem; border-radius: 4px;">
                            <strong>IRR = {intercept:.4f} + ({coef_investment:.6f} × 투자비변화율) + ({coef_price:.6f} × 판매가격변화율) + ({coef_cost:.6f} × 제조원가변화율)</strong>
                        </div>
                        <p style="margin-top: 1rem; color: #6c757d; font-size: 0.9rem;">
                            * 변화율은 백분율 단위 (예: 10% 증가 시 10 입력)
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Coefficient interpretation
                    st.markdown("#### 계수 해석")
                    
                    coef_data = {
                        '변수': ['투자비 변화율', '판매가격 변화율', '제조원가 변화율'],
                        '계수': [f"{coef_investment:.6f}", f"{coef_price:.6f}", f"{coef_cost:.6f}"],
                        '영향도': [
                            "부정적" if coef_investment < 0 else "긍정적",
                            "긍정적" if coef_price > 0 else "부정적", 
                            "부정적" if coef_cost < 0 else "긍정적"
                        ],
                        '해석': [
                            f"투자비 1% 증가 시 IRR {coef_investment:.4f} 변화",
                            f"판매가격 1% 증가 시 IRR {coef_price:.4f} 변화",
                            f"제조원가 1% 증가 시 IRR {coef_cost:.4f} 변화"
                        ]
                    }
                    
                    coef_df = pd.DataFrame(coef_data)
                    st.dataframe(coef_df, use_container_width=True)
                
                with col2:
                    st.markdown("#### 모델 성능")
                    
                    st.markdown(f"""
                    <div class="metric-container">
                        <h4>결정계수 (R²)</h4>
                        <h2>{r2:.3f}</h2>
                        <p>모델 설명력: {r2*100:.1f}%</p>
                        <p>샘플 수: {len(sample_irrs):,}개</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Model quality assessment
                    if r2 >= 0.8:
                        quality = "우수"
                        quality_color = "#28a745"
                    elif r2 >= 0.6:
                        quality = "양호"
                        quality_color = "#ffc107"
                    else:
                        quality = "보통"
                        quality_color = "#dc3545"
                    
    
                    
                    st.markdown("#### 활용 방법")
                    st.markdown("""
                    <div style="font-size: 0.9rem; color: #6c757d;">
                        <p>• 각 변수의 1% 변화가 IRR에 미치는 영향을 수치로 확인</p>
                        <p>• 투자 시나리오별 IRR 예측 가능</p>
                        <p>• 민감도가 높은 변수 우선 관리</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Sensitivity ranking
                st.markdown("#### 민감도 순위")
                
                sensitivity_ranking = [
                    ("투자비", abs(coef_investment)),
                    ("판매가격", abs(coef_price)),
                    ("제조원가", abs(coef_cost))
                ]
                sensitivity_ranking.sort(key=lambda x: x[1], reverse=True)
                
                rank_cols = st.columns(3)
                for i, (var_name, sensitivity) in enumerate(sensitivity_ranking):
                    with rank_cols[i]:
                        rank_color = "#FFD700" if i == 0 else "#C0C0C0" if i == 1 else "#CD7F32"
                        st.markdown(f"""
                        <div style="text-align: center; padding: 1rem; border: 2px solid {rank_color}; border-radius: 8px; background: white;">
                            <h3 style="color: {rank_color}; margin: 0;">{i+1}위</h3>
                            <h4 style="margin: 0.5rem 0;">{var_name}</h4>
                            <p style="margin: 0; color: #6c757d;">민감도: {sensitivity:.4f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
            else:
                st.error("회귀분석을 위한 충분한 데이터를 생성할 수 없습니다.")
                st.info("파라미터 범위를 조정하거나 입력 데이터를 확인해 주세요.")
                
        except Exception as e:
            st.error("회귀분석 계산 중 오류가 발생했습니다.")
            st.info("극단적인 파라미터 값으로 인한 계산 오류일 수 있습니다.")

def display_results(results, params):
    # Key metrics summary with skyblue styling
    st.markdown("""
    <div class="section-header">
        <h3> 주요 재무지표 요약</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <h4>IRR (내부수익률)</h4>
            <h2>{results['irr']:.2%}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_revenue = sum([v for v in results['total_revenue'].values() if v > 0])
        st.markdown(f"""
        <div class="metric-container">
            <h4>총 매출액</h4>
            <h2>${total_revenue:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        final_year = params['business_period'] + params['construction_period']
        final_cash_flow = results['net_cash_flow'].get(final_year, 0)
        st.markdown(f"""
        <div class="metric-container">
            <h4>최종년도 순현금흐름</h4>
            <h2>${final_cash_flow:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_investment = params['total_investment']
        st.markdown(f"""
        <div class="metric-container">
            <h4>총 투자비</h4>
            <h2>${total_investment:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Cash flow chart with skyblue theme
    st.markdown("""
    <div class="section-header">
        <h3> 연도별 순현금흐름</h3>
    </div>
    """, unsafe_allow_html=True)
    
    years = list(results['net_cash_flow'].keys())
    cash_flows = list(results['net_cash_flow'].values())
    
    fig = go.Figure()
    colors = ['#dc3545' if cf < 0 else '#000000' for cf in cash_flows]
    
    fig.add_trace(go.Bar(
        x=[f"Year {y}" for y in years],
        y=cash_flows,
        marker_color=colors,
        name="순현금흐름",
        marker_line=dict(color='rgba(0,0,0,0.1)', width=1)
    ))
    
    fig.update_layout(
        title={
            'text': "연도별 순현금흐름",
            'x': 0.5,
            'font': {'color': '#333333', 'size': 18, 'family': 'Noto Sans KR'}
        },
        xaxis_title="연도",
        yaxis_title="현금흐름 ($)",
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font={'color': '#333333', 'family': 'Noto Sans KR'},
        xaxis=dict(
            gridcolor='#f0f0f0',
            linecolor='#e0e0e0'
        ),
        yaxis=dict(
            gridcolor='#f0f0f0',
            linecolor='#e0e0e0'
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Revenue and costs over time with skyblue theme
    st.markdown("""
    <div class="section-header">
        <h3> 매출액 및 제조원가 추이</h3>
    </div>
    """, unsafe_allow_html=True)
    
    revenue_years = [y for y in years if results['total_revenue'].get(y, 0) > 0]
    revenues = [results['total_revenue'][y] for y in revenue_years]
    manufacturing_costs = [results['manufacturing_cost'][y] for y in revenue_years]
    
    fig2 = go.Figure()
    
    fig2.add_trace(go.Scatter(
        x=[f"Year {y}" for y in revenue_years],
        y=revenues,
        mode='lines+markers',
        name='총 매출액',
        line=dict(color='#000000', width=3),
        marker=dict(color='#000000', size=8)
    ))
    
    fig2.add_trace(go.Scatter(
        x=[f"Year {y}" for y in revenue_years],
        y=manufacturing_costs,
        mode='lines+markers',
        name='제조원가',
        line=dict(color='#6c757d', width=3),
        marker=dict(color='#6c757d', size=8)
    ))
    
    fig2.update_layout(
        title={
            'text': "매출액 및 제조원가 추이",
            'x': 0.5,
            'font': {'color': '#333333', 'size': 18, 'family': 'Noto Sans KR'}
        },
        xaxis_title="연도",
        yaxis_title="금액 ($)",
        legend=dict(x=0, y=1, bgcolor='rgba(255,255,255,0.9)', bordercolor='#e0e0e0', borderwidth=1),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font={'color': '#333333', 'family': 'Noto Sans KR'},
        xaxis=dict(
            gridcolor='#f0f0f0',
            linecolor='#e0e0e0'
        ),
        yaxis=dict(
            gridcolor='#f0f0f0',
            linecolor='#e0e0e0'
        )
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    

    
    # Detailed financial statements
    st.markdown("""
    <div class="section-header">
        <h3> 상세 재무제표</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 손익계산서 Table
    st.markdown("#### 손익계산서")
    df_income_statement = pd.DataFrame()
    
    for year in years:
        year_data = {
            '연도': f"Year {year}",
            '총매출액': results['total_revenue'].get(year, 0),
            '제조원가': results['manufacturing_cost'].get(year, 0),
            '판매관리비': results['sales_admin_expense'].get(year, 0),
            'EBIT': results['ebit'].get(year, 0),
            '금융비용': results['financial_cost'].get(year, 0),
            '세전이익': results['pretax_income'].get(year, 0),
            '법인세': results['corporate_tax'].get(year, 0),
            '순이익': results['net_income'].get(year, 0)
        }
        df_income_statement = pd.concat([df_income_statement, pd.DataFrame([year_data])], ignore_index=True)
    
    # Format numbers for income statement
    numeric_cols = df_income_statement.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if col != '연도':
            df_income_statement[col] = df_income_statement[col].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else "$0")
    
    st.dataframe(df_income_statement, use_container_width=True)
    
    # Free Cash Flow Table
    st.markdown("#### Free Cash Flow")
    df_cashflow = pd.DataFrame()
    
    for year in years:
        year_data = {
            '연도': f"Year {year}",
            '현금유입': results['cash_inflow'].get(year, 0),
            '순이익': results['net_income'].get(year, 0),
            '금융비용': results['financial_cost'].get(year, 0),
            '감가상각': results['depreciation'].get(year, 0),
            '잔존가치': results['residual_value'].get(year, 0),
            '운전자금유입': results['working_capital_inflow'].get(year, 0),
            '현금유출': results['cash_outflow'].get(year, 0),
            '투자비': results['investment'].get(year, 0),
            '운전자금유출': results['working_capital_increase'].get(year, 0)
        }
        df_cashflow = pd.concat([df_cashflow, pd.DataFrame([year_data])], ignore_index=True)
    
    # Format numbers for cash flow
    numeric_cols = df_cashflow.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if col != '연도':
            df_cashflow[col] = df_cashflow[col].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else "$0")
    
    st.dataframe(df_cashflow, use_container_width=True)
    
    # Download button for results
    col1, col2 = st.columns(2)
    with col1:
        csv_income = df_income_statement.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="손익계산서 CSV 다운로드",
            data=csv_income,
            file_name="income_statement.csv",
            mime="text/csv"
        )
    
    with col2:
        csv_cashflow = df_cashflow.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="Cash Flow CSV 다운로드",
            data=csv_cashflow,
            file_name="cash_flow_statement.csv",
            mime="text/csv"
        )
    
    

def display_advanced_analysis(results, params):
    cost_data = st.session_state.get('cost_data', pd.DataFrame())
    sales_data = st.session_state.get('sales_data', pd.DataFrame())

if __name__ == "__main__":
    main()
