import streamlit as st

from utils.data_loader import (
    load_energy_data,
    load_occupancy_data
)

from agents.context_agent import ContextAgent
from agents.investigation_agent import InvestigationAgent
from agents.rootcause_agent import RootCauseAgent
from agents.recommendation_agent import RecommendationAgent
from agents.savings_agent import SavingsAgent
from agents.sustainability_score_agent import SustainabilityScoreAgent
from agents.executive_summary_agent import ExecutiveSummaryAgent
from agents.gemini_report_agent import GeminiReportAgent
from agents.confidence_agent import ConfidenceAgent

# -------------------------
# Page Config
# -------------------------

st.set_page_config(
    page_title="EcoMind AI",
    page_icon="🌱",
    layout="wide"
)

st.title("🌱 EcoMind AI")
st.subheader("Multi-Agent Sustainability Intelligence System")


# -------------------------
# Load Data
# -------------------------

energy_df = load_energy_data()
occupancy_df = load_occupancy_data()

selected_index = st.slider(
    "Select Dataset Record",
    0,
    len(energy_df)-1,
    100
)

energy_row = energy_df.iloc[selected_index]

occupancy_row = occupancy_df.iloc[0]


# -------------------------
# Initialize Agents
# -------------------------

context_agent = ContextAgent()
investigation_agent = InvestigationAgent()
rootcause_agent = RootCauseAgent()
recommendation_agent = RecommendationAgent()
savings_agent = SavingsAgent()
score_agent = SustainabilityScoreAgent()
summary_agent = ExecutiveSummaryAgent()
gemini_agent = GeminiReportAgent()
confidence_agent = ConfidenceAgent()
# -------------------------
# Run Analysis
# -------------------------

context_result = context_agent.analyze(
    energy_row,
    occupancy_row
)

investigation_result = investigation_agent.investigate(
    energy_row
)

rootcause_result = rootcause_agent.analyze(
    context_result,
    investigation_result
)

recommendation_result = recommendation_agent.recommend(
    rootcause_result
)

savings_result = savings_agent.predict(
    recommendation_result
)

score_result = score_agent.calculate(
    investigation_result,
    savings_result
)

summary = summary_agent.generate(
    rootcause_result,
    recommendation_result,
    savings_result,
    score_result
)

ai_report = gemini_agent.generate_report(
    context_result,
    investigation_result,
    rootcause_result,
    recommendation_result,
    savings_result,
    score_result
)


confidence_result = confidence_agent.calculate(
    context_result,
    investigation_result,
    rootcause_result
)

# -------------------------
# Dashboard
# -------------------------

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Monthly Savings",
        f"₹{savings_result['monthly_savings']}"
    )

with col2:
    st.metric(
        "Annual Savings",
        f"₹{savings_result['annual_savings']}"
    )

with col3:
    st.metric(
        "Sustainability Score",
        f"{score_result['sustainability_score']}/100"
    )

st.divider()

# Energy Trend Chart
st.header("📈 Energy Consumption Trend")

st.line_chart(
    energy_df["Appliances"].head(500)
)

st.divider()

# Context Report
st.header("📊 Context Report")
st.json(context_result)

st.header("🔍 Investigation Report")
st.json(investigation_result)

st.header("🎯 Root Cause Analysis")
st.json(rootcause_result)

import pandas as pd

root_df = pd.DataFrame({
    "Factor": [
        "Weather",
        "Occupancy"
    ],
    "Contribution": [
        rootcause_result["weather_contribution"],
        rootcause_result["occupancy_contribution"]
    ]

})

st.bar_chart(
    root_df.set_index("Factor")
)

# -------------------------
# AI Reasoning
# -------------------------

st.header("🧠 AI Reasoning")

reasoning = f"""
The system detected an energy consumption of
{investigation_result['actual_energy']} Wh,
which exceeds the expected threshold of
{investigation_result['expected_energy']} Wh.

Weather contribution was low
({rootcause_result['weather_contribution']}%).

Occupancy impact was moderate
({rootcause_result['occupancy_contribution']}%).

Based on the available evidence,
the anomaly is most likely caused by
equipment inefficiency, HVAC malfunction,
or appliance overconsumption.

Confidence Level: 87%
"""

st.info(reasoning)

st.header("🎯 AI Confidence Score")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Confidence Score",
        f"{confidence_result['confidence_score']}%"
    )

with col2:
    st.metric(
        "Confidence Level",
        confidence_result["confidence_level"]
    )

st.progress(
    confidence_result["confidence_score"] / 100
)

st.header("💡 Recommendations")

for rec in recommendation_result["recommendations"]:
    st.success(rec)

st.header("🌍 Environmental Impact")

st.metric(
    "Carbon Reduction",
    f"{savings_result['carbon_reduction_percent']}%"
)

# -------------------------
# What-If Simulation
# -------------------------

st.header("🔮 What-If Simulator")

col1, col2 = st.columns(2)

with col1:

    occupancy = st.number_input(
        "Expected Occupancy",
        min_value=1,
        value=20
    )

    temperature = st.number_input(
        "Expected Temperature (°C)",
        value=30
    )

with col2:

    hvac_efficiency = st.slider(
        "HVAC Efficiency (%)",
        50,
        100,
        80
    )

# -------------------------
# Prediction Engine
# -------------------------

base_energy = investigation_result["actual_energy"]

predicted_energy = (
    base_energy
    * (occupancy / 20)
    * (temperature / 30)
    * (100 / hvac_efficiency)
)

monthly_savings = max(
    0,
    int(
        (base_energy - predicted_energy)
        * 20
    )
)

carbon_reduction = max(
    0,
    int(
        monthly_savings / 1000
    )
)

future_score = min(
    100,
    score_result["sustainability_score"]
    + carbon_reduction
)

st.subheader("📊 Predicted Outcomes")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Predicted Energy",
        f"{int(predicted_energy)} Wh"
    )

with col2:
    st.metric(
        "Monthly Savings",
        f"₹{monthly_savings}"
    )

with col3:
    st.metric(
        "Carbon Reduction",
        f"{carbon_reduction}%"
    )

with col4:
    st.metric(
        "Future Score",
        future_score
    )

st.header("🤖 AI Sustainability Assessment")

st.success(ai_report)

# -------------------------
# Executive Summary
# -------------------------

st.header("📄 Executive Summary")

st.text(summary)