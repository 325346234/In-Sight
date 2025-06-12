import pandas as pd
import numpy as np
from scipy.optimize import fsolve
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class SteelInvestmentAnalyzer:
    def __init__(self):
        self.project_params = {}
        self.sales_data = None
        self.cost_data = None
        
    def load_data(self, sales_file, cost_file):
        """Load sales and cost data from Excel files"""
        try:
            self.sales_data = pd.read_excel(sales_file)
            self.cost_data = pd.read_excel(cost_file)
            return True
        except Exception as e:
            st.error(f"데이터 로딩 중 오류 발생: {e}")
            return False
    
    def calculate_unit_price_and_costs(self):
        """Calculate unit selling price and material costs from historical data"""
        if self.sales_data is None or self.cost_data is None:
            return None, None, None
        
        # 단위당 판매가격 = 총 매출액의 합계 / 판매량의 합계
        total_revenue = self.sales_data['총 매출액'].sum()
        total_quantity = self.sales_data['판매량'].sum()
        unit_selling_price = total_revenue / total_quantity if total_quantity > 0 else 0
        
        # 소재가격 평균
        avg_material_cost = self.cost_data['소재가격'].mean()
        
        # 가공비 평균
        avg_processing_cost = self.cost_data['가공비'].mean()
        
        return unit_selling_price, avg_material_cost, avg_processing_cost
    
    def calculate_investment_analysis(self, params):
        """Perform comprehensive investment analysis"""
        self.project_params = params
        
        # 기본 계산 파라미터
        project_duration = params['사업기간']  # 15년
        construction_period = params['공사기간']  # 4년
        total_period = project_duration + construction_period  # 19년
        discount_rate = params['할인율'] / 100  # 6.92%
        
        # 투자 관련 파라미터
        total_investment = params['총투자비']  # 400,000,000
        machinery_ratio = params['기계설비투자비비율'] / 100  # 80%
        building_ratio = params['건축물투자비비율'] / 100  # 20%
        
        # 판매량 설정
        sales_volumes = [0, 0, 0, 0, 70000, 80000] + [100000] * (total_period - 6)
        
        # 투자비 집행 비율
        investment_execution = [0.3, 0.3, 0.3, 0.1] + [0] * (total_period - 4)
        
        # 단위당 가격 및 원가 계산
        unit_price, material_cost_per_unit, processing_cost_per_unit = self.calculate_unit_price_and_costs()
        
        if unit_price is None:
            st.error("가격 및 원가 데이터를 계산할 수 없습니다.")
            return None
        
        # 연도별 계산을 위한 리스트 초기화
        years = list(range(1, total_period + 1))
        results = []
        
        # 장기차입금 관련 계산
        debt_ratio = params['차입비율'] / 100  # 50%
        equity_ratio = params['자본비율'] / 100  # 50%
        long_term_interest_rate = params['장기차입금리'] / 100  # 3.7%
        grace_period = params['장기거치기간']  # 4년
        repayment_period = params['장기상환기간']  # 8년
        
        # 세율 및 기타 비율
        tax_rate = params['법인세율'] / 100  # 25%
        sales_admin_ratio = params['판매관리비비율'] / 100  # 4%
        
        # 매출채권, 매입채무, 재고 관련
        receivables_days = params['매출채권일수']  # 30일
        payables_days = params['매입채무일수']  # 50일
        product_inventory_days = params['제품재고일수']  # 30일
        material_inventory_days = params['소재재고일수']  # 40일
        
        # 연도별 상세 계산
        previous_working_capital = 0
        debt_balance = 0
        total_debt_principal = total_investment * debt_ratio
        annual_repayment = total_debt_principal / repayment_period
        
        for year in years:
            year_data = {'년도': year}
            
            # 판매량
            if year <= len(sales_volumes):
                sales_volume = sales_volumes[year - 1]
            else:
                sales_volume = sales_volumes[-1]
            year_data['판매량'] = sales_volume
            
            # 총매출액
            total_revenue = unit_price * sales_volume
            year_data['총매출액'] = total_revenue
            
            # 소재가격 및 가공비
            material_cost = material_cost_per_unit * sales_volume
            processing_cost = processing_cost_per_unit * sales_volume
            year_data['소재가격'] = material_cost
            year_data['가공비'] = processing_cost
            
            # 감가상각
            if year > construction_period:
                machinery_depreciation = (total_investment * machinery_ratio) / 15
                building_depreciation = (total_investment * building_ratio) / 20
                depreciation = machinery_depreciation + building_depreciation
            else:
                depreciation = 0
            year_data['감가상각'] = depreciation
            
            # 제조원가
            manufacturing_cost = material_cost + processing_cost + depreciation
            year_data['제조원가'] = manufacturing_cost
            
            # 투자비
            if year <= len(investment_execution):
                investment = total_investment * investment_execution[year - 1]
            else:
                investment = 0
            year_data['투자비'] = investment
            
            # 자본 및 차입
            equity = investment * equity_ratio
            debt_increase = investment * debt_ratio
            year_data['자본'] = equity
            year_data['차입증가'] = debt_increase
            
            # 장기차입금 상환
            if year > grace_period and year <= grace_period + repayment_period:
                debt_decrease = annual_repayment
            else:
                debt_decrease = 0
            year_data['차입감소'] = debt_decrease
            
            # 장기차입금 잔액
            debt_balance = debt_balance + debt_increase - debt_decrease
            year_data['차입금잔액'] = debt_balance
            
            # 금융비용
            financial_cost = debt_balance * long_term_interest_rate
            year_data['금융비용'] = financial_cost
            
            # 운전자금 계산
            if total_revenue > 0:
                receivables = (total_revenue / 365) * receivables_days
                product_inventory = (total_revenue * product_inventory_days) / 365
            else:
                receivables = 0
                product_inventory = 0
                
            if material_cost > 0:
                payables = (material_cost / 365) * payables_days
                material_inventory = (material_cost * material_inventory_days) / 365
            else:
                payables = 0
                material_inventory = 0
            
            total_inventory = product_inventory + material_inventory
            working_capital = receivables - payables + total_inventory
            year_data['운전자금'] = working_capital
            
            # 운전자금 증가분
            if year > construction_period:
                working_capital_increase = working_capital - previous_working_capital
            else:
                working_capital_increase = 0
            year_data['운전자금증가분'] = working_capital_increase
            previous_working_capital = working_capital
            
            # 판매관리비
            sales_admin_cost = total_revenue * sales_admin_ratio
            year_data['판매관리비'] = sales_admin_cost
            
            # 손익계산
            ebit = total_revenue - manufacturing_cost - sales_admin_cost
            year_data['EBIT'] = ebit
            
            pretax_income = ebit - financial_cost
            year_data['세전이익'] = pretax_income
            
            corporate_tax = max(0, pretax_income * tax_rate)
            year_data['법인세'] = corporate_tax
            
            net_income = pretax_income - corporate_tax
            year_data['순이익'] = net_income
            
            # 잔존가치 (마지막 년도에만)
            if year == total_period:
                total_depreciation = depreciation * (total_period - construction_period)
                residual_value = total_investment - total_depreciation
                working_capital_recovery = working_capital
            else:
                residual_value = 0
                working_capital_recovery = 0
            year_data['잔존가치'] = residual_value
            year_data['운전자금회수'] = working_capital_recovery
            
            # 현금흐름
            cash_inflow = net_income + financial_cost + depreciation + residual_value + working_capital_recovery
            cash_outflow = investment + working_capital_increase
            net_cash_flow = cash_inflow - cash_outflow
            
            year_data['현금유입'] = cash_inflow
            year_data['현금유출'] = cash_outflow
            year_data['순현금흐름'] = net_cash_flow
            
            results.append(year_data)
        
        # IRR 계산
        cash_flows = [row['순현금흐름'] for row in results]
        irr = self.calculate_irr(cash_flows)
        
        # NPV 계산
        npv = self.calculate_npv(cash_flows, discount_rate)
        
        return {
            'results': results,
            'irr': irr,
            'npv': npv,
            'unit_selling_price': unit_price,
            'material_cost_per_unit': material_cost_per_unit,
            'processing_cost_per_unit': processing_cost_per_unit,
            'cash_flows': cash_flows
        }
    
    def calculate_irr(self, cash_flows):
        """Calculate Internal Rate of Return"""
        def npv_func(rate):
            return sum(cf / (1 + rate) ** i for i, cf in enumerate(cash_flows))
        
        try:
            irr = fsolve(npv_func, 0.1)[0]
            # Validation check
            if abs(npv_func(irr)) < 1e-6 and -0.99 < irr < 10:
                return irr
            else:
                return None
        except:
            return None
    
    def calculate_npv(self, cash_flows, discount_rate):
        """Calculate Net Present Value"""
        return sum(cf / (1 + discount_rate) ** i for i, cf in enumerate(cash_flows))

