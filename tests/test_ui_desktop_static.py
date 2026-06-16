import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from ui_desktop import main_window


def _window_with_model(model=object()):
    window = main_window.MainWindow.__new__(main_window.MainWindow)
    window.model_canvas = SimpleNamespace(builder=SimpleNamespace(model=model))
    window.messages = []
    window._write_status = window.messages.append
    window.latest_static_results = None
    window.static_analysis_error = None
    return window


def test_desktop_run_static_analysis_stores_result_and_status(monkeypatch):
    expected_results = SimpleNamespace(load_case_id="LC1", displacements={1: [0.0]}, reactions={1: [10.0]})

    def fake_run_static_analysis(model):
        return SimpleNamespace(ok=True, results=expected_results, error=None)

    monkeypatch.setattr(main_window, "run_static_analysis", fake_run_static_analysis)
    window = _window_with_model()

    window._toolbar_action("Run Static Analysis")

    assert window.latest_static_results is expected_results
    assert window.static_analysis_error is None
    assert "Static analysis complete for LC1" in window.messages[-1]


def test_desktop_run_static_analysis_reports_failure_without_crashing(monkeypatch):
    def fake_run_static_analysis(model):
        return SimpleNamespace(ok=False, results=None, error="Static analysis failed: unstable")

    monkeypatch.setattr(main_window, "run_static_analysis", fake_run_static_analysis)
    window = _window_with_model()
    window.latest_static_results = object()

    window._toolbar_action("Run Static Analysis")

    assert window.latest_static_results is None
    assert window.static_analysis_error == "Static analysis failed: unstable"
    assert window.messages[-1] == "Static analysis failed: unstable"


def test_desktop_static_result_tables_use_cached_result_fields():
    results = SimpleNamespace(
        displacements={1: [0.001, 0.0, 0.0]},
        reactions={1: [10.0, -2.5, 0.0]},
        element_forces={"e1": {"i": [10.0, 0.0, 0.0], "j": [-10.0, 0.0, 0.0]}},
        dof_map={(1, "ux"): 0},
        K=[[1.0, 0.0], [0.0, 1.0]],
        Kff=[[1.0]],
        F=[10.0, 0.0],
        Ff=[10.0],
    )
    window = _window_with_model()
    window.latest_static_results = results

    columns, rows = window._static_result_table_data("Nodal Displacements")
    assert columns == ("Node", "UX", "UY", "RZ")
    assert rows == [("1", "0.001", "0", "0")]

    columns, rows = window._static_result_table_data("Member End Forces")
    assert columns == ("Element", "Location", "Values")
    assert ("e1", "i", "10, 0, 0") in rows

    columns, rows = window._static_result_table_data("Matrix Summary")
    assert columns == ("Item", "Rows", "Columns")
    assert ("K", "2", "2") in rows


def test_desktop_static_result_table_empty_state():
    window = _window_with_model()

    columns, rows = window._static_result_table_data("Nodal Displacements")

    assert columns == ("Message",)
    assert rows == [("Run Static Analysis first.",)]
