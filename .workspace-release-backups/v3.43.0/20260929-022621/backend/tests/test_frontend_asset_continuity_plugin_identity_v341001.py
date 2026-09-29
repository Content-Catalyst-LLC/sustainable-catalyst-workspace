import importlib.util
from pathlib import Path


def _service():
    root=Path(__file__).resolve().parents[1]
    spec=importlib.util.spec_from_file_location('workspace_neural_v341001', root/'neural-runtime/service.py')
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_patch_identity_preserves_distributed_runtime_contract():
    s=_service()
    h=s.health()
    assert h['version'] in {'3.41.0.1','3.42.0'}
    assert len(h['operations'])>=117
    assert h['distributedNeuralExecutionWorkerFabricRuntime'] is True
    assert h['distributedClientSuppliedWorkerEndpointsAllowed'] is False
    assert h['distributedServerManagedTransportOnly'] is True


def test_patch_adds_no_new_neural_operations():
    s=_service()
    required={
        'workspace.neural.distributed-worker-contract',
        'workspace.neural.distributed-worker-pool-plan',
        'workspace.neural.distributed-capability-match',
        'workspace.neural.distributed-shard-plan',
        'workspace.neural.distributed-dispatch-plan',
        'workspace.neural.distributed-lease-heartbeat',
        'workspace.neural.distributed-retry-failover-plan',
        'workspace.neural.distributed-execution-receipt',
    }
    assert required.issubset(set(s.OPERATIONS))
    assert len(s.OPERATIONS)>=117
