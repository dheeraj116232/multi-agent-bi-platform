"""
LangGraph pipeline — wires all 5 agents into a sequential state graph.
"""

from langgraph.graph import StateGraph, END
from core.state import AgentState
from agents.cleaner    import data_cleaning_agent
from agents.analytics  import analytics_agent
from agents.visualizer import visualization_agent
from agents.forecaster import forecast_agent
from agents.reporter   import summary_agent


def build_graph():
    g = StateGraph(AgentState)
    g.add_node("cleaner",    data_cleaning_agent)
    g.add_node("analytics",  analytics_agent)
    g.add_node("visualizer", visualization_agent)
    g.add_node("forecaster", forecast_agent)
    g.add_node("reporter",   summary_agent)

    g.set_entry_point("cleaner")
    g.add_edge("cleaner",    "analytics")
    g.add_edge("analytics",  "visualizer")
    g.add_edge("visualizer", "forecaster")
    g.add_edge("forecaster", "reporter")
    g.add_edge("reporter",   END)

    return g.compile()


# Compiled once at startup — reused for all requests
pipeline = build_graph()