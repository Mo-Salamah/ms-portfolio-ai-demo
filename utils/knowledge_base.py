"""
قاعدة المعرفة لنظام المحفظة الذكي
"""

import csv
import json
from pathlib import Path
from typing import List, Dict, Optional


# CSV files for the 5 target cities
CITY_CSV_FILES = {
    "الرياض": "riyadh_events.csv",
    "جدة": "jeddah_events.csv",
    "العلا": "ula_events.csv",
    "عسير": "aseer_events.csv",
    "حاضرة الدمام": "dammam_events.csv",
}


class KnowledgeBase:
    """
    قاعدة المعرفة لاسترجاع البيانات والاستعلام عنها
    """

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            current_dir = Path(__file__).parent
            data_dir = current_dir.parent / "data"
        else:
            data_dir = Path(data_dir)

        self.data_dir = data_dir
        self._events_data: List[Dict] = []
        self._benchmarks_data: Dict = {}
        self._kpis_data: Dict = {}
        self._organizations_data: Dict = {}

        self._load_all_data()

    def _load_all_data(self):
        """Load all data files into memory."""
        try:
            # Load events from CSV files
            self._events_data = self._load_events_from_csv()

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

        except Exception as e:
            print(f"Error loading data: {e}")
            raise

    def _load_events_from_csv(self) -> List[Dict]:
        """Load events from the 5 city CSV files."""
        all_events = []

        for city_name, csv_filename in CITY_CSV_FILES.items():
            csv_path = self.data_dir / csv_filename
            if not csv_path.exists():
                continue

            try:
                with open(csv_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        event_name = (row.get("اسم الفعالية") or "").strip()
                        if not event_name:
                            continue

                        event = {
                            "name": event_name,
                            "responsible_org": (row.get("الجهة المسؤولة") or "").strip(),
                            "description": (row.get("وصف الفعالية") or "").strip(),
                            "start_date": (row.get("تاريخ البداية") or "").strip(),
                            "end_date": (row.get("تاريخ النهاية") or "").strip(),
                            "duration_days": (row.get("عدد الأيام") or "").strip(),
                            "tier": (row.get("التصنيف") or "").strip(),
                            "type": (row.get("النوع") or "").strip(),
                            "city": (row.get("المدينة") or city_name).strip(),
                            "subcategory": (row.get("الفئة الفرعية") or "").strip(),
                            "addition_status": (row.get("حالة الإضافة") or "").strip(),
                            "funding": (row.get("التمويل") or "").strip(),
                            "communication": (row.get("التواصل") or "").strip(),
                            "stay_period": (row.get("فترة الإقامة") or "").strip(),
                            "inclusion_status": (row.get("حالة التضمين") or "").strip(),
                            "exclusion_reason": (row.get("سبب الاستبعاد") or "").strip(),
                        }
                        all_events.append(event)
            except Exception as e:
                print(f"Error loading {csv_filename}: {e}")

        return all_events

    # ==================== Events Methods ====================

    def get_all_events(self) -> List[Dict]:
        """Get all events across all cities."""
        return self._events_data

    def get_events_by_city(self, city: str) -> List[Dict]:
        """Get events filtered by city."""
        return [e for e in self._events_data if e.get("city") == city]

    def get_events_by_tier(self, tier: str) -> List[Dict]:
        """Get events filtered by tier (Marquee, Tier 1, Tier 2, Tier 3)."""
        return [e for e in self._events_data if e.get("tier") == tier]

    def get_events_by_type(self, event_type: str) -> List[Dict]:
        """Get events filtered by type (أعمال, ترفيه)."""
        return [e for e in self._events_data if e.get("type") == event_type]

    def get_events_by_organization(self, org_name: str) -> List[Dict]:
        """Get events by responsible organization (partial match)."""
        return [e for e in self._events_data if org_name in e.get("responsible_org", "")]

    def get_events_by_inclusion_status(self, status: str) -> List[Dict]:
        """Get events by inclusion status (تضمن, لن تضمن, تحسب بدون تضمين)."""
        return [e for e in self._events_data if e.get("inclusion_status") == status]

    def get_events_summary(self) -> Dict:
        """Get a summary of all events by various dimensions."""
        events = self._events_data

        summary = {
            "total_count": len(events),
            "by_city": {},
            "by_tier": {},
            "by_type": {},
            "by_inclusion_status": {},
        }

        for event in events:
            city = event.get("city", "غير محدد")
            summary["by_city"][city] = summary["by_city"].get(city, 0) + 1

            tier = event.get("tier", "غير محدد")
            if tier:
                summary["by_tier"][tier] = summary["by_tier"].get(tier, 0) + 1

            event_type = event.get("type", "غير محدد")
            if event_type:
                summary["by_type"][event_type] = summary["by_type"].get(event_type, 0) + 1

            inclusion = event.get("inclusion_status", "غير محدد")
            if inclusion:
                summary["by_inclusion_status"][inclusion] = summary["by_inclusion_status"].get(inclusion, 0) + 1

        return summary

    def get_available_cities(self) -> List[str]:
        """Get list of available cities."""
        return list(CITY_CSV_FILES.keys())

    # ==================== Benchmarks Methods ====================

    def get_all_benchmarks(self) -> List[Dict]:
        """Get all benchmark case studies."""
        return self._benchmarks_data.get("benchmarks", [])

    def get_benchmark_by_id(self, benchmark_id: str) -> Optional[Dict]:
        for benchmark in self.get_all_benchmarks():
            if benchmark.get("id") == benchmark_id:
                return benchmark
        return None

    def get_benchmark_by_name(self, name: str) -> Optional[Dict]:
        name_lower = name.lower()
        for benchmark in self.get_all_benchmarks():
            if (name_lower in benchmark.get("name", "").lower() or
                name_lower in benchmark.get("name_en", "").lower()):
                return benchmark
        return None

    def search_benchmarks(self, query: str) -> List[Dict]:
        query_lower = query.lower()
        results = []
        for benchmark in self.get_all_benchmarks():
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
        benchmark = self.get_benchmark_by_id(benchmark_id)
        if benchmark:
            return benchmark.get("lessons_learned", {})
        return None

    def get_all_benchmarks_summary(self) -> str:
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
        return self._kpis_data.get("categories", [])

    def get_kpis_by_category(self, category_name: str) -> List[Dict]:
        for category in self.get_all_kpi_categories():
            if category_name in category.get("name", ""):
                return category.get("kpis", [])
        return []

    def get_all_kpis(self) -> List[Dict]:
        all_kpis = []
        for category in self.get_all_kpi_categories():
            for kpi in category.get("kpis", []):
                kpi_with_category = kpi.copy()
                kpi_with_category["category_name"] = category.get("name")
                kpi_with_category["category_id"] = category.get("id")
                all_kpis.append(kpi_with_category)
        return all_kpis

    def get_kpi_by_id(self, kpi_id: str) -> Optional[Dict]:
        for kpi in self.get_all_kpis():
            if kpi.get("id") == kpi_id:
                return kpi
        return None

    def search_kpis(self, query: str) -> List[Dict]:
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
        return self._organizations_data.get("organizations", [])

    def get_organization_by_id(self, org_id: str) -> Optional[Dict]:
        for org in self.get_all_organizations():
            if org.get("id") == org_id:
                return org
        return None

    def get_organization_by_name(self, name: str) -> Optional[Dict]:
        for org in self.get_all_organizations():
            if name in org.get("name", "") or name in org.get("name_en", ""):
                return org
        return None

    # ==================== Combined Context ====================

    def get_full_context(self) -> str:
        """Get comprehensive context string for agent prompts."""
        events_summary = self.get_events_summary()

        context = f"""
## ملخص بيانات الفعاليات

### الإجمالي: {events_summary.get('total_count', 0)} فعالية

### التوزيع حسب المدينة:
"""
        for city, count in sorted(events_summary.get('by_city', {}).items(), key=lambda x: x[1], reverse=True):
            context += f"- {city}: {count} فعالية\n"

        context += "\n### التوزيع حسب التصنيف:\n"
        for tier, count in sorted(events_summary.get('by_tier', {}).items(), key=lambda x: x[1], reverse=True):
            context += f"- {tier}: {count}\n"

        context += "\n### التوزيع حسب النوع:\n"
        for t, count in sorted(events_summary.get('by_type', {}).items(), key=lambda x: x[1], reverse=True):
            context += f"- {t}: {count}\n"

        context += f"""
## دراسات المقارنة المتاحة
{self.get_all_benchmarks_summary()}

## فئات مؤشرات الأداء المتاحة
{self.get_kpis_summary()}
"""
        return context
