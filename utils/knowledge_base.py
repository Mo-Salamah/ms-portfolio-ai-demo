"""
Knowledge Base for MS Portfolio AI Agent Demo
قاعدة المعرفة لنظام المحفظة الذكي

This module provides data retrieval utilities for accessing synthetic data
including events, benchmarks, KPIs, and organizations.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Any


class KnowledgeBase:
    """
    Knowledge base for retrieving and querying synthetic data.
    قاعدة المعرفة لاسترجاع البيانات والاستعلام عنها
    """

    def __init__(self, data_dir: str = None):
        """
        Initialize the knowledge base by loading all JSON data files.

        Args:
            data_dir: Path to the data directory. Defaults to 'data' in project root.
        """
        if data_dir is None:
            # Get the directory where this file is located
            current_dir = Path(__file__).parent
            # Go up one level to project root, then into data
            data_dir = current_dir.parent / "data"
        else:
            data_dir = Path(data_dir)

        self.data_dir = data_dir
        self._events_data: Dict = {}
        self._benchmarks_data: Dict = {}
        self._kpis_data: Dict = {}
        self._organizations_data: Dict = {}

        self._load_all_data()

    def _load_all_data(self):
        """Load all JSON data files into memory."""
        try:
            # Load events
            events_path = self.data_dir / "events.json"
            if events_path.exists():
                with open(events_path, "r", encoding="utf-8") as f:
                    self._events_data = json.load(f)

            # Load benchmarks
            benchmarks_path = self.data_dir / "benchmarks.json"
            if benchmarks_path.exists():
                with open(benchmarks_path, "r", encoding="utf-8") as f:
                    self._benchmarks_data = json.load(f)

            # Load KPIs
            kpis_path = self.data_dir / "kpi_library.json"
            if kpis_path.exists():
                with open(kpis_path, "r", encoding="utf-8") as f:
                    self._kpis_data = json.load(f)

            # Load organizations
            orgs_path = self.data_dir / "organizations.json"
            if orgs_path.exists():
                with open(orgs_path, "r", encoding="utf-8") as f:
                    self._organizations_data = json.load(f)

        except json.JSONDecodeError as e:
            print(f"Error loading JSON data: {e}")
            raise

    # ==================== Events Methods ====================

    def get_celebration_info(self) -> Dict:
        """Get information about the main celebration."""
        return self._events_data.get("celebration", {})

    def get_all_events(self) -> List[Dict]:
        """Get all events."""
        return self._events_data.get("events", [])

    def get_event_by_id(self, event_id: str) -> Optional[Dict]:
        """Get a specific event by its ID."""
        for event in self.get_all_events():
            if event.get("id") == event_id:
                return event
        return None

    def get_events_by_city(self, city: str) -> List[Dict]:
        """
        Get events filtered by city.

        Args:
            city: City name in Arabic (e.g., "العاصمة", "ميناء الأمل", "منطقة الجبال")
        """
        return [e for e in self.get_all_events() if e.get("city") == city]

    def get_events_by_tier(self, tier: str) -> List[Dict]:
        """
        Get events filtered by tier.

        Args:
            tier: Event tier (e.g., "Marquee", "Tier 1", "Tier 2", "Tier 3")
        """
        return [e for e in self.get_all_events() if e.get("tier") == tier]

    def get_events_by_category(self, category: str) -> List[Dict]:
        """
        Get events filtered by category.

        Args:
            category: Event category in Arabic (e.g., "أعمال", "ترفيه")
        """
        return [e for e in self.get_all_events() if e.get("category") == category]

    def get_events_by_type(self, event_type: str) -> List[Dict]:
        """
        Get events filtered by type.

        Args:
            event_type: Event type in Arabic (e.g., "مؤتمرات", "مهرجانات", "معارض")
        """
        return [e for e in self.get_all_events() if e.get("event_type") == event_type]

    def get_events_by_organization(self, org_name: str) -> List[Dict]:
        """Get events organized by a specific organization."""
        return [e for e in self.get_all_events() if e.get("responsible_org") == org_name]

    def get_events_summary(self) -> Dict:
        """Get a summary of all events by various dimensions."""
        events = self.get_all_events()

        summary = {
            "total_count": len(events),
            "by_city": {},
            "by_tier": {},
            "by_category": {},
            "by_type": {},
            "total_expected_attendance": 0
        }

        for event in events:
            # By city
            city = event.get("city", "غير محدد")
            summary["by_city"][city] = summary["by_city"].get(city, 0) + 1

            # By tier
            tier = event.get("tier", "غير محدد")
            summary["by_tier"][tier] = summary["by_tier"].get(tier, 0) + 1

            # By category
            category = event.get("category", "غير محدد")
            summary["by_category"][category] = summary["by_category"].get(category, 0) + 1

            # By type
            event_type = event.get("event_type", "غير محدد")
            summary["by_type"][event_type] = summary["by_type"].get(event_type, 0) + 1

            # Total attendance
            summary["total_expected_attendance"] += event.get("expected_attendance", 0)

        return summary

    # ==================== Benchmarks Methods ====================

    def get_all_benchmarks(self) -> List[Dict]:
        """Get all benchmark case studies."""
        return self._benchmarks_data.get("benchmarks", [])

    def get_benchmark_by_id(self, benchmark_id: str) -> Optional[Dict]:
        """Get a specific benchmark by its ID."""
        for benchmark in self.get_all_benchmarks():
            if benchmark.get("id") == benchmark_id:
                return benchmark
        return None

    def get_benchmark_by_name(self, name: str) -> Optional[Dict]:
        """
        Get a benchmark by name (partial match supported).

        Args:
            name: Benchmark name in Arabic or English (partial match)
        """
        name_lower = name.lower()
        for benchmark in self.get_all_benchmarks():
            if (name_lower in benchmark.get("name", "").lower() or
                name_lower in benchmark.get("name_en", "").lower()):
                return benchmark
        return None

    def search_benchmarks(self, query: str) -> List[Dict]:
        """
        Search benchmarks by keyword across multiple fields.

        Args:
            query: Search query in Arabic or English
        """
        query_lower = query.lower()
        results = []

        for benchmark in self.get_all_benchmarks():
            # Search in name, country, overview
            searchable = [
                benchmark.get("name", ""),
                benchmark.get("name_en", ""),
                benchmark.get("country", ""),
                benchmark.get("overview", {}).get("summary", ""),
            ]

            if any(query_lower in str(field).lower() for field in searchable):
                results.append(benchmark)

        return results

    def get_benchmark_lessons(self, benchmark_id: str) -> Optional[Dict]:
        """Get lessons learned from a specific benchmark."""
        benchmark = self.get_benchmark_by_id(benchmark_id)
        if benchmark:
            return benchmark.get("lessons_learned", {})
        return None

    def get_all_benchmarks_summary(self) -> str:
        """Get a formatted summary of all benchmarks for context."""
        benchmarks = self.get_all_benchmarks()
        summary_parts = []

        for b in benchmarks:
            metrics = b.get("key_metrics", {})
            summary_parts.append(f"""
