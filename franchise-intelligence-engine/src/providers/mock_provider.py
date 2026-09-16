"""Mock provider with sample findings across all 5 agents."""
from typing import List
from src.contracts.finding import Finding
from src.providers.base import FindingProvider


class MockProvider(FindingProvider):
    """Provides realistic mock data for standalone demo/testing."""

    def get_outlet_performance_findings(self) -> List[Finding]:
        return [
            Finding(agent_name="Outlet Performance Agent", outlet_id="OUT-101",
                    category="sales", metric="monthly_sales", value=42000, baseline=55000,
                    severity="HIGH", trend="DECLINING", finding_type="TREND",
                    description="Sales declined 23% vs baseline over 3 months.",
                    evidence=["Month1: 55k", "Month2: 48k", "Month3: 42k"],
                    confidence=0.9),
            Finding(agent_name="Outlet Performance Agent", outlet_id="OUT-102",
                    category="sales", metric="monthly_sales", value=61000, baseline=58000,
                    severity="LOW", trend="IMPROVING", finding_type="TREND",
                    description="Sales up 5% vs baseline.",
                    evidence=["Steady growth"], confidence=0.85),
            Finding(agent_name="Outlet Performance Agent", outlet_id="OUT-103",
                    category="sales", metric="monthly_sales", value=38000, baseline=52000,
                    severity="CRITICAL", trend="DECLINING", finding_type="ALERT",
                    description="Sales dropped 27% vs baseline.",
                    evidence=["Sharp decline"], confidence=0.9),
            Finding(agent_name="Outlet Performance Agent", outlet_id="OUT-104",
                    category="sales", metric="monthly_sales", value=75000, baseline=70000,
                    severity="LOW", trend="IMPROVING", finding_type="TREND",
                    description="Top performer, +7% above baseline.",
                    evidence=["Consistent performance"], confidence=0.9),
        ]

    def get_inventory_findings(self) -> List[Finding]:
        return [
            Finding(agent_name="Inventory Agent", outlet_id="OUT-101",
                    category="inventory", metric="stockout_events", value=8, baseline=2,
                    severity="HIGH", trend="DECLINING", finding_type="ALERT",
                    description="8 stockout events this month vs baseline 2.",
                    evidence=["SKU-12, SKU-19, SKU-44 repeatedly out"],
                    confidence=0.88),
            Finding(agent_name="Inventory Agent", outlet_id="OUT-103",
                    category="inventory", metric="wastage_pct", value=12.5, baseline=4.0,
                    severity="CRITICAL", trend="DECLINING", finding_type="ALERT",
                    description="Wastage at 12.5%, well above 4% baseline.",
                    evidence=["Perishables spoiling"], confidence=0.92),
            Finding(agent_name="Inventory Agent", outlet_id="OUT-102",
                    category="inventory", metric="stockout_events", value=1, baseline=2,
                    severity="LOW", trend="IMPROVING", finding_type="FACT",
                    description="Stockouts improved.", confidence=0.8),
        ]

    def get_staff_findings(self) -> List[Finding]:
        return [
            Finding(agent_name="Staff Agent", outlet_id="OUT-101",
                    category="workforce", metric="absenteeism_pct", value=18, baseline=7,
                    severity="HIGH", trend="DECLINING", finding_type="ALERT",
                    description="Absenteeism at 18% vs 7% baseline.",
                    evidence=["3 senior staff on leave"], confidence=0.85),
            Finding(agent_name="Staff Agent", outlet_id="OUT-103",
                    category="workforce", metric="staff_turnover", value=35, baseline=15,
                    severity="HIGH", trend="DECLINING", finding_type="ALERT",
                    description="Turnover at 35% vs 15% baseline.",
                    confidence=0.82),
            Finding(agent_name="Staff Agent", outlet_id="OUT-104",
                    category="workforce", metric="productivity_index", value=112, baseline=100,
                    severity="LOW", trend="IMPROVING", finding_type="OPPORTUNITY",
                    description="High productivity index.",
                    confidence=0.8),
        ]

    def get_marketing_findings(self) -> List[Finding]:
        return [
            Finding(agent_name="Marketing Agent", outlet_id="OUT-101",
                    category="marketing", metric="conversion_rate", value=1.2, baseline=3.5,
                    severity="HIGH", trend="DECLINING", finding_type="ALERT",
                    description="Conversion fell to 1.2% from 3.5%.",
                    evidence=["Campaign clicks high, purchases low"], confidence=0.83),
            Finding(agent_name="Marketing Agent", outlet_id="OUT-104",
                    category="marketing", metric="campaign_roi", value=4.2, baseline=2.5,
                    severity="LOW", trend="IMPROVING", finding_type="OPPORTUNITY",
                    description="Campaign ROI 4.2x vs 2.5x baseline.",
                    confidence=0.88),
        ]

    def get_audit_findings(self) -> List[Finding]:
        return [
            Finding(agent_name="Audit Agent", outlet_id="OUT-103",
                    category="compliance", metric="violations", value=6, baseline=1,
                    severity="CRITICAL", trend="DECLINING", finding_type="ALERT",
                    description="6 audit violations this quarter.",
                    evidence=["Hygiene, safety, documentation"],
                    confidence=0.95, requires_human_approval=True),
            Finding(agent_name="Audit Agent", outlet_id="OUT-102",
                    category="compliance", metric="violations", value=0, baseline=1,
                    severity="LOW", trend="IMPROVING", finding_type="FACT",
                    description="Zero violations.", confidence=0.9),
        ]

    def get_historical_franchise_findings(self) -> List[Finding]:
        return [
            Finding(agent_name="Outlet Performance Agent", outlet_id="OUT-101",
                    category="sales", metric="monthly_sales", value=55000,
                    timestamp="2024-08-01T00:00:00", confidence=0.9),
            Finding(agent_name="Outlet Performance Agent", outlet_id="OUT-101",
                    category="sales", metric="monthly_sales", value=48000,
                    timestamp="2024-09-01T00:00:00", confidence=0.9),
            Finding(agent_name="Outlet Performance Agent", outlet_id="OUT-101",
                    category="sales", metric="monthly_sales", value=42000,
                    timestamp="2024-10-01T00:00:00", confidence=0.9),
        ]