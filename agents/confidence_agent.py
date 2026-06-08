class ConfidenceAgent:

    def calculate(
        self,
        context_result,
        investigation_result,
        rootcause_result
    ):

        score = 50

        # Large anomaly
        if investigation_result["status"] == "Anomaly Detected":
            score += 25

        # Weather not influencing much
        if rootcause_result["weather_contribution"] <= 10:
            score += 10

        # Occupancy not influencing much
        if rootcause_result["occupancy_contribution"] <= 15:
            score += 10

        # High energy spike
        if investigation_result["actual_energy"] > 500:
            score += 5

        if score > 100:
            score = 100

        return {
            "confidence_score": score,
            "confidence_level":
                "High" if score >= 80
                else "Medium"
        }