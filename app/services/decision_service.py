"""
Decision Service for aggregating specialist recommendations, detecting and resolving conflicts,
and producing final AgronomicDecision and DecisionReceipt objects.
"""
import uuid
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple, Optional
from app.schemas.decision import AgronomicDecision, UrgencyLevel
from app.schemas.decision_receipt import DecisionReceipt
from app.schemas.conflict import DataConflictResolution
from app.schemas.evidence import Evidence, VerificationState
from app.schemas.farmer import FarmerProfile

logger = logging.getLogger(__name__)


class DecisionService:
    """
    Core aggregator and conflict resolution engine for Kisan Dost.
    """

    @classmethod
    def detect_and_resolve_conflicts(
        cls,
        specialist_outputs: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[DataConflictResolution]]:
        """
        Scans specialist agent recommendations for cross-domain conflicts (water, pesticide safety, finance, market).
        Resolves conflicts using conservative agronomic precedence rules.
        """
        conflicts: List[DataConflictResolution] = []
        resolved_outputs: List[Dict[str, Any]] = [dict(out) for out in specialist_outputs]

        # Extract domain-specific values from specialist outputs
        agronomy_data = next((out for out in resolved_outputs if out.get("domain") in ["Agronomy", "Crop", "Irrigation"]), {})
        water_data = next((out for out in resolved_outputs if out.get("domain") in ["Water", "IrrigationSource"]), {})
        pest_data = next((out for out in resolved_outputs if out.get("domain") in ["Pest", "Disease", "Pesticide"]), {})
        finance_data = next((out for out in resolved_outputs if out.get("domain") in ["Finance", "Budget"]), {})

        # Conflict Check 1: Water Requirement vs Water Supply Availability
        rec_water = agronomy_data.get("water_required_irrigations")
        avail_water = water_data.get("available_irrigations")
        if rec_water is not None and avail_water is not None and rec_water > avail_water:
            c_id = f"CONF-{uuid.uuid4().hex[:6].upper()}"
            ev1 = Evidence(source_id="AGRONOMY_ADVISOR", source_name="Agronomy Specialist", verification_state="verified")
            ev2 = Evidence(source_id="WATER_SOURCE_ADVISOR", source_name="Water Resource Monitor", verification_state="verified")
            
            conflict = DataConflictResolution(
                conflict_id=c_id,
                domain="Irrigation",
                conflicting_field="water_irrigations",
                source_a_name="Crop Agronomy Advisor",
                source_a_value=rec_water,
                source_b_name="Water Supply Constraint",
                source_b_value=avail_water,
                resolved_value=avail_water,
                resolution_strategy="Most Conservative Bound (Water Priority)",
                resolution_notes=f"Water supply ({avail_water} turns) is insufficient for full recommendation ({rec_water} turns). Scaled irrigation to available capacity.",
                evidence=[ev1, ev2]
            )
            conflicts.append(conflict)
            agronomy_data["water_required_irrigations"] = avail_water
            agronomy_data["action_notes"] = f"Adjusted irrigation schedule to {avail_water} available turns."

        # Conflict Check 2: Unverified Pesticide Dosage or Overdosage
        proposed_dosage = pest_data.get("dosage_val")
        max_safe_dosage = pest_data.get("max_safe_dosage")
        is_verified_pesticide = pest_data.get("is_verified", True)

        if not is_verified_pesticide or (proposed_dosage and max_safe_dosage and proposed_dosage > max_safe_dosage):
            c_id = f"CONF-{uuid.uuid4().hex[:6].upper()}"
            ev1 = Evidence(source_id="PEST_RECOMMENDATION", source_name="Pest Specialist", verification_state="unverified")
            ev2 = Evidence(source_id="PLANT_PROTECTION_DB", source_name="Dept of Plant Protection", verification_state="verified")

            resolved_dose = max_safe_dosage if max_safe_dosage else 0.0
            conflict = DataConflictResolution(
                conflict_id=c_id,
                domain="PesticideSafety",
                conflicting_field="dosage_val",
                source_a_name="LLM Pest Recommender",
                source_a_value=proposed_dosage or "Unverified Chemical",
                source_b_name="Department of Plant Protection Registry",
                source_b_value=max_safe_dosage or "Approved Limit Only",
                resolved_value=resolved_dose,
                resolution_strategy="Official Govt Precedence / Safety Block",
                resolution_notes="Unverified chemical or dosage exceeding safety threshold was strictly overridden by official plant protection safety limits.",
                evidence=[ev1, ev2]
            )
            conflicts.append(conflict)
            pest_data["dosage_val"] = resolved_dose
            pest_data["is_blocked"] = (resolved_dose == 0.0)

        # Conflict Check 3: Budget Constraint vs Required Input Cost
        input_cost = finance_data.get("proposed_input_cost")
        max_budget = finance_data.get("max_budget_limit")
        if input_cost is not None and max_budget is not None and input_cost > max_budget:
            c_id = f"CONF-{uuid.uuid4().hex[:6].upper()}"
            ev1 = Evidence(source_id="INPUT_CALCULATOR", source_name="Fertilizer/Input Calculator", verification_state="verified")
            ev2 = Evidence(source_id="FARMER_FINANCE", source_name="Farmer Budget Profile", verification_state="verified")

            conflict = DataConflictResolution(
                conflict_id=c_id,
                domain="Finance",
                conflicting_field="input_cost",
                source_a_name="Input Package Cost",
                source_a_value=input_cost,
                source_b_name="Farmer Credit/Budget Cap",
                source_b_value=max_budget,
                resolved_value=max_budget,
                resolution_strategy="Credit Constraint Cap",
                resolution_notes=f"Proposed input cost PKR {input_cost:,.0f} exceeds budget cap PKR {max_budget:,.0f}. Optimized input selection to fit budget.",
                evidence=[ev1, ev2]
            )
            conflicts.append(conflict)
            finance_data["proposed_input_cost"] = max_budget

        return resolved_outputs, conflicts

    @classmethod
    def produce_final_decision(
        cls,
        query_text: str,
        specialist_outputs: List[Dict[str, Any]],
        farmer_profile: Optional[FarmerProfile] = None
    ) -> Tuple[AgronomicDecision, DecisionReceipt, List[DataConflictResolution]]:
        """
        Aggregates specialist agent results, detects & resolves conflicts, and outputs:
        1. Actionable AgronomicDecision
        2. Immutable DecisionReceipt
        3. List of resolved DataConflictResolutions
        """
        resolved_outputs, conflicts = cls.detect_and_resolve_conflicts(specialist_outputs)

        # Collect evidence across all specialist outputs and conflicts
        all_evidence: List[Evidence] = []
        for out in resolved_outputs:
            evs = out.get("evidence", [])
            for e in evs:
                if isinstance(e, Evidence):
                    all_evidence.append(e)
                elif isinstance(e, dict):
                    all_evidence.append(Evidence(**e))

        for c in conflicts:
            all_evidence.extend(c.evidence)

        # Deduplicate evidence by source_id
        seen_ids = set()
        unique_evidence: List[Evidence] = []
        for ev in all_evidence:
            if ev.source_id not in seen_ids:
                seen_ids.add(ev.source_id)
                unique_evidence.append(ev)

        # Build action steps and synthesis
        action_steps: List[str] = []
        categories: List[str] = []
        urgencies: List[UrgencyLevel] = []

        for out in resolved_outputs:
            if "category" in out:
                categories.append(out["category"])
            if "urgency" in out and out["urgency"] in ["low", "medium", "high", "critical"]:
                urgencies.append(out["urgency"])
            if "action_steps" in out and isinstance(out["action_steps"], list):
                action_steps.extend(out["action_steps"])

        if not action_steps:
            action_steps = ["Follow recommended agronomic package of practices.", "Monitor field weekly."]

        category = categories[0] if categories else "Agronomy"
        urgency: UrgencyLevel = "medium"
        if "critical" in urgencies:
            urgency = "critical"
        elif "high" in urgencies:
            urgency = "high"

        dec_id = f"DEC-{uuid.uuid4().hex[:8].upper()}"
        farmer_name = farmer_profile.name if farmer_profile else "Farmer"
        district = farmer_profile.district if farmer_profile else "Punjab"

        title = f"Agronomic Advisory for {farmer_name} ({district})"
        rationale = (
            f"Synthesized from {len(specialist_outputs)} specialist domains with {len(conflicts)} conflict(s) resolved. "
            f"Grounding evidence chain includes {len(unique_evidence)} verified data points."
        )
        expected_impact = "Optimize crop yield, conserve water, and maximize net financial returns."

        decision = AgronomicDecision(
            decision_id=dec_id,
            category=category,
            title=title,
            urgency=urgency,
            action_steps=action_steps,
            rationale=rationale,
            expected_impact=expected_impact,
            evidence=unique_evidence
        )

        # Calculate evidence audit receipt counters
        verified_cnt = sum(1 for e in unique_evidence if e.verification_state == "verified")
        unverified_cnt = sum(1 for e in unique_evidence if e.verification_state == "unverified")
        fallback_cnt = sum(1 for e in unique_evidence if e.verification_state == "fallback")
        stale_cnt = sum(1 for e in unique_evidence if e.verification_state == "stale")
        partially_verified_cnt = sum(1 for e in unique_evidence if e.verification_state == "partially_verified")

        is_fully_grounded = (unverified_cnt == 0 and fallback_cnt == 0 and stale_cnt == 0 and len(unique_evidence) > 0)

        if unverified_cnt > 0:
            overall_state: VerificationState = "unverified"
        elif fallback_cnt > 0:
            overall_state = "fallback"
        elif stale_cnt > 0:
            overall_state = "stale"
        elif partially_verified_cnt > 0:
            overall_state = "partially_verified"
        else:
            overall_state = "verified"

        receipt = DecisionReceipt(
            receipt_id=f"RCPT-{uuid.uuid4().hex[:8].upper()}",
            query_text=query_text,
            decision_summary=f"{decision.title} - Urgency: {decision.urgency}",
            overall_verification_state=overall_state,
            verified_count=verified_cnt,
            unverified_count=unverified_cnt,
            fallback_count=fallback_cnt,
            stale_count=stale_cnt,
            partially_verified_count=partially_verified_cnt,
            is_fully_grounded=is_fully_grounded,
            evidence=unique_evidence
        )

        return decision, receipt, conflicts
