"""Host-owned scene tools; each Qt panel borrows one view generation."""

from .maya_outliner import MayaOutliner
from .scene import SceneAPI
from .tools import create_tools


class OutlinerRuntime:
    """Retain this owner in the host/plugin until final unload.

    ``close_view`` permits reopening with the same tools and agent registration.
    ``close`` is final: published Core retains unloaded catalog metadata, so a
    new owner with the same name cannot attach to that server afterward.
    """

    def __init__(self, server, commands=None, subscribe=None, singleton_key="maya-outliner",
                 context_menu=False, dockable=False):
        self.server = server
        self.scene = SceneAPI(commands, on_change=self._schedule_scene_update)
        self.scene._check_thread()
        self._subscribe = subscribe
        self._options = dict(singleton_key=singleton_key, context_menu=context_menu,
                             dockable=dockable)
        self.tools = None
        self.agent = None
        self.panel = None
        self._closing = False
        self.closed = False

    def _check_open(self):
        self.scene._check_thread()
        if self._closing:
            raise RuntimeError("The host outliner runtime is closing or closed.")

    def attach(self):
        """Attach once to the explicit borrowed server; never start a service."""
        self._check_open()
        if self.agent is None:
            if self.tools is None:
                self.tools = create_tools(self.scene, subscribe=self._subscribe)
            try:
                self.agent = self.tools.attach(self.server)
            except Exception:
                # A failed public attach can retain partial cleanup inside the
                # ToolSet. Keep that owner for final cleanup; never attach twice.
                self._closing = True
                raise
        return self.agent

    def open(self, url=None, use_local=False):
        """Open one new view, or raise the current live view without reattaching."""
        self._check_open()
        if self.panel is not None:
            if self.panel._cleanup_pending or (self.panel._closing and self.panel.dialog):
                raise RuntimeError("Previous view cleanup is pending. Retry close_view() first.")
            if self.panel.dialog:
                self.panel.dialog.show()
                self.panel.dialog.raise_()
                return self.panel
            # Native close callbacks have already released this view generation.
            self.panel = None
        self.attach()
        self.panel = MayaOutliner(api=self.scene, **self._options)
        try:
            self.panel.run(url=url, use_local=use_local, tools=self.tools)
        except Exception:
            self.close_view()
            raise
        return self.panel

    def _schedule_scene_update(self, *args):
        if self.panel is not None:
            self.panel._schedule_scene_update(*args)

    def close_view(self):
        """Release only view resources; keep the agent usable without a panel."""
        self.scene._check_thread()
        if self.panel is not None:
            self.panel.close()
            self.panel = None

    def close(self):
        """Final owner cleanup; retain failed resources so callers can retry."""
        self.scene._check_thread()
        self._closing = True
        self.close_view()
        if self.tools is not None:
            self.tools.close()
        self._subscribe = None
        self.agent = None
        self.closed = True
