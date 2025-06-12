import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
from financial_calculator import FinancialCalculator
from data_loader import DataLoader
from scipy import stats
from sklearn.linear_model import LinearRegression
from openai import OpenAI
import os

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
    
    .progress-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    .spinner {
        font-size: 4rem;
        animation: spin 2s linear infinite;
        margin-bottom: 2rem;
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
    
    /* Section headers */
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
            st.markdown("#### 📊 통계 요약")
            
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
    
    # Dynamic Sensitivity Analysis Dashboard
    st.markdown("---")
    st.markdown("### 🎛️ 실시간 민감도 대시보드")
    
    sensitivity_col1, sensitivity_col2 = st.columns([1, 2])
    
    with sensitivity_col1:
        st.markdown("#### 변수 조정")
        
        # Vertical sliders for dynamic sensitivity
        sales_factor = st.slider(
            "판매가격 조정 (%)",
            min_value=-50,
            max_value=50,
            value=0,
            step=5,
            key="sales_sensitivity"
        )
        
        cost_factor = st.slider(
            "제조원가 조정 (%)",
            min_value=-50,
            max_value=50,
            value=0,
            step=5,
            key="cost_sensitivity"
        )
        
        investment_factor = st.slider(
            "총투자비 조정 (%)",
            min_value=-50,
            max_value=50,
            value=0,
            step=5,
            key="investment_sensitivity"
        )
        
        # Real-time IRR calculation
        if st.button("실시간 IRR 계산", key="realtime_irr"):
            modified_params = params.copy()
            modified_params['sales_price_factor'] = 1 + (sales_factor / 100)
            modified_params['cost_factor'] = 1 + (cost_factor / 100)
            modified_params['total_investment'] = params['total_investment'] * (1 + investment_factor / 100)
            
            try:
                calculator = FinancialCalculator(modified_params, cost_data, sales_data)
                modified_results = calculator.calculate_all_metrics()
                modified_irr = modified_results['irr']
                
                st.session_state['sensitivity_irr'] = modified_irr
                st.session_state['sensitivity_factors'] = {
                    'sales': sales_factor,
                    'cost': cost_factor,
                    'investment': investment_factor
                }
            except Exception as e:
                st.error("민감도 분석 중 오류가 발생했습니다.")
    
    with sensitivity_col2:
        if 'sensitivity_irr' in st.session_state:
            st.markdown("#### 📊 민감도 분석 결과")
            
            base_irr = results['irr']
            sensitivity_irr = st.session_state['sensitivity_irr']
            factors = st.session_state['sensitivity_factors']
            
            # Display comparison
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("기준 IRR", f"{base_irr:.2%}")
            with col2:
                st.metric("조정 IRR", f"{sensitivity_irr:.2%}")
            with col3:
                irr_change = sensitivity_irr - base_irr
                st.metric("IRR 변화", f"{irr_change:.2%}", delta=f"{irr_change:.2%}")
            
            # Sensitivity chart
            fig_sensitivity = go.Figure()
            
            factor_names = ['판매가격', '제조원가', '총투자비']
            factor_values = [factors['sales'], factors['cost'], factors['investment']]
            
            fig_sensitivity.add_trace(go.Bar(
                x=factor_names,
                y=factor_values,
                name='변수 조정 (%)',
                marker_color=['green' if v >= 0 else 'red' for v in factor_values]
            ))
            
            fig_sensitivity.update_layout(
                title="변수별 조정 현황",
                xaxis_title="변수",
                yaxis_title="조정률 (%)",
                height=300
            )
            
            st.plotly_chart(fig_sensitivity, use_container_width=True)
    
    # IRR Regression Analysis Section
    st.markdown("---")
    st.markdown("### 📈 IRR 회귀분석")
    
    regression_col1, regression_col2 = st.columns([1, 1])
    
    with regression_col1:
        st.markdown("#### 분석 설정")
        
        regression_variable = st.selectbox(
            "회귀분석 변수 선택",
            options=['price', 'cost', 'investment'],
            format_func=lambda x: {'price': '판매가격', 'cost': '원가실적', 'investment': '총투자비'}[x],
            key="regression_variable"
        )
        
        regression_range = st.slider(
            "분석 범위 (%)",
            min_value=10,
            max_value=100,
            value=50,
            step=10,
            key="regression_range"
        )
        
        if st.button("회귀분석 실행", key="run_regression"):
            with st.spinner("회귀분석 실행 중..."):
                # Generate data points for regression
                factor_range = np.linspace(-regression_range/100, regression_range/100, 21)
                irr_values = []
                factor_values = []
                
                for factor in factor_range:
                    try:
                        modified_params = params.copy()
                        
                        if regression_variable == 'price':
                            modified_params['sales_price_factor'] = 1 + factor
                        elif regression_variable == 'cost':
                            modified_params['cost_factor'] = 1 + factor
                        elif regression_variable == 'investment':
                            modified_params['total_investment'] = params['total_investment'] * (1 + factor)
                        
                        calculator = FinancialCalculator(modified_params, cost_data, sales_data)
                        reg_results = calculator.calculate_all_metrics()
                        reg_irr = reg_results['irr']
                        
                        if reg_irr is not None and not (np.isnan(reg_irr) or np.isinf(reg_irr)):
                            irr_values.append(reg_irr)
                            factor_values.append(factor * 100)
                    except:
                        continue
                
                if len(irr_values) > 5:
                    # Perform linear regression
                    
                    X = np.array(factor_values).reshape(-1, 1)
                    y = np.array(irr_values)
                    
                    reg_model = LinearRegression()
                    reg_model.fit(X, y)
                    
                    st.session_state['regression_results'] = {
                        'factor_values': factor_values,
                        'irr_values': irr_values,
                        'slope': reg_model.coef_[0],
                        'intercept': reg_model.intercept_,
                        'r_squared': reg_model.score(X, y),
                        'variable': regression_variable
                    }
                else:
                    st.error("회귀분석을 위한 충분한 데이터를 생성할 수 없습니다.")
    
    with regression_col2:
        if 'regression_results' in st.session_state:
            reg_data = st.session_state['regression_results']
            
            st.markdown("#### 📊 회귀분석 결과")
            
            # Display regression statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("기울기", f"{reg_data['slope']:.6f}")
            with col2:
                st.metric("절편", f"{reg_data['intercept']:.4f}")
            with col3:
                st.metric("R²", f"{reg_data['r_squared']:.4f}")
            
            # Regression plot
            fig_reg = go.Figure()
            
            # Scatter plot of actual data
            fig_reg.add_trace(go.Scatter(
                x=reg_data['factor_values'],
                y=[irr * 100 for irr in reg_data['irr_values']],
                mode='markers',
                name='실제 데이터',
                marker=dict(size=8, color='blue')
            ))
            
            # Regression line
            x_line = np.array(reg_data['factor_values'])
            y_line = (reg_data['slope'] * x_line + reg_data['intercept']) * 100
            
            fig_reg.add_trace(go.Scatter(
                x=x_line,
                y=y_line,
                mode='lines',
                name='회귀선',
                line=dict(color='red', width=2)
            ))
            
            variable_names = {'price': '판매가격', 'cost': '원가실적', 'investment': '총투자비'}
            
            fig_reg.update_layout(
                title=f"{variable_names[reg_data['variable']]} vs IRR 회귀분석",
                xaxis_title=f"{variable_names[reg_data['variable']]} 변화율 (%)",
                yaxis_title="IRR (%)",
                height=400
            )
            
            st.plotly_chart(fig_reg, use_container_width=True)
            
            # Regression formula
            st.markdown("#### 회귀 공식")
            slope_sign = "+" if reg_data['slope'] >= 0 else ""
            st.code(f"IRR = {reg_data['intercept']:.4f} {slope_sign} {reg_data['slope']:.6f} × {variable_names[reg_data['variable']]}변화율")
            
            # Interpretation
            st.markdown("#### 해석")
            if reg_data['variable'] == 'price':
                st.info(f"판매가격이 1% 증가할 때마다 IRR이 약 {reg_data['slope']:.4%} 변화합니다.")
            elif reg_data['variable'] == 'cost':
                st.info(f"원가가 1% 증가할 때마다 IRR이 약 {reg_data['slope']:.4%} 변화합니다.")
            elif reg_data['variable'] == 'investment':
                st.info(f"총투자비가 1% 증가할 때마다 IRR이 약 {reg_data['slope']:.4%} 변화합니다.")

def show_insights_page():
    """Insights page with competitor investment trends and market intelligence"""
    
    # Competitor Investment Trends Section
    st.markdown("### 🏢 경쟁사 투자동향")
    
    if st.button("최신 투자동향 분석", key="analyze_trends"):
        try:
            import openai
            from openai import OpenAI
            import os
            
            # Initialize OpenAI client
            client = OpenAI(api_key=os.environ.get("API_KEY"))
            
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

def show_input_page():
    
    # Add CSS for black text labels
    st.markdown("""
    <style>
    .stMarkdown p, .stMarkdown h4, .stMarkdown h5 {
        color: black !important;
    }
    label[data-testid="stNumberInput"] > div > div > p {
        color: black !important;
    }
    div[data-testid="stMarkdownContainer"] p {
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create input form columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💰 투자 및 재무 정보")
        
        total_investment = st.number_input(
            "총 투자비 ($)",
            min_value=0.0,
            value=400000000.0,
            step=1000000.0,
            help="프로젝트 전체 투자 규모를 달러로 입력하세요"
        )
        
        machinery_ratio = st.number_input(
            "기계설비 투자비 비율 (%)",
            min_value=0.0,
            max_value=100.0,
            value=80.0,
            step=1.0
        )
        
        building_ratio = st.number_input(
            "건축물 투자비 비율 (%)",
            min_value=0.0,
            max_value=100.0,
            value=20.0,
            step=1.0
        )
        
        equity_ratio = st.number_input(
            "자본 비율 (%)",
            min_value=0.0,
            max_value=100.0,
            value=50.0,
            step=1.0
        )
        
        debt_ratio = st.number_input(
            "차입 비율 (%)",
            min_value=0.0,
            max_value=100.0,
            value=50.0,
            step=1.0
        )
    
    with col2:
        st.markdown("#### 📅 기간 및 금리 정보")
        
        project_start_year = st.number_input(
            "사업시작년도",
            min_value=2020,
            max_value=2050,
            value=2029,
            step=1
        )
        
        construction_period = st.number_input(
            "공사기간 (년)",
            min_value=1,
            max_value=10,
            value=4,
            step=1
        )
        
        operation_period = st.number_input(
            "사업기간 (년)",
            min_value=1,
            max_value=50,
            value=15,
            step=1
        )
        
        discount_rate = st.number_input(
            "할인율 (%)",
            min_value=0.0,
            max_value=30.0,
            value=6.92,
            step=0.01
        )
        
        grace_period = st.number_input(
            "기계설비 감가상각 연수",
            min_value=1,
            max_value=30,
            value=15,
            step=1
        )
        
        building_depreciation = st.number_input(
            "건축물 감가상각 연수",
            min_value=1,
            max_value=50,
            value=20,
            step=1
        )
        
        loan_grace_period = st.number_input(
            "장기차입 거치기간 (년)",
            min_value=0,
            max_value=10,
            value=4,
            step=1
        )
        
        loan_repayment_period = st.number_input(
            "장기차입 상환기간 (년)",
            min_value=1,
            max_value=30,
            value=8,
            step=1
        )
    
    # Investment execution timeline
    st.markdown("#### 📊 투자비 집행 계획")
    inv_col1, inv_col2, inv_col3, inv_col4 = st.columns(4)
    
    with inv_col1:
        investment_year1 = st.number_input("Year 1 집행비율 (%)", min_value=0.0, max_value=100.0, value=30.0, step=1.0)
    with inv_col2:
        investment_year2 = st.number_input("Year 2 집행비율 (%)", min_value=0.0, max_value=100.0, value=30.0, step=1.0)
    with inv_col3:
        investment_year3 = st.number_input("Year 3 집행비율 (%)", min_value=0.0, max_value=100.0, value=30.0, step=1.0)
    with inv_col4:
        investment_year4 = st.number_input("Year 4 집행비율 (%)", min_value=0.0, max_value=100.0, value=10.0, step=1.0)
    
    # Financial rates
    st.markdown("#### 💳 금리 및 세율 정보")
    rate_col1, rate_col2, rate_col3 = st.columns(3)
    
    with rate_col1:
        loan_interest_rate = st.number_input(
            "장기차입금리 (%)",
            min_value=0.0,
            max_value=20.0,
            value=3.7,
            step=0.1
        )
    
    with rate_col2:
        short_term_interest_rate = st.number_input(
            "단기차입금리 (%)",
            min_value=0.0,
            max_value=20.0,
            value=4.8,
            step=0.1
        )
    
    with rate_col3:
        corporate_tax_rate = st.number_input(
            "법인세율 (%)",
            min_value=0.0,
            max_value=50.0,
            value=25.0,
            step=0.5
        )
    
    # Sales and operational parameters
    st.markdown("#### 📈 판매 및 운영 정보")
    
    sales_admin_ratio = st.number_input(
        "판매관리비 비율 (%)",
        min_value=0.0,
        max_value=20.0,
        value=4.0,
        step=0.1
    )
    
    # Operation rates
    st.markdown("##### 가동률 계획")
    op_col1, op_col2, op_col3 = st.columns(3)
    
    with op_col1:
        operation_rate_year1 = st.number_input("1년차 가동률 (%)", min_value=0.0, max_value=100.0, value=70.0, step=1.0)
    with op_col2:
        operation_rate_year2 = st.number_input("2년차 가동률 (%)", min_value=0.0, max_value=100.0, value=80.0, step=1.0)
    with op_col3:
        operation_rate_after_year3 = st.number_input("3년차 이후 가동률 (%)", min_value=0.0, max_value=100.0, value=100.0, step=1.0)
    
    # Sales volume projections - expanded to include all years
    st.markdown("##### 판매량 계획")
    sales_col1, sales_col2, sales_col3, sales_col4 = st.columns(4)
    
    with sales_col1:
        sales_year1 = st.number_input("Year 1 판매량", min_value=0.0, value=0.0, step=1000.0)
        sales_year2 = st.number_input("Year 2 판매량", min_value=0.0, value=0.0, step=1000.0)
    with sales_col2:
        sales_year3 = st.number_input("Year 3 판매량", min_value=0.0, value=0.0, step=1000.0)
        sales_year4 = st.number_input("Year 4 판매량", min_value=0.0, value=0.0, step=1000.0)
    with sales_col3:
        sales_year5 = st.number_input("Year 5 판매량", min_value=0.0, value=70000.0, step=1000.0)
        sales_year6 = st.number_input("Year 6 판매량", min_value=0.0, value=80000.0, step=1000.0)
    with sales_col4:
        sales_after_year7 = st.number_input("Year 7+ 판매량", min_value=0.0, value=100000.0, step=1000.0)
    
    # Working capital parameters
    st.markdown("#### 💼 운전자금 정보")
    wc_col1, wc_col2, wc_col3, wc_col4 = st.columns(4)
    
    with wc_col1:
        receivables_days = st.number_input("매출채권 일수", min_value=0, value=30, step=1)
    with wc_col2:
        payables_days = st.number_input("매입채무 일수", min_value=0, value=50, step=1)
    with wc_col3:
        product_inventory_days = st.number_input("제품재고 일수", min_value=0, value=30, step=1)
    with wc_col4:
        material_inventory_days = st.number_input("소재재고 일수", min_value=0, value=40, step=1)
    
    # Submit button
    if st.button("📊 경제성 분석 실행", use_container_width=True):
        # Validation
        if machinery_ratio + building_ratio != 100:
            st.error("기계설비와 건축물 투자비 비율의 합이 100%가 되어야 합니다.")
            return
        
        if equity_ratio + debt_ratio != 100:
            st.error("자본과 차입 비율의 합이 100%가 되어야 합니다.")
            return
        
        if investment_year1 + investment_year2 + investment_year3 + investment_year4 != 100:
            st.error("투자비 집행 비율의 합이 100%가 되어야 합니다.")
            return
        
        # Create parameters dictionary
        params = {
            'construction_period': construction_period,
            'business_period': operation_period,
            'total_investment': total_investment,  # Already in dollars
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
                1: sales_year1,
                2: sales_year2,
                3: sales_year3,
                4: sales_year4,
                5: sales_year5,
                6: sales_year6,
                'after_7': sales_after_year7
            },
            'operation_rates': {
                1: operation_rate_year1 / 100,
                2: operation_rate_year2 / 100,
                'after_3': operation_rate_after_year3 / 100
            },
            'project_start_year': project_start_year,
            'discount_rate': discount_rate / 100,
            'working_capital_days': {
                'receivables': receivables_days,
                'payables': payables_days,
                'product_inventory': product_inventory_days,
                'material_inventory': material_inventory_days
            }
        }
        st.session_state['project_params'] = params
        st.session_state['current_page'] = 'analysis'
        st.rerun()

def show_analysis_page():
    
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
        if st.button("프로젝트 파라미터 입력하기"):
            st.session_state['current_page'] = 'input'
            st.rerun()
        return
    
    params = st.session_state['project_params']
    
    # Validate required parameters
    required_params = ['business_period', 'construction_period', 'total_investment']
    for param in required_params:
        if param not in params:
            st.error(f"필수 파라미터 '{param}'이 없습니다. 프로젝트 파라미터를 다시 입력해주세요.")
            if st.button("프로젝트 파라미터 입력하기"):
                st.session_state['current_page'] = 'input'
                st.rerun()
            return
    
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
        
        # Store analysis results for advanced analysis page
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
        
        # Store analysis results for advanced analysis page
        st.session_state['analysis_results'] = results
        st.session_state['params'] = params
        
        display_results(results, params)

def display_results(results, params):
    # Key metrics summary
    
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
    
    # Cash flow chart
    st.markdown("### 📈 연도별 순현금흐름")
    
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
    
    # Revenue and costs over time
    st.markdown("### 💰 매출액 및 제조원가 추이")
    
    revenue_years = [y for y in years if results['total_revenue'].get(y, 0) > 0]
    revenues = [results['total_revenue'][y] for y in revenue_years]
    manufacturing_costs = [results['manufacturing_cost'][y] for y in revenue_years]
    
    fig2 = go.Figure()
    
    fig2.add_trace(go.Scatter(
        x=[f"Year {y}" for y in revenue_years],
        y=revenues,
        mode='lines+markers',
        name='총매출액',
        line=dict(color='#003366', width=3),
        marker=dict(size=8)
    ))
    
    fig2.add_trace(go.Scatter(
        x=[f"Year {y}" for y in revenue_years],
        y=manufacturing_costs,
        mode='lines+markers',
        name='제조원가',
        line=dict(color='#dc3545', width=3),
        marker=dict(size=8)
    ))
    
    fig2.update_layout(
        title={
            'text': "매출액 및 제조원가 추이",
            'x': 0.5,
            'font': {'color': '#333333', 'size': 18, 'family': 'Noto Sans KR'}
        },
        xaxis_title="연도",
        yaxis_title="금액 ($)",
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
    
    # Financial statements
    st.markdown("### 📋 재무제표")
    
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
    
    # Download buttons
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
    
    # Guidance for advanced analysis
    st.markdown("### 🔬 추가 분석 옵션")
    
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