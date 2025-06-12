import json
import os
from openai import OpenAI
import numpy as np
from datetime import datetime

class AIAnalyzer:
    """
    AI-powered investment analyzer using OpenAI GPT-4o for steel industry investment analysis.
    Provides intelligent insights, risk assessment, and investment recommendations.
    """
    
    def __init__(self):
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.model = "gpt-4o"
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Steel industry context and knowledge base
        self.steel_industry_context = """
        You are an expert investment analyst specializing in the steel industry with deep knowledge of:
        - Steel production processes (blast furnace, electric arc furnace, mini mills)
        - Raw material markets (iron ore, coking coal, scrap metal)
        - Steel product markets and pricing dynamics
        - Industry cyclicality and economic indicators
        - Environmental regulations and sustainability trends
        - Technology disruptions and automation
        - Global trade dynamics and tariffs
        - Industry consolidation trends
        """
    
    def analyze_investment(self, financial_data):
        """
        Perform comprehensive AI-powered investment analysis.
        
        Args:
            financial_data (dict): Complete financial analysis results
            
        Returns:
            dict: AI analysis results with recommendations and insights
        """
        if not self.api_key:
            raise Exception("OpenAI API key not configured")
        
        try:
            # Prepare analysis prompt
            analysis_prompt = self._create_analysis_prompt(financial_data)
            
            # Get AI analysis
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.steel_industry_context
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=2000
            )
            
            # Parse and validate response
            ai_analysis = json.loads(response.choices[0].message.content)
            
            # Enhance with quantitative insights
            enhanced_analysis = self._enhance_with_quantitative_insights(ai_analysis, financial_data)
            
            return enhanced_analysis
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse AI response: {str(e)}")
        except Exception as e:
            raise Exception(f"AI analysis failed: {str(e)}")
    
    def _create_analysis_prompt(self, financial_data):
        """
        Create comprehensive analysis prompt for the AI model.
        """
        steel_params = financial_data.get('steel_parameters', {})
        
        prompt = f"""
        Analyze this steel industry investment project and provide detailed insights in JSON format.
        
        PROJECT DETAILS:
        - Project Name: {financial_data.get('project_name', 'N/A')}
        - Initial Investment: ${financial_data.get('initial_investment', 0):.1f} Million USD
        - Project Duration: {len(financial_data.get('cash_flows', []))} years
        - Production Capacity: {steel_params.get('production_capacity', 0)} Million Tons/Year
        - Steel Grade: {steel_params.get('steel_grade', 'N/A')}
        - Facility Type: {steel_params.get('facility_type', 'N/A')}
        
        FINANCIAL METRICS:
        - NPV: ${financial_data.get('npv', 0):.2f} Million USD
        - IRR: {financial_data.get('irr', 0):.2%} (if available)
        - Payback Period: {financial_data.get('payback_period', 'N/A')} years
        - Discount Rate: {financial_data.get('discount_rate', 0):.1%}
        
        MARKET CONDITIONS:
        - Iron Ore Price: ${steel_params.get('iron_ore_price', 0)}/ton
        - Coal Price: ${steel_params.get('coal_price', 0)}/ton  
        - Steel Price: ${steel_params.get('steel_price', 0)}/ton
        
        RISK METRICS:
        - Value at Risk (95%): ${financial_data.get('risk_metrics', {}).get('var_95', 0):.1f} Million USD
        - Standard Deviation: ${financial_data.get('risk_metrics', {}).get('std_dev', 0):.1f} Million USD
        - Coefficient of Variation: {financial_data.get('risk_metrics', {}).get('coeff_variation', 0):.2f}
        
        CASH FLOWS (Million USD):
        {', '.join([f'Year {i+1}: ${cf:.1f}' for i, cf in enumerate(financial_data.get('cash_flows', []))])}
        
        Please provide analysis in this exact JSON format:
        {{
            "recommendation": "Strong Buy/Buy/Hold/Sell/Strong Sell",
            "confidence_score": 0.0-1.0,
            "key_insights": ["insight1", "insight2", "insight3"],
            "risk_factors": ["risk1", "risk2", "risk3"],
            "opportunities": ["opportunity1", "opportunity2", "opportunity3"],
            "market_outlook": "brief market assessment",
            "competitive_position": "assessment of competitive position",
            "financial_strength": "assessment of financial metrics",
            "operational_efficiency": "assessment of operational aspects",
            "detailed_analysis": "comprehensive analysis paragraph",
            "action_items": ["action1", "action2", "action3"]
        }}
        
        Consider current steel industry trends, market cycles, environmental regulations, 
        technology changes, and global economic conditions in your analysis.
        """
        
        return prompt
    
    def _enhance_with_quantitative_insights(self, ai_analysis, financial_data):
        """
        Enhance AI analysis with additional quantitative insights.
        """
        # Add quantitative benchmarks
        npv = financial_data.get('npv', 0)
        irr = financial_data.get('irr', 0)
        payback = financial_data.get('payback_period', float('inf'))
        
        # Industry benchmarks (these would come from real data in production)
        industry_benchmarks = {
            'typical_irr_range': (0.12, 0.18),
            'typical_payback_range': (5, 8),
            'min_acceptable_npv': 0
        }
        
        # Add benchmark comparisons
        benchmark_analysis = []
        
        if irr:
            if irr > industry_benchmarks['typical_irr_range'][1]:
                benchmark_analysis.append("IRR significantly exceeds industry typical range")
            elif irr < industry_benchmarks['typical_irr_range'][0]:
                benchmark_analysis.append("IRR below industry typical range - higher risk")
            else:
                benchmark_analysis.append("IRR within industry typical range")
        
        if payback and payback != float('inf'):
            if payback < industry_benchmarks['typical_payback_range'][0]:
                benchmark_analysis.append("Excellent payback period - faster than industry average")
            elif payback > industry_benchmarks['typical_payback_range'][1]:
                benchmark_analysis.append("Payback period longer than industry average")
            else:
                benchmark_analysis.append("Payback period aligned with industry standards")
        
        # Add steel industry specific insights
        steel_params = financial_data.get('steel_parameters', {})
        steel_insights = self._generate_steel_specific_insights(steel_params)
        
        # Enhance the AI analysis
        enhanced_analysis = ai_analysis.copy()
        enhanced_analysis['benchmark_analysis'] = benchmark_analysis
        enhanced_analysis['steel_industry_insights'] = steel_insights
        enhanced_analysis['analysis_timestamp'] = datetime.now().isoformat()
        
        # Add quantitative risk assessment
        risk_metrics = financial_data.get('risk_metrics', {})
        if risk_metrics:
            enhanced_analysis['quantitative_risk_level'] = self._assess_quantitative_risk(risk_metrics)
        
        return enhanced_analysis
    
    def _generate_steel_specific_insights(self, steel_params):
        """
        Generate steel industry specific insights based on project parameters.
        """
        insights = []
        
        capacity = steel_params.get('production_capacity', 0)
        facility_type = steel_params.get('facility_type', '')
        steel_grade = steel_params.get('steel_grade', '')
        
        # Capacity analysis
        if capacity > 10:
            insights.append("Large-scale operation with potential economies of scale benefits")
        elif capacity < 2:
            insights.append("Small-scale operation - focus on niche markets and specialty products")
        else:
            insights.append("Medium-scale operation suitable for regional market serving")
        
        # Facility type insights
        if 'Electric Arc Furnace' in facility_type:
            insights.append("EAF technology offers flexibility and lower capex, suitable for scrap-based production")
        elif 'Integrated' in facility_type:
            insights.append("Integrated plant requires higher investment but offers better cost control over raw materials")
        elif 'Mini Mill' in facility_type:
            insights.append("Mini mill model provides operational flexibility and market responsiveness")
        
        # Steel grade considerations
        if 'Specialty' in steel_grade or 'Stainless' in steel_grade:
            insights.append("Specialty steel grades typically command premium pricing but require specialized expertise")
        elif 'Carbon' in steel_grade:
            insights.append("Carbon steel production benefits from commodity scale but faces price volatility")
        
        return insights
    
    def _assess_quantitative_risk(self, risk_metrics):
        """
        Assess quantitative risk level based on calculated metrics.
        """
        var_95 = risk_metrics.get('var_95', 0)
        coeff_variation = risk_metrics.get('coeff_variation', 0)
        
        if var_95 > 100 or coeff_variation > 0.5:
            return "High Risk"
        elif var_95 > 50 or coeff_variation > 0.3:
            return "Medium Risk"
        else:
            return "Low Risk"
    
    def generate_scenario_analysis(self, base_case_data, scenarios):
        """
        Generate AI-powered scenario analysis for different market conditions.
        
        Args:
            base_case_data (dict): Base case financial data
            scenarios (list): List of scenario descriptions
            
        Returns:
            dict: Scenario analysis with AI insights
        """
        if not self.api_key:
            raise Exception("OpenAI API key not configured")
        
        try:
            scenario_prompt = f"""
            Analyze the following steel industry investment scenarios and provide insights for each.
            
            BASE CASE:
            NPV: ${base_case_data.get('npv', 0):.2f}M
            IRR: {base_case_data.get('irr', 0):.2%}
            
            SCENARIOS TO ANALYZE:
            {', '.join(scenarios)}
            
            For each scenario, provide:
            1. Expected impact on NPV and IRR
            2. Key risk factors
            3. Mitigation strategies
            4. Investment recommendation adjustments
            
            Respond in JSON format with scenario analysis for each case.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.steel_industry_context},
                    {"role": "user", "content": scenario_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.4,
                max_tokens=1500
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            raise Exception(f"Scenario analysis failed: {str(e)}")
    
    def generate_market_intelligence(self):
        """
        Generate current market intelligence and trends analysis for steel industry.
        
        Returns:
            dict: Market intelligence insights
        """
        if not self.api_key:
            raise Exception("OpenAI API key not configured")
        
        try:
            market_prompt = """
            Provide current steel industry market intelligence and investment considerations.
            Include:
            1. Current market trends and outlook
            2. Key price drivers and volatility factors
            3. Regulatory and environmental considerations
            4. Technology trends affecting investments
            5. Geographic and trade considerations
            6. Investment timing recommendations
            
            Focus on actionable insights for investment decision-making.
            Respond in JSON format with structured market intelligence.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.steel_industry_context},
                    {"role": "user", "content": market_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.5,
                max_tokens=1200
            )
            
            market_intelligence = json.loads(response.choices[0].message.content)
            market_intelligence['generated_at'] = datetime.now().isoformat()
            
            return market_intelligence
            
        except Exception as e:
            raise Exception(f"Market intelligence generation failed: {str(e)}")
