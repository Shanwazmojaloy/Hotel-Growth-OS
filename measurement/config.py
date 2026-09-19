"""Hotel configuration — one JSON file per property, mirroring measurement_plan."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class HotelConfig:
    # identity
    slug: str
    organization: str
    property_name: str
    city: str
    rooms: int
    currency: str = "BDT"

    # commercial reality (from the signed measurement plan §2 and §3)
    adr_bdt: float = 0.0
    effective_ota_commission: float = 0.0     # all-in, not headline
    direct_variable_cost: float = 0.045       # payment processing + booking engine
    engagement_fee_bdt: float = 0.0           # per month

    # measurement design (from the signed measurement plan §4)
    counterfactual_design: str = "pre_post"   # pre_post | conservative_attribution | geo_holdout
    haircut_factor: float = 0.500             # used only for conservative_attribution
    market_trend_factor: float = 1.000        # used only for pre_post

    # targets and rules (from §3 and §6)
    target_incremental_room_nights: float = 0.0
    target_lift_multiplier: float = 0.0        # optional: target as a multiple of baseline direct rn
    stop_threshold_share_of_target: float = 0.50
    guardrail_direct_value_tolerance: float = 0.10   # ADR of direct bookings may not fall >10%
    reconciliation_tolerance: float = 0.10

    # window
    pilot_start: str = ""                      # YYYY-MM
    synthetic: bool = False
    notes: list[str] = field(default_factory=list)

    @staticmethod
    def load(path: str | Path) -> "HotelConfig":
        data = json.loads(Path(path).read_text())
        known = {f for f in HotelConfig.__dataclass_fields__}
        unknown = set(data) - known
        if unknown:
            raise ValueError(f"{path}: unknown config keys {sorted(unknown)}")
        return HotelConfig(**data)

    def saving_per_room_night(self) -> float:
        """Commission avoided by a direct room-night, net of direct variable cost."""
        return self.adr_bdt * (self.effective_ota_commission - self.direct_variable_cost)

    def validate(self) -> list[str]:
        problems: list[str] = []
        if self.effective_ota_commission <= self.direct_variable_cost:
            problems.append(
                f"effective OTA commission ({self.effective_ota_commission:.1%}) does not exceed "
                f"direct cost ({self.direct_variable_cost:.1%}) — shifting to direct saves nothing"
            )
        if self.counterfactual_design not in {"pre_post", "conservative_attribution", "geo_holdout"}:
            problems.append(f"unknown counterfactual design '{self.counterfactual_design}'")
        if not self.pilot_start:
            problems.append("pilot_start is required (YYYY-MM)")
        if self.target_incremental_room_nights <= 0 and self.target_lift_multiplier <= 0:
            problems.append("either target_incremental_room_nights or target_lift_multiplier must be set")
        return problems
