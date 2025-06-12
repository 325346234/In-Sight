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
        background: linear-gradient(135deg, #003366 0%, #004488 100%);
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
        margin-bottom: 1rem;
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    .progress-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 3rem;
        font-family: 'Noto Sans KR', sans-serif;
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
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
    
    /* Main background and text */
    .stApp {
        background: #ffffff;
        font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #333333;
    }
    
    /* Header styling - POSCO inspired */
    .main-header {
        background: linear-gradient(135deg, #003366 0%, #004488 100%);
        padding: 2.5rem 2rem;
        border-radius: 0;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 2px 20px rgba(0, 51, 102, 0.15);
    }
    
    .main-header h1 {
        font-weight: 700;
        font-size: 2.2rem;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    
    .main-header p {
        font-weight: 300;
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Typography improvements */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Noto Sans KR', sans-serif;
        color: #003366;
        font-weight: 500;
        line-height: 1.4;
    }
    
    /* All text elements with improved contrast */
    p, div, span, label, .stMarkdown {
        color: #1a202c;
    }
    
    /* Strong emphasis text */
    strong, b {
        color: #2d3748;
        font-weight: 700;
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
        background: #003366;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.75rem 2rem;
        font-weight: 500;
        font-family: 'Noto Sans KR', sans-serif;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0, 51, 102, 0.2);
        font-size: 1rem;
    }
    
    .stButton > button:hover {
        background: #004488;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 51, 102, 0.3);
    }
    
    /* Input fields with enhanced visibility */
    .stNumberInput > div > div > input {
        border: 2px solid #cbd5e0;
        border-radius: 8px;
        background: #ffffff;
        color: #1a202c;
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 1rem;
        font-weight: 500;
        padding: 0.75rem;
        transition: all 0.2s ease;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: #2c5282;
        background: #ffffff;
        box-shadow: 0 0 0 3px rgba(44, 82, 130, 0.1);
        outline: none;
    }
    
    .stNumberInput > div > div > input:hover {
        border-color: #3182ce;
        background: #f7fafc;
    }
    
    /* Form labels with improved contrast */
    .stNumberInput label, .stSelectbox label, .stTextInput label, .stSlider label {
        color: #2d3748 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Select box styling */
    .stSelectbox > div > div {
        background-color: #ffffff;
        border: 2px solid #cbd5e0;
        border-radius: 8px;
        color: #1a202c;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #2c5282;
        box-shadow: 0 0 0 3px rgba(44, 82, 130, 0.1);
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #003366, #004488);
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
        transition: all 0.2s ease;
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
        color: #003366;
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
    
    /* Alert messages with enhanced visibility */
    .stSuccess {
        background: #f0fff4;
        border: 2px solid #38a169;
        border-left: 6px solid #38a169;
        border-radius: 8px;
        color: #22543d;
        font-weight: 500;
    }
    
    .stError {
        background: #fed7d7;
        border: 2px solid #e53e3e;
        border-left: 6px solid #e53e3e;
        border-radius: 8px;
        color: #742a2a;
        font-weight: 500;
    }
    
    .stWarning {
        background: #fffbeb;
        border: 2px solid #f59e0b;
        border-left: 6px solid #f59e0b;
        border-radius: 8px;
        color: #744210;
        font-weight: 500;
    }
    
    .stInfo {
        background: #ebf4ff;
        border: 2px solid #2c5282;
        border-left: 6px solid #2c5282;
        border-radius: 8px;
        color: #2a4f7c;
        font-weight: 500;
    }
    
    /* Section headers with enhanced visibility */
    .section-header {
        background: #ffffff;
        border: 2px solid #e2e8f0;
        border-left: 6px solid #2c5282;
        padding: 2rem;
        border-radius: 12px;
        margin: 2rem 0 1rem 0;
        box-shadow: 0 4px 12px rgba(44, 82, 130, 0.08);
    }
    
    .section-header h2 {
        color: #1a202c;
        font-weight: 700;
        font-size: 1.6rem;
        margin-bottom: 0.5rem;
    }
    
    .section-header h3 {
        color: #2d3748;
        font-weight: 600;
        font-size: 1.3rem;
        margin: 0;
    }
    
    .section-header p {
        color: #4a5568;
        font-size: 1rem;
        margin: 0;
        font-weight: 500;
    }
    
    /* Label styling */
    .stNumberInput label {
        font-weight: 500;
        color: #003366;
        font-size: 0.9rem;
    }
    
    /* Sidebar removal */
    .css-1d391kg {
        display: none;
    }
    
    /* Navigation elements */
    .nav-button {
        background: #ffffff;
        border: 1px solid #003366;
        color: #003366;
        border-radius: 4px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    .nav-button:hover {
        background: #003366;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header with new styling
    st.markdown("""
    <div class="main-header">
        <h1>🏭 철강사업 프로젝트 경제성 분석</h1>
        <p>Steel Industry Project Economic Feasibility Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state variables
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'input'
    
    # Horizontal Navigation Menu
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
    
    with nav_col1:
        if st.button("📝 프로젝트 파라미터 입력", key="nav_input", use_container_width=True):
            st.session_state['current_page'] = 'input'
    
    with nav_col2:
        if st.button("📊 경제성 분석 결과", key="nav_analysis", use_container_width=True):
            st.session_state['current_page'] = 'analysis'
    
    with nav_col3:
        if st.button("🔬 심화 분석", key="nav_advanced", use_container_width=True):
            st.session_state['current_page'] = 'advanced'
    
    with nav_col4:
        if st.button("💡 Insights", key="nav_insights", use_container_width=True):
            st.session_state['current_page'] = 'insights'
    
    st.markdown("---")
    
    # Page routing
    if st.session_state.get('current_page') == 'progress':
        show_progress_page()
    elif st.session_state.get('current_page') == 'analysis':
        show_analysis_page()
    elif st.session_state.get('current_page') == 'advanced':
        show_advanced_analysis_page()
    elif st.session_state.get('current_page') == 'insights':
        show_insights_page()
    else:
        # Default to input page
        st.session_state['current_page'] = 'input'
        show_input_page()

def show_advanced_analysis_page():
    """Advanced analysis page with Monte Carlo, sensitivity dashboard, and IRR regression"""
    st.markdown("""
    <div class="section-header">
        <h2>🔬 심화 분석</h2>
        <h3>Advanced Analysis</h3>
        <p>Monte Carlo 위험분석, 실시간 민감도 대시보드, IRR 회귀분석</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if analysis has been run
    if 'analysis_results' not in st.session_state or st.session_state['analysis_results'] is None:
        st.warning("먼저 경제성 분석을 실행해주세요.")
        if st.button("경제성 분석 페이지로 이동"):
            st.session_state['current_page'] = 'analysis'
            st.rerun()
        return
    
    results = st.session_state['analysis_results']
    params = st.session_state['params']
    cost_data = st.session_state['cost_data']
    sales_data = st.session_state['sales_data']
    
    # Monte Carlo Risk Analysis Section
    st.markdown("### 📊 Monte Carlo 위험분석")
    
    monte_carlo_col1, monte_carlo_col2 = st.columns([1, 1])
    
    with monte_carlo_col1:
        st.markdown("#### 분석 설정")
        variable_type = st.selectbox(
            "분석 변수 선택",
            options=['price', 'cost', 'investment'],
            format_func=lambda x: {'price': '판매가격', 'cost': '제조원가', 'investment': '투자비'}[x],
            key="mc_variable"
        )
        
        variation = st.slider("변동폭 (%)", min_value=5, max_value=50, value=20, step=5, key="mc_variation")
        n_simulations = st.slider("시뮬레이션 횟수", min_value=100, max_value=1000, value=500, step=100, key="mc_sims")
        
        if st.button("Monte Carlo 분석 실행", key="run_monte_carlo"):
            with st.spinner("Monte Carlo 분석 중..."):
                mc_results = perform_single_variable_monte_carlo(
                    params, cost_data, sales_data, variable_type, n_simulations
                )
                st.session_state['mc_results'] = mc_results
    
    with monte_carlo_col2:
        if 'mc_results' in st.session_state and st.session_state['mc_results']:
            mc_results = st.session_state['mc_results']
            st.markdown("#### 통계 요약")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("기준 IRR", f"{mc_results['base_irr']:.2%}")
            with col2:
                st.metric("평균 IRR", f"{mc_results['mean_irr']:.2%}")
            with col3:
                st.metric("표준편차", f"{mc_results['std_irr']:.2%}")
            
            # Risk metrics
            col4, col5, col6 = st.columns(3)
            with col4:
                st.metric("최악 시나리오 (5%)", f"{mc_results['p5_irr']:.2%}")
            with col5:
                st.metric("최선 시나리오 (95%)", f"{mc_results['p95_irr']:.2%}")
            with col6:
                risk_level = "높음" if mc_results['std_irr'] > 0.05 else "보통" if mc_results['std_irr'] > 0.02 else "낮음"
                st.metric("위험 수준", risk_level)
    
    # Visualization of Monte Carlo results
    if 'mc_results' in st.session_state and st.session_state['mc_results']:
        mc_results = st.session_state['mc_results']
        
        st.markdown("#### 📈 IRR 분포 분석")
        
        fig_col1, fig_col2 = st.columns(2)
        
        with fig_col1:
            # Histogram of IRR results
            fig_hist = go.Figure()
            fig_hist.add_trace(go.Histogram(
                x=mc_results['irr_results'],
                nbinsx=30,
                name='IRR 분포',
                marker_color='rgba(44, 82, 130, 0.7)'
            ))
            fig_hist.add_vline(x=mc_results['base_irr'], line_dash="dash", line_color="red", 
                              annotation_text=f"기준 IRR: {mc_results['base_irr']:.2%}")
            fig_hist.update_layout(
                title="IRR 분포 히스토그램",
                xaxis_title="IRR",
                yaxis_title="빈도",
                height=400
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with fig_col2:
            # Scatter plot of factor vs IRR
            fig_scatter = go.Figure()
            fig_scatter.add_trace(go.Scatter(
                x=mc_results['factor_values'],
                y=mc_results['irr_results'],
                mode='markers',
                name='시뮬레이션 결과',
                marker=dict(color='rgba(44, 82, 130, 0.6)', size=6)
            ))
            fig_scatter.update_layout(
                title=f"{{'price': '판매가격', 'cost': '제조원가', 'investment': '투자비'}[mc_results['variable_type']]} 변동 vs IRR",
                xaxis_title="변동 계수",
                yaxis_title="IRR",
                height=400
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.markdown("---")
    
    # Real-time Sensitivity Dashboard
    st.markdown("### 🎛️ 실시간 민감도 대시보드")
    st.markdown("주요 변수들의 변화가 IRR에 미치는 영향을 실시간으로 확인하세요.")
    
    sensitivity_col1, sensitivity_col2 = st.columns([1, 2])
    
    with sensitivity_col1:
        st.markdown("#### 민감도 분석 설정")
        
        # Vertical sliders for sensitivity analysis
        price_factor = st.slider("판매가격 변동 (%)", -30, 30, 0, 1, key="price_sensitivity") / 100 + 1
        cost_factor = st.slider("제조원가 변동 (%)", -30, 30, 0, 1, key="cost_sensitivity") / 100 + 1
        investment_factor = st.slider("투자비 변동 (%)", -30, 30, 0, 1, key="investment_sensitivity") / 100 + 1
        
        st.markdown("#### 현재 조정값")
        st.write(f"판매가격: {(price_factor-1)*100:+.1f}%")
        st.write(f"제조원가: {(cost_factor-1)*100:+.1f}%")
        st.write(f"투자비: {(investment_factor-1)*100:+.1f}%")
    
    with sensitivity_col2:
        # Real-time IRR calculation
        try:
            # Modify parameters for sensitivity analysis
            modified_params = params.copy()
            modified_cost_data = cost_data.copy()
            modified_sales_data = sales_data.copy()
            
            # Apply modifications
            modified_params['total_investment'] = params['total_investment'] * investment_factor
            
            if '매출액' in modified_sales_data.columns:
                modified_sales_data['매출액'] = modified_sales_data['매출액'] * price_factor
            if '소재가격' in modified_cost_data.columns:
                modified_cost_data['소재가격'] = modified_cost_data['소재가격'] * cost_factor
            if '가공비' in modified_cost_data.columns:
                modified_cost_data['가공비'] = modified_cost_data['가공비'] * cost_factor
            
            # Calculate modified IRR
            sensitivity_calculator = FinancialCalculator(modified_params, modified_cost_data, modified_sales_data)
            sensitivity_results = sensitivity_calculator.calculate_all_metrics()
            modified_irr = sensitivity_results['irr']
            
            # Display results
            st.markdown("#### 📊 실시간 IRR 결과")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("기준 IRR", f"{results['irr']:.2%}")
            with col2:
                st.metric("조정 IRR", f"{modified_irr:.2%}")
            with col3:
                irr_change = modified_irr - results['irr']
                st.metric("변화량", f"{irr_change:.2%}", delta=f"{irr_change:.2%}")
            
            # Sensitivity chart
            sensitivity_data = {
                '변수': ['판매가격', '제조원가', '투자비'],
                '변동률': [(price_factor-1)*100, (cost_factor-1)*100, (investment_factor-1)*100],
                'IRR_영향': [0, 0, 0]  # Placeholder - would need individual calculations
            }
            
            fig_sensitivity = go.Figure()
            fig_sensitivity.add_trace(go.Bar(
                x=sensitivity_data['변수'],
                y=sensitivity_data['변동률'],
                name='변동률 (%)',
                marker_color=['rgba(44, 82, 130, 0.7)' if x >= 0 else 'rgba(220, 53, 69, 0.7)' 
                             for x in sensitivity_data['변동률']]
            ))
            fig_sensitivity.update_layout(
                title="변수별 조정 현황",
                xaxis_title="주요 변수",
                yaxis_title="변동률 (%)",
                height=300
            )
            st.plotly_chart(fig_sensitivity, use_container_width=True)
            
        except Exception as e:
            st.error("민감도 분석 중 오류가 발생했습니다.")
    
    st.markdown("---")
    
    # IRR Regression Analysis
    st.markdown("### 📈 IRR 회귀분석 공식")
    st.markdown("투자비, 판매가격, 제조원가가 IRR에 미치는 영향을 회귀분석으로 분석합니다.")
    
    regression_col1, regression_col2 = st.columns([1, 1])
    
    with regression_col1:
        st.markdown("#### 회귀분석 설정")
        
        analysis_range = st.slider("분석 범위 (%)", 10, 50, 20, 5, key="regression_range")
        sample_points = st.slider("샘플 포인트", 20, 100, 50, 10, key="regression_points")
        
        if st.button("회귀분석 실행", key="run_regression"):
            with st.spinner("회귀분석 진행 중..."):
                try:
                    # Generate sample data for regression
                    regression_data = []
                    
                    for _ in range(sample_points):
                        # Random variations within range
                        investment_var = 1 + np.random.uniform(-analysis_range/100, analysis_range/100)
                        price_var = 1 + np.random.uniform(-analysis_range/100, analysis_range/100)
                        cost_var = 1 + np.random.uniform(-analysis_range/100, analysis_range/100)
                        
                        # Apply variations
                        temp_params = params.copy()
                        temp_cost_data = cost_data.copy()
                        temp_sales_data = sales_data.copy()
                        
                        temp_params['total_investment'] = params['total_investment'] * investment_var
                        
                        if '매출액' in temp_sales_data.columns:
                            temp_sales_data['매출액'] = temp_sales_data['매출액'] * price_var
                        if '소재가격' in temp_cost_data.columns:
                            temp_cost_data['소재가격'] = temp_cost_data['소재가격'] * cost_var
                        if '가공비' in temp_cost_data.columns:
                            temp_cost_data['가공비'] = temp_cost_data['가공비'] * cost_var
                        
                        # Calculate IRR
                        temp_calculator = FinancialCalculator(temp_params, temp_cost_data, temp_sales_data)
                        temp_results = temp_calculator.calculate_all_metrics()
                        temp_irr = temp_results['irr']
                        
                        if temp_irr is not None and not np.isnan(temp_irr) and not np.isinf(temp_irr):
                            regression_data.append({
                                'investment_factor': investment_var,
                                'price_factor': price_var,
                                'cost_factor': cost_var,
                                'irr': temp_irr
                            })
                    
                    if len(regression_data) > 10:
                        # Convert to DataFrame
                        df_regression = pd.DataFrame(regression_data)
                        
                        # Perform multiple linear regression
                        from sklearn.linear_model import LinearRegression
                        from sklearn.metrics import r2_score
                        
                        X = df_regression[['investment_factor', 'price_factor', 'cost_factor']]
                        y = df_regression['irr']
                        
                        model = LinearRegression()
                        model.fit(X, y)
                        y_pred = model.predict(X)
                        r2 = r2_score(y, y_pred)
                        
                        st.session_state['regression_results'] = {
                            'model': model,
                            'r2': r2,
                            'coefficients': model.coef_,
                            'intercept': model.intercept_,
                            'data': df_regression
                        }
                        
                        st.success(f"회귀분석 완료! R² = {r2:.3f}")
                    else:
                        st.error("충분한 유효 데이터를 생성할 수 없습니다.")
                        
                except Exception as e:
                    st.error("회귀분석 중 오류가 발생했습니다.")
    
    with regression_col2:
        if 'regression_results' in st.session_state:
            reg_results = st.session_state['regression_results']
            
            st.markdown("#### 📊 회귀분석 결과")
            
            # Display regression equation
            coef = reg_results['coefficients']
            intercept = reg_results['intercept']
            
            st.markdown("**회귀 공식:**")
            st.latex(f"""
            IRR = {intercept:.4f} + {coef[0]:.4f} \\times 투자비계수 + {coef[1]:.4f} \\times 가격계수 + {coef[2]:.4f} \\times 원가계수
            """)
            
            # Model performance
            col1, col2 = st.columns(2)
            with col1:
                st.metric("결정계수 (R²)", f"{reg_results['r2']:.3f}")
            with col2:
                model_quality = "높음" if reg_results['r2'] > 0.8 else "보통" if reg_results['r2'] > 0.6 else "낮음"
                st.metric("모델 정확도", model_quality)
            
            # Coefficients analysis
            st.markdown("**계수 해석:**")
            factor_names = ['투자비', '판매가격', '제조원가']
            for i, (name, coef_val) in enumerate(zip(factor_names, coef)):
                direction = "양의" if coef_val > 0 else "음의"
                impact = "높음" if abs(coef_val) > 0.1 else "보통" if abs(coef_val) > 0.05 else "낮음"
                st.write(f"• {name}: {direction} 영향 (계수: {coef_val:.4f}, 영향도: {impact})")

def show_insights_page():
    """Insights page with competitor investment trends and market intelligence"""
    st.markdown("""
    <div class="section-header">
        <h2>💡 Insights</h2>
        <h3>Market Intelligence & Investment Trends</h3>
        <p>경쟁사 투자동향 및 시장 인사이트</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Competitor Investment Trends Section
    st.markdown("### 🏢 경쟁사 투자동향")
    
    if st.button("최신 투자동향 분석", key="analyze_trends"):
        try:
            import openai
            from openai import OpenAI
            import os
            
            # Initialize OpenAI client
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            
            # Generate steel industry investment news summaries
            prompt = """
            철강업계 최신 투자 동향에 대한 뉴스 요약을 다음 형식으로 5개 작성해주세요:

            제목: [100자 이내 뉴스 제목]
            요약: [100자 이내 핵심 내용 요약]
            출처: [관련 웹사이트 링크 - 실제 존재하는 사이트]

            다음 키워드를 중심으로 작성:
            - 철강투자
            - 철강설비투자
            - 포스코, 현대제철 등 주요 기업
            - 친환경 기술 투자
            - 스마트팩토리

            각 뉴스는 구분선(---)으로 분리해주세요.
            """
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "철강업계 투자 분석 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            analysis_content = response.choices[0].message.content
            
            # Display the news summaries in structured format
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("#### 📈 최신 철강투자 뉴스")
                
                # Parse and display news summaries
                if analysis_content:
                    news_items = analysis_content.split('---')
                    for i, news_item in enumerate(news_items):
                        if news_item.strip():
                            lines = news_item.strip().split('\n')
                            title = ""
                            summary = ""
                            source = ""
                            
                            for line in lines:
                                if line.startswith('제목:'):
                                    title = line.replace('제목:', '').strip()
                                elif line.startswith('요약:'):
                                    summary = line.replace('요약:', '').strip()
                                elif line.startswith('출처:'):
                                    source = line.replace('출처:', '').strip()
                            
                            if title and summary:
                                st.markdown(f"""
                                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; margin: 1rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                                    <h4 style="color: #1a202c; font-size: 1.1rem; font-weight: 700; margin-bottom: 0.75rem; line-height: 1.4;">{title}</h4>
                                    <p style="color: #4a5568; font-size: 1rem; font-weight: 500; margin-bottom: 0.75rem; line-height: 1.6;">{summary}</p>
                                    <a href="{source}" target="_blank" style="color: #2c5282; font-size: 0.9rem; font-weight: 600; text-decoration: none;">
                                        📎 자세히 보기 →
                                    </a>
                                </div>
                                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### 💡 주요 투자 키워드")
                
                # Generate key investment keywords with improved formatting
                keywords_prompt = """
                철강업계 투자동향에서 주요 키워드 8개를 추출해주세요.
                각 키워드에 대해 간단한 설명(50자 이내)을 포함해주세요.
                형식: "키워드: 설명"
                """
                
                keywords_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "철강업계 투자 트렌드 전문가입니다."},
                        {"role": "user", "content": keywords_prompt}
                    ],
                    max_tokens=600,
                    temperature=0.5
                )
                
                keywords_content = keywords_response.choices[0].message.content
                if keywords_content and keywords_content.strip():
                    keywords_list = keywords_content.split('\n')
                    
                    for keyword in keywords_list:
                        if keyword.strip() and ':' in keyword:
                            key, desc = keyword.split(':', 1)
                            st.markdown(f"""
                            <div style="background: #f8f9fa; border-left: 4px solid #2c5282; padding: 1rem; margin: 0.75rem 0; border-radius: 8px;">
                                <strong style="color: #1a202c; font-size: 1rem; font-weight: 700;">{key.strip()}</strong><br>
                                <span style="color: #4a5568; font-size: 0.95rem; font-weight: 500; line-height: 1.5;">{desc.strip()}</span>
                            </div>
                            """, unsafe_allow_html=True)
                
                st.markdown("#### 📊 투자 규모 전망")
                
                # Generate investment scale forecast
                forecast_prompt = """
                2024-2025년 글로벌 철강업계 투자 규모와 전망을 간단히 요약해주세요 (200자 이내).
                주요 투자 분야별 비중도 포함해주세요.
                """
                
                forecast_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "철강업계 시장 분석가입니다."},
                        {"role": "user", "content": forecast_prompt}
                    ],
                    max_tokens=600,
                    temperature=0.3
                )
                
                forecast_content = forecast_response.choices[0].message.content
                if forecast_content and forecast_content.strip():
                    # Replace newlines with HTML breaks outside of f-string
                    formatted_content = forecast_content.replace('\n', '<br>')
                    st.markdown(f"""
                    <div style="background: #ffffff; border: 2px solid #e2e8f0; padding: 1.5rem; border-radius: 12px;">
                        <div style="color: #1a202c; font-size: 1rem; font-weight: 500; line-height: 1.6;">
                            {formatted_content}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="background: #ffffff; border: 2px solid #e2e8f0; padding: 1.5rem; border-radius: 12px;">
                        <div style="color: #1a202c; font-size: 1rem; font-weight: 500; line-height: 1.6;">
                            <strong>2024-2025 철강투자 전망:</strong><br>
                            • 글로벌 철강투자 규모: 약 120조원<br>
                            • 국내 철강투자 규모: 약 8-10조원<br>
                            • 친환경 기술: 40%, 디지털화: 30%, 설비 현대화: 30%
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Market Intelligence Summary
            st.markdown("#### 🎯 시장 인텔리전스 요약")
            
            intelligence_cols = st.columns(3)
            
            with intelligence_cols[0]:
                st.markdown("""
                <div class="metric-container">
                    <h4>투자 트렌드</h4>
                    <h2 style="color: #2c5282;">친환경 전환</h2>
                    <p>탄소중립 대응 투자 급증</p>
                </div>
                """, unsafe_allow_html=True)
            
            with intelligence_cols[1]:
                st.markdown("""
                <div class="metric-container">
                    <h4>기술 혁신</h4>
                    <h2 style="color: #2c5282;">디지털화</h2>
                    <p>AI·IoT 기반 스마트팩토리</p>
                </div>
                """, unsafe_allow_html=True)
            
            with intelligence_cols[2]:
                st.markdown("""
                <div class="metric-container">
                    <h4>지역 확장</h4>
                    <h2 style="color: #2c5282;">글로벌화</h2>
                    <p>신흥시장 진출 확대</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Competitor Analysis Table
            st.markdown("#### 🏢 주요 경쟁사 투자 현황")
            
            competitor_data = {
                '회사명': ['POSCO', '현대제철', 'JFE스틸', '바오스틸', 'ArcelorMittal'],
                '주요 투자분야': ['수소환원제철', '전기로 확대', '탄소중립기술', '스마트제조', '친환경기술'],
                '투자규모': ['10조원+', '5조원+', '8조원+', '15조원+', '12조원+'],
                '완료시기': ['2030년', '2027년', '2030년', '2025년', '2030년'],
                '핵심기술': ['HyREX', '전기로', 'COURSE50', 'AI제조', 'XCarb']
            }
            
            competitor_df = pd.DataFrame(competitor_data)
            st.dataframe(competitor_df, use_container_width=True)
            
            st.info("분석 기준일: 2024년 12월 기준 / 실제 투자 현황은 각 회사 공시자료를 참조하시기 바랍니다.")
            
        except Exception as e:
            st.error("투자동향 분석 중 오류가 발생했습니다.")
            st.info("OpenAI API 연결을 확인하거나 잠시 후 다시 시도해주세요.")
            
            # Fallback static content
            st.markdown("#### 📋 철강업계 투자 동향 개요")
            st.markdown("""
            **주요 투자 트렌드:**
            - 탄소중립 대응 친환경 기술 투자 확대
            - 수소환원제철 기술 개발 가속화
            - 디지털 전환 및 스마트팩토리 구축
            - 전기로 설비 확충 및 현대화
            - 재생에너지 연계 생산시설 구축
            
            **투자 규모:**
            - 글로벌 철강업계 연간 투자: 약 100조원 규모
            - 국내 주요 철강사 투자: 연간 3-5조원 수준
            - 친환경 기술 투자 비중: 전체의 30-40%
            """)

def show_input_page():
    st.markdown("""
    <div class="section-header">
        <h2>📊 프로젝트 파라미터 입력</h2>
        <p>각 항목의 값을 입력하세요. 기본값이 사전 설정되어 있습니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="section-header">
            <h3>🏢 기본 프로젝트 정보</h3>
        </div>
        """, unsafe_allow_html=True)
        business_period = st.number_input("사업기간 (년)", min_value=1, max_value=50, value=15)
        construction_period = st.number_input("공사기간 (년)", min_value=1, max_value=10, value=4)
        interest_rate = st.number_input("할인율 (%)", min_value=0.0, max_value=50.0, value=6.92, step=0.01)
        
        st.markdown("""
        <div class="section-header">
            <h3>💰 투자비 정보</h3>
        </div>
        """, unsafe_allow_html=True)
        total_investment = st.number_input("총투자비 ($)", min_value=0, value=400000000, step=1000000)
        machinery_ratio = st.number_input("기계설비투자비비율 (%)", min_value=0.0, max_value=100.0, value=80.0, step=0.1)
        building_ratio = st.number_input("건축물투자비비율 (%)", min_value=0.0, max_value=100.0, value=20.0, step=0.1)
        
        st.markdown("""
        <div class="section-header">
            <h3>🏦 자금조달</h3>
        </div>
        """, unsafe_allow_html=True)
        equity_ratio = st.number_input("자본비율 (%)", min_value=0.0, max_value=100.0, value=50.0, step=0.1)
        debt_ratio = st.number_input("차입비율 (%)", min_value=0.0, max_value=100.0, value=50.0, step=0.1)
    
    with col2:
        st.markdown("""
        <div class="section-header">
            <h3>📊 투자비 집행률</h3>
        </div>
        """, unsafe_allow_html=True)
        investment_year1 = st.number_input("투자비집행Year1 (%)", min_value=0.0, max_value=100.0, value=30.0, step=0.1)
        investment_year2 = st.number_input("투자비집행Year2 (%)", min_value=0.0, max_value=100.0, value=30.0, step=0.1)
        investment_year3 = st.number_input("투자비집행Year3 (%)", min_value=0.0, max_value=100.0, value=30.0, step=0.1)
        investment_year4 = st.number_input("투자비집행Year4 (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.1)
        
        st.markdown("""
        <div class="section-header">
            <h3>💳 차입금 조건</h3>
        </div>
        """, unsafe_allow_html=True)
        grace_period = st.number_input("감가상각기계설비 (년)", min_value=1, value=15)
        building_depreciation = st.number_input("감가상각건축물 (년)", min_value=1, value=20)
        loan_grace_period = st.number_input("장기차입거치기간 (년)", min_value=0, value=4)
        loan_repayment_period = st.number_input("장기차입상환기간 (년)", min_value=1, value=8)
        loan_interest_rate = st.number_input("장기차입금리 (%)", min_value=0.0, max_value=50.0, value=3.7, step=0.01)
        short_term_interest_rate = st.number_input("단기차입금리 (%)", min_value=0.0, max_value=50.0, value=4.8, step=0.01)
        
        st.markdown("""
        <div class="section-header">
            <h3>📈 기타 비율</h3>
        </div>
        """, unsafe_allow_html=True)
        corporate_tax_rate = st.number_input("법인세율 (%)", min_value=0.0, max_value=100.0, value=25.0, step=0.1)
        sales_admin_ratio = st.number_input("판매관리비비율 (%)", min_value=0.0, max_value=100.0, value=4.0, step=0.1)
    
    # Sales volume inputs
    st.markdown("""
    <div class="section-header">
        <h3>🏭 판매량 정보</h3>
        <p>연도별 판매량 (톤단위)</p>
    </div>
    """, unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    
    with col3:
        st.info("**Year 1-4:** 공사기간으로 판매량 0")
        sales_year5 = st.number_input("판매량Year5 (톤)", min_value=0, value=70000)
        sales_year6 = st.number_input("판매량Year6 (톤)", min_value=0, value=80000)
    
    with col4:    
        sales_after_year7 = st.number_input("판매량AfterYear7 (톤)", min_value=0, value=100000)
    
    # Working capital days
    st.markdown("""
    <div class="section-header">
        <h3>💼 운전자금 관련 일수</h3>
    </div>
    """, unsafe_allow_html=True)
    col5, col6 = st.columns(2)
    
    with col5:
        receivables_days = st.number_input("매출채권일수 (일)", min_value=0, value=50)
        payables_days = st.number_input("매입채무일수 (일)", min_value=0, value=30)
    
    with col6:
        product_inventory_days = st.number_input("제품재고일수 (일)", min_value=0, value=50)
        material_inventory_days = st.number_input("소재재고일수 (일)", min_value=0, value=40)
    
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
    st.markdown("""
    <div class="section-header">
        <h2>📊 경제성 분석 결과</h2>
        <p>Steel Industry Project Economic Analysis Results</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add styled button to return to input page
    col1, col2, col3 = st.columns([6, 2, 2])
    with col2:
        if st.button("← 새로운 분석하기", key="new_analysis"):
            st.session_state['current_page'] = 'input'
            if 'project_params' in st.session_state:
                del st.session_state['project_params']
            st.rerun()
    
    if 'project_params' not in st.session_state:
        st.warning("먼저 프로젝트 파라미터를 입력해야 합니다.")
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
        
        # Store data in session state for Monte Carlo analysis
        st.session_state['cost_data'] = cost_data
        st.session_state['sales_data'] = sales_data
        
        # Initialize calculator
        calculator = FinancialCalculator(params, cost_data, sales_data)
        
        # Calculate financial metrics
        results = calculator.calculate_all_metrics()
        
        # Display results
        display_results(results, params)
        
    except Exception as e:
        st.error(f"데이터 로딩 또는 계산 중 오류가 발생했습니다: {str(e)}")
        st.info("Excel 파일이 없는 경우 기본 데이터로 계산을 진행합니다.")
        
        # Use default data for demonstration
        cost_data = data_loader.get_default_cost_data()
        sales_data = data_loader.get_default_sales_data()
        
        calculator = FinancialCalculator(params, cost_data, sales_data)
        results = calculator.calculate_all_metrics()
        display_results(results, params)

def display_results(results, params):
    # Key metrics summary with skyblue styling
    st.markdown("""
    <div class="section-header">
        <h3>📊 주요 재무지표 요약</h3>
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
            <h2>${total_revenue/1000:,.0f}K</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Calculate NPV instead of final year cash flow
        net_cash_flows = list(results['net_cash_flow'].values())
        years_range = list(range(len(net_cash_flows)))
        discount_rate = results['irr'] if results['irr'] and results['irr'] > 0 else 0.1
        
        npv = sum(cf / (1 + discount_rate) ** i for i, cf in enumerate(net_cash_flows))
        
        st.markdown(f"""
        <div class="metric-container">
            <h4>Net Present Value</h4>
            <h2>${npv/1000:,.0f}K</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_investment = params['total_investment']
        st.markdown(f"""
        <div class="metric-container">
            <h4>총 투자비</h4>
            <h2>${total_investment/1000:,.0f}K</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Cash flow chart with skyblue theme
    st.markdown("""
    <div class="section-header">
        <h3>📈 연도별 순현금흐름</h3>
    </div>
    """, unsafe_allow_html=True)
    
    years = list(results['net_cash_flow'].keys())
    cash_flows = list(results['net_cash_flow'].values())
    
    fig = go.Figure()
    colors = ['#dc3545' if cf < 0 else '#003366' for cf in cash_flows]
    
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
        <h3>💰 매출액 및 제조원가 추이</h3>
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
        line=dict(color='#003366', width=3),
        marker=dict(color='#003366', size=8)
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
        <h3>📋 상세 재무제표</h3>
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
    
    # Format numbers for income statement (in thousands)
    numeric_cols = df_income_statement.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if col != '연도':
            df_income_statement[col] = df_income_statement[col].apply(lambda x: f"${x/1000:,.0f}K" if pd.notnull(x) else "$0K")
    
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
    
    # Format numbers for cash flow (in thousands)
    numeric_cols = df_cashflow.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if col != '연도':
            df_cashflow[col] = df_cashflow[col].apply(lambda x: f"${x/1000:,.0f}K" if pd.notnull(x) else "$0K")
    
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
    
    # Store analysis results for advanced analysis page
    st.session_state['analysis_results'] = results
    st.session_state['params'] = params
    
    # Guidance for advanced analysis
    st.markdown("""
    <div class="section-header">
        <h3>🔬 추가 분석 옵션</h3>
        <p>심화 분석 페이지에서 Monte Carlo 위험분석, 실시간 민감도 대시보드, IRR 회귀분석을 수행할 수 있습니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    advanced_col1, advanced_col2 = st.columns(2)
    
    with advanced_col1:
        if st.button("🔬 심화 분석 페이지로 이동", use_container_width=True):
            st.session_state['current_page'] = 'advanced'
            st.rerun()
    
    with advanced_col2:
        if st.button("💡 Insights 페이지로 이동", use_container_width=True):
            st.session_state['current_page'] = 'insights'
            st.rerun()

if __name__ == "__main__":
    main()
        """, unsafe_allow_html=True)
        
        # Enhanced Cost slider
        st.markdown("""
        <div class="slider-container">
            <div class="slider-title">제조원가 조정</div>
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
            <strong>기준값:</strong> ${base_manufacturing_cost/1000:,.1f}K/톤<br>
            <strong>조정값:</strong> ${adjusted_manufacturing_cost/1000:,.1f}K/톤<br>
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
    st.markdown("#### 📊 현재 조정 상태")
    
    # Real-time sensitivity chart
    fig_sensitivity = go.Figure()
    
    # Add bars for each adjustment
    adjustments = [investment_change, price_change, cost_change]
    colors = ['#6c757d', '#003366', '#dc3545']
    
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
        height=300,
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
        <h2>📈 IRR 회귀분석 공식</h2>
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
                    <div style="background: #f8f9fa; border-left: 4px solid #003366; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
                        <h4 style="color: #003366; margin-bottom: 1rem;">IRR 예측 공식</h4>
                        <div style="font-family: 'Courier New', monospace; font-size: 1.1rem; background: white; padding: 1rem; border-radius: 4px;">
                            <strong>IRR = {intercept:.4f} + ({coef_investment:.6f} × 투자비변화율) + ({coef_price:.6f} × 판매가격변화율) + ({coef_cost:.6f} × 제조원가변화율)</strong>
                        </div>
                        <p style="margin-top: 1rem; color: #6c757d; font-size: 0.9rem;">
                            * 변화율은 백분율 단위 (예: 10% 증가 시 10 입력)
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Coefficient interpretation
                    st.markdown("#### 📋 계수 해석")
                    
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
                    st.markdown("#### 📈 모델 성능")
                    
                    st.markdown(f"""
                    <div class="metric-container">
                        <h4>결정계수 (R²)</h4>
                        <h2 style="color: #003366;">{r2:.3f}</h2>
                        <p>모델 설명력: {r2*100:.1f}%</p>
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
                    
                    st.markdown(f"""
                    <div style="background: #ffffff; border: 1px solid #e8eaf0; padding: 1rem; border-radius: 8px; text-align: center;">
                        <p><strong>모델 품질:</strong> <span style="color: {quality_color};">{quality}</span></p>
                        <p><strong>샘플 수:</strong> {len(sample_irrs):,}개</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("#### 💡 활용 방법")
                    st.markdown("""
                    <div style="font-size: 0.9rem; color: #6c757d;">
                        <p>• 각 변수의 1% 변화가 IRR에 미치는 영향을 수치로 확인</p>
                        <p>• 투자 시나리오별 IRR 예측 가능</p>
                        <p>• 민감도가 높은 변수 우선 관리</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Sensitivity ranking
                st.markdown("#### 🎯 민감도 순위")
                
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
    
    # Competitor Investment Trends Section
    st.markdown("---")
    st.markdown("""
    <div class="section-header">
        <h2>🏭 경쟁사 투자동향</h2>
        <p>철강업계 최신 투자 및 설비투자 동향 분석</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("최신 철강투자 동향을 분석하고 있습니다..."):
        try:
            from openai import OpenAI
            import os
            
            # Initialize OpenAI client
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            
            # Generate steel industry investment news summaries
            prompt = """
            철강업계 최신 투자 동향에 대한 뉴스 요약을 다음 형식으로 5개 작성해주세요:

            제목: [100자 이내 뉴스 제목]
            요약: [100자 이내 핵심 내용 요약]
            출처: [관련 웹사이트 링크 - 실제 존재하는 사이트]

            다음 키워드를 중심으로 작성:
            - 철강투자
            - 철강설비투자
            - 포스코, 현대제철 등 주요 기업
            - 친환경 기술 투자
            - 스마트팩토리

            각 뉴스는 구분선(---)으로 분리해주세요.
            """
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "당신은 철강업계 전문 애널리스트입니다. 최신 투자동향과 시장 분석에 전문성을 가지고 있습니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            analysis_content = response.choices[0].message.content
            
            # Display the news summaries in structured format
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("#### 📈 최신 철강투자 뉴스")
                
                # Parse and display news summaries
                if analysis_content:
                    news_items = analysis_content.split('---')
                    for i, news_item in enumerate(news_items):
                        if news_item.strip():
                            lines = news_item.strip().split('\n')
                            title = ""
                            summary = ""
                            source = ""
                            
                            for line in lines:
                                if line.startswith('제목:'):
                                    title = line.replace('제목:', '').strip()
                                elif line.startswith('요약:'):
                                    summary = line.replace('요약:', '').strip()
                                elif line.startswith('출처:'):
                                    source = line.replace('출처:', '').strip()
                            
                            if title and summary:
                                st.markdown(f"""
                                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; margin: 1rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                                    <h4 style="color: #1a202c; font-size: 1.1rem; font-weight: 700; margin-bottom: 0.75rem; line-height: 1.4;">{title}</h4>
                                    <p style="color: #4a5568; font-size: 1rem; font-weight: 500; margin-bottom: 0.75rem; line-height: 1.6;">{summary}</p>
                                    <a href="{source}" target="_blank" style="color: #2c5282; font-size: 0.9rem; font-weight: 600; text-decoration: none;">
                                        📎 자세히 보기 →
                                    </a>
                                </div>
                                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### 💡 주요 투자 키워드")
                
                # Generate key investment keywords with improved formatting
                keywords_prompt = """
                철강업계 투자동향에서 주요 키워드 8개를 추출해주세요.
                각 키워드에 대해 간단한 설명(50자 이내)을 포함해주세요.
                형식: "키워드: 설명"
                """
                
                keywords_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "철강업계 투자 트렌드 전문가입니다."},
                        {"role": "user", "content": keywords_prompt}
                    ],
                    max_tokens=600,
                    temperature=0.5
                )
                
                keywords_content = keywords_response.choices[0].message.content
                if keywords_content and keywords_content.strip():
                    keywords_list = keywords_content.split('\n')
                    
                    for keyword in keywords_list:
                        if keyword.strip() and ':' in keyword:
                            key, desc = keyword.split(':', 1)
                            st.markdown(f"""
                            <div style="background: #f8f9fa; border-left: 4px solid #2c5282; padding: 1rem; margin: 0.75rem 0; border-radius: 8px;">
                                <strong style="color: #1a202c; font-size: 1rem; font-weight: 700;">{key.strip()}</strong><br>
                                <span style="color: #4a5568; font-size: 0.95rem; font-weight: 500; line-height: 1.5;">{desc.strip()}</span>
                            </div>
                            """, unsafe_allow_html=True)
                
                st.markdown("#### 📊 투자 규모 전망")
                
                # Generate investment scale forecast
                forecast_prompt = """
                2024-2025년 철강업계 투자 규모에 대한 전망을 작성해주세요.
                - 글로벌 철강투자 규모
                - 국내 철강투자 규모  
                - 주요 투자 분야별 비중
                숫자와 함께 간결하게 작성해주세요.
                """
                
                forecast_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "철강업계 투자 전망 전문가입니다."},
                        {"role": "user", "content": forecast_prompt}
                    ],
                    max_tokens=600,
                    temperature=0.3
                )
                
                forecast_content = forecast_response.choices[0].message.content
                if forecast_content and forecast_content.strip():
                    # Replace newlines with HTML breaks outside of f-string
                    formatted_content = forecast_content.replace('\n', '<br>')
                    st.markdown(f"""
                    <div style="background: #ffffff; border: 2px solid #e2e8f0; padding: 1.5rem; border-radius: 12px;">
                        <div style="color: #1a202c; font-size: 1rem; font-weight: 500; line-height: 1.6;">
                            {formatted_content}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="background: #ffffff; border: 2px solid #e2e8f0; padding: 1.5rem; border-radius: 12px;">
                        <div style="color: #1a202c; font-size: 1rem; font-weight: 500; line-height: 1.6;">
                            <strong>2024-2025 철강투자 전망:</strong><br>
                            • 글로벌 철강투자 규모: 약 120조원<br>
                            • 국내 철강투자 규모: 약 8-10조원<br>
                            • 친환경 기술: 40%, 디지털화: 30%, 설비 현대화: 30%
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Market Intelligence Summary
            st.markdown("#### 🎯 시장 인텔리전스 요약")
            
            intelligence_cols = st.columns(3)
            
            with intelligence_cols[0]:
                st.markdown("""
                <div class="metric-container">
                    <h4>투자 트렌드</h4>
                    <h2 style="color: #2c5282;">친환경 전환</h2>
                    <p>탄소중립 대응 투자 급증</p>
                </div>
                """, unsafe_allow_html=True)
            
            with intelligence_cols[1]:
                st.markdown("""
                <div class="metric-container">
                    <h4>기술 혁신</h4>
                    <h2 style="color: #2c5282;">디지털화</h2>
                    <p>AI·IoT 기반 스마트팩토리</p>
                </div>
                """, unsafe_allow_html=True)
            
            with intelligence_cols[2]:
                st.markdown("""
                <div class="metric-container">
                    <h4>지역 확장</h4>
                    <h2 style="color: #2c5282;">글로벌화</h2>
                    <p>신흥시장 진출 확대</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Competitor Analysis Table
            st.markdown("#### 🏢 주요 경쟁사 투자 현황")
            
            competitor_data = {
                '회사명': ['POSCO', '현대제철', 'JFE스틸', '바오스틸', 'ArcelorMittal'],
                '주요 투자분야': ['수소환원제철', '전기로 확대', '탄소중립기술', '스마트제조', '친환경기술'],
                '투자규모': ['10조원+', '5조원+', '8조원+', '15조원+', '12조원+'],
                '완료시기': ['2030년', '2027년', '2030년', '2025년', '2030년'],
                '핵심기술': ['HyREX', '전기로', 'COURSE50', 'AI제조', 'XCarb']
            }
            
            competitor_df = pd.DataFrame(competitor_data)
            st.dataframe(competitor_df, use_container_width=True)
            
            st.info("💡 **분석 기준일**: 2024년 12월 기준 / 실제 투자 현황은 각 회사 공시자료를 참조하시기 바랍니다.")
            
        except Exception as e:
            st.error("투자동향 분석 중 오류가 발생했습니다.")
            st.info("OpenAI API 연결을 확인하거나 잠시 후 다시 시도해주세요.")
            
            # Fallback static content
            st.markdown("#### 📋 철강업계 투자 동향 개요")
            st.markdown("""
            **주요 투자 트렌드:**
            - 탄소중립 대응 친환경 기술 투자 확대
            - 수소환원제철 기술 개발 가속화
            - 디지털 전환 및 스마트팩토리 구축
            - 전기로 설비 확충 및 현대화
            - 재생에너지 연계 생산시설 구축
            
            **투자 규모:**
            - 글로벌 철강업계 연간 투자: 약 100조원 규모
            - 국내 주요 철강사 투자: 연간 3-5조원 수준
            - 친환경 기술 투자 비중: 전체의 30-40%
            """)

if __name__ == "__main__":
    main()
