class ContextAgent:

    def analyze(self, energy_row, occupancy_row):

        context = {}

        # Energy Status
        if energy_row["Appliances"] > 150:
            context["energy_status"] = "High"
        else:
            context["energy_status"] = "Normal"

        # Weather Status
        if energy_row["T_out"] > 25:
            context["weather_status"] = "Hot"
        else:
            context["weather_status"] = "Normal"

        # Humidity Status
        if energy_row["RH_out"] > 70:
            context["humidity_status"] = "High"
        else:
            context["humidity_status"] = "Normal"

        # Occupancy Status
        if occupancy_row["Occupancy"] == 1:
            context["occupancy_status"] = "Occupied"
        else:
            context["occupancy_status"] = "Unoccupied"

        return context