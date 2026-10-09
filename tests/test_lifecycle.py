"""Lifecycle tests verify disposal at the host boundaries, without opening a UI."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from auroraview_maya_outliner.maya_outliner import MayaOutliner


def test_close_stops_refresh_before_callbacks_and_native_view():
    calls = []
    outliner = object.__new__(MayaOutliner)
    outliner._closing = False
    outliner._singleton_key = "lifecycle-test"
    outliner._scene_timer = SimpleNamespace(stop=lambda: calls.append("stop"))
    outliner._callbacks = SimpleNamespace(ids=[], close=lambda: calls.append("callbacks"))
    outliner.webview = SimpleNamespace(destroy=lambda: calls.append("webview"))
    outliner.dialog = object()
    outliner._instances["lifecycle-test"] = outliner
    outliner._dispose()
    outliner._dispose()
    assert calls == ["stop", "callbacks", "webview"]
    assert outliner.webview is None
    assert outliner.dialog is None
    assert "lifecycle-test" not in outliner._instances


def test_callbacks_after_close_do_not_emit():
    outliner = object.__new__(MayaOutliner)
    outliner._closing = True
    outliner.webview = object()
    outliner._scene_timer = None
    # These callbacks may already be queued when the user closes the dialog.
    outliner.send_scene_update()
    outliner.send_selection_changed()
    outliner._schedule_scene_update()


def test_callback_failure_releases_view_but_retains_owner_for_retry():
    outliner = object.__new__(MayaOutliner)
    outliner._closing = False
    outliner._singleton_key = "failed-cleanup"
    timer = SimpleNamespace(stop=Mock())
    callbacks = SimpleNamespace(ids=[3], close=Mock(side_effect=RuntimeError("callback removal failed")))
    view = SimpleNamespace(destroy=Mock())
    dialog = SimpleNamespace(close=Mock())
    outliner._scene_timer = timer
    outliner._callbacks = callbacks
    outliner.webview = view
    outliner.dialog = dialog
    outliner.api = SimpleNamespace(_check_thread=lambda: None)
    outliner._instances[outliner._singleton_key] = outliner

    with pytest.raises(RuntimeError, match="callback removal failed"):
        outliner.close()

    timer.stop.assert_called_once_with()
    view.destroy.assert_called_once_with()
    dialog.close.assert_not_called()
    assert outliner.webview is None
    assert outliner.dialog is dialog
    assert outliner._instances[outliner._singleton_key] is outliner

    # A failed host callback remains visible and can be retried without a view.
    callbacks.close.side_effect = lambda: callbacks.ids.clear()
    outliner.close()
    assert callbacks.ids == []
    view.destroy.assert_called_once_with()
    dialog.close.assert_called_once_with()
    assert outliner.dialog is None
    assert outliner._singleton_key not in outliner._instances


def test_panel_closes_borrowed_binding_before_callbacks_and_native_view():
    calls = []
    panel = object.__new__(MayaOutliner)
    panel._closing = False
    panel._singleton_key = "shared-lifecycle"
    panel._scene_timer = SimpleNamespace(stop=lambda: calls.append("timer"))
    panel._ui_binding = SimpleNamespace(closed=False)

    def release():
        calls.append("binding")
        panel._ui_binding.closed = True

    panel._ui_binding.close = release
    panel._callbacks = SimpleNamespace(ids=[], close=lambda: calls.append("callbacks"))
    panel.webview = SimpleNamespace(destroy=lambda: calls.append("webview"))
    panel.dialog = object()
    panel._dispose()
    panel._dispose()
    assert calls == ["timer", "binding", "callbacks", "webview"]


def test_failed_native_destroy_retains_view_and_dialog_until_retry():
    panel = object.__new__(MayaOutliner)
    panel._singleton_key = "native-retry"
    panel._scene_timer = None
    panel._callbacks = SimpleNamespace(ids=[], close=Mock())
    panel.api = SimpleNamespace(_check_thread=lambda: None)
    view = SimpleNamespace(destroy=Mock(side_effect=[RuntimeError("native busy"), None]))
    dialog = SimpleNamespace(close=Mock())
    panel.webview, panel.dialog = view, dialog
    panel._instances[panel._singleton_key] = panel
    with pytest.raises(RuntimeError, match="native busy"):
        panel.close()
    assert panel.webview is view and panel.dialog is dialog
    assert panel._instances[panel._singleton_key] is panel
    dialog.close.assert_not_called()
    panel.close()
    assert view.destroy.call_count == 2
    panel._callbacks.close.assert_called_once_with()
    dialog.close.assert_called_once_with()
    assert panel.webview is None and panel.dialog is None
    assert panel._singleton_key not in panel._instances


def test_native_close_refusal_retains_window_owner_until_retry():
    panel = object.__new__(MayaOutliner)
    panel._singleton_key = "window-retry"
    panel._scene_timer = None
    panel._callbacks = None
    panel.webview = None
    panel.api = SimpleNamespace(_check_thread=lambda: None)
    dialog = SimpleNamespace(close=Mock(side_effect=[False, True]))
    panel.dialog = dialog
    panel._instances[panel._singleton_key] = panel
    with pytest.raises(RuntimeError, match="refused to close"):
        panel.close()
    assert panel.dialog is dialog
    assert panel._instances[panel._singleton_key] is panel
    panel.close()
    assert panel.dialog is None and panel._singleton_key not in panel._instances
