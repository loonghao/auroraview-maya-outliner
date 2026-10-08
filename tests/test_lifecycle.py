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


def test_callback_failure_still_destroys_view_and_releases_registry():
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
    dialog.close.assert_called_once_with()
    assert outliner.webview is None
    assert outliner.dialog is None
    assert outliner._singleton_key not in outliner._instances

    # A failed host callback remains visible and can be retried without a view.
    callbacks.close.side_effect = lambda: callbacks.ids.clear()
    outliner._dispose()
    assert callbacks.ids == []
    view.destroy.assert_called_once_with()
