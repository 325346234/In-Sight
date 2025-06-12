import pandas as pd
import numpy as np
from scipy.optimize import fsolve
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 철강 투자 경제성 분석 데모
def run_steel_analysis_demo():
    st.title("🏭 철강 투자 경제성 분석 결과")
    
    # 실제 첨부된 엑셀 파일을 사용한 분석
    try:
        # 판매실적 데이터 로드
        sales_df = pd.read_excel('attached_assets/Sales_1749725372842.xlsx')
        cost_df = pd.read_excel('attached_assets/Cost_1749725372842.xlsx')
        
        # 단위당 판매가격 계산 (총 매출액의 합계 / 판매량의 합계)
        total_revenue = sales_df['총 매출액'].sum()
        total_quantity = sales_df['판매량'].sum()
        unit_selling_price = total_revenue / total_quantity
        
        # 소재가격 및 가공비 평균
        avg_material_cost = cost_df['소재가격'].mean()
        avg_processing_cost = cost_df['가공비'].mean()
        
        st.success("✅ 실제 데이터로부터 계산된 기본 값들:")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("단위당 판매가격", f"{unit_selling_price:,.0f} 원/톤")
        with col2:
            st.metric("소재가격 (평균)", f"{avg_material_cost:,.0f} 원/톤")
        with col3:
            st.metric("가공비 (평균)", f"{avg_processing_cost:,.0f} 원/톤")
        
        # 프로젝트 파라미터 (사용자 제공 값들)
        project_params = {
            '사업기간': 15,
            '사업시작년도': 2029,
            '공사기간': 4,
            '할인율': 6.92,
            '자본비율': 50.0,
            '차입비율': 50.0,
            '총투자비': 400000000,  # 4억원
            '기계설비투자비비율': 80.0,
            '건축물투자비비율': 20.0,
            '장기차입금리': 3.7,
            '장기거치기간': 4,
            '장기상환기간': 8,
            '법인세율': 25.0,
            '판매관리비비율': 4.0,
            '매출채권일수': 30,
            '매입채무일수': 50,
            '제품재고일수': 30,
            '소재재고일수': 40
        }
        
        # 판매량 설정 (Year 1-4: 0, Year 5: 70,000, Year 6: 80,000, Year 7이후: 100,000)
        total_period = project_params['사업기간'] + project_params['공사기간']  # 19년
        sales_volumes = [0, 0, 0, 0, 70000, 80000] + [100000] * (total_period - 6)
        
        # 투자비 집행 비율
        investment_execution = [0.3, 0.3, 0.3, 0.1] + [0] * (total_period - 4)
        
        # 연도별 상세 계산
        results = []
        debt_balance = 0
        previous_working_capital = 0
        total_debt_principal = project_params['총투자비'] * (project_params['차입비율'] / 100)
        annual_repayment = total_debt_principal / project_params['장기상환기간']
        
        for year in range(1, total_period + 1):
            year_data = {'년도': year}
            
            # 판매량
            sales_volume = sales_volumes[year - 1] if year <= len(sales_volumes) else sales_volumes[-1]
            year_data['판매량'] = sales_volume
            
            # 총매출액
            total_revenue_year = unit_selling_price * sales_volume
            year_data['총매출액'] = total_revenue_year
            
            # 소재가격 및 가공비
            material_cost = avg_material_cost * sales_volume
            processing_cost = avg_processing_cost * sales_volume
            year_data['소재가격'] = material_cost
            year_data['가공비'] = processing_cost
            
            # 감가상각 (공사기간 이후부터)
            if year > project_params['공사기간']:
                machinery_depreciation = (project_params['총투자비'] * project_params['기계설비투자비비율'] / 100) / 15
                building_depreciation = (project_params['총투자비'] * project_params['건축물투자비비율'] / 100) / 20
                depreciation = machinery_depreciation + building_depreciation
            else:
                depreciation = 0
            year_data['감가상각'] = depreciation
            
            # 제조원가
            manufacturing_cost = material_cost + processing_cost + depreciation
            year_data['제조원가'] = manufacturing_cost
            
            # 투자비
            investment = project_params['총투자비'] * investment_execution[year - 1] if year <= len(investment_execution) else 0
            year_data['투자비'] = investment
            
            # 차입금 관리
            debt_increase = investment * (project_params['차입비율'] / 100)
            if year > project_params['장기거치기간'] and year <= project_params['장기거치기간'] + project_params['장기상환기간']:
                debt_decrease = annual_repayment
            else:
                debt_decrease = 0
            
            debt_balance = debt_balance + debt_increase - debt_decrease
            year_data['차입금잔액'] = debt_balance
            
            # 금융비용
            financial_cost = debt_balance * (project_params['장기차입금리'] / 100)
            year_data['금융비용'] = financial_cost
            
            # 운전자금 계산
            if total_revenue_year > 0:
                receivables = (total_revenue_year / 365) * project_params['매출채권일수']
                product_inventory = (total_revenue_year * project_params['제품재고일수']) / 365
            else:
                receivables = 0
                product_inventory = 0
                
            if material_cost > 0:
                payables = (material_cost / 365) * project_params['매입채무일수']
                material_inventory = (material_cost * project_params['소재재고일수']) / 365
            else:
                payables = 0
                material_inventory = 0
            
            working_capital = receivables - payables + product_inventory + material_inventory
            year_data['운전자금'] = working_capital
            
            # 운전자금 증가분
            if year > project_params['공사기간']:
                working_capital_increase = working_capital - previous_working_capital
            else:
                working_capital_increase = 0
            year_data['운전자금증가분'] = working_capital_increase
            previous_working_capital = working_capital
            
            # 판매관리비
            sales_admin_cost = total_revenue_year * (project_params['판매관리비비율'] / 100)
            year_data['판매관리비'] = sales_admin_cost
            
            # 손익계산
            ebit = total_revenue_year - manufacturing_cost - sales_admin_cost
            year_data['EBIT'] = ebit
            
            pretax_income = ebit - financial_cost
            year_data['세전이익'] = pretax_income
            
            corporate_tax = max(0, pretax_income * (project_params['법인세율'] / 100))
            year_data['법인세'] = corporate_tax
            
            net_income = pretax_income - corporate_tax
            year_data['순이익'] = net_income
            
            # 잔존가치 (마지막 년도)
            if year == total_period:
                total_depreciation_sum = depreciation * (total_period - project_params['공사기간'])
                residual_value = project_params['총투자비'] - total_depreciation_sum
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
        
        def calculate_irr(cash_flows):
            def npv_func(rate):
                return sum(cf / (1 + rate) ** i for i, cf in enumerate(cash_flows))
            try:
                irr = fsolve(npv_func, 0.1)[0]
                if abs(npv_func(irr)) < 1e-6 and -0.99 < irr < 10:
                    return irr
                else:
                    return None
            except:
                return None
        
        # NPV 계산
        def calculate_npv(cash_flows, discount_rate):
            return sum(cf / (1 + discount_rate) ** i for i, cf in enumerate(cash_flows))
        
        irr = calculate_irr(cash_flows)
        npv = calculate_npv(cash_flows, project_params['할인율'] / 100)
        
        # 결과 표시
        st.header("📈 투자 경제성 분석 결과")
        
        # 주요 지표
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            npv_billion = npv / 1e8  # 억원 단위
            st.metric("순현재가치 (NPV)", f"{npv_billion:.1f} 억원")
        
        with col2:
            irr_pct = irr * 100 if irr else 0
            st.metric("내부수익률 (IRR)", f"{irr_pct:.2f}%")
            
        with col3:
            discount_rate = project_params['할인율']
            st.metric("할인율", f"{discount_rate:.2f}%")
            
        with col4:
            investment_billion = project_params['총투자비'] / 1e8
            st.metric("총투자비", f"{investment_billion:.0f} 억원")
        
        # 투자 결정 지원
        st.subheader("💡 투자 결정 지원")
        
        if npv > 0:
            st.success("✅ NPV가 양수입니다. 경제적으로 타당한 투자입니다.")
        else:
            st.error("❌ NPV가 음수입니다. 투자에 신중을 기하시기 바랍니다.")
        
        if irr and irr > project_params['할인율']/100:
            st.success(f"✅ IRR({irr_pct:.2f}%)이 할인율({discount_rate:.2f}%)보다 높습니다.")
        else:
            st.error(f"❌ IRR이 할인율보다 낮습니다. 투자 수익성을 재검토하시기 바랍니다.")
        
        # 상세 결과 테이블
        st.subheader("📊 연도별 상세 분석 결과")
        df_results = pd.DataFrame(results)
        
        # 주요 컬럼만 표시 (단위: 백만원)
        display_columns = ['년도', '판매량', '총매출액', '제조원가', '순이익', '순현금흐름']
        df_display = df_results[display_columns].copy()
        
        # 금액을 백만원 단위로 변환
        money_columns = ['총매출액', '제조원가', '순이익', '순현금흐름']
        for col in money_columns:
            df_display[col] = df_display[col] / 1e6
        
        # 소수점 표시 형식 지정
        format_dict = {}
        for col in money_columns:
            format_dict[col] = "{:.1f}"
        format_dict['판매량'] = "{:,.0f}"
        
        st.dataframe(df_display.style.format(format_dict), use_container_width=True)
        
        # 현금흐름 차트
        st.subheader("💰 현금흐름 분석")
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('연도별 순현금흐름 (백만원)', '누적 현금흐름 (백만원)'),
            vertical_spacing=0.12
        )
        
        years = df_results['년도'].tolist()
        cash_flows_million = (df_results['순현금흐름'] / 1e6).tolist()
        cumulative_cf = np.cumsum(cash_flows_million)
        
        # 연도별 현금흐름
        colors = ['red' if cf < 0 else 'green' for cf in cash_flows_million]
        fig.add_trace(
            go.Bar(x=years, y=cash_flows_million, name='연도별 순현금흐름', 
                   marker_color=colors),
            row=1, col=1
        )
        
        # 누적 현금흐름
        fig.add_trace(
            go.Scatter(x=years, y=cumulative_cf, mode='lines+markers', 
                     name='누적 현금흐름', line=dict(color='blue', width=3)),
            row=2, col=1
        )
        
        # 손익분기점 표시
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        
        fig.update_layout(height=600, showlegend=True)
        fig.update_xaxes(title_text="년도", row=2, col=1)
        fig.update_yaxes(title_text="현금흐름 (백만원)", row=1, col=1)
        fig.update_yaxes(title_text="누적 현금흐름 (백만원)", row=2, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Excel 다운로드
        st.subheader("📥 결과 다운로드")
        
        from io import BytesIO
        output = BytesIO()
        
        # 요약 정보 데이터 준비
        summary_data = {
            '항목': ['총투자비(억원)', 'NPV(억원)', 'IRR(%)', '할인율(%)', '단위판매가격(원/톤)', '소재원가(원/톤)', '가공비(원/톤)'],
            '값': [
                project_params['총투자비']/1e8,
                npv/1e8,
                irr_pct,
                project_params['할인율'],
                unit_selling_price,
                avg_material_cost,
                avg_processing_cost
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        
        # Excel 파일 작성 (임시 파일 사용)
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            with pd.ExcelWriter(tmp_file.name, engine='xlsxwriter') as writer:
                df_results.to_excel(writer, sheet_name='투자분석결과', index=False)
                summary_df.to_excel(writer, sheet_name='투자요약', index=False)
        
        # 파일을 BytesIO로 읽기
        with open(tmp_file.name, 'rb') as f:
            output.write(f.read())
        
        # 임시 파일 삭제
        os.unlink(tmp_file.name)
        
        excel_data = output.getvalue()
        
        st.download_button(
            label="📊 분석결과 Excel 다운로드",
            data=excel_data,
            file_name=f"철강투자분석_{project_params['사업시작년도']}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        st.error(f"분석 중 오류가 발생했습니다: {str(e)}")
        st.info("첨부된 엑셀 파일을 확인해 주세요.")

if __name__ == "__main__":
    run_steel_analysis_demo()