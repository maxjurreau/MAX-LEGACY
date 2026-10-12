import collections
from typing import List, Dict, Set


class QCERuntime:
    """Quantum Correlation Engine (QCE)

    Loads schema/dependencies.yaml and provides dependency and impact analysis.
    """

    def __init__(self, path: str = "schema/dependencies.yaml") -> None:
        self.path = path
        self.raw: Dict[str, Dict] = {}
        self._deps: Dict[str, List[str]] = {}
        self._affects: Dict[str, List[str]] = {}

    def load_dependencies(self) -> Dict[str, List[str]]:
        try:
            import yaml
            with open(self.path, "r", encoding="utf-8") as f:
                self.raw = yaml.safe_load(f) or {}
        except Exception:
            # small in-house parser for the expected format
            self.raw = {"schema_version": "1.0", "dependencies": {}}
            cur = None
            section = None
            with open(self.path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.rstrip("\n")
                    if not line.strip() or line.strip().startswith("#"):
                        continue
                    if line.startswith("  ") and not line.startswith("    ") and line.strip().endswith(":"):
                        cur = line.strip()[:-1]
                        self.raw["dependencies"][cur] = {}
                    elif line.strip().startswith("depends_on:"):
                        section = "depends_on"
                        self.raw["dependencies"][cur][section] = []
                    elif line.strip().startswith("affects:"):
                        section = "affects"
                        self.raw["dependencies"][cur][section] = []
                    elif line.strip().startswith("- ") and section:
                        val = line.strip()[2:]
                        self.raw["dependencies"][cur].setdefault(section, []).append(val)

        deps: Dict[str, List[str]] = {}
        affects: Dict[str, List[str]] = {}
        for name, block in (self.raw.get("dependencies") or {}).items():
            d = block.get("depends_on") or []
            a = block.get("affects") or []
            deps[name] = list(d)
            affects[name] = list(a)
        self._deps = deps
        self._affects = affects
        return self._deps

    def get_dependencies(self, domain: str) -> List[str]:
        return list(self._deps.get(domain, []))

    def get_dependents(self, domain: str) -> List[str]:
        res: List[str] = []
        for k, deps in self._deps.items():
            if domain in deps:
                res.append(k)
        return res

    def analyze_impact(self, changed_items: List[str]) -> List[str]:
        if not isinstance(changed_items, (list, tuple, set)):
            changed_items = [changed_items]
        changed = set(changed_items)
        affected: Set[str] = set()
        queue = collections.deque()
        # domains that depend on changed items
        for domain, deps in self._deps.items():
            if any(d in changed for d in deps):
                affected.add(domain)
                queue.append(domain)
        # propagate via affects edges
        while queue:
            d = queue.popleft()
            for a in self._affects.get(d, []):
                if a not in affected:
                    affected.add(a)
                    if a in self._affects:
                        queue.append(a)
        return sorted(affected)

    def propagate_change(self, change: str) -> List[str]:
        return self.analyze_impact([change])
