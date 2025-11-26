# Changelog

## [0.1.3](https://github.com/loonghao/auroraview-maya-outliner/compare/maya-outliner-v0.1.2...maya-outliner-v0.1.3) (2025-11-26)


### Features

* add unit tests for release package validation ([b9d85dc](https://github.com/loonghao/auroraview-maya-outliner/commit/b9d85dc06794b6eef990042ed925cd365a9f64df))


### Bug Fixes

* **deps:** update dependency lucide-vue-next to ^0.555.0 ([54556c5](https://github.com/loonghao/auroraview-maya-outliner/commit/54556c5c780ffc3f424b30109bbad8fb5673273f))
* resolve release package issues with shelf, module loading and environment detection ([025df84](https://github.com/loonghao/auroraview-maya-outliner/commit/025df84a258981878c4dd877b4d9751bfffa182d))

## [0.1.2](https://github.com/loonghao/auroraview-maya-outliner/compare/maya-outliner-v0.1.1...maya-outliner-v0.1.2) (2025-11-26)


### Bug Fixes

* **deps:** update dependency lucide-vue-next to ^0.554.0 ([7103373](https://github.com/loonghao/auroraview-maya-outliner/commit/7103373b05762f872aae3166ee2a55e26eaf7ac9))

## [0.1.1](https://github.com/loonghao/auroraview-maya-outliner/compare/maya-outliner-v0.1.0...maya-outliner-v0.1.1) (2025-11-26)


### Features

* add IndexedDB persistence for user preferences ([974528f](https://github.com/loonghao/auroraview-maya-outliner/commit/974528fce8c47b65260e9d17579975009bfa33ee))
* add justfile for easy Maya setup and remove test files ([ac91adb](https://github.com/loonghao/auroraview-maya-outliner/commit/ac91adbf7577f9bb78d5c067434d3ba1ec00b23f))
* add local development mode for custom AuroraView path ([a393bd7](https://github.com/loonghao/auroraview-maya-outliner/commit/a393bd7f22fd51b0d06a82c8164189d726cd787e))
* add multi-selection, double-click rename, and display filters ([a8c9d5c](https://github.com/loonghao/auroraview-maya-outliner/commit/a8c9d5c4428ec8181c682441a6573f317edb7103))
* enhance node type icons and implement display filters ([5e266fc](https://github.com/loonghao/auroraview-maya-outliner/commit/5e266fc50c1d0988c77d1f8c30be550ebf49f154))
* implement complete Maya Outliner context menu functionality ([03477ec](https://github.com/loonghao/auroraview-maya-outliner/commit/03477ecb52fb68d120cf1634c504e03c2b920892))
* implement drag-and-drop node parenting like Maya Outliner ([7c947d7](https://github.com/loonghao/auroraview-maya-outliner/commit/7c947d7de2efbea51e14748732b622d48c5f8058))
* modernize API to use bind_api pattern ([67468b4](https://github.com/loonghao/auroraview-maya-outliner/commit/67468b45e77e0a889c6a42e78090db5081db374c))
* remove emoji debug info, enhance multi-selection UI, add keyboard shortcuts ([45a8c5e](https://github.com/loonghao/auroraview-maya-outliner/commit/45a8c5ed79eee3134e0fb7e936b792d44f0a6610))
* restore eventAdapter utility for Maya event handling ([8f7a197](https://github.com/loonghao/auroraview-maya-outliner/commit/8f7a197801014485976709731be50b7186ea01fb))
* update to latest AuroraView API (2025) ([3eb91e6](https://github.com/loonghao/auroraview-maya-outliner/commit/3eb91e648675fbfb4c750506ed88bf5045e12650))


### Bug Fixes

* add better error handling and debug output for shelf creation ([181b88b](https://github.com/loonghao/auroraview-maya-outliner/commit/181b88b264b97476e0f16e5264371f59626f233d))
* add scene change callbacks and improve node detection ([95dda98](https://github.com/loonghao/auroraview-maya-outliner/commit/95dda981a9d766ebc4140fea3beaa08e1f79853c))
* adjust display filter defaults to show all objects ([a06521a](https://github.com/loonghao/auroraview-maya-outliner/commit/a06521a1e2b6a88528ee427b0f589a0e66b04c4c))
* auto-adjust dialog size to fit webview content ([faa7940](https://github.com/loonghao/auroraview-maya-outliner/commit/faa7940ed77eb273c0b8a23bee0765f147d8f01f))
* create PowerShell script for Maya environment setup ([7c173e5](https://github.com/loonghao/auroraview-maya-outliner/commit/7c173e543a6f6746fcd245ee35c90d0b321017a7))
* enhance DAG node type detection and filtering ([bd2fa72](https://github.com/loonghao/auroraview-maya-outliner/commit/bd2fa72aba2ffc4cbe0b32161b9ebd35c7d39150))
* handle AuroraView parameter passing for methods with no params ([3fb8ea7](https://github.com/loonghao/auroraview-maya-outliner/commit/3fb8ea74c60b7a130f98ffbd146af14fd261ddb6))
* improve Maya module installation and packaging ([b321d7b](https://github.com/loonghao/auroraview-maya-outliner/commit/b321d7b1c51e29e24a6ea6c0806ce81e32c24f5b))
* remove excessive debug logging and fix Qt dialog sizing ([dc8d4e9](https://github.com/loonghao/auroraview-maya-outliner/commit/dc8d4e90ee7aa9c32ffb43e279d308ca9c5c0797))
* remove executeDeferred and default to Qt backend to prevent Maya UI freezing ([6a8851b](https://github.com/loonghao/auroraview-maya-outliner/commit/6a8851be267bbb11bf4e825c63e3f72f2e1d4bdf))
* remove remaining _use_qt references and simplify window handle code ([603e0cb](https://github.com/loonghao/auroraview-maya-outliner/commit/603e0cb5b01faf3b5f16d57cedbdb95702737b66))
* resolve QResizeEvent lifetime issue in resize handler ([f19bd74](https://github.com/loonghao/auroraview-maya-outliner/commit/f19bd74d1738e62d53ae25c24b101eb2cf0d1d2e))
* resolve TypeScript build errors ([f91671d](https://github.com/loonghao/auroraview-maya-outliner/commit/f91671daeeca6855857192f4f974de4ca0549028))
* update justfile to use PowerShell on Windows ([67c7325](https://github.com/loonghao/auroraview-maya-outliner/commit/67c7325d885c1e131b465b4cd79e467f867915a9))
* use QDialog container for QtWebView to fix parent issue ([8e94606](https://github.com/loonghao/auroraview-maya-outliner/commit/8e9460681f6cd35d12ba096a107a887a90c23665))


### Code Refactoring

* cleanup codebase and enhance examples ([ac4dbf9](https://github.com/loonghao/auroraview-maya-outliner/commit/ac4dbf9049f4a4d8c773336b81000fdeae70f397))
* rename namespace to auroraview_maya_outliner and cleanup debug docs ([29f3385](https://github.com/loonghao/auroraview-maya-outliner/commit/29f33853ca4303eb06e938141b5b7823d1131bad))
* replace emoji icons with SVG-based icon system ([66a12dd](https://github.com/loonghao/auroraview-maya-outliner/commit/66a12dd788b50809b62faaedc574fea31d6d90f3))
* simplify to Qt backend only for cleaner example ([20a8b4d](https://github.com/loonghao/auroraview-maya-outliner/commit/20a8b4ded7a328eaa735d8f503e30bf653f7b327))
* use official AuroraView wrapper pattern for cleaner API binding ([59783ff](https://github.com/loonghao/auroraview-maya-outliner/commit/59783ffb87a2c4e0df5195a0677b0084994ab796))


### Documentation

* add API modernization summary ([7d77462](https://github.com/loonghao/auroraview-maya-outliner/commit/7d7746205be9e8b6d49422284cd6e4a9852daa1a))
* add build and packaging documentation ([6e5d5f4](https://github.com/loonghao/auroraview-maya-outliner/commit/6e5d5f4ab2647d0366e49d19461099ab5001d0cb))
* add comprehensive CI/CD workflow documentation ([b9f5891](https://github.com/loonghao/auroraview-maya-outliner/commit/b9f5891236e955029cac30bc8cc873318a83a9f3))
* add troubleshooting guide and test script ([3c03129](https://github.com/loonghao/auroraview-maya-outliner/commit/3c031298d676606788758ea6c91260d94150b5c8))
* update documentation for justfile usage ([6becabe](https://github.com/loonghao/auroraview-maya-outliner/commit/6becabe24cc9ec03fe60f57d6a41cdeea16c8fae))
* update README with local development mode information ([25f7aa2](https://github.com/loonghao/auroraview-maya-outliner/commit/25f7aa25f5c53a0c98656a899a8e10375f330efc))
