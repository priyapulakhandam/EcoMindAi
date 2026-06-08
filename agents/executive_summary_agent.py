class ExecutiveSummaryAgent:

    def generate(
        self,
        rootcause_result,
        recommendation_result,
        savings_result,
        score_result
    ):

        summary = f"""
        EXECUTIVE SUMMARY

        Root Cause:
        {rootcause_result['root_cause']}

        Recommendations:
        {', '.join(recommendation_result['recommendations'])}

        Monthly Savings:
        ₹{savings_result['monthly_savings']}

        Annual Savings:
        ₹{savings_result['annual_savings']}

        Carbon Reduction:
        {savings_result['carbon_reduction_percent']}%

        Sustainability Score:
        {score_result['sustainability_score']}/100
        """

        return summary