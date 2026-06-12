"""Streamlit UI shell for the CE 4011 structural analysis app."""

from __future__ import annotations

try:
    from .state import NAVIGATION_SECTIONS, initialize_session_state
except ImportError:  # pragma: no cover - supports direct `streamlit run src/ui/app.py`
    from state import NAVIGATION_SECTIONS, initialize_session_state


def render_shell(st_module) -> None:
    """Render the navigation shell without performing analysis work."""
    initialize_session_state(st_module.session_state)

    st_module.set_page_config(
        page_title="CE 4011 Structural Analysis",
        layout="wide",
    )
    st_module.title("CE 4011 Structural Analysis")

    selected_section = st_module.sidebar.radio(
        "Navigation",
        NAVIGATION_SECTIONS,
        key="ui_current_section",
    )

    st_module.header(selected_section)
    st_module.info("This phase establishes the UI shell and session defaults.")


def main() -> None:
    """Run the Streamlit app."""
    import streamlit as st

    render_shell(st)


if __name__ == "__main__":
    main()
