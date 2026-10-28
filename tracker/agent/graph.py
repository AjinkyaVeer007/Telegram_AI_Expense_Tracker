"""Assemble and compile the LangGraph workflow.

START -> agent -> (tools -> agent | tools -> process -> validate -> save -> END) | END
"""

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from tracker.agent.nodes import (
    expense_tracker_agent,
    process_tool_result,
    save_to_mongodb,
    validate_transaction,
)
from tracker.agent.routing import route_after_tool, route_agent, route_validation
from tracker.agent.state import ExpenseState
from tracker.tools import ALL_TOOLS


def build_graph():
    graph = StateGraph(ExpenseState)

    graph.add_node("expense_tracker_agent", expense_tracker_agent)
    graph.add_node("tools", ToolNode(ALL_TOOLS))
    graph.add_node("process_tool_result", process_tool_result)
    graph.add_node("validate_transaction", validate_transaction)
    graph.add_node("save_to_mongodb", save_to_mongodb)

    graph.add_edge(START, "expense_tracker_agent")
    graph.add_conditional_edges(
        "expense_tracker_agent",
        route_agent,
        {"tool": "tools", "end": END},
    )
    graph.add_conditional_edges(
        "tools",
        route_after_tool,
        {"process_transaction": "process_tool_result", "agent": "expense_tracker_agent"},
    )
    graph.add_edge("process_tool_result", "validate_transaction")
    graph.add_conditional_edges(
        "validate_transaction",
        route_validation,
        {"valid": "save_to_mongodb", "invalid": END},
    )
    graph.add_edge("save_to_mongodb", END)

    return graph.compile()


app = build_graph()