### {b.get('name')} ({b.get('year')}) - {b.get('country')}
- إجمالي الفعاليات: {metrics.get('total_events', 'غير متاح')}
- الزوار: {metrics.get('total_visitors', 'غير متاح')}
- الأثر الاقتصادي: {metrics.get('economic_impact_usd', 'غير متاح')}
- نمو السياحة: {metrics.get('tourism_increase_percent', 'غير متاح')}%
""")

        return "\n".join(summary_parts)

    # ==================== KPIs Methods ====================

    def get_all_kpi_categories(self) -> List[Dict]:
        """Get all KPI categories."""
        return self._kpis_data.get("categories", [])

    def get_kpis_by_category(self, category_name: str) -> List[Dict]:
        """
        Get KPIs filtered by category name.

        Args:
            category_name: Category name in Arabic (partial match supported)
        """
        for category in self.get_all_kpi_categories():
            if category_name in category.get("name", ""):
                return category.get("kpis", [])
        return []

    def get_all_kpis(self) -> List[Dict]:
        """Get all KPIs across all categories."""
        all_kpis = []
        for category in self.get_all_kpi_categories():
            for kpi in category.get("kpis", []):
                # Add category info to each KPI
                kpi_with_category = kpi.copy()
                kpi_with_category["category_name"] = category.get("name")
                kpi_with_category["category_id"] = category.get("id")
                all_kpis.append(kpi_with_category)
        return all_kpis

    def get_kpi_by_id(self, kpi_id: str) -> Optional[Dict]:
        """Get a specific KPI by its ID."""
        for kpi in self.get_all_kpis():
            if kpi.get("id") == kpi_id:
                return kpi
        return None

    def search_kpis(self, query: str) -> List[Dict]:
        """
        Search KPIs by keyword across name and definition.

        Args:
            query: Search query in Arabic
        """
        query_lower = query.lower()
        results = []

        for kpi in self.get_all_kpis():
            searchable = [
                kpi.get("name", ""),
                kpi.get("definition", ""),
                kpi.get("category_name", ""),
            ]

            if any(query_lower in str(field).lower() for field in searchable):
                results.append(kpi)

        return results

    def get_kpis_summary(self) -> str:
        """Get a formatted summary of all KPI categories."""
        categories = self.get_all_kpi_categories()
        summary_parts = []

        for cat in categories:
            kpi_names = [kpi.get("name") for kpi in cat.get("kpis", [])]
            summary_parts.append(f"""
