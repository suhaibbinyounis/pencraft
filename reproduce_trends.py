
from openblog.tools.trends import TrendsTool
import logging

# Configure logging to print warnings
logging.basicConfig(level=logging.WARNING)

tool = TrendsTool()
topic = "The 2026 Recession Playbook: How to Profit When the Market Bleeds"
print(f"Testing trends for: {topic}")

try:
    tool.get_trends_data(topic)
    print("Success")
except Exception as e:
    print(f"Failed: {e}")
