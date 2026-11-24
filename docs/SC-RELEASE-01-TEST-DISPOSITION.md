# SC-RELEASE-01 — Workspace backend test failure disposition

Measured on 2026-11-10 on the isolated staging host. Each run:
- is the full suite, `pytest --continue-on-collection-errors`;
- uses the backend image built from the tree;
- has a throwaway PostgreSQL 16;
- mounts the whole repository, so tests that read sibling runtime sources find them;
- has `statsmodels` installed, as the forecast runtime image does.

| Tree | Failed | Errors | Passed | Skipped |
|---|---|---|---|---|
| `main` `c483cd6` | 176 | 9 | 458 | 0 |
| Release candidate `release/sc-release-01-rc1` | 176 | 9 | 612 | 11 |

**Regression comparison:** the candidate's failing set is identical to `main`'s, with no new failure and none fixed. The 154 extra passing tests are the SC-MODEL-01, NB-01, ED-01, SIM-01, MATH-01 and recovered Wexford tests.

The earlier figure of 196 failed / 11 errors came from a backend-only mount, which hides sibling runtime sources and `statsmodels`. These numbers replace it.

`backend/tests/BASELINE_FAILURES.txt` lists the 185 accepted ids. A candidate is acceptable only if its failing set is a subset of it.

## Disposition by cause

### Neural and ML runtime tests need torch or joblib, which only the neural and ML runtime images install — 127

These tests import `backend/neural-runtime/service.py` or `backend/ml-runtime/service.py`. Production runs those runtimes as separate images (`…-v3450-…-neural-runtime`, `…-v3190-…-ml-runtime`). **This release does not change either runtime's source or image.**

**Disposition:** Out of scope for this release. Run them in the runtime images when those runtimes are next released.

- `tests/test_advanced_accelerator_scheduling_resource_governance_v34200.py` (1)
- `tests/test_cross_runtime_ml_neural_workflow_orchestration_v34400.py` (1)
- `tests/test_deep_learning_runtime_production_certification_ii_v34500.py` (1)
- `tests/test_distributed_neural_execution_worker_fabric_v34100.py` (1)
- `tests/test_frontend_asset_continuity_plugin_identity_v341001.py` (2)
- `tests/test_ml_runtime_operations_v2150.py` (1)
- `tests/test_ml_runtime_v2150.py` (2)
- `tests/test_model_serving_batch_inference_research_deployment_v34300.py` (1)
- `tests/test_neural_accelerator_device_orchestration_v32900.py` (7)
- `tests/test_neural_batch_trial_hyperparameter_execution_v33000.py` (7)
- `tests/test_neural_checkpoint_resume_v32300.py` (6)
- `tests/test_neural_computer_vision_remote_sensing_v33600.py` (5)
- `tests/test_neural_dataset_interchange_v32100.py` (5)
- `tests/test_neural_embedding_representation_v32600.py` (7)
- `tests/test_neural_evaluation_calibration_uncertainty_v32400.py` (6)
- `tests/test_neural_explainability_v32500.py` (7)
- `tests/test_neural_gnn_evaluation_explainability_embeddings_v33500.py` (5)
- `tests/test_neural_gnn_runtime_foundation_v33300.py` (1)
- `tests/test_neural_gnn_training_runtime_v33400.py` (5)
- `tests/test_neural_inference_prediction_provenance_v32700.py` (8)
- `tests/test_neural_multimodal_runtime_v33800.py` (1)
- `tests/test_neural_remote_gpu_execution_broker_v33100.py` (9)
- `tests/test_neural_reproducible_model_packages_v32800.py` (8)
- `tests/test_neural_runtime_foundation_v32000.py` (4)
- `tests/test_neural_runtime_production_certification_v33200.py` (8)
- `tests/test_neural_symbolic_research_intelligence_v33900.py` (1)
- `tests/test_neural_temporal_sequence_models_v33700.py` (5)
- `tests/test_neural_training_runtime_v32200.py` (6)
- `tests/test_neural_training_runtime_v322001.py` (3)
- `tests/test_neural_training_runtime_v322002.py` (2)
- `tests/test_reproducible_deep_learning_research_packages_v34000.py` (1)

### Stale release-version assertions — 53

