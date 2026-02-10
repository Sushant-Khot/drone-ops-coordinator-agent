import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd
import streamlit as st

_PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Ensure `import app.*` works even when Streamlit is launched from a different
# working directory / Python environment.
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def _load_env_fallback(env_path: str = ".env") -> None:
    """
    Minimal `.env` loader used only if `python-dotenv` isn't installed
    in the same Python environment as Streamlit.
    """
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for raw in f.readlines():
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v
    except FileNotFoundError:
        return


# Load dotenv if available (for local run)
try:
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except ModuleNotFoundError:
    _load_env_fallback()


from app.agent import CoordinatorAgent  # noqa: E402
from app.sheets_client import SheetsClient  # noqa: E402


def _as_df(data: Any) -> pd.DataFrame:
    if isinstance(data, list):
        return pd.DataFrame(data)
    if isinstance(data, dict):
        return pd.DataFrame([data])
    return pd.DataFrame()


def _count_available(rows: List[Dict[str, Any]], key: str = "status") -> int:
    return sum(1 for r in rows if str(r.get(key, "")).strip().lower() == "available")


@st.cache_resource
def _get_client_and_agent(script_url: str) -> Tuple[SheetsClient, CoordinatorAgent]:
    client = SheetsClient(script_url)
    agent = CoordinatorAgent(client)
    return client, agent


@st.cache_data(ttl=30)
def _fetch_tables(script_url: str):
    # Cache by script_url (hashable), not by client (unhashable).
    client = SheetsClient(script_url)
    pilots = client.get_pilot_data()
    drones = client.get_drone_data()
    return pilots, drones


def _init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hi — I’m the Drone Ops Coordinator. Ask me about available pilots/drones, status updates, or assignments.",
            }
        ]


def _get_script_url() -> str:
    """
    Loads GOOGLE_SCRIPT_URL from:
    1) local .env environment variable
    2) Streamlit Cloud secrets
    """
    script_url = os.getenv("GOOGLE_SCRIPT_URL", "").strip()

    if not script_url:
        try:
            script_url = str(st.secrets["GOOGLE_SCRIPT_URL"]).strip()
        except Exception:
            script_url = ""

    return script_url.strip()


def main() -> None:
    st.set_page_config(
        page_title="Skylark Drones — Ops Coordinator",
        page_icon="🛩️",
        layout="wide",
    )

    st.markdown(
        """
        <style>
          .block-container { padding-top: 1.25rem; padding-bottom: 2rem; }
          [data-testid="stSidebar"] .block-container { padding-top: 1rem; }
          .small-muted { color: rgba(49, 51, 63, 0.7); font-size: 0.9rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Load Script URL from .env OR Streamlit secrets
    script_url = _get_script_url()

    if not script_url:
        st.error("Missing `GOOGLE_SCRIPT_URL`.")
        st.info("✅ Local Run: Add it to `.env` in the project root.")
        st.info("✅ Streamlit Cloud: Add it in App Settings → Secrets.")
        st.code('GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/XXXX/exec"')
        st.stop()

    client, agent = _get_client_and_agent(script_url)

    with st.sidebar:
        st.markdown("## Ops Console")
        st.markdown(
            '<div class="small-muted">Live data via Google Apps Script</div>',
            unsafe_allow_html=True,
        )
        st.markdown(" ")
        st.text_input("Google Script URL", value=script_url, disabled=True)

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Refresh data", use_container_width=True):
                _fetch_tables.clear()
        with col_b:
            if st.button("Clear chat", use_container_width=True):
                st.session_state.messages = [
                    {
                        "role": "assistant",
                        "content": "Chat cleared. What would you like to do?",
                    }
                ]

        st.markdown("---")
        st.markdown("### Example queries")
        st.code(
            "\n".join(
                [
                    "show available pilots in Bangalore",
                    "show available drones thermal",
                    "update pilot Arjun to On Leave",
                    "update drone D001 to Maintenance",
                    "assign project PRJ003 in Bangalore thermal dgca",
                    "urgent assign project PRJ002 in Mumbai night ops",
                ]
            )
        )

    _init_state()

    # Header
    left, right = st.columns([0.65, 0.35], gap="large")
    with left:
        st.markdown("## Drone Operations Coordinator")
        st.markdown(
            '<div class="small-muted">Chat-driven coordination + live roster and fleet tables.</div>',
            unsafe_allow_html=True,
        )

    # Data snapshot + metrics
    pilots, drones = _fetch_tables(script_url)
    pilots_rows: List[Dict[str, Any]] = pilots if isinstance(pilots, list) else []
    drones_rows: List[Dict[str, Any]] = drones if isinstance(drones, list) else []

    with right:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Pilots", len(pilots_rows))
        c2.metric("Available", _count_available(pilots_rows))
        c3.metric("Drones", len(drones_rows))
        c4.metric("Available", _count_available(drones_rows))

    st.markdown("---")

    tab_chat, tab_tables = st.tabs(["Chat", "Pilots & Drones"])

    with tab_chat:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        prompt = st.chat_input("Type a request (e.g. “show available pilots in Bangalore”)")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Working..."):
                    result = agent.handle_query(prompt)

                # Normalize output
                message = ""
                if isinstance(result, dict):
                    message = str(result.get("message", "")) or str(result)
                else:
                    message = str(result)

                st.markdown(message)

                # Optional: show match details if present
                if isinstance(result, dict) and "match" in result and isinstance(result["match"], dict):
                    st.markdown("#### Match details")
                    st.json(result["match"])

            st.session_state.messages.append({"role": "assistant", "content": message})

    with tab_tables:
        st.markdown("### Pilots")
        df_p = _as_df(pilots_rows)
        if not df_p.empty:
            st.dataframe(df_p, use_container_width=True, hide_index=True)
        else:
            st.info("No pilot rows available.")

        st.markdown("### Drones")
        df_d = _as_df(drones_rows)
        if not df_d.empty:
            st.dataframe(df_d, use_container_width=True, hide_index=True)
        else:
            st.info("No drone rows available.")


if __name__ == "__main__":
    main()
