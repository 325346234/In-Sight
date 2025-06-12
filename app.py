import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io
import json
from datetime import datetime, timedelta

from financial_calculator import FinancialCalculator
from ai_analyzer import AIAnalyzer
from steel_industry_data import SteelIndustryData

# Page configuration
st.set_page_config(
    page_title="Steel Industry Investment Analysis",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'ai_analysis' not in st.session_state:
    st.session_state.ai_analysis = None

# Initialize components
@st.cache_resource
def get_components():
    return FinancialCalculator(), AIAnalyzer(), SteelIndustryData()

financial_calc, ai_analyzer, steel_data = get_components()

# Main title and description
st.title("🏭 Steel Industry Investment Economic Analysis")
st.markdown("""
This application provides comprehensive investment analysis for steel industry projects, 
including AI-powered economic evaluation, risk assessment, and investment recommendations.
""")

# Sidebar for navigation
st.sidebar.title("Navigation")
analysis_type = st.sidebar.selectbox(
    "Select Analysis Type",
    ["Project Analysis", "Detailed Steel Investment Analysis", "Comparative Analysis", "Market Analysis"]
)

# Main content area
if analysis_type == "Project Analysis":
    # Project Input Section
    st.header("📊 Project Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Basic Project Details")
        project_name = st.text_input("Project Name", placeholder="Enter project name")
        initial_investment = st.number_input(
            "Initial Investment (Million USD)", 
            min_value=0.0, 
            value=100.0, 
            step=1.0,
            help="Total initial capital required for the project"
        )
        project_duration = st.number_input(
            "Project Duration (Years)", 
            min_value=1, 
            max_value=30, 
            value=10,
            help="Expected operational lifetime of the project"
        )
        
    with col2:
        st.subheader("Steel Industry Parameters")
        production_capacity = st.number_input(
            "Annual Production Capacity (Million Tons)", 
            min_value=0.1, 
            value=5.0, 
            step=0.1
        )
        steel_grade = st.selectbox(
            "Primary Steel Grade",
            steel_data.get_steel_grades()
        )
        facility_type = st.selectbox(
            "Facility Type",
            ["Integrated Steel Plant", "Electric Arc Furnace", "Mini Mill", "Specialty Steel Plant"]
        )
    
    # Cash Flow Inputs
    st.subheader("💰 Cash Flow Projections")
    
    # Option to input cash flows manually or use templates
    input_method = st.radio(
        "Cash Flow Input Method",
        ["Manual Input", "Use Industry Template", "Upload Data"]
    )
    
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
    # Import and display the detailed analysis
    from steel_investment_analysis import display_analysis_results
    display_analysis_results()

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
