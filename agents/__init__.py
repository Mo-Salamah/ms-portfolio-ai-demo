"""
Agents for MS Portfolio AI Agent Demo
وكلاء نظام المحفظة الذكي

Includes:
- Base agent and response classes
- Legacy orchestrator and specialist agents
- Project 1 agents (Events Oversight)
- Project 2 agents (Major Celebrations)
"""

from .base_agent import BaseAgent, AgentResponse

# Legacy agents (for backward compatibility)
from .orchestrator import OrchestratorAgent
from .benchmarking_agent import BenchmarkingAgent
from .kpi_agent import KPIAgent
from .critique_agent import CritiqueAgent
from .media_agent import MediaAgent
from .slide_agent import SlideAgent

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
    BenchmarkingAgent as P2BenchmarkingAgent,
    KPIAgent as P2KPIAgent,
    CritiqueAgent as P2CritiqueAgent,
    ContentPrepAgent
)

__all__ = [
    # Base
    "BaseAgent",
    "AgentResponse",
    # Legacy
    "OrchestratorAgent",
    "BenchmarkingAgent",
    "KPIAgent",
    "CritiqueAgent",
    "MediaAgent",
    "SlideAgent",
    # Project 1
    "CoordinatorAgent",
    "DataAnalysisAgent",
    "FollowupAgent",
    "ReportingAgent",
    "QualityCheckAgent",
    # Project 2
    "StrategicPlanningAgent",
    "P2BenchmarkingAgent",
    "P2KPIAgent",
    "P2CritiqueAgent",
    "ContentPrepAgent",
]
