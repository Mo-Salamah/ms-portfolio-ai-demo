"""
وكلاء منصة الذكاء الاصطناعي للمحفظة (أ)
"""

from .base_agent import BaseAgent, AgentResponse

# Project 1 agents
from .project1 import (
    CoordinatorAgent,
    DataAnalysisAgent,
    FollowupAgent,
    ReportingAgent,
    QualityCheckAgent
)

# Project 2 agents
from .project2 import (
    StrategicPlanningAgent,
    BenchmarkingAgent,
    KPIAgent,
    CritiqueAgent,
    ContentPrepAgent
)

__all__ = [
    # Base
    "BaseAgent",
    "AgentResponse",
    # Project 1
    "CoordinatorAgent",
    "DataAnalysisAgent",
    "FollowupAgent",
    "ReportingAgent",
    "QualityCheckAgent",
    # Project 2
    "StrategicPlanningAgent",
    "BenchmarkingAgent",
    "KPIAgent",
    "CritiqueAgent",
    "ContentPrepAgent",
]
