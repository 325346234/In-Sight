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
from scipy.optimize import fsolve

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
    """Display POSCO Holdings logo"""
    try:
        # Load POSCO Holdings logo
        import base64
        
        # Load the uploaded POSCO Holdings logo
        logo_path = "attached_assets/POSCO Holdings_eng_1749727332592.png"
        
        # Convert image to base64 for HTML display
        with open(logo_path, "rb") as f:
            img_bytes = f.read()
            img_base64 = base64.b64encode(img_bytes).decode()
        
        logo_html = f"""
        <div style="text-align: center; margin: 20px 0;">
            <div style="
                background: transparent;
                padding: 20px;
                border-radius: 15px;
                margin-bottom: 20px;
            ">
                <img src="data:image/png;base64,{img_base64}" 
                     style="max-width: 200px; height: auto;" 
                     alt="POSCO Holdings">
            </div>
        </div>
        """
        return logo_html
    except Exception as e:
        # Fallback to original logo if image loading fails
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
    st.markdown("""
    <style>
        .ai-analysis-title {
            color: #2E5084 !important;
            font-size: 28px !important;
            font-weight: bold !important;
            margin: 15px 0 !important;
            text-align: center !important;
        }
    </style>
    <div class="ai-analysis-title">
        🤖 AI 경제성 분석
    </div>
    """, unsafe_allow_html=True)
    if st.button("AI 경제성 분석", key="ai_analysis", use_container_width=True):
        st.session_state.current_page = "AI 경제성 분석"
    
    st.markdown("---")
    
    # 메인페이지로 돌아가기
    if st.button("🏠 메인페이지", key="main_page", use_container_width=True):
        st.session_state.current_page = "메인"

# 메인 페이지 구성
if st.session_state.current_page == "메인":
    # 유튜브 동영상 전체화면 재생 - 최대한 크게
    st.markdown("""
    <style>
        .main > div {
            padding: 0 !important;
        }
        .block-container {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
        }
        .video-container {
            position: relative;
            width: 100vw;
            height: 100vh;
            margin: 0;
            padding: 0;
            left: 50%;
            right: 50%;
            margin-left: -50vw;
            margin-right: -50vw;
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
            if DATABASE_URL:
                engine = create_engine(DATABASE_URL)
                
                sales_df = pd.read_sql('SELECT * FROM sales_data', engine)
                cost_df = pd.read_sql('SELECT * FROM cost_data', engine)
                
                return sales_df, cost_df
            else:
                return None, None
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
            st.metric("단위당 판매가격", f"${unit_selling_price:,.0f}/톤")
        with col2:
            year5_volume = st.number_input("5년차 판매량 (톤)", value=70000, min_value=0)
        with col3:
            year6_volume = st.number_input("6년차 판매량 (톤)", value=80000, min_value=0)
        
        col1, col2 = st.columns(2)
        with col1:
            year7_plus_volume = st.number_input("7년차 이후 판매량 (톤)", value=100000, min_value=0)
        with col2:
            st.metric("연간 매출 전망 (7년차 기준)", f"${(unit_selling_price * year7_plus_volume / 1e6):,.1f}M")
        
        # 사업계획 섹션
        st.markdown('<div class="section-header"><h3>🏗️ 사업계획</h3></div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            business_period = st.number_input("사업기간 (년)", value=15, min_value=1, max_value=30)
            construction_period = st.number_input("공사기간 (년)", value=4, min_value=1, max_value=10)
        with col2:
            total_investment = st.number_input("총 투자비 (Million USD)", value=400.0, min_value=0.1, step=0.1) * 1e6
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
            # 판매량 설정
            total_period = business_period + construction_period
            sales_volumes = [0, 0, 0, 0, year5_volume, year6_volume] + [year7_plus_volume] * (total_period - 6)
            
            with st.spinner("투자 경제성 분석을 수행하고 있습니다..."):
                # 상세 재무 모델 계산
                cash_flows = []
                debt_balance = 0
                previous_working_capital = 0
                total_debt_principal = total_investment * (debt_ratio / 100)
                annual_repayment = total_debt_principal / repayment_period
                investment_execution = [0.3, 0.3, 0.3, 0.1] + [0] * (total_period - 4)
                
                for year in range(1, total_period + 1):
                    # 기본 값들
                    sales_volume = sales_volumes[year-1] if year <= len(sales_volumes) else sales_volumes[-1]
                    total_revenue_year = unit_selling_price * sales_volume
                    material_cost = avg_material_cost * sales_volume
                    processing_cost = avg_processing_cost * sales_volume
                    
                    # 감가상각 (기계설비/건축물 분리)
                    if year > construction_period:
                        machinery_depreciation = (total_investment * machinery_ratio / 100) / 15
                        building_depreciation = (total_investment * building_ratio / 100) / 20
                        depreciation = machinery_depreciation + building_depreciation
                    else:
                        depreciation = 0
                    
                    manufacturing_cost = material_cost + processing_cost + depreciation
                    
                    # 투자비
                    investment = total_investment * investment_execution[year - 1] if year <= len(investment_execution) else 0
                    
                    # 차입금 관리
                    debt_increase = investment * (debt_ratio / 100)
                    if year > grace_period and year <= grace_period + repayment_period:
                        debt_decrease = annual_repayment
                    else:
                        debt_decrease = 0
                    
                    debt_balance = debt_balance + debt_increase - debt_decrease
                    financial_cost = debt_balance * (long_term_rate / 100)
                    
                    # 운전자금 계산
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
                    
                    # 손익계산
                    sales_admin_cost = total_revenue_year * (sales_admin_ratio / 100)
                    ebit = total_revenue_year - manufacturing_cost - sales_admin_cost
                    pretax_income = ebit - financial_cost
                    corporate_tax = max(0, pretax_income * (tax_rate / 100))
                    net_income = pretax_income - corporate_tax
                    
                    # 잔존가치 (마지막 년도)
                    if year == total_period:
                        total_depreciation_sum = depreciation * (total_period - construction_period)
                        residual_value = total_investment - total_depreciation_sum
                        working_capital_recovery = working_capital
                    else:
                        residual_value = 0
                        working_capital_recovery = 0
                    
                    # 현금흐름
                    cash_inflow = net_income + financial_cost + depreciation + residual_value + working_capital_recovery
                    cash_outflow = investment + working_capital_increase
                    cash_flow = cash_inflow - cash_outflow
                    
                    cash_flows.append(cash_flow)
                
                # IRR 계산
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
                st.metric("순현재가치 (NPV)", f"${npv/1e6:.2f}M")
            with col2:
                irr_pct = irr * 100 if irr else 0
                st.metric("내부수익률 (IRR)", f"{irr_pct:.2f}%" if irr else "계산불가")
            with col3:
                st.metric("할인율", f"{discount_rate:.2f}%")
            with col4:
                st.metric("총투자비", f"${total_investment/1e6:.1f}M")
            
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
                yaxis=dict(title="연도별 현금흐름 (Million USD)", side="left"),
                yaxis2=dict(title="누적 현금흐름 (Million USD)", side="right", overlaying="y"),
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