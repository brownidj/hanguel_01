from __future__ import annotations

from typing import Optional

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QFrame, QMainWindow, QPushButton, QToolBar, QWidget

from app.controllers.drawer_controller import DrawerController
from app.ui.icons import build_hamburger_icon


class DrawerUiController:
    """Owns drawer UI discovery and wiring."""

    def __init__(self, *, window: QWidget) -> None:
        self._window = window
        self._drawer_controller: Optional[DrawerController] = None

    def wire(self) -> None:
        drawer = self._window.findChild(QFrame, "drawerLeft")
        self._drawer_controller = DrawerController(drawer)
        if self._drawer_controller is None:
            return

        if drawer is not None:
            self._drawer_controller.hide()

        close_btn = self._window.findChild(QPushButton, "buttonCloseDrawer")
        if close_btn is not None:
            try:
                close_btn.clicked.connect(self._drawer_controller.hide)
            except Exception:
                pass

        if isinstance(self._window, QMainWindow):
            self._wire_toolbar_action()

        button_hamburger = self._window.findChild(QPushButton, "buttonHamburger")
        if button_hamburger is not None:
            try:
                button_hamburger.clicked.connect(self._drawer_controller.toggle)
            except Exception:
                pass

    def _wire_toolbar_action(self) -> None:
        try:
            menubar = self._window.menuBar()
            if menubar is not None:
                try:
                    menubar.setNativeMenuBar(False)
                except Exception:
                    pass
        except Exception:
            pass

        try:
            toolbar = self._window.findChild(QToolBar, "mainToolbar")
            if toolbar is None:
                toolbar = QToolBar("MainToolbar", self._window)
                toolbar.setObjectName("mainToolbar")
                self._window.addToolBar(toolbar)

            action_toggle = QAction(build_hamburger_icon(20), "Toggle Drawer", self._window)
            action_toggle.setToolTip("Open or close the settings drawer")
            if self._drawer_controller is not None:
                action_toggle.triggered.connect(self._drawer_controller.toggle)
            toolbar.addAction(action_toggle)
        except Exception:
            pass
