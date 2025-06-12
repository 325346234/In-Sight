#!/usr/bin/env python3
"""
운전자금증가 계산 테스트 스크립트
"""

def calculate_working_capital_increase_demo():
    """운전자금증가 계산 공식 데모"""
    
    # 파라미터 설정
    construction_period = 4  # 공사기간
    
    # 예시 운전자금 데이터 (Year별)
    working_capitals = {
        1: 0,        # 공사기간 - 매출 없음
        2: 0,        # 공사기간 - 매출 없음  
        3: 0,        # 공사기간 - 매출 없음
        4: 0,        # 공사기간 - 매출 없음
        5: 5000000,  # 사업 시작 - 운전자금 발생
        6: 6000000,  # 매출 증가에 따른 운전자금 증가
        7: 8000000,  # 매출 증가에 따른 운전자금 증가
        8: 8000000,  # 매출 안정화
    }
    
    print("=" * 60)
    print("운전자금증가 계산 공식:")
    print("Year 1부터 Year(공사기간) 까지는 0")
    print("Year(공사기간+1) 부터: (YearX 운전자금) - (Year X-1 운전자금)")
    print("=" * 60)
    print()
    
    print(f"공사기간: {construction_period}년")
    print()
    
    print("연도별 운전자금:")
    for year in sorted(working_capitals.keys()):
        print(f"Year {year}: ${working_capitals[year]:,}")
    print()
    
    print("=" * 60)
    print("운전자금증가 계산 결과:")
    print("=" * 60)
    
    for year in sorted(working_capitals.keys()):
        if year <= construction_period:
            # 공사기간 중에는 운전자금증가 = 0
            increase = 0
            print(f"Year {year}: 운전자금증가 = 0")
            print(f"         (공사기간이므로 0으로 적용)")
        else:
            # 사업기간: (현재년도 운전자금) - (전년도 운전자금)
            current_wc = working_capitals[year]
            previous_wc = working_capitals[year - 1]
            increase = current_wc - previous_wc
            
            print(f"Year {year}: 운전자금증가 = ${current_wc:,} - ${previous_wc:,} = ${increase:,}")
            
        print()

if __name__ == "__main__":
    calculate_working_capital_increase_demo()