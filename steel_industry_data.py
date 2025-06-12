import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import json

class SteelIndustryData:
    """
    Steel industry data provider and analysis support class.
    Provides industry-specific parameters, templates, and market data.
    """
    
    def __init__(self):
        self.steel_grades = [
            "Carbon Steel - Low Carbon",
            "Carbon Steel - Medium Carbon", 
            "Carbon Steel - High Carbon",
            "Alloy Steel - Low Alloy",
            "Alloy Steel - High Alloy",
            "Stainless Steel - Austenitic",
            "Stainless Steel - Ferritic",
            "Stainless Steel - Martensitic",
            "Tool Steel",
            "Specialty Steel - HSLA",
            "Specialty Steel - Weathering",
            "Spring Steel",
            "Bearing Steel"
        ]
        
        self.facility_types = [
            "Integrated Steel Plant",
            "Electric Arc Furnace",
            "Mini Mill",
            "Specialty Steel Plant"
        ]
        
        # Industry benchmarks and parameters
        self.industry_benchmarks = {
            "typical_capex_per_ton": {
                "Integrated Steel Plant": 800,  # USD per annual ton capacity
                "Electric Arc Furnace": 300,
                "Mini Mill": 250,
                "Specialty Steel Plant": 1200
            },
            "typical_ebitda_margin": {
                "Carbon Steel": 0.12,
                "Alloy Steel": 0.15,
                "Stainless Steel": 0.18,
                "Specialty Steel": 0.22
            },
            "production_costs": {
                "raw_material_percentage": 0.65,  # % of total production cost
                "energy_percentage": 0.15,
                "labor_percentage": 0.08,
                "other_percentage": 0.12
            }
        }
    
    def get_steel_grades(self):
        """Return list of available steel grades."""
        return self.steel_grades
    
    def get_facility_types(self):
        """Return list of facility types."""
        return self.facility_types
    
    def get_cash_flow_template(self, template_type, duration, initial_investment):
        """
        Generate cash flow template based on industry patterns.
        
        Args:
            template_type (str): Conservative, Moderate, or Aggressive Growth
            duration (int): Project duration in years
            initial_investment (float): Initial investment amount
            
        Returns:
            list: Cash flow projections
        """
        if duration <= 0:
            return []
        
        # Base annual cash flow as percentage of initial investment
        base_templates = {
            "Conservative Growth": {
                "base_cf_ratio": 0.15,  # 15% of initial investment annually
                "growth_rate": 0.02,    # 2% annual growth
                "ramp_up_years": 2,     # Years to reach full production
                "decline_start": 0.8    # Start decline at 80% of project life
            },
            "Moderate Growth": {
                "base_cf_ratio": 0.18,
                "growth_rate": 0.04,
                "ramp_up_years": 2,
                "decline_start": 0.85
            },
            "Aggressive Growth": {
                "base_cf_ratio": 0.22,
                "growth_rate": 0.06,
                "ramp_up_years": 1,
                "decline_start": 0.9
            }
        }
        
        template = base_templates.get(template_type, base_templates["Moderate Growth"])
        base_cf = initial_investment * template["base_cf_ratio"]
        
        cash_flows = []
        decline_year = int(duration * template["decline_start"])
        
        for year in range(duration):
            if year < template["ramp_up_years"]:
                # Ramp-up period
                ramp_factor = (year + 1) / template["ramp_up_years"]
                cf = base_cf * ramp_factor
            elif year < decline_year:
                # Growth period
                growth_years = year - template["ramp_up_years"] + 1
                cf = base_cf * (1 + template["growth_rate"]) ** growth_years
            else:
                # Decline period
                decline_factor = 1 - (year - decline_year) * 0.05  # 5% annual decline
                decline_factor = max(decline_factor, 0.7)  # Minimum 70% of peak
                peak_cf = base_cf * (1 + template["growth_rate"]) ** (decline_year - template["ramp_up_years"])
                cf = peak_cf * decline_factor
            
            cash_flows.append(round(cf, 2))
        
        return cash_flows
    
    def get_market_data(self):
        """
        Get current steel market data and prices.
        Note: In production, this would fetch from real APIs like Bloomberg, Reuters, etc.
        """
        try:
            # In a real implementation, this would fetch from actual market data APIs
            # For now, return realistic current market data based on recent trends
            
            market_data = {
                "steel_price": 650,  # USD per metric ton for hot-rolled coil
                "iron_ore_price": 115,  # USD per metric ton, 62% Fe content
                "coal_price": 180,  # USD per metric ton, coking coal
                "scrap_price": 380,  # USD per metric ton
                "natural_gas_price": 3.2,  # USD per MMBtu
                "electricity_price": 0.08,  # USD per kWh industrial rate
                "freight_rate": 25,  # USD per metric ton (average)
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data_source": "Market Analysis (Simulated)"
            }
            
            # Add price trends (simulated based on recent market patterns)
            market_data["price_trends"] = {
                "steel_price_change_30d": 2.1,  # % change
                "iron_ore_change_30d": -1.8,
                "coal_price_change_30d": 0.5,
                "market_sentiment": "Cautiously Optimistic"
            }
            
            return market_data
            
        except Exception as e:
            # Return default values if data fetch fails
            return {
                "steel_price": 600,
                "iron_ore_price": 120,
                "coal_price": 200,
                "scrap_price": 350,
                "natural_gas_price": 3.5,
                "electricity_price": 0.09,
                "freight_rate": 30,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data_source": "Default Values",
                "error": str(e)
            }
    
    def calculate_production_costs(self, facility_type, production_capacity, 
                                 steel_grade="Carbon Steel", location="USA"):
        """
        Calculate estimated production costs for steel facility.
        
        Args:
            facility_type (str): Type of steel facility
            production_capacity (float): Annual capacity in million tons
            steel_grade (str): Primary steel grade
            location (str): Facility location
            
        Returns:
            dict: Production cost breakdown
        """
        market_data = self.get_market_data()
        
        # Base costs per ton produced
        base_costs = {
            "Integrated Steel Plant": {
                "raw_materials": 420,  # Iron ore, coal, limestone
                "energy": 85,
                "labor": 45,
                "maintenance": 25,
                "other": 35
            },
            "Electric Arc Furnace": {
                "raw_materials": 380,  # Scrap metal primarily
                "energy": 120,  # Higher electricity usage
                "labor": 35,
                "maintenance": 20,
                "other": 25
            },
            "Mini Mill": {
                "raw_materials": 360,
                "energy": 100,
                "labor": 30,
                "maintenance": 18,
                "other": 22
            },
            "Specialty Steel Plant": {
                "raw_materials": 520,  # Premium alloys
                "energy": 110,
                "labor": 60,
                "maintenance": 35,
                "other": 45
            }
        }
        
        facility_costs = base_costs.get(facility_type, base_costs["Mini Mill"])
        
        # Apply grade multipliers
        grade_multipliers = {
            "Carbon Steel": 1.0,
            "Alloy Steel": 1.2,
            "Stainless Steel": 1.8,
            "Specialty Steel": 2.2
        }
        
        grade_key = next((k for k in grade_multipliers.keys() if k in steel_grade), "Carbon Steel")
        grade_multiplier = grade_multipliers[grade_key]
        
        # Calculate total costs
        adjusted_costs = {}
        total_cost_per_ton = 0
        
        for cost_type, base_cost in facility_costs.items():
            if cost_type == "raw_materials":
                # Adjust based on current market prices
                market_adjustment = 1.0  # Could adjust based on actual vs historical prices
                adjusted_cost = base_cost * grade_multiplier * market_adjustment
            else:
                adjusted_cost = base_cost * grade_multiplier
            
            adjusted_costs[cost_type] = adjusted_cost
            total_cost_per_ton += adjusted_cost
        
        # Calculate annual costs
        annual_production = production_capacity * 1000000  # Convert to tons
        annual_costs = {k: v * annual_production / 1000000 for k, v in adjusted_costs.items()}  # Million USD
        
        return {
            "cost_per_ton": adjusted_costs,
            "total_cost_per_ton": total_cost_per_ton,
            "annual_costs_million_usd": annual_costs,
            "total_annual_cost": sum(annual_costs.values()),
            "cost_breakdown_percentage": {
                k: (v / total_cost_per_ton) * 100 
                for k, v in adjusted_costs.items()
            }
        }
    
    def get_industry_ratios(self):
        """
        Get typical financial ratios for steel industry companies.
        
        Returns:
            dict: Industry financial ratios and benchmarks
        """
        return {
            "profitability_ratios": {
                "gross_margin_range": (0.15, 0.25),
                "ebitda_margin_range": (0.08, 0.20),
                "net_margin_range": (0.03, 0.12),
                "roe_range": (0.05, 0.15),
                "roa_range": (0.02, 0.08)
            },
            "efficiency_ratios": {
                "asset_turnover_range": (0.8, 1.5),
                "inventory_turnover_range": (6, 12),
                "receivables_turnover_range": (8, 15)
            },
            "leverage_ratios": {
                "debt_to_equity_range": (0.3, 0.8),
                "debt_to_assets_range": (0.2, 0.5),
                "interest_coverage_range": (2.5, 8.0)
            },
            "valuation_ratios": {
                "pe_ratio_range": (8, 18),
                "pb_ratio_range": (0.5, 1.5),
                "ev_ebitda_range": (4, 12)
            },
            "steel_specific_ratios": {
                "revenue_per_ton_range": (550, 750),
                "ebitda_per_ton_range": (50, 150),
                "capex_intensity_range": (0.04, 0.08)  # Capex as % of revenue
            }
        }
    
    def get_cyclical_patterns(self):
        """
        Get steel industry cyclical patterns and indicators.
        
        Returns:
            dict: Cyclical analysis data
        """
        return {
            "cycle_length": {
                "typical_cycle_years": 7,
                "expansion_phase_years": 3,
                "contraction_phase_years": 4
            },
            "leading_indicators": [
                "Construction activity",
                "Automotive production",
                "Manufacturing PMI",
                "Infrastructure spending",
                "GDP growth rate"
            ],
            "price_volatility": {
                "steel_price_volatility": 0.25,  # Annual standard deviation
                "raw_material_volatility": 0.30,
                "margin_volatility": 0.40
            },
            "capacity_utilization": {
                "peak_utilization": 0.90,
                "trough_utilization": 0.65,
                "current_estimated": 0.78
            }
        }
    
    def generate_comparable_projects(self, project_params):
        """
        Generate comparable steel industry projects for benchmarking.
        
        Args:
            project_params (dict): Current project parameters
            
        Returns:
            list: List of comparable project profiles
        """
        capacity = project_params.get('production_capacity', 5.0)
        facility_type = project_params.get('facility_type', 'Mini Mill')
        
        # Generate 3-5 comparable projects with similar characteristics
        comparables = []
        
        for i in range(4):
            # Vary capacity by ±30%
            comp_capacity = capacity * (0.7 + 0.6 * np.random.random())
            
            # Similar facility types
            similar_facilities = {
                "Integrated Steel Plant": ["Integrated Steel Plant", "Mini Mill"],
                "Electric Arc Furnace": ["Electric Arc Furnace", "Mini Mill"],
                "Mini Mill": ["Mini Mill", "Electric Arc Furnace"],
                "Specialty Steel Plant": ["Specialty Steel Plant", "Mini Mill"]
            }
            
            comp_facility = np.random.choice(similar_facilities.get(facility_type, ["Mini Mill"]))
            
            # Generate realistic financial metrics
            base_investment = comp_capacity * self.industry_benchmarks["typical_capex_per_ton"][comp_facility]
            investment_variation = 0.8 + 0.4 * np.random.random()
            comp_investment = base_investment * investment_variation
            
            # Generate returns based on facility type and market conditions
            base_irr = {
                "Integrated Steel Plant": 0.12,
                "Electric Arc Furnace": 0.15,
                "Mini Mill": 0.16,
                "Specialty Steel Plant": 0.18
            }.get(comp_facility, 0.14)
            
            comp_irr = base_irr * (0.8 + 0.4 * np.random.random())
            
            comparable = {
                "project_name": f"Steel Project {chr(65+i)}",
                "capacity_mt": round(comp_capacity, 1),
                "facility_type": comp_facility,
                "investment_musd": round(comp_investment, 1),
                "irr": round(comp_irr, 3),
                "payback_years": round(4 + 3 * np.random.random(), 1),
                "location": np.random.choice(["USA", "Europe", "Asia", "South America"]),
                "completion_year": 2020 + int(5 * np.random.random())
            }
            
            comparables.append(comparable)
        
        return comparables
    
    def get_environmental_factors(self):
        """
        Get environmental regulations and sustainability factors affecting steel investments.
        
        Returns:
            dict: Environmental considerations
        """
        return {
            "carbon_regulations": {
                "carbon_price_range_usd_per_ton": (20, 80),
                "emission_intensity_tons_co2_per_ton_steel": 2.3,
                "reduction_targets_by_2030": 0.30  # 30% reduction target
            },
            "sustainability_trends": [
                "Green hydrogen for steel production",
                "Electric arc furnace expansion",
                "Carbon capture and storage",
                "Scrap steel utilization increase",
                "Renewable energy adoption"
            ],
            "regulatory_compliance_costs": {
                "environmental_capex_percentage": 0.08,  # 8% of total capex
                "annual_compliance_cost_per_ton": 15
            },
            "sustainability_opportunities": {
                "green_steel_premium_percentage": 0.05,  # 5% price premium
                "carbon_credit_potential_usd_per_ton": 25,
                "energy_efficiency_savings_percentage": 0.12
            }
        }
