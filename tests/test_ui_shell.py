import importlib
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from ui.state import NAVIGATION_SECTIONS, initialize_session_state


def test_ui_state_defaults():
    state = initialize_session_state({})

    assert state["model"] is None
    assert state["model_is_dirty"] is True
    assert state["ui_current_section"] == "Model Input"


def test_ui_navigation_sections_exist():
    assert NAVIGATION_SECTIONS == (
        "Model Input",
        "Static Analysis",
        "Dynamic Analysis",
        "Results",
        "Visualization",
    )


def test_ui_app_imports_without_running_streamlit_server():
    app = importlib.import_module("ui.app")

    assert callable(app.main)
    assert callable(app.render_shell)
