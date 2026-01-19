"""
System Prompts for MS Portfolio AI Agent Demo
التعليمات النظامية لوكلاء نظام المحفظة الذكي
"""

from .orchestrator_prompt import ORCHESTRATOR_SYSTEM_PROMPT
from .benchmarking_prompt import BENCHMARKING_SYSTEM_PROMPT
from .kpi_prompt import KPI_SYSTEM_PROMPT
from .critique_prompt import CRITIQUE_SYSTEM_PROMPT
from .slide_prompt import SLIDE_SYSTEM_PROMPT

__all__ = [
    "ORCHESTRATOR_SYSTEM_PROMPT",
    "BENCHMARKING_SYSTEM_PROMPT",
    "KPI_SYSTEM_PROMPT",
    "CRITIQUE_SYSTEM_PROMPT",
    "SLIDE_SYSTEM_PROMPT",
]
