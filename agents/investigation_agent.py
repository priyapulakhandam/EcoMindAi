class InvestigationAgent:

    def investigate(self, energy_row):

        actual_energy = energy_row["Appliances"]

        # Baseline threshold
        expected_energy = 150

        deviation = actual_energy - expected_energy

        if actual_energy > expected_energy:
            status = "Anomaly Detected"
        else:
            status = "Normal"

        return {
            "actual_energy": actual_energy,
            "expected_energy": expected_energy,
            "deviation": deviation,
            "status": status
        }