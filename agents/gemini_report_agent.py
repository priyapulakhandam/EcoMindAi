import os
from urllib import response
import google.generativeai as genai

from dotenv import load_dotenv

load_dotenv()


class GeminiReportAgent:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        genai.configure(
            api_key=api_key
        )

        self.model = genai.GenerativeModel(
            "gemini-2.5-flash"
        )

    def generate_report(
        self,
        context_result,
        investigation_result,
        rootcause_result,
        recommendation_result,
        savings_result,
        score_result
    ):

        prompt = f"""
You are an expert Sustainability Consultant.

Analyze the following sustainability assessment.

Context:
{context_result}

Investigation:
{investigation_result}

Root Cause:
{rootcause_result}

Recommendations:
{recommendation_result}

Savings:
{savings_result}

Sustainability Score:
{score_result}

Generate:

1. Executive Summary
2. Root Cause Analysis
3. Business Impact
4. Sustainability Impact
5. Recommended Next Actions

Use professional consulting language.
"""

        try:

            response = self.model.generate_content(
                prompt
            )

            return response.text

        except Exception as e:

            return f"Gemini Error: {str(e)}"