Each test pins the Workspace version of the milestone that added it. The backend now reports a later version.

**Disposition:** Update the asserts to the release constant in one reviewed change. Not a release blocker.

- `tests/test_anonymous_research_object_browser_initialization_repair_v37401.py::test_v37401`: `assert "workspaceVersion: '3.74.0.1'" in "(function (root) {\n  'use strict';\n\n  const config = Object.freeze({\n    schema: 'sc-workspace`
- `tests/test_app.py::test_health_is_database_independent`: `AssertionError: assert '3.83.0' == '3.0.0'`
- `tests/test_backend_native_scientific_workspace_v3000.py::test_backend_native_profile_is_major_v3_boundary`: `AssertionError: assert '3.5.0' == '3.0.0'`
- `tests/test_backend_native_scientific_workspace_v3000.py::test_health_and_typed_contract_advertise_backend_native_v3`: `AssertionError: assert '3.83.0' == '3.0.0'`
- `tests/test_catalyst_analytics_r_provider_promotion_v3910.py::test_workspace_391_health_promotes_analytics_r_220`: `AssertionError: assert '3.83.0' == '3.9.1'`
- `tests/test_catalyst_analytics_r_provider_promotion_v3910.py::test_provider_profile_preserves_workspace_authority_and_diagnostics_boundary`: `AssertionError: assert '3.83.0' == '3.9.1'`
- `tests/test_catalyst_analytics_r_provider_promotion_v3910.py::test_typed_client_surface_is_complete_and_promoted`: `AssertionError: assert '3.46.0' == '3.9.1'`
- `tests/test_catalyst_analytics_r_provider_promotion_v3910.py::test_wordpress_plugin_promotes_provider_without_exposing_credentials`: `assert 'Version: 3.9.1' in "<?php\n/**\n * Plugin Name: Sustainable Catalyst Workspace\n * Plugin URI: https://sustainablecatalyst.com/platf`
- `tests/test_catalyst_analytics_r_runtime_adapter_v3500.py::test_workspace_version_and_health_flags`: `AssertionError: assert '3.83.0' == '3.5.0'`
- `tests/test_catalyst_analytics_r_runtime_adapter_v3500.py::test_provider_profile_preserves_workspace_authority`: `AssertionError: assert '3.83.0' == '3.5.0'`
- `tests/test_catalyst_analytics_r_runtime_adapter_v3500.py::test_vendored_provider_identity`: `AssertionError: assert 'Version: 2.1.0' in 'Package: catalystanalyticsr\nType: Package\nTitle: Sustainable Development Scenario Engine for t`
- `tests/test_claims_evidence_investigative_research_workspace_v3700.py::test_v370_release_lineage_frontend_and_routes`: `AssertionError: assert '3.11.0' == '3.7.0'`
- `tests/test_cross_product_research_handoff_v2330.py::test_typed_contract_exposes_handoff_routes`: `AssertionError: assert '3.46.0' == '3.2.0'`
- `tests/test_cross_product_research_handoff_v2330.py::test_health_advertises_handoff_fabric_without_generic_destination_mutation`: `AssertionError: assert '3.83.0' == '3.2.0'`
- `tests/test_cross_runtime_verification_v2170.py::test_version_and_profiles`: `AssertionError: assert '3.83.0' == '3.0.0'`
- `tests/test_frontend_runtime_v2360.py::test_profile_reduces_browser_authority`: `AssertionError: assert '3.7.0' == '3.0.0'`
- `tests/test_frontend_runtime_v2360.py::test_health_advertises_frontend_reduction`: `AssertionError: assert '3.83.0' == '3.0.0'`
- `tests/test_interchange_v2160.py::test_version_and_registry`: `AssertionError: assert '3.83.0' == '3.0.0'`
- `tests/test_investigation_documentary_workspace_v31100.py::test_documentary_typed_operations_and_openapi`: `AssertionError: assert '3.46.0' == '3.11.0'`
- `tests/test_investigation_documentary_workspace_v31100.py::test_release_lineage`: `AssertionError: assert '3.83.0' == '3.11.0'`
- `tests/test_investigation_entity_workspace_v31000.py::test_entity_typed_operations_and_openapi`: `AssertionError: assert '3.46.0' == '3.10.0'`
- `tests/test_investigation_entity_workspace_v31000.py::test_release_lineage`: `AssertionError: assert '3.83.0' == '3.10.0'`
- `tests/test_investigation_graph_workspace_v3800.py::test_release_lineage`: `AssertionError: assert '3.83.0' == '3.8.0'`
- `tests/test_investigation_timeline_workspace_v3900.py::test_release_lineage`: `AssertionError: assert '3.83.0' == '3.9.1'`
- `tests/test_local_first_sync_v2310.py::test_typed_contract_includes_all_sync_routes`: `AssertionError: assert '3.46.0' in {'2.31.0', '2.32.0', '2.34.0', '3.0.0'}`
- `tests/test_local_first_sync_v2310.py::test_health_advertises_local_first_protocol`: `AssertionError: assert '3.83.0' in {'2.31.0', '2.32.0', '2.34.0', '3.0.0'}`
- `tests/test_multilingual_text_corpus_runtime_foundation_v34600.py::test_backend_and_wordpress_release_integration_markers`: `assert 'service_version: str = "3.46.0"' in 'from functools import lru_cache\nfrom pydantic_settings import BaseSettings, SettingsConfigDict`
- `tests/test_neural_accelerator_device_orchestration_v32900.py::test_workspace_registry_compose_and_typed_contract_expose_v329`: `AssertionError: assert ('3.46.0' in {'3.29.0', '3.30.0', '3.31.0', '3.32.0'})`
- `tests/test_neural_batch_trial_hyperparameter_execution_v33000.py::test_workspace_registry_persistence_and_typed_contract_expose_v330`: `AssertionError: assert ('3.46.0' in {'3.30.0', '3.31.0', '3.32.0'})`
- `tests/test_neural_checkpoint_resume_v32300.py::test_polyglot_registry_and_workspace_contract_expose_v323_checkpoint_lineage`: `AssertionError: assert '3.46.0' in {'3.28.0', '3.29.0', '3.30.0', '3.31.0', '3.32.0'}`
- `tests/test_neural_dataset_interchange_v32100.py::test_client_contract_version_and_count`: `AssertionError: assert '3.46.0' in {'3.28.0', '3.29.0', '3.30.0', '3.31.0', '3.32.0'}`
- `tests/test_neural_embedding_representation_v32600.py::test_workspace_registry_and_contract_expose_v326`: `AssertionError: assert '3.46.0' in {'3.28.0', '3.29.0', '3.30.0', '3.31.0', '3.32.0'}`
- `tests/test_neural_evaluation_calibration_uncertainty_v32400.py::test_registry_and_workspace_contract_expose_v324_runtime`: `AssertionError: assert '3.46.0' in {'3.28.0', '3.29.0', '3.30.0', '3.31.0', '3.32.0'}`
- `tests/test_neural_explainability_v32500.py::test_bounds_and_workspace_registry`: `AssertionError: assert '3.46.0' in {'3.28.0', '3.29.0', '3.30.0', '3.31.0', '3.32.0'}`
- `tests/test_neural_inference_prediction_provenance_v32700.py::test_workspace_registry_and_contract_expose_v327`: `AssertionError: assert '3.46.0' in {'3.28.0', '3.29.0', '3.30.0', '3.31.0', '3.32.0'}`
- `tests/test_neural_reproducible_model_packages_v32800.py::test_workspace_registry_and_persistence_contract_expose_v328`: `AssertionError: assert ('3.46.0' in {'3.28.0', '3.29.0', '3.30.0', '3.31.0', '3.32.0'})`
- `tests/test_platform_core_v3_runtime_integration_v3100.py::test_platform_core_profile_preserves_authority_boundaries`: `AssertionError: assert '3.83.0' == '3.2.0'`
- `tests/test_platform_core_v3_runtime_integration_v3100.py::test_health_and_typed_contract_advertise_v3100_platform_core_integration`: `AssertionError: assert '3.83.0' == '3.2.0'`
- `tests/test_platform_core_visual_research_workspace_v3600.py::test_v360_release_lineage_and_frontend`: `AssertionError: assert '3.11.0' == '3.6.0'`
- `tests/test_production_architecture_certification_v2360.py::test_architecture_certification_profile_is_explicit_and_bounded`: `AssertionError: assert '3.11.0' == '3.0.0'`
- `tests/test_production_architecture_certification_v2360.py::test_health_advertises_production_architecture_certification`: `AssertionError: assert '3.83.0' == '3.0.0'`
- `tests/test_production_architecture_certification_v2360.py::test_typed_contract_includes_certification_endpoint`: `AssertionError: assert '3.46.0' == '3.0.0'`
- `tests/test_research_session_object_binding_runtime_v3300.py::test_v3300_profile_preserves_authority_boundaries`: `AssertionError: assert '3.5.0' == '3.3.0'`
- `tests/test_research_session_object_binding_runtime_v3300.py::test_v3300_health_and_typed_contract`: `AssertionError: assert '3.83.0' == '3.3.0'`
- `tests/test_scientific_execution_provenance_workspace_v3400.py::test_v3400_profile_preserves_research_authority_boundaries`: `AssertionError: assert '3.5.0' == '3.4.0'`
- `tests/test_scientific_execution_provenance_workspace_v3400.py::test_v3400_health_and_typed_contract`: `AssertionError: assert '3.83.0' == '3.4.0'`
- `tests/test_thin_client_state_v2300.py::test_typed_contract_includes_thin_state_endpoints`: `AssertionError: assert '3.46.0' in {'2.30.0', '2.31.0', '2.32.0', '2.34.0', '3.0.0'}`
- `tests/test_thin_client_state_v2300.py::test_health_advertises_thin_client_state_architecture`: `AssertionError: assert '3.83.0' in {'2.30.0', '2.31.0', '2.32.0', '2.34.0', '3.0.0'}`
- `tests/test_typed_client_contracts_v2290.py::test_contract_profile_is_backend_authoritative_and_proxy_only`: `AssertionError: assert ('sc-workspace...-contract/1.0' == 'sc-workspace...-contract/1.0'`
- `tests/test_unified_research_project_context_v3200.py::test_v3200_profile_preserves_specialist_authority`: `AssertionError: assert '3.5.0' == '3.2.0'`
- `tests/test_unified_research_project_context_v3200.py::test_v3200_health_and_typed_contract`: `AssertionError: assert '3.83.0' == '3.2.0'`
- `tests/test_unified_scientific_object_api_v2320.py::test_typed_contract_exposes_five_unified_scientific_object_routes`: `AssertionError: assert '3.46.0' in {'2.32.0', '2.34.0', '3.0.0', '3.1.0', '3.2.0'}`
- `tests/test_unified_scientific_object_api_v2320.py::test_health_advertises_unified_scientific_object_api`: `AssertionError: assert '3.83.0' in {'2.32.0', '2.34.0', '3.0.0', '3.1.0', '3.2.0'}`

