# Demo validation

Evidence is tracked separately for source, builds and native interaction. A passing ordinary test or mayapy process does not establish WebView rendering inside interactive Maya.

| Gate | Current record |
| --- | --- |
| Source migration | Repository transferred on 2026-10-08; identity and 71 source commits retained. See [provenance](PROVENANCE.md). |
| Frontend build | Passed on 2026-10-09: TypeScript and Vite 7.3.7 production build via `vx just check`. |
| Scene contracts outside Maya | Passed on 2026-10-09: 34 tests via `vx just test`; full DAG identity, ambiguous names, empty/multiple selection, host errors, main-thread refusal and callback teardown. |
| Source demo archive | Passed on 2026-10-09: `vx just package 0.1.0-test` and `vx just verify-package`; Python modules, built JS, tutorial and provenance present. Runtime is installed separately. |
| Native Maya scene smoke | Passed on Maya 2026 on 2026-10-09 via `vx just maya-smoke "<Maya>/bin/mayapy.exe"`: hierarchy, duplicate DAG names, selection, multiple/empty selection, visibility and callback registration/removal. All 10 registered callbacks were released. |
| Interactive Maya/WebView demo | Not yet recorded for the migrated revision. Requires interactive Maya, the matching AuroraView wheel/qtpy, WebView2 Runtime, and a verified launch/selection/visibility/close cycle. |
| Other Maya versions / operating systems | Not certified by this migration. |

Installed interpreters observed locally on 2026-10-08 include Maya 2025 and 2026. Installation discovery is not a runtime pass.

Dependency audit after the compatible update reported zero advisories across 108
packages. This is a dependency snapshot, not a complete security assessment.

The scene-only smoke gate does not import or render AuroraView. The matching
runtime and Qt binding still need installation before interactive acceptance.

For interactive acceptance, open the demo using the README, verify both directions of selection (including duplicate leaf names), multiple and empty selection, visibility, rename, resize and repeated close/reopen. Record the exact Git commit, Maya/Python/AuroraView versions and test output. Use the project's DCC-CUA route for UI automation.
