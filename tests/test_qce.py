from runtime.qce import QCERuntime


def test_qce_load_and_query():
    q = QCERuntime(path="schema/dependencies.yaml")
    deps = q.load_dependencies()
    assert "MAX-QUANTUMN" in deps
    assert q.get_dependencies("MAX-QUANTUMN") == ["MAX-Math", "MAX-Calculus"]
    affected = q.analyze_impact(["MAX-Math"])
    assert "MAX-QUANTUMN" in affected
    assert "Knowledge-Graph" in affected
