# Workspace v3.46.0.3 — Local Project Deletion & Lifecycle Binding Repair

Repairs the reported case where New Project works but Delete from this device does nothing.

- project deletion is a shared lifecycle action
- direct and delegated event routes both invoke the same deletion function
- duplicate execution is prevented with an event marker
- the project is removed before optional Personal Knowledge cleanup
- cleanup exceptions cannot block deletion
- local persistence is verified
- if persistence verification fails, the project is restored in memory and the user is warned
- backend/cloud copies are not deleted by the local-device action
- v3.46.0.2 standalone/WordPress decoupling boundary is preserved
- no database migration
