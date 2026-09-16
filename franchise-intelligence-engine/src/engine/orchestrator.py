"""Top-level orchestrator — ties everything together."""
from __future__ import annotations
from typing import Dict, Any, List
from src.contracts.finding import Finding
from src.providers.base import FindingProvider
from src.engine.consolidator import Consolidator
from src.engine.health_scorer import HealthScorer
from src.engine.outlet_ranker import OutletRanker
from src.analysis.risk_predictor import RiskPredictor
from src.analysis.cross_agent import CrossAgentAnalyzer
from src.analysis.opportunity_detector import OpportunityDetector
from src.analysis.data_quality import DataQualityChecker
from src.llm.query_handler import QueryHandler
from src.llm.summary_generator import SummaryGenerator
from src.llm.gemini_client import GeminiClient
from src.output.structured_output import StructuredOutputBuilder, build_proposed_action


class FranchiseIntelligenceEngine:
    def __init__(self, provider: FindingProvider, config: dict, use_llm: bool = True):
        self.provider = provider
        self.config = config
        self.consolidator = Consolidator(config)
        self.scorer = HealthScorer(config)
        self.ranker = OutletRanker(config)
        self.risk = RiskPredictor(config)
        self.cross = CrossAgentAnalyzer()
        self.opp = OpportunityDetector()
        self.dq = DataQualityChecker()
        self.builder = StructuredOutputBuilder()

        llm = GeminiClient() if use_llm else None
        self.query_handler = QueryHandler(llm)
        self.summarizer = SummaryGenerator(llm)

    def run(self, query: str = "How is the franchise performing?") -> Dict[str, Any]:
        # 1. Fetch
        findings = self.provider.get_all_findings()
        if not findings:
            return {"intent": "error", "warnings": ["No findings available."]}

        # 2. Consolidate
        consolidated = self.consolidator.consolidate(findings)

        # 3. Health
        franchise_health = self.scorer.score_franchise(consolidated["findings"])

        # 4. Ranking
        ranking = self.ranker.rank(consolidated["findings"])

        # 5. Risks
        risks = self.risk.predict(consolidated["findings"])

        # 6. Cross-agent insights
        cross_insights = self.cross.analyze(consolidated["findings"])

        # 7. Opportunities
        opportunities = self.opp.detect(consolidated["findings"])

        # 8. Recommendations (deterministic)
        recommendations = self._build_recommendations(risks, opportunities, cross_insights)

        # 9. Proposed actions (PENDING_APPROVAL only)
        proposed = self._build_proposed_actions(risks, ranking)

        # 10. Data quality
        dq = self.dq.check(
            consolidated["findings"],
            consolidated["duplicates"],
            consolidated["conflicts"],
            consolidated["stale"],
        )

        # 11. Executive summary
        summary_payload = {
            "franchise_health": franchise_health,
            "risks": risks,
            "opportunities": opportunities,
            "recommendations": recommendations,
        }
        exec_summary = self.summarizer.generate(summary_payload)

        # 12. Intent
        intent = self.query_handler.classify_intent(query)

        # 13. Warnings
        warnings = list(franchise_health.get("warnings", []))
        if not consolidated["by_agent"].get("Marketing Agent"):
            warnings.append("Marketing dimension: DATA UNAVAILABLE.")
        if not consolidated["by_agent"].get("Audit Agent"):
            warnings.append("Compliance dimension: DATA UNAVAILABLE.")

        # 14. Structured output
        return self.builder.build(
            intent=intent,
            franchise_health=franchise_health,
            outlet_rankings=ranking,
            risks=risks,
            opportunities=opportunities,
            cross_agent=cross_insights,
            recommendations=recommendations,
            proposed_actions=proposed,
            data_quality=dq,
            executive_summary=exec_summary,
            warnings=warnings,
        )

    # ------------- helpers -------------

    def _build_recommendations(self,
                               risks: List[Dict[str, Any]],
                               opportunities: List[Dict[str, Any]],
                               cross: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        recs = []
        for r in risks[:5]:
            recs.append({
                "recommendation": r["recommended_mitigation"],
                "priority": "HIGH" if r["risk_level"] in ("HIGH", "CRITICAL") else "MEDIUM",
                "expected_impact": r["potential_impact"],
                "evidence": r["evidence"],
                "confidence": r["confidence"],
                "required_approval": True,
                "source_risk_id": r["risk_id"],
            })
        for o in opportunities[:3]:
            recs.append({
                "recommendation": o["suggested_next_step"],
                "priority": "MEDIUM",
                "expected_impact": o["expected_benefit"],
                "evidence": o["supporting_evidence"],
                "confidence": o["confidence"],
                "required_approval": False,
                "source_opportunity": o["opportunity"],
            })
        # Sort priorities
        order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        recs.sort(key=lambda x: order.get(x["priority"], 4))
        return recs

    def _build_proposed_actions(self,
                                risks: List[Dict[str, Any]],
                                ranking: Dict[str, Any]) -> List[Dict[str, Any]]:
        actions: List[Dict[str, Any]] = []
        for r in risks[:3]:
            if r["risk_level"] not in ("HIGH", "CRITICAL"):
                continue
            actions.append(build_proposed_action(
                action_type="operational_intervention",
                affected_outlet=r["affected_outlet"],
                reason=r["description"],
                supporting_findings=[r["source_finding_id"]],
                expected_benefit=r["potential_impact"],
                risks=["Requires operational disruption."],
                priority=r["risk_level"],
                confidence=r["confidence"],
            ))
        return actions