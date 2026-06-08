class SavingsAgent:

    def predict(self, recommendation_result):

        recommendations = recommendation_result["recommendations"]

        if "System operating normally" in recommendations:

            monthly_savings = 0
            annual_savings = 0
            carbon_reduction = 0

        else:

            monthly_savings = 12000
            annual_savings = monthly_savings * 12
            carbon_reduction = 15

        return {
            "monthly_savings": monthly_savings,
            "annual_savings": annual_savings,
            "carbon_reduction_percent": carbon_reduction
        }