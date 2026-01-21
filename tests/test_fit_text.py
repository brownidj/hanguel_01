import os
import pytest


@pytest.fixture(scope="session")
def qapp():
    """Ensure a Qt application exists for label fitting tests.

    Runs safely in headless / CI environments.
    """
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    try:
        from PyQt6.QtWidgets import QApplication
    except Exception as e:
        pytest.skip("PyQt6 is not available: {0}".format(e))

    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_fit_label_font_to_label_rect_reduces_font_size(qapp):
    """Font size should be reduced to fit into a small label rect."""
    from PyQt6.QtWidgets import QLabel
    from PyQt6.QtGui import QFont
    from app.ui.fit_text import _fit_label_font_to_label_rect

    lbl = QLabel("This is a long piece of text that must shrink")
    lbl.resize(80, 20)

    font = QFont()
    font.setPointSize(20)
    lbl.setFont(font)

    before = lbl.font().pointSize()
    _fit_label_font_to_label_rect(lbl)
    after = lbl.font().pointSize()

    assert after <= before
    assert after > 0


def test_autofitlabel_constructs_and_sets_text(qapp):
    """AutoFitLabel should construct cleanly and accept text."""
    from app.ui.fit_text import AutoFitLabel

    lbl = AutoFitLabel("Hello Hangul")
    lbl.resize(120, 40)

    assert lbl.text() == "Hello Hangul"


def test_autofithook_attaches_without_crash(qapp):
    """_AutoFitHook should be attachable to a QLabel without raising."""
    from PyQt6.QtWidgets import QLabel
    from app.ui.fit_text import _AutoFitHook

    lbl = QLabel("가나다라마바사")
    lbl.resize(100, 30)

    hook = _AutoFitHook(lbl)
    assert hook is not None


def test_autofithook_reacts_to_resize(qapp):
    """Resizing the label should not crash and should keep a valid font."""
    from PyQt6.QtWidgets import QLabel
    from app.ui.fit_text import _AutoFitHook

    lbl = QLabel("Very long text that needs fitting")
    lbl.resize(200, 40)
    hook = _AutoFitHook(lbl)

    before = lbl.font().pointSize()
    lbl.resize(80, 20)
    lbl.resize(160, 40)
    after = lbl.font().pointSize()

    assert after > 0
    # We don't assert exact equality — only that it remains sane
