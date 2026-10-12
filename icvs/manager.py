from __future__ import annotations

from typing import Dict, List

from .base import BaseICV
from .research_icv import ResearchICV
from .reality_icv import RealityICV
from .sports_icv import SportsICV
from .markets_icv import MarketsICV
from .law_icv import LawICV
from .learning_icv import LearningICV
from .health_icv import HealthICV
from .weather_icv import WeatherICV
from .economics_icv import EconomicsICV
from .citystates_icv import CityStatesICV


REGISTRY: Dict[str, type[BaseICV]] = {
    ResearchICV.name: ResearchICV,
    RealityICV.name: RealityICV,
    SportsICV.name: SportsICV,
    MarketsICV.name: MarketsICV,
    LawICV.name: LawICV,
    LearningICV.name: LearningICV,
    HealthICV.name: HealthICV,
    WeatherICV.name: WeatherICV,
    EconomicsICV.name: EconomicsICV,
    CityStatesICV.name: CityStatesICV,
}


class ICVManager:
    def list_icvs(self) -> List[str]:
        return sorted(list(REGISTRY.keys()))

    def get_icv(self, name: str) -> type[BaseICV] | None:
        return REGISTRY.get(name)

    def instantiate(self, name: str, root: str | None = None) -> BaseICV:
        cls = self.get_icv(name)
        if cls is None:
            raise KeyError(f"unknown icv: {name}")
        return cls(root=root)
