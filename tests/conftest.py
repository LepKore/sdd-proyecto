"""Qt runs without a screen during the tests: no real window ever opens."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
