import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io
import json
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine

# Page configuration
st.set_page_config(
    page_title="AI 투자 경제성 분석",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'mode' not in st.session_state:
    st.session_state.mode = "실전모드"
if 'current_page' not in st.session_state:
    st.session_state.current_page = "메인"

# CSS 스타일링
st.markdown("""
<style>
    .main-video {
        width: 100%;
        height: 100vh;
        object-fit: cover;
    }
    
    .mode-button {
        width: 100%;
        padding: 10px;
        margin: 5px 0;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-weight: bold;
    }
    
    .mode-active {
        background-color: #2E5084 !important;
        color: white !important;
    }
    
    .mode-inactive {
        background-color: #f0f2f6 !important;
        color: #262730 !important;
    }
    
    .menu-item {
        padding: 8px 12px;
        margin: 2px 0;
        border-radius: 5px;
        cursor: pointer;
        color: #262730;
    }
    
    .menu-item:hover {
        background-color: #e8eaf6;
    }
    
    .submenu-item {
        padding: 5px 20px;
        margin: 1px 0;
        font-size: 0.9em;
        color: #666;
    }
    
    .submenu-item:hover {
        background-color: #f5f5f5;
    }
    
    .company-logo {
        text-align: center;
        margin-bottom: 20px;
    }
    
    .section-header {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        border-left: 4px solid #2E5084;
    }
</style>
""", unsafe_allow_html=True)

# 회사 로고 (SVG로 간단히 생성)
def create_company_logo():
    logo_svg = """
    <div class="company-logo">
        <svg width="120" height="80" viewBox="0 0 120 80" xmlns="http://www.w3.org/2000/svg">
            <rect width="120" height="80" fill="#2E5084" rx="10"/>
            <rect x="20" y="25" width="15" height="30" fill="white"/>
            <rect x="40" y="20" width="15" height="35" fill="white"/>
            <rect x="60" y="15" width="15" height="40" fill="white"/>
            <rect x="80" y="30" width="15" height="25" fill="white"/>
            <text x="60" y="70" text-anchor="middle" fill="white" font-size="10" font-weight="bold">STEEL TECH</text>
        </svg>
    </div>
    """
    return logo_svg

# 사이드바 구성
with st.sidebar:
    # 회사 로고
    st.markdown(create_company_logo(), unsafe_allow_html=True)
    
    # 제목
    st.markdown("<h3 style='text-align: center; color: #2E5084;'>AI 투자 경제성 분석</h3>", unsafe_allow_html=True)
    
    # 모드 선택
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("실전모드", key="real_mode", 
                    help="실제 업무에서 사용하는 모드"):
            st.session_state.mode = "실전모드"
    
    with col2:
        if st.button("연습모드", key="practice_mode",
                    help="학습 및 연습을 위한 모드"):
            st.session_state.mode = "연습모드"
    
    # 모드 표시
    st.markdown(f"**현재 모드:** {st.session_state.mode}")
    
    st.markdown("---")
    
    # 메뉴 구성
    if st.session_state.mode == "실전모드":
        # 권한 관리 메뉴
        st.markdown("### 📋 권한 관리")
        if st.button("권한 요청하기", key="request_permission", use_container_width=True):
            st.session_state.current_page = "권한 요청하기"
        if st.button("요청받은 권한", key="received_permission", use_container_width=True):
            st.session_state.current_page = "요청받은 권한"
        if st.button("결재 현황", key="approval_status", use_container_width=True):
            st.session_state.current_page = "결재 현황"
        
        st.markdown("---")
    
    # AI 경제성 분석 메뉴
    st.markdown("### 🤖 AI 경제성 분석")
    if st.button("AI 경제성 분석", key="ai_analysis", use_container_width=True):
        st.session_state.current_page = "AI 경제성 분석"
    
    st.markdown("---")
    
    # 메인페이지로 돌아가기
    if st.button("🏠 메인페이지", key="main_page", use_container_width=True):
        st.session_state.current_page = "메인"

# 메인 페이지 구성
if st.session_state.current_page == "메인":
    # 유튜브 동영상 전체화면 재생
    st.markdown("""
    <style>
        .main-content {
            padding: 0;
            margin: 0;
        }
        .video-container {
            position: relative;
            width: 100%;
            height: 80vh;
            margin: 0;
            padding: 0;
        }
        .video-container iframe {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # 유튜브 동영상 자동재생
    youtube_url = "https://www.youtube.com/embed/lukBN6Dg3LU?autoplay=1&mute=1&loop=1&playlist=lukBN6Dg3LU"
    
    st.markdown(f"""
    <div class="video-container">
        <iframe src="{youtube_url}" 
                allow="autoplay; encrypted-media" 
                allowfullscreen>
        </iframe>
    </div>
    """, unsafe_allow_html=True)
    
    # 동영상 하단에 간단한 설명
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <h2 style='color: #2E5084;'>AI 기반 철강 투자 경제성 분석 시스템</h2>
        <p style='font-size: 18px; color: #666;'>
            정확한 데이터 분석과 AI 인사이트로 최적의 투자 결정을 지원합니다
        </p>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.current_page == "권한 요청하기":
    st.header("📋 권한 요청하기")
    st.info("권한 요청 기능은 개발 중입니다.")
    
elif st.session_state.current_page == "요청받은 권한":
    st.header("📨 요청받은 권한")
    st.info("요청받은 권한 관리 기능은 개발 중입니다.")
    
elif st.session_state.current_page == "결재 현황":
    st.header("📊 결재 현황")
    st.info("결재 현황 확인 기능은 개발 중입니다.")

elif st.session_state.current_page == "AI 경제성 분석":
    st.header("🤖 AI 투자 경제성 분석")
    
    # 데이터베이스에서 Sales 및 Cost 데이터 로드
    @st.cache_data
    def load_data_from_db():
        try:
            DATABASE_URL = os.environ.get('DATABASE_URL')
            engine = create_engine(DATABASE_URL)
            
            sales_df = pd.read_sql('SELECT * FROM sales_data', engine)
            cost_df = pd.read_sql('SELECT * FROM cost_data', engine)
            
            return sales_df, cost_df
        except Exception as e:
            st.error(f"데이터베이스 연결 오류: {e}")
            return None, None
    
    sales_data, cost_data = load_data_from_db()
    
    if sales_data is not None and cost_data is not None:
        # 기본 계산값들
        total_revenue = sales_data['total_revenue'].sum()
        total_quantity = sales_data['sales_volume'].sum()
        unit_selling_price = total_revenue / total_quantity if total_quantity > 0 else 0
        avg_material_cost = cost_data['material_cost'].mean()
        avg_processing_cost = cost_data['processing_cost'].mean()
        
        # 판매계획 섹션
        st.markdown('<div class="section-header"><h3>📈 판매계획</h3></div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("단위당 판매가격", f"{unit_selling_price:,.0f} 원/톤")
        with col2:
            year5_volume = st.number_input("5년차 판매량 (톤)", value=70000, min_value=0)
        with col3:
            year6_volume = st.number_input("6년차 판매량 (톤)", value=80000, min_value=0)
        
        col1, col2 = st.columns(2)
        with col1:
            year7_plus_volume = st.number_input("7년차 이후 판매량 (톤)", value=100000, min_value=0)
        with col2:
            st.metric("연간 매출 전망 (7년차 기준)", f"{(unit_selling_price * year7_plus_volume / 1e6):,.1f} 백만원")
        
        # 사업계획 섹션
        st.markdown('<div class="section-header"><h3>🏗️ 사업계획</h3></div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            business_period = st.number_input("사업기간 (년)", value=15, min_value=1, max_value=30)
            construction_period = st.number_input("공사기간 (년)", value=4, min_value=1, max_value=10)
        with col2:
            total_investment = st.number_input("총 투자비 (억원)", value=4.0, min_value=0.1, step=0.1) * 1e8
            machinery_ratio = st.number_input("기계설비 투자비 비율 (%)", value=80.0, min_value=0.0, max_value=100.0)
        with col3:
            building_ratio = st.number_input("건축물 투자비 비율 (%)", value=20.0, min_value=0.0, max_value=100.0)
            if machinery_ratio + building_ratio != 100:
                st.warning("⚠️ 기계설비 + 건축물 비율이 100%가 되어야 합니다")
        
        # 전제사항 섹션 (접을 수 있도록)
        with st.expander("📋 전제사항", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("재무 조건")
                discount_rate = st.number_input("할인율 (%)", value=6.92, min_value=0.1, step=0.01)
                equity_ratio = st.number_input("자본비율 (%)", value=50.0, min_value=0.0, max_value=100.0)
                debt_ratio = st.number_input("차입비율 (%)", value=50.0, min_value=0.0, max_value=100.0)
                long_term_rate = st.number_input("장기차입금리 (%)", value=3.7, min_value=0.1, step=0.01)
                
            with col2:
                st.subheader("운영 조건")
                tax_rate = st.number_input("법인세율 (%)", value=25.0, min_value=0.0, max_value=50.0)
                sales_admin_ratio = st.number_input("판매관리비 비율 (%)", value=4.0, min_value=0.0, step=0.1)
                grace_period = st.number_input("장기거치기간 (년)", value=4, min_value=0)
                repayment_period = st.number_input("장기상환기간 (년)", value=8, min_value=1)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                receivables_days = st.number_input("매출채권일수", value=30, min_value=0)
            with col2:
                payables_days = st.number_input("매입채무일수", value=50, min_value=0)
            with col3:
                product_inventory_days = st.number_input("제품재고일수", value=30, min_value=0)
            with col4:
                material_inventory_days = st.number_input("소재재고일수", value=40, min_value=0)
        
        # 분석 실행 버튼
        if st.button("🔍 투자 경제성 분석 실행", type="primary", use_container_width=True):
            # 상세 분석 실행
            from steel_analysis_demo import SteelInvestmentAnalyzer
            
            analyzer = SteelInvestmentAnalyzer()
            
            # 파라미터 설정
            params = {
                '사업기간': business_period,
                '사업시작년도': 2029,
                '공사기간': construction_period,
                '할인율': discount_rate,
                '자본비율': equity_ratio,
                '차입비율': debt_ratio,
                '총투자비': total_investment,
                '기계설비투자비비율': machinery_ratio,
                '건축물투자비비율': building_ratio,
                '장기차입금리': long_term_rate,
                '장기거치기간': grace_period,
                '장기상환기간': repayment_period,
                '법인세율': tax_rate,
                '판매관리비비율': sales_admin_ratio,
                '매출채권일수': receivables_days,
                '매입채무일수': payables_days,
                '제품재고일수': product_inventory_days,
                '소재재고일수': material_inventory_days
            }
            
            # 판매량 설정
            total_period = business_period + construction_period
            sales_volumes = [0, 0, 0, 0, year5_volume, year6_volume] + [year7_plus_volume] * (total_period - 6)
            
            with st.spinner("투자 경제성 분석을 수행하고 있습니다..."):
                # 분석 실행 (간단한 계산)
                cash_flows = []
                for year in range(1, total_period + 1):
                    if year <= 4:  # 건설기간
                        investment = total_investment * [0.3, 0.3, 0.3, 0.1][year-1]
                        cash_flow = -investment
                    else:  # 운영기간
                        volume = sales_volumes[year-1] if year <= len(sales_volumes) else sales_volumes[-1]
                        revenue = unit_selling_price * volume
                        cost = (avg_material_cost + avg_processing_cost) * volume
                        
                        # 간단한 감가상각
                        depreciation = total_investment / business_period if year > construction_period else 0
                        
                        # 세전이익
                        pretax_income = revenue - cost - depreciation - (revenue * sales_admin_ratio / 100)
                        tax = max(0, pretax_income * tax_rate / 100)
                        net_income = pretax_income - tax
                        
                        cash_flow = net_income + depreciation
                    
                    cash_flows.append(cash_flow)
                
                # IRR 계산
                from scipy.optimize import fsolve
                
                def npv_func(rate):
                    return sum(cf / (1 + rate) ** i for i, cf in enumerate(cash_flows))
                
                try:
                    irr = fsolve(npv_func, 0.1)[0]
                    if abs(npv_func(irr)) > 1e-6 or irr < -0.99 or irr > 10:
                        irr = None
                except:
                    irr = None
                
                # NPV 계산
                npv = sum(cf / (1 + discount_rate/100) ** i for i, cf in enumerate(cash_flows))
            
            # 결과 표시
            st.success("✅ 분석이 완료되었습니다!")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("순현재가치 (NPV)", f"{npv/1e8:.2f} 억원")
            with col2:
                irr_pct = irr * 100 if irr else 0
                st.metric("내부수익률 (IRR)", f"{irr_pct:.2f}%" if irr else "계산불가")
            with col3:
                st.metric("할인율", f"{discount_rate:.2f}%")
            with col4:
                st.metric("총투자비", f"{total_investment/1e8:.1f} 억원")
            
            # 투자 결정 지원
            st.subheader("💡 투자 결정 지원")
            
            if npv > 0:
                st.success("✅ NPV가 양수입니다. 경제적으로 타당한 투자입니다.")
            else:
                st.error("❌ NPV가 음수입니다. 투자에 신중을 기하시기 바랍니다.")
            
            if irr and irr > discount_rate/100:
                st.success(f"✅ IRR({irr_pct:.2f}%)이 할인율({discount_rate:.2f}%)보다 높습니다.")
            else:
                st.error(f"❌ IRR이 할인율보다 낮습니다. 투자 수익성을 재검토하시기 바랍니다.")
            
            # 현금흐름 차트
            st.subheader("💰 현금흐름 분석")
            
            fig = go.Figure()
            
            years = list(range(1, len(cash_flows) + 1))
            cash_flows_million = [cf / 1e6 for cf in cash_flows]
            cumulative_cf = np.cumsum(cash_flows_million)
            
            # 연도별 현금흐름
            colors = ['red' if cf < 0 else 'green' for cf in cash_flows_million]
            fig.add_trace(go.Bar(
                x=years, y=cash_flows_million, 
                name='연도별 순현금흐름',
                marker_color=colors
            ))
            
            # 누적 현금흐름
            fig.add_trace(go.Scatter(
                x=years, y=cumulative_cf, 
                mode='lines+markers',
                name='누적 현금흐름',
                line=dict(color='blue', width=3),
                yaxis='y2'
            ))
            
            # 이중 y축 설정
            fig.update_layout(
                title="현금흐름 분석",
                xaxis_title="년도",
                yaxis=dict(title="연도별 현금흐름 (백만원)", side="left"),
                yaxis2=dict(title="누적 현금흐름 (백만원)", side="right", overlaying="y"),
                height=500,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.error("데이터베이스에서 데이터를 로드할 수 없습니다.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>Steel Industry AI Investment Analysis Tool</p>
    <p>Powered by AI • Built for Investment Decisions</p>
</div>
""", unsafe_allow_html=True)
    
    cash_flows = []
    
    if input_method == "Manual Input":
        st.write("Enter annual cash flows for each year:")
        cash_flow_cols = st.columns(min(5, project_duration))
        
        for i in range(project_duration):
            col_idx = i % 5
            with cash_flow_cols[col_idx]:
                if i % 5 == 0 and i > 0:
                    cash_flow_cols = st.columns(min(5, project_duration - i))
                    col_idx = 0
                
                cash_flow = st.number_input(
                    f"Year {i+1} (Million USD)",
                    value=20.0,
                    step=1.0,
                    key=f"cash_flow_{i}"
                )
                cash_flows.append(cash_flow)
    
    elif input_method == "Use Industry Template":
        template_type = st.selectbox(
            "Select Template",
            ["Conservative Growth", "Moderate Growth", "Aggressive Growth"]
        )
        cash_flows = steel_data.get_cash_flow_template(
            template_type, project_duration, initial_investment
        )
        
        # Display template cash flows
        st.write("Template Cash Flows (Million USD):")
        cf_df = pd.DataFrame({
            'Year': range(1, len(cash_flows) + 1),
            'Cash Flow': cash_flows
        })
        st.dataframe(cf_df.T, use_container_width=True)
    
    # Market Parameters
    st.subheader("🏭 Market & Cost Parameters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Raw Material Costs**")
        iron_ore_price = st.number_input(
            "Iron Ore Price ($/ton)", 
            min_value=0.0, 
            value=120.0
        )
        coal_price = st.number_input(
            "Coking Coal Price ($/ton)", 
            min_value=0.0, 
            value=200.0
        )
        
    with col2:
        st.write("**Market Prices**")
        steel_price = st.number_input(
            "Steel Price ($/ton)", 
            min_value=0.0, 
            value=600.0
        )
        price_volatility = st.slider(
            "Price Volatility (%)", 
            min_value=5, 
            max_value=50, 
            value=20
        )
        
    with col3:
        st.write("**Financial Parameters**")
        discount_rate = st.slider(
            "Discount Rate (%)", 
            min_value=1.0, 
            max_value=20.0, 
            value=8.0, 
            step=0.1
        ) / 100
        tax_rate = st.slider(
            "Tax Rate (%)", 
            min_value=0.0, 
            max_value=50.0, 
            value=25.0
        ) / 100
    
    # Analysis Button
    if st.button("🔍 Perform Analysis", type="primary", use_container_width=True):
        if project_name and cash_flows and len(cash_flows) > 0:
            with st.spinner("Performing financial analysis..."):
                # Financial calculations
                npv = financial_calc.calculate_npv(cash_flows, discount_rate, initial_investment)
                irr = financial_calc.calculate_irr([-initial_investment] + cash_flows)
                payback_period = financial_calc.calculate_payback_period(cash_flows, initial_investment)
                
                # Risk analysis
                risk_metrics = financial_calc.calculate_risk_metrics(
                    cash_flows, discount_rate, price_volatility/100
                )
                
                # Sensitivity analysis
                sensitivity_data = financial_calc.sensitivity_analysis(
                    cash_flows, initial_investment, discount_rate
                )
                
                st.session_state.analysis_results = {
                    'project_name': project_name,
                    'npv': npv,
                    'irr': irr,
                    'payback_period': payback_period,
                    'risk_metrics': risk_metrics,
                    'sensitivity_data': sensitivity_data,
                    'cash_flows': cash_flows,
                    'initial_investment': initial_investment,
                    'discount_rate': discount_rate,
                    'steel_parameters': {
                        'production_capacity': production_capacity,
                        'steel_grade': steel_grade,
                        'facility_type': facility_type,
                        'iron_ore_price': iron_ore_price,
                        'coal_price': coal_price,
                        'steel_price': steel_price
                    }
                }
            
            # AI Analysis
            with st.spinner("Generating AI-powered investment insights..."):
                try:
                    ai_analysis = ai_analyzer.analyze_investment(st.session_state.analysis_results)
                    st.session_state.ai_analysis = ai_analysis
                except Exception as e:
                    st.error(f"AI analysis failed: {str(e)}")
                    st.session_state.ai_analysis = None
        else:
            st.error("Please fill in all required fields including project name and cash flows.")
    
    # Display Results
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        st.header("📈 Analysis Results")
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Net Present Value",
                f"${results['npv']:.2f}M",
                delta=f"{'Positive' if results['npv'] > 0 else 'Negative'} NPV"
            )
            
        with col2:
            st.metric(
                "Internal Rate of Return",
                f"{results['irr']:.2%}" if results['irr'] is not None else "N/A",
                delta=f"vs {results['discount_rate']:.1%} discount rate"
            )
            
        with col3:
            st.metric(
                "Payback Period",
                f"{results['payback_period']:.1f} years" if results['payback_period'] is not None else "N/A"
            )
            
        with col4:
            risk_level = "Low" if results['risk_metrics']['var_95'] < 50 else "Medium" if results['risk_metrics']['var_95'] < 100 else "High"
            st.metric(
                "Risk Level",
                risk_level,
                delta=f"VaR 95%: ${results['risk_metrics']['var_95']:.1f}M"
            )
        
        # Charts
        tab1, tab2, tab3, tab4 = st.tabs(["Cash Flow Analysis", "Sensitivity Analysis", "Risk Assessment", "Investment Recommendation"])
        
        with tab1:
            # Cash flow chart
            years = list(range(1, len(results['cash_flows']) + 1))
            cumulative_cf = np.cumsum([-results['initial_investment']] + results['cash_flows'])
            
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Annual Cash Flows', 'Cumulative Cash Flow'),
                vertical_spacing=0.1
            )
            
            fig.add_trace(
                go.Bar(x=years, y=results['cash_flows'], name='Annual Cash Flow'),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=[0] + years, y=cumulative_cf, mode='lines+markers', name='Cumulative Cash Flow'),
                row=2, col=1
            )
            
            fig.update_layout(height=600, showlegend=True)
            fig.update_xaxes(title_text="Year", row=2, col=1)
            fig.update_yaxes(title_text="Million USD", row=1, col=1)
            fig.update_yaxes(title_text="Million USD", row=2, col=1)
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Sensitivity analysis chart
            sens_data = results['sensitivity_data']
            
            fig = go.Figure()
            
            for param, values in sens_data.items():
                fig.add_trace(go.Scatter(
                    x=values['changes'],
                    y=values['npv_changes'],
                    mode='lines+markers',
                    name=param.replace('_', ' ').title()
                ))
            
            fig.update_layout(
                title="NPV Sensitivity to Key Parameters",
                xaxis_title="Parameter Change (%)",
                yaxis_title="NPV Change (Million USD)",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # Risk metrics display
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Risk Metrics")
                risk_df = pd.DataFrame({
                    'Metric': ['Value at Risk (95%)', 'Expected Shortfall', 'Standard Deviation', 'Coefficient of Variation'],
                    'Value': [
                        f"${results['risk_metrics']['var_95']:.1f}M",
                        f"${results['risk_metrics']['expected_shortfall']:.1f}M",
                        f"${results['risk_metrics']['std_dev']:.1f}M",
                        f"{results['risk_metrics']['coeff_variation']:.2f}"
                    ]
                })
                st.dataframe(risk_df, use_container_width=True, hide_index=True)
            
            with col2:
                # Risk visualization
                risk_scenarios = np.random.normal(results['npv'], results['risk_metrics']['std_dev'], 1000)
                
                fig = go.Figure()
                fig.add_trace(go.Histogram(x=risk_scenarios, nbinsx=50, name='NPV Distribution'))
                fig.add_vline(x=results['npv'], line_dash="dash", line_color="red", 
                             annotation_text=f"Expected NPV: ${results['npv']:.1f}M")
                fig.add_vline(x=results['npv'] - results['risk_metrics']['var_95'], 
                             line_dash="dash", line_color="orange",
                             annotation_text=f"VaR 95%")
                
                fig.update_layout(
                    title="NPV Risk Distribution",
                    xaxis_title="NPV (Million USD)",
                    yaxis_title="Frequency",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with tab4:
            # AI Analysis Results
            if st.session_state.ai_analysis:
                ai_results = st.session_state.ai_analysis
                
                # Investment Recommendation
                st.subheader("🤖 AI Investment Recommendation")
                
                recommendation_color = {
                    "Strong Buy": "green",
                    "Buy": "lightgreen", 
                    "Hold": "yellow",
                    "Sell": "orange",
                    "Strong Sell": "red"
                }.get(ai_results.get('recommendation', 'Hold'), 'gray')
                
                st.markdown(f"""
                <div style="padding: 20px; border-radius: 10px; background-color: {recommendation_color}; color: white; text-align: center;">
                    <h2>Recommendation: {ai_results.get('recommendation', 'Not Available')}</h2>
                    <h3>Confidence Score: {ai_results.get('confidence_score', 0):.1%}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                st.subheader("Key Insights")
                for insight in ai_results.get('key_insights', []):
                    st.write(f"• {insight}")
                
                st.subheader("Risk Factors")
                for risk in ai_results.get('risk_factors', []):
                    st.write(f"⚠️ {risk}")
                
                st.subheader("Opportunities")
                for opportunity in ai_results.get('opportunities', []):
                    st.write(f"✅ {opportunity}")
                
                if ai_results.get('detailed_analysis'):
                    st.subheader("Detailed Analysis")
                    st.write(ai_results['detailed_analysis'])
            else:
                st.info("AI analysis not available. Please check your OpenAI API configuration.")

elif analysis_type == "Detailed Steel Investment Analysis":
    # Import and display the detailed analysis using actual Excel data
    from steel_analysis_demo import run_steel_analysis_demo
    run_steel_analysis_demo()

elif analysis_type == "Comparative Analysis":
    st.header("🔄 Comparative Investment Analysis")
    st.info("Compare multiple steel industry investment projects side by side.")
    
    # This would be expanded for comparing multiple projects
    st.write("Feature coming soon - Compare multiple investment opportunities")

elif analysis_type == "Market Analysis":
    st.header("📊 Steel Market Analysis")
    st.info("Analyze current steel market conditions and forecasts.")
    
    # Display current market data
    market_data = steel_data.get_market_data()
    if market_data:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current Steel Price", f"${market_data['steel_price']}/ton")
        with col2:
            st.metric("Iron Ore Price", f"${market_data['iron_ore_price']}/ton")
        with col3:
            st.metric("Coal Price", f"${market_data['coal_price']}/ton")
    
    st.write("Detailed market analysis features coming soon...")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>Steel Industry Investment Analysis Tool</p>
    <p>Powered by AI • Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)
