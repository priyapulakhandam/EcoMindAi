class SimulationAgent:

    def simulate(self, savings_result):

        monthly_savings = savings_result["monthly_savings"]

        simulated_savings = monthly_savings * 1.5

        return {
            "scenario":
                "Optimize HVAC runtime by 15%",

            "predicted_monthly_savings":
                int(simulated_savings),

            "predicted_carbon_reduction":
                20,

            "predicted_score":
                85
        }