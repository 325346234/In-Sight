import pandas as pd
import streamlit as st
import os

class DataLoader:
    def load_cost_data(self):
        """Load cost data from cost.xlsx file"""
        try:
            # Try to load from attached_assets folder first
            cost_file_path = 'attached_assets/Cost_1749724942946.xlsx'
            if os.path.exists(cost_file_path):
                df = pd.read_excel(cost_file_path)
                return df
            elif os.path.exists('cost.xlsx'):
                df = pd.read_excel('cost.xlsx')
                return df
            else:
                st.warning("원가 데이터 파일을 찾을 수 없습니다. 기본 데이터를 사용합니다.")
                return self.get_default_cost_data()
        except Exception as e:
            st.error(f"원가 데이터 파일 로딩 중 오류: {str(e)}")
            return self.get_default_cost_data()
    
    def load_sales_data(self):
        """Load sales data from sales.xlsx file"""
        try:
            # Try to load from attached_assets folder first
            sales_file_path = 'attached_assets/Sales_1749724937515.xlsx'
            if os.path.exists(sales_file_path):
                df = pd.read_excel(sales_file_path)
                return df
            elif os.path.exists('sales.xlsx'):
                df = pd.read_excel('sales.xlsx')
                return df
            else:
                st.warning("판매 데이터 파일을 찾을 수 없습니다. 기본 데이터를 사용합니다.")
                return self.get_default_sales_data()
        except Exception as e:
            st.error(f"판매 데이터 파일 로딩 중 오류: {str(e)}")
            return self.get_default_sales_data()
    
    def get_default_cost_data(self):
        """기본 원가 데이터 (Excel 파일이 없을 때 사용)"""
        # 실제 업로드된 파일을 읽을 수 없으므로 철강업계 일반적인 값으로 설정
        data = {
            '소재가격': [450, 480, 460, 470, 465, 455, 475, 485, 490, 460],  # 톤당 달러
            '가공비': [150, 160, 155, 165, 170, 160, 155, 165, 170, 160]      # 톤당 달러
        }
        return pd.DataFrame(data)
    
    def get_default_sales_data(self):
        """기본 판매 데이터 (Excel 파일이 없을 때 사용)"""
        # 실제 업로드된 파일을 읽을 수 없으므로 철강업계 일반적인 값으로 설정
        data = {
            '매출액': [45000000, 48000000, 46000000, 47000000, 46500000, 
                      45500000, 47500000, 48500000, 49000000, 46000000],  # 달러
            '판매량': [75000, 80000, 76000, 78000, 77000, 
                      75500, 79000, 80500, 81000, 76000]               # 톤
        }
        return pd.DataFrame(data)
    
    def validate_data(self, df, required_columns):
        """데이터 유효성 검증"""
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"필수 컬럼이 누락되었습니다: {missing_columns}")
        
        # 숫자 데이터 검증
        for col in required_columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except:
                    raise ValueError(f"컬럼 '{col}'의 데이터를 숫자로 변환할 수 없습니다.")
        
        return df
    
    def process_uploaded_file(self, uploaded_file, file_type):
        """업로드된 파일 처리"""
        try:
            if uploaded_file is not None:
                df = pd.read_excel(uploaded_file)
                
                if file_type == 'cost':
                    required_columns = ['소재가격', '가공비']
                    df = self.validate_data(df, required_columns)
                    st.success("원가 데이터가 성공적으로 로드되었습니다.")
                    return df
                    
                elif file_type == 'sales':
                    required_columns = ['매출액', '판매량']
                    df = self.validate_data(df, required_columns)
                    st.success("판매 데이터가 성공적으로 로드되었습니다.")
                    return df
                    
        except Exception as e:
            st.error(f"파일 처리 중 오류가 발생했습니다: {str(e)}")
            return None
