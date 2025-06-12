import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
from financial_calculator import FinancialCalculator
from data_loader import DataLoader

def show_progress_page():
    """Show analysis progress page with animation"""
    st.header("경제성 분석 진행 중")
    
    # Hide sidebar during analysis
    st.sidebar.empty()
    
    # Create centered layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Show analysis graphic
        st.markdown("""
        <div style="text-align: center; padding: 3rem;">
            <div style="font-size: 5rem; margin-bottom: 2rem; animation: spin 2s linear infinite;">⚙️</div>
            <h2>데이터 분석 중...</h2>
            <p>잠시만 기다려주세요</p>
        </div>
        <style>
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Analysis steps
        steps = [
            "데이터 로딩 중...",
            "재무지표 계산 중...", 
            "현금흐름 분석 중...",
            "IRR 계산 중...",
            "분석 완료!"
        ]
        
        # Simulate analysis with progress
        for i, step in enumerate(steps):
            status_text.text(f"📊 {step}")
            progress_bar.progress((i + 1) / len(steps))
            time.sleep(1)
        
        # Show completion
        st.success("경제성 분석이 완료되었습니다!")
        time.sleep(2)
        
        # Clear progress flag and set results flag
        st.session_state['analysis_in_progress'] = False
        st.session_state['show_results'] = True
        st.rerun()

def main():
    st.set_page_config(
        page_title="철강사업 프로젝트 경제성 분석",
        page_icon="🏭",
        layout="wide"
    )
    
    # Custom CSS styling with skyblue and white theme
    st.markdown("""
    <style>
    /* Main background and text */
    .stApp {
        background: linear-gradient(135deg, #e6f3ff 0%, #ffffff 100%);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #87ceeb, #4682b4);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(70, 130, 180, 0.3);
    }
    
    /* Cards and containers */
    .stContainer > div {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 10px rgba(135, 206, 235, 0.2);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(45deg, #87ceeb, #4682b4);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 3px 10px rgba(70, 130, 180, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, #4682b4, #1e90ff);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(70, 130, 180, 0.4);
    }
    
    /* Input fields */
    .stNumberInput > div > div > input {
        border: 2px solid #87ceeb;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.9);
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: #4682b4;
        box-shadow: 0 0 10px rgba(135, 206, 235, 0.5);
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #87ceeb, #4682b4);
    }
    
    /* Metrics */
    .metric-container {
        background: linear-gradient(135deg, #ffffff, #f0f8ff);
        border: 2px solid #87ceeb;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem;
        text-align: center;
        box-shadow: 0 3px 10px rgba(135, 206, 235, 0.2);
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background: white;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 3px 15px rgba(135, 206, 235, 0.2);
    }
    
    /* Success/Info messages */
    .stSuccess {
        background: linear-gradient(90deg, #e6f3ff, #ffffff);
        border-left: 5px solid #4682b4;
        border-radius: 5px;
    }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #f0f8ff, #e6f3ff);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #4682b4;
        margin: 1rem 0;
    }
    
    /* Navigation elements */
    .nav-button {
        background: linear-gradient(45deg, #ffffff, #f0f8ff);
        border: 2px solid #87ceeb;
        color: #4682b4;
        border-radius: 20px;
        padding: 0.5rem 1.5rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .nav-button:hover {
        background: linear-gradient(45deg, #87ceeb, #4682b4);
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
    
    # Check if analysis is in progress
    if st.session_state.get('analysis_in_progress', False):
        show_progress_page()
    elif st.session_state.get('show_results', False):
        # Force show results page after analysis
        st.session_state['show_results'] = False  # Reset flag
        show_analysis_page()
    elif 'project_params' in st.session_state and not st.session_state.get('reset_to_input', False):
        # If parameters exist, show results page
        show_analysis_page()
    else:
        # Default to input page
        st.session_state['reset_to_input'] = False  # Reset flag
        show_input_page()

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
        st.session_state['analysis_in_progress'] = True
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
            st.session_state['reset_to_input'] = True
            if 'project_params' in st.session_state:
                del st.session_state['project_params']
            st.rerun()
    
    if 'project_params' not in st.session_state:
        st.warning("먼저 프로젝트 파라미터를 입력해야 합니다.")
        st.session_state['reset_to_input'] = True
        st.rerun()
        return
    
    params = st.session_state['project_params']
    
    # Load data from Excel files
    data_loader = DataLoader()
    
    try:
        # Try to load Excel files
        cost_data = data_loader.load_cost_data()
        sales_data = data_loader.load_sales_data()
        
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
            <h2 style="color: #4682b4;">{results['irr']:.2%}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_revenue = sum([v for v in results['total_revenue'].values() if v > 0])
        st.markdown(f"""
        <div class="metric-container">
            <h4>총 매출액</h4>
            <h2 style="color: #4682b4;">${total_revenue:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        final_year = params['business_period'] + params['construction_period']
        final_cash_flow = results['net_cash_flow'].get(final_year, 0)
        st.markdown(f"""
        <div class="metric-container">
            <h4>최종년도 순현금흐름</h4>
            <h2 style="color: #4682b4;">${final_cash_flow:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_investment = params['total_investment']
        st.markdown(f"""
        <div class="metric-container">
            <h4>총 투자비</h4>
            <h2 style="color: #4682b4;">${total_investment:,.0f}</h2>
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
    colors = ['#ff6b6b' if cf < 0 else '#4682b4' for cf in cash_flows]
    
    fig.add_trace(go.Bar(
        x=[f"Year {y}" for y in years],
        y=cash_flows,
        marker_color=colors,
        name="순현금흐름"
    ))
    
    fig.update_layout(
        title={
            'text': "연도별 순현금흐름",
            'x': 0.5,
            'font': {'color': '#4682b4', 'size': 20}
        },
        xaxis_title="연도",
        yaxis_title="현금흐름 ($)",
        showlegend=False,
        plot_bgcolor='rgba(240, 248, 255, 0.3)',
        paper_bgcolor='white',
        font={'color': '#4682b4'}
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
        line=dict(color='#4682b4', width=3),
        marker=dict(color='#4682b4', size=8)
    ))
    
    fig2.add_trace(go.Scatter(
        x=[f"Year {y}" for y in revenue_years],
        y=manufacturing_costs,
        mode='lines+markers',
        name='제조원가',
        line=dict(color='#87ceeb', width=3),
        marker=dict(color='#87ceeb', size=8)
    ))
    
    fig2.update_layout(
        title={
            'text': "매출액 및 제조원가 추이",
            'x': 0.5,
            'font': {'color': '#4682b4', 'size': 20}
        },
        xaxis_title="연도",
        yaxis_title="금액 ($)",
        legend=dict(x=0, y=1, bgcolor='rgba(255,255,255,0.8)'),
        plot_bgcolor='rgba(240, 248, 255, 0.3)',
        paper_bgcolor='white',
        font={'color': '#4682b4'}
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Free Cash Flow breakdown with skyblue theme
    st.markdown("""
    <div class="section-header">
        <h3>💸 Free Cash Flow 계산 내역</h3>
        <div style="background: linear-gradient(90deg, #f0f8ff, #ffffff); padding: 1rem; border-radius: 8px; margin: 1rem 0;">
            <p><strong style="color: #4682b4;">현금유입 = 순이익 + 금융비용 + 감가상각 + 잔존가치 + 운전자금유입</strong></p>
            <p><strong style="color: #4682b4;">현금유출 = 투자비 + 운전자금유출 (운전자금증가분)</strong></p>
            <p><strong style="color: #4682b4;">순현금흐름(FCF) = 현금유입 - 현금유출</strong></p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Detailed financial statements
    st.markdown("""
    <div class="section-header">
        <h3>📋 상세 재무제표</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Create comprehensive dataframe
    df_results = pd.DataFrame()
    
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
            '순이익': results['net_income'].get(year, 0),
            '감가상각': results['depreciation'].get(year, 0),
            '잔존가치': results['residual_value'].get(year, 0),
            '운전자금유입': results['working_capital_inflow'].get(year, 0),
            '현금유입': results['cash_inflow'].get(year, 0),
            '투자비': results['investment'].get(year, 0),
            '운전자금': results['working_capital'].get(year, 0),
            '운전자금증가': results['working_capital_increase'].get(year, 0),
            '현금유출': results['cash_outflow'].get(year, 0),
            '순현금흐름(FCF)': results['net_cash_flow'].get(year, 0)
        }
        df_results = pd.concat([df_results, pd.DataFrame([year_data])], ignore_index=True)
    
    # Format numbers for display
    numeric_cols = df_results.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if col != '연도':
            df_results[col] = df_results[col].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else "$0")
    
    st.dataframe(df_results, use_container_width=True)
    
    # Download button for results
    csv = df_results.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="결과를 CSV로 다운로드",
        data=csv,
        file_name="financial_analysis_results.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()
