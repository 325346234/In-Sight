#!/usr/bin/env python3
"""
운전자금 계산 공식 검증 테스트
운전자금 = 매출채권 - 매입채무 + 재고자산
"""

def test_working_capital_formula():
    """운전자금 계산 공식의 각 구성요소 테스트"""
    
    print("=" * 80)
    print("운전자금 계산 공식: 운전자금 = 매출채권 - 매입채무 + 재고자산")
    print("=" * 80)
    print()
    
    # 예시 데이터 (Year 5 기준)
    year = 5
    sales_volume = 70000  # 톤
    unit_price = 600      # 달러/톤 (예시)
    material_cost_per_unit = 460  # 달러/톤
    
    # 총매출액과 소재가격 계산
    total_revenue = sales_volume * unit_price
    total_material_cost = sales_volume * material_cost_per_unit
    
    print(f"Year {year} 기준 계산:")
    print(f"판매량: {sales_volume:,} 톤")
    print(f"단위당 판매가격: ${unit_price}/톤")
    print(f"단위당 소재가격: ${material_cost_per_unit}/톤")
    print(f"총매출액: ${total_revenue:,}")
    print(f"총소재가격: ${total_material_cost:,}")
    print()
    
    # 운전자금 구성요소별 계산
    print("=" * 50)
    print("1. 매출채권 계산")
    print("=" * 50)
    receivables_days = 50  # 매출채권일수
    receivables = total_revenue / 365 * receivables_days
    print(f"매출채권 = 총매출액/365 × 매출채권일수")
    print(f"매출채권 = ${total_revenue:,}/365 × {receivables_days}일")
    print(f"매출채권 = ${receivables:,.0f}")
    print()
    
    print("=" * 50)
    print("2. 매입채무 계산")
    print("=" * 50)
    payables_days = 30  # 매입채무일수
    payables = total_material_cost / 365 * payables_days
    print(f"매입채무 = 소재가격/365 × 매입채무일수")
    print(f"매입채무 = ${total_material_cost:,}/365 × {payables_days}일")
    print(f"매입채무 = ${payables:,.0f}")
    print()
    
    print("=" * 50)
    print("3. 재고자산 계산")
    print("=" * 50)
    product_inventory_days = 50  # 제품재고일수
    material_inventory_days = 40  # 소재재고일수
    
    product_inventory = total_revenue * product_inventory_days / 365
    material_inventory = total_material_cost * material_inventory_days / 365
    total_inventory = product_inventory + material_inventory
    
    print(f"제품재고 = 총매출액 × 제품재고일수 / 365")
    print(f"제품재고 = ${total_revenue:,} × {product_inventory_days}일 / 365")
    print(f"제품재고 = ${product_inventory:,.0f}")
    print()
    print(f"소재재고 = 소재가격 × 소재재고일수 / 365")
    print(f"소재재고 = ${total_material_cost:,} × {material_inventory_days}일 / 365")
    print(f"소재재고 = ${material_inventory:,.0f}")
    print()
    print(f"재고자산 = 제품재고 + 소재재고")
    print(f"재고자산 = ${product_inventory:,.0f} + ${material_inventory:,.0f}")
    print(f"재고자산 = ${total_inventory:,.0f}")
    print()
    
    print("=" * 80)
    print("최종 운전자금 계산")
    print("=" * 80)
    working_capital = receivables - payables + total_inventory
    
    print(f"운전자금 = 매출채권 - 매입채무 + 재고자산")
    print(f"운전자금 = ${receivables:,.0f} - ${payables:,.0f} + ${total_inventory:,.0f}")
    print(f"운전자금 = ${working_capital:,.0f}")
    print()
    
    # 구성요소별 비중 표시
    print("=" * 50)
    print("구성요소별 분석")
    print("=" * 50)
    print(f"매출채권: ${receivables:,.0f} ({receivables/working_capital*100:.1f}%)")
    print(f"매입채무: -${payables:,.0f} ({-payables/working_capital*100:.1f}%)")
    print(f"재고자산: ${total_inventory:,.0f} ({total_inventory/working_capital*100:.1f}%)")
    print(f"순운전자금: ${working_capital:,.0f} (100.0%)")

if __name__ == "__main__":
    test_working_capital_formula()