### Stale route or registry counts — 3

Each test pins a count (for example 294 == 69) that later additive milestones increased.

**Disposition:** Update with the release-constant change. Not a release blocker.

- `tests/test_catalyst_analytics_r_runtime_adapter_v3500.py::test_provider_routes_are_typed_and_present_in_openapi`: `AssertionError: assert 294 == 69`
- `tests/test_neural_runtime_foundation_v32000.py::test_workspace_registers_neural_runtime_and_status_endpoint`: `AssertionError: assert 294 == 291`
- `tests/test_neural_runtime_production_certification_v33200.py::test_workspace_registry_persistence_and_typed_contract_expose_v332`: `AssertionError: assert 141 == 52`

### Stale latest-migration assertions — 2

Each test asserts that its milestone added no migration, or names the latest one. 051–053 (SC-MODEL-01, SC-NB-01, SC-ED-01) are later migrations.

**Disposition:** Update the expectation. Not a release blocker. The migration impact is reviewed separately.

- `tests/test_catalyst_analytics_r_provider_promotion_v3910.py::test_no_new_database_migration_and_v390_lineage_is_preserved`: `AssertionError: assert '053_sc_ed_01...approvals.sql' == '040_timeline...workspace.sql'`
- `tests/test_production_architecture_certification_v2360.py::test_certification_has_no_new_schema_migration`: `assert True is False`

