# Demo validation

Evidence is tracked separately for source, builds and native interaction. A passing ordinary test or mayapy process does not establish WebView rendering inside interactive Maya.

| Gate | Current record |
| --- | --- |
| Source migration | Repository transferred on 2026-10-08; identity and 71 source commits retained. See [provenance](PROVENANCE.md). |
| Frontend build | Passed on 2026-10-09: TypeScript and Vite 7.3.7 production build via `vx just check`. |
| Scene contracts outside Maya | Passed on 2026-10-09: 34 tests via `vx just test`; full DAG identity, ambiguous names, empty/multiple selection, host errors, main-thread refusal and callback teardown. |
| Source demo archive | Passed on 2026-10-09: `vx just package 0.1.0-test` and `vx just verify-package`; Python modules, built JS, tutorial and provenance present. Runtime is installed separately. |
| Native Maya scene smoke | Passed on Maya 2026 on 2026-10-09 via `vx just maya-smoke "<Maya>/bin/mayapy.exe"`: hierarchy, duplicate DAG names, selection, multiple/empty selection, visibility and callback registration/removal. All 10 registered callbacks were released. |
| Shared ToolSet preparation | Passed on 2026-10-09: 46 ordinary tests and 7 factory tests against the verified public preview wheel. Factory schema/handler reuse, UI/session lifetimes, worker-thread refusal, artifact checks and complete tools/list pagination are covered. See [shared tools](SHARED_TOOLS.md). |
| Public contract wheel in native Maya | Passed on Maya 2026 / Python 3.11.9 with public contract preview 0.1.0 and Core 0.20.41: actual HTTP/MCP discovery across 32 + 10 tools, rename/readback/Undo, binding unload/stale refusal, borrowed server survival, all 10 callbacks removed, endpoint/registry cleanup. See the [receipt](receipts/maya-contract-preview-1.json). |
| Opt-in GUI preparation | Passed on 2026-10-09: 75 source tests and TypeScript/Vite production build. Tests cover native parent-before-WebView order, borrowed ToolSet routes, readiness and retryable cleanup failures. |
| Pinned public GUI runtime imports | Passed in Maya 2026 / Python 3.11.9: AuroraView 0.5.12, QtPy 2.4.3 and packaging 25.0 with contract 0.1.0 / Core 0.20.41. All 110 installed AuroraView files matched the SHA256-verified public wheel. No QApplication or GUI was created. |
| Interactive Maya/WebView demo | Opt-in shared GUI binding and native docking candidate implemented; interactive rendering, docking, keyboard/pointer input, DPI and repeated close/reopen acceptance remain pending. Requires an interactive Maya session and WebView2 Runtime. |
| Other Maya versions / operating systems | Not certified by this migration. |

Installed interpreters observed locally on 2026-10-08 include Maya 2025 and 2026. Installation discovery is not a runtime pass.

Dependency audit after the compatible update reported zero advisories across 108
packages. This is a dependency snapshot, not a complete security assessment.

The scene-only smoke gate does not import or render AuroraView. The separate
pinned public import gate confirms runtime compatibility without rendering a
view. Follow the [README](../README.md#optional-native-dock-and-shared-rename)
to prepare the fixed GUI runtime and opt into docking or shared tools.

For interactive acceptance, open the demo using the README, verify both directions of selection (including duplicate leaf names), multiple and empty selection, visibility, rename, resize and repeated close/reopen. Record the exact Git commit, Maya/Python/AuroraView versions and test output. Use the project's DCC-CUA route for UI automation. The optional `scripts/maya_gui_probe.py` harness borrows the existing Core server and records main-thread ownership, ready state, native window identities and retryable cleanup; its report remains awaiting interactive acceptance until the UI checks are recorded.
