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



# Load datasets
energy_df = load_energy_data()
occupancy_df = load_occupancy_data()


# Initialize agents
context_agent = ContextAgent()
investigation_agent = InvestigationAgent()
rootcause_agent = RootCauseAgent()
recommendation_agent = RecommendationAgent()
savings_agent = SavingsAgent()
score_agent = SustainabilityScoreAgent()
summary_agent = ExecutiveSummaryAgent()


# Select sample records
energy_row = energy_df.loc[
    energy_df["Appliances"].idxmax()
]
occupancy_row = occupancy_df.iloc[0]


# Context Analysis
context_result = context_agent.analyze(
    energy_row,
    occupancy_row
)

print("\n===================================")
print("EcoMind AI Context Report")
print("===================================")
print(context_result)


# Investigation Analysis
investigation_result = investigation_agent.investigate(
    energy_row
)

print("\n===================================")
print("Investigation Report")
print("===================================")
print(investigation_result)

# Root Cause Analysis
rootcause_result = rootcause_agent.analyze(
    context_result,
    investigation_result
)

print("\n===================================")
print("Root Cause Analysis")
print("===================================")
print(rootcause_result)

# Recommendation Analysis
recommendation_result = recommendation_agent.recommend(
    rootcause_result
)

print("\n===================================")
print("Recommendation Report")
print("===================================")
print(recommendation_result)

# Savings Prediction
savings_result = savings_agent.predict(
    recommendation_result
)

print("\n===================================")
print("Savings Prediction")
print("===================================")
print(savings_result)

score_result = score_agent.calculate(
    investigation_result,
    savings_result
)

print("\n===================================")
print("Sustainability Score")
print("===================================")
print(score_result)

# Generate Executive Summary
summary = summary_agent.generate(
    rootcause_result,
    recommendation_result,
    savings_result,
    score_result
)

print("\n===================================")
print("Executive Summary")
print("===================================")
print(summary)

