import os
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def qapp():
    """Ensure a Qt application exists for QIcon/QPixmap operations.

    This is intentionally lightweight and safe for CI/offscreen execution.
    """
    # Avoid platform plugin popups in headless environments.
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    try:
        from PyQt6.QtWidgets import QApplication
    except Exception as e:
        pytest.skip("PyQt6 is not available: {0}".format(e))

    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_build_hamburger_icon_returns_non_null_icon(qapp):
    from PyQt6.QtGui import QIcon
    from app.ui.icons import build_hamburger_icon

    icon = build_hamburger_icon(size=24)
    assert isinstance(icon, QIcon)
    assert not icon.isNull()


def test_build_hamburger_icon_pixmap_size_and_transparency(qapp):
    from PyQt6.QtGui import QImage
    from app.ui.icons import build_hamburger_icon

    size = 32
    icon = build_hamburger_icon(size=size)
    pm = icon.pixmap(size, size)

    assert not pm.isNull()
    assert pm.width() == size
    assert pm.height() == size

    img = pm.toImage().convertToFormat(QImage.Format.Format_ARGB32)
    # Corners should remain fully transparent (we draw centered horizontal lines).
    for x, y in [(0, 0), (size - 1, 0), (0, size - 1), (size - 1, size - 1)]:
        alpha = img.pixelColor(x, y).alpha()
        assert alpha == 0


def test_safe_icon_from_path_returns_icon_for_existing_png(qapp, tmp_path: Path):
    from PIL import Image
    from PyQt6.QtGui import QIcon
    from app.ui.icons import safe_icon_from_path

    p = tmp_path / "sample.png"
    Image.new("RGBA", (16, 16), (255, 0, 0, 255)).save(str(p))

    icon = safe_icon_from_path(str(p))
    assert icon is not None
    assert isinstance(icon, QIcon)
    assert not icon.isNull()


def test_safe_icon_from_path_returns_none_for_missing_file(qapp, tmp_path: Path):
    from PyQt6.QtGui import QIcon
    from app.ui.icons import safe_icon_from_path

    missing = tmp_path / "does_not_exist.png"
    icon = safe_icon_from_path(str(missing))

    # Some implementations return None; others return a null QIcon().
    if icon is None:
        return

    assert isinstance(icon, QIcon)
    assert icon.isNull()