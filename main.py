import sys

from PyQt6.QtWidgets import (
    QApplication,
)

from app.domain.jamo_data import (
    get_consonant_order,
    get_vowel_order_basic10,
    get_vowel_order_advanced
)
from app.domain.block_types import block_type_for_pair
from app.ui.main_window import create_main_window

# --- Slow mode globals (module scope) ---
_DEBUG_MAIN = False

# -------------------------------------------------
#           DOMAIN-LOADED ORDERING
# -------------------------------------------------
# Canonical consonant/vowel ordering.
# Loaded from YAML via app/domain/jamo_data.py.
# main.py must not define or override ordering rules.
CONSONANT_ORDER: list[str] = get_consonant_order()
VOWEL_ORDER_BASIC10: list[str] = get_vowel_order_basic10()
VOWEL_ORDER_ADVANCED: list[str] = get_vowel_order_advanced()


def main():
    app = QApplication(sys.argv)
    # Use the imported create_main_window from app.ui.main_window
    result = create_main_window(expose_handles=True)
    if isinstance(result, tuple) and len(result) == 2:
        window, _handles = result
    else:
        window, _handles = result, None
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
