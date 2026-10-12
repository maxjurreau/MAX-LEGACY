from runtime.qce import QCERuntime


def test_qce_loading(tmp_path):
    # copy the repo schema from the repository location (we assume schema exists)
    q = QCERuntime(path="schema/dependencies.yaml")
    deps = q.load_dependencies()
    assert isinstance(deps, dict)
    # basic analyze invocation
    affected = q.analyze_impact(["MAX-Math"]) if deps else []
    assert isinstance(affected, list)
