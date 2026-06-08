class SustainabilityScoreAgent:

    def calculate(
        self,
        investigation_result,
        savings_result
    ):

        score = 100

        if investigation_result["status"] == "Anomaly Detected":
            score -= 20

        if savings_result["carbon_reduction_percent"] > 0:
            score -= 10

        if score < 0:
            score = 0

        return {
            "sustainability_score": score
        }