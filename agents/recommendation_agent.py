class RecommendationAgent:

    def recommend(self, rootcause_result):

        cause = rootcause_result["root_cause"]

        recommendations = []

        if cause == "Potential Infrastructure Inefficiency":

            recommendations.append(
                "Inspect cooling and HVAC systems"
            )

            recommendations.append(
                "Perform equipment maintenance"
            )

            recommendations.append(
                "Optimize appliance schedules"
            )

        elif cause == "Environment Driven Consumption":

            recommendations.append(
                "Adjust cooling schedule"
            )

            recommendations.append(
                "Improve insulation"
            )

            recommendations.append(
                "Use smart temperature controls"
            )

        else:

            recommendations.append(
                "System operating normally"
            )

        return {
            "recommendations": recommendations
        }