### {cat.get('name')}
المؤشرات: {', '.join(kpi_names)}
""")

        return "\n".join(summary_parts)

    # ==================== Organizations Methods ====================

    def get_all_organizations(self) -> List[Dict]:
        """Get all organizations."""
        return self._organizations_data.get("organizations", [])

    def get_organization_by_id(self, org_id: str) -> Optional[Dict]:
        """Get a specific organization by its ID."""
        for org in self.get_all_organizations():
            if org.get("id") == org_id:
                return org
        return None

    def get_organization_by_name(self, name: str) -> Optional[Dict]:
        """Get an organization by name (partial match supported)."""
        for org in self.get_all_organizations():
            if name in org.get("name", "") or name in org.get("name_en", ""):
                return org
        return None

    def get_organizations_by_type(self, org_type: str) -> List[Dict]:
        """Get organizations filtered by type (e.g., "حكومية", "خاصة")."""
        return [o for o in self.get_all_organizations() if o.get("type") == org_type]

    def get_organizations_by_city(self, city: str) -> List[Dict]:
        """Get organizations filtered by contact city."""
        return [o for o in self.get_all_organizations() if o.get("contact_city") == city]

    # ==================== Combined Context Methods ====================

    def get_full_context(self) -> str:
        """
        Get a comprehensive context string for agent prompts.
        Returns a formatted string with key information about the celebration.
        """
        celebration = self.get_celebration_info()
        events_summary = self.get_events_summary()

        context = f"""
## معلومات الاحتفالية
- الاسم: {celebration.get('name', 'غير متاح')}
- السنة: {celebration.get('year', 'غير متاح')}
- المدة: {celebration.get('duration_months', 'غير متاح')} أشهر
- الشعار: {celebration.get('theme', 'غير متاح')}

## ملخص الفعاليات
- إجمالي الفعاليات: {events_summary.get('total_count', 0)}
- توزيع المدن: {events_summary.get('by_city', {})}
- توزيع المستويات: {events_summary.get('by_tier', {})}
- إجمالي الحضور المتوقع: {events_summary.get('total_expected_attendance', 0):,}

## دراسات المقارنة المتاحة
{self.get_all_benchmarks_summary()}

## فئات مؤشرات الأداء المتاحة
{self.get_kpis_summary()}
"""
        return context
