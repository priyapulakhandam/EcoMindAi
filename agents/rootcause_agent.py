class RootCauseAgent:

    def analyze(self, context_result, investigation_result):

        weather_factor = 0
        occupancy_factor = 0

        # Weather Impact
        if context_result["weather_status"] == "Hot":
            weather_factor = 15

        # Occupancy Impact
        if context_result["occupancy_status"] == "Occupied":
            occupancy_factor = 10

        total_known_factor = weather_factor + occupancy_factor

        # Root Cause Logic
        if investigation_result["status"] == "Anomaly Detected":

            if total_known_factor < 25:
                cause = "Potential Infrastructure Inefficiency"
            else:
                cause = "Environment Driven Consumption"

        else:
            cause = "Normal Operation"

        return {
            "weather_contribution": weather_factor,
            "occupancy_contribution": occupancy_factor,
            "root_cause": cause
        }