def display_analysis_results():
    """Display comprehensive analysis results in Streamlit"""
    st.title("🏭 철강 투자 경제성 분석 결과")
    
    # 프로젝트 기본 정보 입력
    st.header("📊 프로젝트 기본 정보")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("사업 기본 사항")
        project_duration = st.number_input("사업기간 (년)", value=15, min_value=1)
        start_year = st.number_input("사업시작년도", value=2029, min_value=2020)
        construction_period = st.number_input("공사기간 (년)", value=4, min_value=1)
        discount_rate = st.number_input("할인율 (%)", value=6.92, min_value=0.1, step=0.01)
        
    with col2:
        st.subheader("자본 구조")
        equity_ratio = st.number_input("자본비율 (%)", value=50.0, min_value=0.1, max_value=100.0)
        debt_ratio = st.number_input("차입비율 (%)", value=50.0, min_value=0.0, max_value=100.0)
        long_term_rate = st.number_input("장기차입금리 (%)", value=3.7, min_value=0.1, step=0.01)
        tax_rate = st.number_input("법인세율 (%)", value=25.0, min_value=0.0, max_value=50.0)
    
    # 투자 관련 정보
    st.subheader("💰 투자 정보")
    col1, col2 = st.columns(2)
    
    with col1:
        total_investment = st.number_input("총투자비 (원)", value=400000000, min_value=1000000, step=1000000)
        machinery_ratio = st.number_input("기계설비투자비비율 (%)", value=80.0, min_value=0.0, max_value=100.0)
        building_ratio = st.number_input("건축물투자비비율 (%)", value=20.0, min_value=0.0, max_value=100.0)
        
    with col2:
        grace_period = st.number_input("장기거치기간 (년)", value=4, min_value=0)
        repayment_period = st.number_input("장기상환기간 (년)", value=8, min_value=1)
        sales_admin_ratio = st.number_input("판매관리비비율 (%)", value=4.0, min_value=0.0, step=0.1)
    
    # 운전자금 관련 정보
    st.subheader("💼 운전자금 정보")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        receivables_days = st.number_input("매출채권일수 (일)", value=30, min_value=0)
    with col2:
        payables_days = st.number_input("매입채무일수 (일)", value=50, min_value=0)
    with col3:
        product_inventory_days = st.number_input("제품재고일수 (일)", value=30, min_value=0)
    with col4:
        material_inventory_days = st.number_input("소재재고일수 (일)", value=40, min_value=0)
    
    # 파일 업로드
    st.header("📁 데이터 파일 업로드")
    col1, col2 = st.columns(2)
    
    with col1:
        sales_file = st.file_uploader("판매실적 파일 (Excel)", type=['xlsx'], key="sales")
    with col2:
        cost_file = st.file_uploader("원가실적 파일 (Excel)", type=['xlsx'], key="cost")
    
    if st.button("🔍 투자 경제성 분석 실행", type="primary"):
        if sales_file is not None and cost_file is not None:
            # 분석기 초기화
            analyzer = SteelInvestmentAnalyzer()
            
            # 데이터 로딩
            if analyzer.load_data(sales_file, cost_file):
                # 파라미터 설정
                params = {
                    '사업기간': project_duration,
                    '사업시작년도': start_year,
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
                
                # 분석 실행
                with st.spinner("투자 경제성 분석을 수행하고 있습니다..."):
                    analysis_results = analyzer.calculate_investment_analysis(params)
                
                if analysis_results:
                    # 결과 표시
                    st.header("📈 분석 결과")
                    
                    # 주요 지표
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        npv_billion = analysis_results['npv'] / 1e9
                        st.metric("순현재가치 (NPV)", f"{npv_billion:.2f} 십억원")
                    
                    with col2:
                        irr_pct = analysis_results['irr'] * 100 if analysis_results['irr'] else 0
                        st.metric("내부수익률 (IRR)", f"{irr_pct:.2f}%")
                    
                    with col3:
                        unit_price_thousand = analysis_results['unit_selling_price'] / 1000
                        st.metric("단위당 판매가격", f"{unit_price_thousand:.0f} 천원/톤")
                    
                    with col4:
                        investment_billion = total_investment / 1e9
                        st.metric("총투자비", f"{investment_billion:.1f} 십억원")
                    
                    # 상세 결과 테이블
                    st.subheader("📊 연도별 상세 분석")
                    df_results = pd.DataFrame(analysis_results['results'])
                    
                    # 주요 컬럼만 표시 (단위: 백만원)
                    display_columns = ['년도', '판매량', '총매출액', '제조원가', '순이익', '순현금흐름']
                    df_display = df_results[display_columns].copy()
                    
                    # 금액을 백만원 단위로 변환
                    money_columns = ['총매출액', '제조원가', '순이익', '순현금흐름']
                    for col in money_columns:
                        df_display[col] = df_display[col] / 1e6  # 백만원 단위로 변환
                    
                    st.dataframe(df_display, use_container_width=True)
                    
                    # 현금흐름 차트
                    st.subheader("💰 현금흐름 분석")
                    
                    fig = make_subplots(
                        rows=2, cols=1,
                        subplot_titles=('연도별 현금흐름', '누적 현금흐름'),
                        vertical_spacing=0.12
                    )
                    
                    years = df_results['년도'].tolist()
                    cash_flows = (df_results['순현금흐름'] / 1e6).tolist()  # 백만원 단위
                    cumulative_cf = np.cumsum(cash_flows)
                    
                    # 연도별 현금흐름
                    fig.add_trace(
                        go.Bar(x=years, y=cash_flows, name='연도별 현금흐름'),
                        row=1, col=1
                    )
                    
                    # 누적 현금흐름
                    fig.add_trace(
                        go.Scatter(x=years, y=cumulative_cf, mode='lines+markers', 
                                 name='누적 현금흐름', line=dict(color='red')),
                        row=2, col=1
                    )
                    
                    fig.update_layout(height=600, showlegend=True)
                    fig.update_xaxes(title_text="년도", row=2, col=1)
                    fig.update_yaxes(title_text="현금흐름 (백만원)", row=1, col=1)
                    fig.update_yaxes(title_text="누적 현금흐름 (백만원)", row=2, col=1)
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 투자 결정 지원
                    st.subheader("💡 투자 결정 지원")
                    
                    if analysis_results['npv'] > 0:
                        st.success("✅ NPV가 양수입니다. 경제적으로 타당한 투자입니다.")
                    else:
                        st.error("❌ NPV가 음수입니다. 투자에 신중을 기하시기 바랍니다.")
                    
                    if analysis_results['irr'] and analysis_results['irr'] > discount_rate/100:
                        st.success(f"✅ IRR({irr_pct:.2f}%)이 할인율({discount_rate:.2f}%)보다 높습니다.")
                    else:
                        st.error(f"❌ IRR이 할인율보다 낮습니다. 투자 수익성을 재검토하시기 바랍니다.")
                    
                    # Excel 다운로드
                    st.subheader("📥 결과 다운로드")
                    
                    # Excel 파일 생성을 위한 데이터 준비
                    from io import BytesIO
                    output = BytesIO()
                    
                    # 요약 정보 데이터 준비
                    summary_data = {
                        '항목': ['총투자비(억원)', 'NPV(억원)', 'IRR(%)', '단위판매가격(원/톤)', '소재원가(원/톤)', '가공비(원/톤)'],
                        '값': [
                            total_investment/1e8,
                            analysis_results['npv']/1e8,
                            irr_pct,
                            analysis_results['unit_selling_price'],
                            analysis_results['material_cost_per_unit'],
                            analysis_results['processing_cost_per_unit']
                        ]
                    }
                    summary_df = pd.DataFrame(summary_data)
                    
                    # Excel 파일 작성
                    try:
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df_results.to_excel(writer, sheet_name='투자분석결과', index=False)
                            summary_df.to_excel(writer, sheet_name='투자요약', index=False)
                    except ImportError:
                        # Fallback to openpyxl with proper buffer handling
                        import tempfile
                        import os
                        
                        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
                            with pd.ExcelWriter(tmp_file.name, engine='openpyxl') as writer:
                                df_results.to_excel(writer, sheet_name='투자분석결과', index=False)
                                summary_df.to_excel(writer, sheet_name='투자요약', index=False)
                        
                        # Read the temporary file into BytesIO
                        with open(tmp_file.name, 'rb') as f:
                            output.write(f.read())
                        
                        # Clean up temporary file
                        os.unlink(tmp_file.name)
                    
                    excel_data = output.getvalue()
                    
                    st.download_button(
                        label="📊 분석결과 Excel 다운로드",
                        data=excel_data,
                        file_name=f"철강투자분석_{start_year}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
                else:
                    st.error("분석 중 오류가 발생했습니다.")
            else:
                st.error("데이터 파일을 읽을 수 없습니다. 파일 형식을 확인해 주세요.")
        else:
            st.warning("판매실적 파일과 원가실적 파일을 모두 업로드해 주세요.")

if __name__ == "__main__":
    display_analysis_results()