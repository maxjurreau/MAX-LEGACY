def test_cloudflare_imports():
    # import checks used as a quick pre-deploy sanity test
    from r2.storage_adapter import R2StorageAdapter
    from queues.event_queue import EventQueue
    from queues.mdt_queue import MDTQueue
    from queues.qce_queue import QCEQueue

    # Basic sanity: classes/imports exist and are constructible
    r2 = R2StorageAdapter(bucket_name="test-bucket")
    q = EventQueue()
    mdt = MDTQueue()
    qce = QCEQueue()

    assert r2 is not None
    assert hasattr(q, "enqueue")
    assert hasattr(mdt, "process_next")
    assert hasattr(qce, "evaluate")
