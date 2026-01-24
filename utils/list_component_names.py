# scripts/dump_ui_tree.py (or run in a scratch file)
from PyQt6.QtWidgets import QApplication, QStackedWidget
from main import create_main_window  # adjust if your factory lives elsewhere

def main():
    app = QApplication([])
    w = create_main_window(expose_handles=True)
    w.show()

    stacked = w.findChild(QStackedWidget, "stackedTemplates")
    print("stackedTemplates:", stacked)

    if stacked is None:
        return

    for i in range(stacked.count()):
        page = stacked.widget(i)
        print("\n=== PAGE {}: {} ===".format(i, page.objectName()))
        # List all named children under the page
        for child in page.findChildren(object):
            try:
                name = child.objectName()
            except Exception:
                continue
            if name:
                print("  {} ({})".format(name, type(child).__name__))

if __name__ == "__main__":
    main()