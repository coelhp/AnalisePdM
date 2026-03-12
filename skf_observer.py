"""
SKF Observer Phoenix — Dashboard de Monitoramento
==================================================
Streamlit app para consulta e visualização de dados de tendência.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timezone, timedelta
import numpy as np

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SKF Observer Phoenix",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS GLOBAL — Industrial Dark Theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&family=Exo+2:wght@300;400;600&display=swap');

:root {
    --bg-base:      #090c10;
    --bg-card:      #0d1117;
    --bg-panel:     #161b22;
    --border:       #21262d;
    --border-glow:  #30363d;
    --accent:       #00d9ff;
    --accent-dim:   #0099bb;
    --accent-glow:  rgba(0,217,255,0.15);
    --warn:         #f0a500;
    --danger:       #ff4757;
    --ok:           #2ed573;
    --text-hi:      #e6edf3;
    --text-mid:     #8b949e;
    --text-lo:      #484f58;
    --font-head:    'Rajdhani', sans-serif;
    --font-mono:    'Share Tech Mono', monospace;
    --font-body:    'Exo 2', sans-serif;
}

/* Base */
html, body, [class*="css"] {
    font-family: var(--font-body) !important;
    background-color: var(--bg-base) !important;
    color: var(--text-hi) !important;
}

/* Hide default header/footer */
#MainMenu, footer, header { visibility: hidden; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--bg-card) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * {
    font-family: var(--font-body) !important;
}

/* Custom header band */
.top-banner {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d1117 100%);
    border-bottom: 1px solid var(--accent);
    box-shadow: 0 0 30px rgba(0,217,255,0.08);
    padding: 18px 32px;
    margin: -1rem -1rem 2rem -1rem;
    display: flex;
    align-items: center;
    gap: 18px;
}
.top-banner .logo-box {
    width: 48px; height: 48px;
    border: 2px solid var(--accent);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
    box-shadow: 0 0 18px var(--accent-glow);
}
.top-banner h1 {
    font-family: var(--font-head) !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    letter-spacing: 3px;
    color: var(--text-hi) !important;
    margin: 0 !important; padding: 0 !important;
    text-transform: uppercase;
}
.top-banner .sub {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    color: var(--accent);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 2px;
}

/* Metric cards */
.metric-row { display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }
.metric-card {
    flex: 1; min-width: 150px;
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-top: 2px solid var(--accent);
    border-radius: 8px;
    padding: 16px 20px;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    opacity: 0.5;
}
.metric-card .label {
    font-family: var(--font-mono);
    font-size: 0.68rem;
    color: var(--text-mid);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.metric-card .value {
    font-family: var(--font-head);
    font-size: 1.9rem;
    font-weight: 700;
    color: var(--accent);
    line-height: 1;
}
.metric-card .unit {
    font-family: var(--font-mono);
    font-size: 0.75rem;
    color: var(--text-mid);
    margin-top: 4px;
}
.metric-card.warn  { border-top-color: var(--warn);   }
.metric-card.warn  .value { color: var(--warn); }
.metric-card.danger { border-top-color: var(--danger); }
.metric-card.danger .value { color: var(--danger); }
.metric-card.ok    { border-top-color: var(--ok); }
.metric-card.ok    .value  { color: var(--ok); }

/* Status badges */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 4px;
    font-family: var(--font-mono);
    font-size: 0.7rem;
    letter-spacing: 1px;
    text-transform: uppercase;
    font-weight: 600;
}
.badge-ok      { background: rgba(46,213,115,0.15); color: var(--ok);     border: 1px solid rgba(46,213,115,0.3); }
.badge-warn    { background: rgba(240,165,0,0.15);  color: var(--warn);   border: 1px solid rgba(240,165,0,0.3); }
.badge-danger  { background: rgba(255,71,87,0.15);  color: var(--danger); border: 1px solid rgba(255,71,87,0.3); }
.badge-offline { background: rgba(139,148,158,0.1); color: var(--text-mid); border: 1px solid var(--border); }

/* Section headers */
.section-title {
    font-family: var(--font-head);
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--text-mid);
    border-left: 3px solid var(--accent);
    padding-left: 10px;
    margin: 24px 0 14px 0;
}

/* Asset/Point table */
.data-table {
    width: 100%;
    border-collapse: collapse;
    font-family: var(--font-body);
    font-size: 0.87rem;
}
.data-table th {
    font-family: var(--font-mono);
    font-size: 0.68rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text-mid);
    padding: 8px 12px;
    border-bottom: 1px solid var(--border);
    text-align: left;
    background: var(--bg-card);
}
.data-table td {
    padding: 9px 12px;
    border-bottom: 1px solid var(--border);
    color: var(--text-hi);
    vertical-align: middle;
}
.data-table tr:hover td { background: rgba(0,217,255,0.04); }
.id-chip {
    font-family: var(--font-mono);
    font-size: 0.78rem;
    color: var(--accent);
    background: rgba(0,217,255,0.08);
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid rgba(0,217,255,0.2);
}

/* Inputs / Selects */
.stSelectbox > div > div,
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: var(--bg-panel) !important;
    border: 1px solid var(--border-glow) !important;
    border-radius: 6px !important;
    color: var(--text-hi) !important;
    font-family: var(--font-body) !important;
}
.stSelectbox > div > div:focus-within,
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-glow) !important;
}

/* Buttons */
.stButton > button {
    background: transparent !important;
    border: 1px solid var(--accent) !important;
    color: var(--accent) !important;
    font-family: var(--font-head) !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    border-radius: 6px !important;
    padding: 10px 24px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: var(--accent-glow) !important;
    box-shadow: 0 0 16px var(--accent-glow) !important;
}
.stButton > button[kind="primary"] {
    background: var(--accent) !important;
    color: #090c10 !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: var(--bg-panel) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    font-family: var(--font-head) !important;
    color: var(--text-hi) !important;
}

/* Sidebar labels */
.sidebar-label {
    font-family: var(--font-mono);
    font-size: 0.68rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text-mid);
    margin-bottom: 4px;
}

/* Divider */
.hline {
    border: none;
    border-top: 1px solid var(--border);
    margin: 20px 0;
}

/* Alert boxes */
.alert-box {
    padding: 12px 16px;
    border-radius: 6px;
    font-family: var(--font-body);
    font-size: 0.88rem;
    margin: 12px 0;
}
.alert-warn   { background: rgba(240,165,0,0.1);  border-left: 3px solid var(--warn);   color: #f5c842; }
.alert-danger { background: rgba(255,71,87,0.1);  border-left: 3px solid var(--danger); color: #ff6b7a; }
.alert-info   { background: rgba(0,217,255,0.08); border-left: 3px solid var(--accent); color: var(--accent); }
.alert-ok     { background: rgba(46,213,115,0.08); border-left: 3px solid var(--ok);    color: var(--ok); }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
for key, default in {
    "token": None,
    "assets": [],
    "points": [],
    "trend_df": None,
    "spectrum_data": None,
    "selected_asset": None,
    "selected_point": None,
    "base_url": "http://127.0.0.1:14050",
    "username": "admin",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ─────────────────────────────────────────────
# HELPERS API
# ─────────────────────────────────────────────
def api_headers():
    return {
        "Authorization": f"Bearer {st.session_state.token}",
        "Accept": "application/json; v=2.0",
    }

def autenticar(base_url, username, password):
    resp = requests.post(
        f"{base_url}/token",
        headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
        data={"grant_type": "password", "username": username, "password": password},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json().get("access_token")

def get_assets(base_url, token):
    resp = requests.get(
        f"{base_url}/v2/assets",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json; v=2.0"},
        params={"includeAcknowledged": "true"},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json() if resp.status_code != 204 else []

def get_points(base_url, token, machine_id):
    resp = requests.get(
        f"{base_url}/v1/machines/{machine_id}/points",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json; v=2.0"},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json() if resp.status_code != 204 else []

def get_trend(base_url, token, point_id, from_date=None, to_date=None, max_readings=1000):
    params = {"pointId": point_id, "maxNumberOfReadings": max_readings, "descending": "false"}
    if from_date:
        params["fromDateUTC"] = from_date
    if to_date:
        params["toDateUTC"] = to_date
    resp = requests.get(
        f"{base_url}/v1/points/{point_id}/trendMeasurements",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json; v=2.0"},
        params=params,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json() if resp.status_code != 204 else []

def get_spectrum(base_url, token, point_id):
    resp = requests.get(
        f"{base_url}/v1/points/{point_id}/dynamicMeasurements",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json() if resp.status_code != 204 else None

def parse_trend(data) -> pd.DataFrame:
    """
    Suporta dois formatos de resposta da API:

    Formato A — legado (campos planos):
        { "timestamp": "...", "value": {"value": 1.2, "unit": "g"} }

    Formato B — real (array Measurements):
        {
          "ReadingTimeUTC": "2026-03-10T18:45:15.353",
          "PointID": 4164,
          "Speed": 0.0, "SpeedUnits": "RPM",
          "Process": 0.0, "ProcessUnits": "",
          "Measurements": [
            {"Channel": 1, "Direction": "X", "ChannelName": "Overall",
             "Level": 37.0, "Units": "C", "BOV": 0.0}
          ]
        }

    Retorna DataFrame com colunas:
        timestamp | value | unit | channel | channel_name | direction | speed | process
    """
    rows = []

    for item in data:
        # ── Formato B: array Measurements ──────────────────────────
        if "Measurements" in item and isinstance(item["Measurements"], list):
            ts_raw = (
                item.get("ReadingTimeUTC")
                or item.get("ReadingTime")
                or item.get("dateUTC")
                or item.get("timestamp")
            )
            speed   = item.get("Speed",   None)
            process = item.get("Process", None)

            measurements = item["Measurements"]
            if not measurements:
                continue

            for meas in measurements:
                rows.append({
                    "timestamp":    ts_raw,
                    "value":        meas.get("Level"),
                    "unit":         meas.get("Units", ""),
                    "channel":      meas.get("Channel", 1),
                    "channel_name": meas.get("ChannelName", "Overall"),
                    "direction":    meas.get("Direction", ""),
                    "bov":          meas.get("BOV", None),
                    "speed":        speed,
                    "process":      process,
                })

        # ── Formato A: campos planos (legado) ───────────────────────
        else:
            ts_raw  = (
                item.get("timestamp")
                or item.get("dateUTC")
                or item.get("date")
                or item.get("ReadingTimeUTC")
            )
            val_obj = item.get("value") or {}
            if isinstance(val_obj, dict):
                value = val_obj.get("value")
                unit  = val_obj.get("unit", "")
            else:
                value = val_obj
                unit  = item.get("unit", "")

            rows.append({
                "timestamp":    ts_raw,
                "value":        value,
                "unit":         unit,
                "channel":      1,
                "channel_name": item.get("source", "Overall"),
                "direction":    "",
                "bov":          None,
                "speed":        None,
                "process":      None,
            })

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df["value"]     = pd.to_numeric(df["value"],     errors="coerce")
    df["speed"]     = pd.to_numeric(df.get("speed"), errors="coerce")
    df["process"]   = pd.to_numeric(df.get("process"), errors="coerce")
    df.dropna(subset=["timestamp", "value"], inplace=True)
    df.sort_values("timestamp", inplace=True)
    df.drop_duplicates(subset=["timestamp", "channel"], keep="last", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def parse_spectrum(data):
    """
    Converte a resposta de /v1/points/{id}/dynamicMeasurements em lista de dicts por canal.

    Estrutura esperada (data pode ser um dict ou lista de dicts):
        {
          "PointID": 5567,
          "SampleRate": 5120.0,
          "Samples": 8192,
          "EU": "m/s^2E",
          "StartFrequency": 0.0,
          "EndFrequency": 2000.0,
          "Speed": 0.0, "SpeedUnits": "RPM",
          "Process": 36.0,
          "Measurements": [
            {
              "MeasurementType": 2,
              "Direction": 0,
              "Values": [0.001, 0.002, ...]   ← amplitudes do espectro
            }
          ]
        }

    Retorna lista de dicts:
        [{
          "channel_idx": 0,
          "direction": 0,
          "mtype": 2,
          "eu": "m/s^2E",
          "start_freq": 0.0,
          "end_freq": 2000.0,
          "freqs": np.ndarray,
          "values": np.ndarray,
          "sample_rate": 5120.0,
          "samples": 8192,
          "speed": 0.0,
          "speed_units": "RPM",
        }]
    """
    if data is None:
        return []

    # aceita tanto dict único quanto lista
    items = data if isinstance(data, list) else [data]
    channels = []

    for item in items:
        eu          = item.get("EU") or item.get("EUSpectrum") or "—"
        start_f     = float(item.get("StartFrequency", 0.0))
        end_f       = float(item.get("EndFrequency",   0.0))
        sample_rate = float(item.get("SampleRate",     0.0))
        samples     = int(item.get("Samples",          0))
        speed       = item.get("Speed", 0.0)
        speed_units = item.get("SpeedUnits", "RPM")
        process     = item.get("Process", None)

        measurements = item.get("Measurements") or []
        for idx, meas in enumerate(measurements):
            values = meas.get("Values") or []
            if not values:
                continue
            n = len(values)
            # eixo de frequência: interpolação linear entre start_f e end_f
            freqs = np.linspace(start_f, end_f, n) if end_f > start_f else np.arange(n)

            channels.append({
                "channel_idx": idx,
                "direction":   meas.get("Direction", idx),
                "mtype":       meas.get("MeasurementType", 0),
                "eu":          eu,
                "start_freq":  start_f,
                "end_freq":    end_f,
                "freqs":       np.array(freqs, dtype=float),
                "values":      np.array(values, dtype=float),
                "sample_rate": sample_rate,
                "samples":     samples,
                "speed":       float(speed) if speed is not None else 0.0,
                "speed_units": speed_units,
                "process":     float(process) if process is not None else 0.0,
            })

    return channels


    """
    Suporta dois formatos de resposta da API:

    Formato A — legado (campos planos):
        { "timestamp": "...", "value": {"value": 1.2, "unit": "g"} }

    Formato B — real (array Measurements):
        {
          "ReadingTimeUTC": "2026-03-10T18:45:15.353",
          "PointID": 4164,
          "Speed": 0.0, "SpeedUnits": "RPM",
          "Process": 0.0, "ProcessUnits": "",
          "Measurements": [
            {"Channel": 1, "Direction": "X", "ChannelName": "Overall",
             "Level": 37.0, "Units": "C", "BOV": 0.0}
          ]
        }

    Retorna DataFrame com colunas:
        timestamp | value | unit | channel | channel_name | direction | speed | process
    """
    rows = []

    for item in data:
        # ── Formato B: array Measurements ──────────────────────────
        if "Measurements" in item and isinstance(item["Measurements"], list):
            ts_raw = (
                item.get("ReadingTimeUTC")
                or item.get("ReadingTime")
                or item.get("dateUTC")
                or item.get("timestamp")
            )
            speed   = item.get("Speed",   None)
            process = item.get("Process", None)

            measurements = item["Measurements"]
            if not measurements:
                continue

            for meas in measurements:
                rows.append({
                    "timestamp":    ts_raw,
                    "value":        meas.get("Level"),
                    "unit":         meas.get("Units", ""),
                    "channel":      meas.get("Channel", 1),
                    "channel_name": meas.get("ChannelName", "Overall"),
                    "direction":    meas.get("Direction", ""),
                    "bov":          meas.get("BOV", None),
                    "speed":        speed,
                    "process":      process,
                })

        # ── Formato A: campos planos (legado) ───────────────────────
        else:
            ts_raw  = (
                item.get("timestamp")
                or item.get("dateUTC")
                or item.get("date")
                or item.get("ReadingTimeUTC")
            )
            val_obj = item.get("value") or {}
            if isinstance(val_obj, dict):
                value = val_obj.get("value")
                unit  = val_obj.get("unit", "")
            else:
                value = val_obj
                unit  = item.get("unit", "")

            rows.append({
                "timestamp":    ts_raw,
                "value":        value,
                "unit":         unit,
                "channel":      1,
                "channel_name": item.get("source", "Overall"),
                "direction":    "",
                "bov":          None,
                "speed":        None,
                "process":      None,
            })

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df["value"]     = pd.to_numeric(df["value"],     errors="coerce")
    df["speed"]     = pd.to_numeric(df.get("speed"), errors="coerce")
    df["process"]   = pd.to_numeric(df.get("process"), errors="coerce")
    df.dropna(subset=["timestamp", "value"], inplace=True)
    df.sort_values("timestamp", inplace=True)
    df.drop_duplicates(subset=["timestamp", "channel"], keep="last", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def get_channel_options(df: pd.DataFrame) -> dict:
    """Retorna dicionário label → channel_id para uso no selectbox."""
    if df.empty or "channel" not in df.columns:
        return {}
    channels = (
        df[["channel", "channel_name", "direction", "unit"]]
        .drop_duplicates(subset=["channel"])
        .sort_values("channel")
    )
    opts = {}
    for _, row in channels.iterrows():
        label = f"Ch{int(row['channel'])}  {row['channel_name']}"
        if row["direction"]:
            label += f"  [{row['direction']}]"
        label += f"  · {row['unit']}"
        opts[label] = int(row["channel"])
    return opts

def status_badge(status_list):
    if not status_list:
        return '<span class="badge badge-offline">Offline</span>'
    s = status_list[0] if isinstance(status_list, list) else status_list
    if s == 0:
        return '<span class="badge badge-ok">OK</span>'
    elif s == 1:
        return '<span class="badge badge-warn">Alerta</span>'
    elif s == 2:
        return '<span class="badge badge-danger">Alarme</span>'
    return '<span class="badge badge-offline">—</span>'


# ─────────────────────────────────────────────
# SIDEBAR — Conexão
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:16px 0 8px;">
        <div style="font-family:'Rajdhani',sans-serif;font-size:1.4rem;font-weight:700;
                    letter-spacing:3px;text-transform:uppercase;color:#e6edf3;">
            ⚙ SKF Observer
        </div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.68rem;
                    color:#00d9ff;letter-spacing:2px;">PHOENIX API v2.0</div>
    </div>
    <hr style="border-color:#21262d;margin:8px 0 20px 0;">
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label">Servidor</div>', unsafe_allow_html=True)
    base_url = st.text_input("", value=st.session_state.base_url,
                              placeholder="http://127.0.0.1:14050", label_visibility="collapsed")
    st.session_state.base_url = base_url

    st.markdown('<div class="sidebar-label" style="margin-top:12px;">Usuário</div>', unsafe_allow_html=True)
    username = st.text_input("", value=st.session_state.username, label_visibility="collapsed")

    st.markdown('<div class="sidebar-label" style="margin-top:12px;">Senha</div>', unsafe_allow_html=True)
    password = st.text_input("", type="password", placeholder="••••••••", label_visibility="collapsed")

    if st.button("🔌  Conectar", use_container_width=True):
        with st.spinner("Autenticando..."):
            try:
                token = autenticar(base_url, username, password)
                st.session_state.token    = token
                st.session_state.username = username
                assets = get_assets(base_url, token)
                st.session_state.assets   = assets
                st.session_state.points   = []
                st.session_state.trend_df = None
                st.session_state.selected_asset = None
                st.session_state.selected_point = None
                st.success(f"✅ Conectado! {len(assets)} asset(s) encontrado(s).")
            except requests.exceptions.ConnectionError:
                st.error("❌ Servidor inacessível.")
            except requests.exceptions.HTTPError as e:
                st.error(f"❌ Erro HTTP {e.response.status_code}")
            except Exception as e:
                st.error(f"❌ {e}")

    # Status de conexão
    st.markdown('<hr style="border-color:#21262d;margin:20px 0;">', unsafe_allow_html=True)
    if st.session_state.token:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:8px;">
            <div style="width:8px;height:8px;background:#2ed573;border-radius:50%;
                        box-shadow:0 0 8px #2ed573;"></div>
            <span style="font-family:'Share Tech Mono',monospace;font-size:0.72rem;
                         color:#8b949e;letter-spacing:1px;">CONECTADO</span>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:8px;">
            <div style="width:8px;height:8px;background:#484f58;border-radius:50%;"></div>
            <span style="font-family:'Share Tech Mono',monospace;font-size:0.72rem;
                         color:#484f58;letter-spacing:1px;">DESCONECTADO</span>
        </div>""", unsafe_allow_html=True)

    # Filtros de data (visível só quando conectado)
    if st.session_state.token:
        st.markdown('<hr style="border-color:#21262d;margin:20px 0;">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-label">Período de tendência</div>', unsafe_allow_html=True)

        today = datetime.now(timezone.utc).date()
        date_from = st.date_input("De", value=today - timedelta(days=90), label_visibility="visible")
        date_to   = st.date_input("Até", value=today, label_visibility="visible")
        max_read  = st.number_input("Máx. leituras", min_value=10, max_value=5000,
                                    value=500, step=50)
        st.session_state["date_from"] = date_from
        st.session_state["date_to"]   = date_to
        st.session_state["max_read"]  = max_read


# ─────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────

# Header banner
st.markdown("""
<div class="top-banner">
    <div class="logo-box">⚙</div>
    <div>
        <h1>SKF Observer Phoenix</h1>
        <div class="sub">Sistema de Monitoramento de Pontos Rotativos</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Sem conexão ──────────────────────────────
if not st.session_state.token:
    st.markdown("""
    <div class="alert-info">
        ⟶  Configure as credenciais na barra lateral e clique em <strong>Conectar</strong> para iniciar.
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="label">Passo 1</div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:1.1rem;font-weight:600;color:#e6edf3;margin-top:6px;">
                🔌 Conectar API
            </div>
            <div style="font-size:0.82rem;color:#8b949e;margin-top:8px;">
                Informe a URL do servidor Observer Phoenix e suas credenciais.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="label">Passo 2</div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:1.1rem;font-weight:600;color:#e6edf3;margin-top:6px;">
                🏭 Selecionar Asset
            </div>
            <div style="font-size:0.82rem;color:#8b949e;margin-top:8px;">
                Escolha a máquina (equipamento) que deseja monitorar.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="label">Passo 3</div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:1.1rem;font-weight:600;color:#e6edf3;margin-top:6px;">
                📈 Visualizar Tendência
            </div>
            <div style="font-size:0.82rem;color:#8b949e;margin-top:8px;">
                Selecione um ponto de medição e explore o gráfico interativo.
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────────
# ASSETS
# ─────────────────────────────────────────────
assets = st.session_state.assets

st.markdown('<div class="section-title">Assets — Máquinas Cadastradas</div>', unsafe_allow_html=True)

# Tabela de assets
rows_html = ""
for a in assets:
    badge = status_badge(a.get("Status", []))
    rows_html += f"""
    <tr>
        <td><span class="id-chip">{a['ID']}</span></td>
        <td><strong>{a['Name']}</strong></td>
        <td style="font-size:0.82rem;color:#8b949e;">{a.get('Description','—')}</td>
        <td style="font-size:0.78rem;font-family:'Share Tech Mono',monospace;color:#484f58;">{a.get('Path','—')}</td>
        <td>{badge}</td>
    </tr>"""

st.markdown(f"""
<table class="data-table">
    <thead><tr>
        <th>ID</th><th>Nome</th><th>Descrição</th><th>Path</th><th>Status</th>
    </tr></thead>
    <tbody>{rows_html}</tbody>
</table>
""", unsafe_allow_html=True)

# Seleção de asset
st.markdown("<br>", unsafe_allow_html=True)
col_sel, col_btn = st.columns([3, 1])
with col_sel:
    asset_options = {f"[{a['ID']}]  {a['Name']}": a for a in assets}
    chosen_asset_label = st.selectbox(
        "Selecionar Asset",
        options=list(asset_options.keys()),
        index=0,
        label_visibility="visible",
    )
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    load_points = st.button("⟶  Carregar Points", use_container_width=True)

if load_points:
    selected_asset = asset_options[chosen_asset_label]
    st.session_state.selected_asset = selected_asset
    st.session_state.trend_df       = None
    st.session_state.spectrum_data  = None
    st.session_state.selected_point = None
    with st.spinner(f"Carregando points de [{selected_asset['ID']}] {selected_asset['Name']}..."):
        try:
            pts = get_points(st.session_state.base_url, st.session_state.token, selected_asset["ID"])
            st.session_state.points = pts
        except Exception as e:
            st.error(f"Erro ao carregar points: {e}")

# ─────────────────────────────────────────────
# POINTS
# ─────────────────────────────────────────────
if st.session_state.points:
    points = st.session_state.points
    asset  = st.session_state.selected_asset

    st.markdown(f'<div class="section-title">Points — {asset["Name"]}</div>', unsafe_allow_html=True)

    # Cards de resumo
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="label">Total de Points</div>
            <div class="value">{len(points)}</div>
            <div class="unit">pontos de medição</div>
        </div>
        <div class="metric-card ok">
            <div class="label">Asset ID</div>
            <div class="value">{asset['ID']}</div>
            <div class="unit">{asset['Name']}</div>
        </div>
        <div class="metric-card">
            <div class="label">Status</div>
            <div class="value" style="font-size:1.2rem;margin-top:4px;">
                {"✅ OK" if not asset.get("Status") or asset["Status"][0]==0 else "⚠ Alerta"}
            </div>
            <div class="unit">{asset.get('Path','')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tabela de points
    rows_html = ""
    for p in points:
        unit  = p.get("unit",  p.get("Unit",  "—"))
        ptype = p.get("type",  p.get("Type",  "—"))
        pname = p.get("name",  p.get("Name",  "—"))
        pid   = p.get("id",    p.get("ID",    "—"))
        rows_html += f"""
        <tr>
            <td><span class="id-chip">{pid}</span></td>
            <td><strong>{pname}</strong></td>
            <td style="font-size:0.82rem;color:#8b949e;">{ptype}</td>
            <td style="font-family:'Share Tech Mono',monospace;font-size:0.8rem;color:#00d9ff;">{unit}</td>
        </tr>"""

    st.markdown(f"""
    <table class="data-table">
        <thead><tr><th>ID</th><th>Nome do Point</th><th>Tipo</th><th>Unidade</th></tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)

    # Seleção de point
    st.markdown("<br>", unsafe_allow_html=True)
    col_pt, col_btn2, col_btn3 = st.columns([3, 1, 1])
    point_opts = {f"[{p.get('id',p.get('ID'))}]  {p.get('name',p.get('Name','?'))}": p for p in points}

    with col_pt:
        chosen_point_label = st.selectbox(
            "Selecionar Point",
            options=list(point_opts.keys()),
            label_visibility="visible",
        )
    with col_btn2:
        st.markdown("<br>", unsafe_allow_html=True)
        load_trend = st.button("📈  Carregar Tendência", use_container_width=True)
    with col_btn3:
        st.markdown("<br>", unsafe_allow_html=True)
        load_spectrum = st.button("〜  Carregar Espectro", use_container_width=True)

    if load_trend:
        pt = point_opts[chosen_point_label]
        st.session_state.selected_point = pt
        st.session_state.spectrum_data  = None
        pid = pt.get("id", pt.get("ID"))

        from_dt = st.session_state.get("date_from")
        to_dt   = st.session_state.get("date_to")
        max_r   = st.session_state.get("max_read", 500)
        from_str = f"{from_dt}T00:00:00Z" if from_dt else None
        to_str   = f"{to_dt}T23:59:59Z"   if to_dt   else None

        with st.spinner(f"Buscando dados de tendência para point [{pid}]..."):
            try:
                raw = get_trend(st.session_state.base_url, st.session_state.token,
                                pid, from_str, to_str, max_r)
                df  = parse_trend(raw)
                st.session_state.trend_df = df
            except Exception as e:
                st.error(f"Erro ao buscar trend: {e}")

    if load_spectrum:
        pt = point_opts[chosen_point_label]
        st.session_state.selected_point = pt
        pid = pt.get("id", pt.get("ID"))

        with st.spinner(f"Buscando espectro de vibração para point [{pid}]..."):
            try:
                raw_spec = get_spectrum(st.session_state.base_url, st.session_state.token, pid)
                channels_spec = parse_spectrum(raw_spec)
                st.session_state.spectrum_data = channels_spec
                if not channels_spec:
                    st.warning("⚠ Nenhum dado de espectro disponível para este ponto.")
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    st.warning("⚠ Este ponto não possui medições dinâmicas (espectro) disponíveis.")
                else:
                    st.error(f"Erro HTTP ao buscar espectro: {e}")
            except Exception as e:
                st.error(f"Erro ao buscar espectro: {e}")


# ─────────────────────────────────────────────
# TREND PLOT
# ─────────────────────────────────────────────
if st.session_state.trend_df is not None:
    df_all = st.session_state.trend_df
    point  = st.session_state.selected_point
    asset  = st.session_state.selected_asset

    pname = point.get("name", point.get("Name", "—"))
    pid   = point.get("id",   point.get("ID",   "—"))

    st.markdown(f'<div class="section-title">Tendência — {pname}</div>', unsafe_allow_html=True)

    if df_all.empty:
        st.markdown("""
        <div class="alert-warn">⚠ Nenhuma leitura encontrada para o período selecionado.</div>
        """, unsafe_allow_html=True)
    else:
        # ── Seletor de canal (quando há múltiplos channels) ─────────
        channel_opts = get_channel_options(df_all)

        if len(channel_opts) > 1:
            chosen_ch_label = st.selectbox(
                "Canal de medição",
                options=list(channel_opts.keys()),
                label_visibility="visible",
            )
            selected_ch = channel_opts[chosen_ch_label]
        else:
            selected_ch = list(channel_opts.values())[0] if channel_opts else 1

        # Filtra pelo canal selecionado
        df = df_all[df_all["channel"] == selected_ch].copy()

        unit         = df["unit"].iloc[-1]         if not df.empty else ""
        channel_name = df["channel_name"].iloc[-1]  if not df.empty else "Overall"
        direction    = df["direction"].iloc[-1]      if not df.empty else ""

        # ── Estatísticas ─────────────────────────
        media   = df["value"].mean()
        desvio  = df["value"].std()
        vmin    = df["value"].min()
        vmax    = df["value"].max()
        vlast   = df["value"].iloc[-1]
        l_alert = media + 2 * desvio
        l_alarm = media + 3 * desvio

        in_alarm   = vlast >= l_alarm
        in_alert   = vlast >= l_alert and not in_alarm
        card_class = "danger" if in_alarm else ("warn" if in_alert else "ok")

        # Velocidade e processo (se disponíveis)
        has_speed = "speed" in df.columns and df["speed"].notna().any()
        speed_last = df["speed"].iloc[-1] if has_speed else None

        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-card {card_class}">
                <div class="label">Última Leitura</div>
                <div class="value">{vlast:.4f}</div>
                <div class="unit">{unit}  ·  {df['timestamp'].iloc[-1].strftime('%d/%m/%Y %H:%M')}</div>
            </div>
            <div class="metric-card">
                <div class="label">Média</div>
                <div class="value">{media:.4f}</div>
                <div class="unit">{unit}</div>
            </div>
            <div class="metric-card">
                <div class="label">Desvio Padrão</div>
                <div class="value">{desvio:.4f}</div>
                <div class="unit">σ</div>
            </div>
            <div class="metric-card">
                <div class="label">Mínimo / Máximo</div>
                <div class="value">{vmin:.3f}</div>
                <div class="unit">min  ·  máx  {vmax:.3f} {unit}</div>
            </div>
            <div class="metric-card">
                <div class="label">Leituras</div>
                <div class="value">{len(df)}</div>
                <div class="unit">pontos no período</div>
            </div>
            <div class="metric-card">
                <div class="label">Velocidade (última)</div>
                <div class="value">{speed_last:.1f}</div>
                <div class="unit">RPM</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if in_alarm:
            st.markdown(f'<div class="alert-danger">🚨 ALARME — Leitura atual ({vlast:.4f} {unit}) ultrapassa μ+3σ ({l_alarm:.4f})</div>',
                        unsafe_allow_html=True)
        elif in_alert:
            st.markdown(f'<div class="alert-warn">⚠ ALERTA — Leitura atual ({vlast:.4f} {unit}) ultrapassa μ+2σ ({l_alert:.4f})</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alert-ok">✔ NORMAL — Leitura dentro dos limites esperados.</div>',
                        unsafe_allow_html=True)

        # ── Plotly Chart ──────────────────────────
        ch_title = f"{channel_name}"
        if direction:
            ch_title += f" [{direction}]"

        fig = go.Figure()

        # Área sombreada
        fig.add_trace(go.Scatter(
            x=df["timestamp"], y=df["value"],
            fill="tozeroy",
            fillcolor="rgba(0,217,255,0.04)",
            line=dict(color="rgba(0,0,0,0)"),
            showlegend=False, hoverinfo="skip",
        ))

        # Banda ±1σ
        fig.add_trace(go.Scatter(
            x=pd.concat([df["timestamp"], df["timestamp"][::-1]]),
            y=pd.concat([
                pd.Series([media + desvio] * len(df)),
                pd.Series([media - desvio] * len(df))[::-1],
            ]),
            fill="toself",
            fillcolor="rgba(46,213,115,0.05)",
            line=dict(color="rgba(0,0,0,0)"),
            name="±1σ (normal)",
            hoverinfo="skip",
        ))

        # Linha principal de leitura
        fig.add_trace(go.Scatter(
            x=df["timestamp"], y=df["value"],
            mode="lines+markers",
            name=f"{ch_title}",
            line=dict(color="#00d9ff", width=2),
            marker=dict(size=5, color="#00d9ff", opacity=0.8),
            hovertemplate=(
                "<b>%{x|%d/%m/%Y %H:%M:%S}</b><br>"
                f"<b>{ch_title}:</b> %{{y:.4f}} {unit}<extra></extra>"
            ),
        ))

        # Linha de velocidade (eixo secundário, se disponível)
        if has_speed and df["speed"].notna().any():
            fig.add_trace(go.Scatter(
                x=df["timestamp"], y=df["speed"],
                mode="lines",
                name="Velocidade (RPM)",
                line=dict(color="#a855f7", width=1, dash="dot"),
                yaxis="y2",
                hovertemplate="<b>Velocidade:</b> %{y:.1f} RPM<extra></extra>",
                opacity=0.7,
            ))

        # Linhas de referência
        fig.add_hline(y=media, line=dict(color="#2ed573", width=1.5, dash="dash"),
                      annotation_text=f"Média  {media:.4f}", annotation_font_color="#2ed573",
                      annotation_position="top right")
        fig.add_hline(y=l_alert, line=dict(color="#f0a500", width=1.2, dash="dot"),
                      annotation_text=f"Alerta  {l_alert:.4f}", annotation_font_color="#f0a500",
                      annotation_position="top right")
        fig.add_hline(y=l_alarm, line=dict(color="#ff4757", width=1.2, dash="dot"),
                      annotation_text=f"Alarme  {l_alarm:.4f}", annotation_font_color="#ff4757",
                      annotation_position="top right")

        layout_extra = {}
        if has_speed:
            layout_extra["yaxis2"] = dict(
                title=dict(text="Velocidade [RPM]", font=dict(color="#a855f7", size=10)),
                overlaying="y", side="right",
                gridcolor="rgba(0,0,0,0)",
                tickfont=dict(family="Share Tech Mono, monospace", size=9, color="#a855f7"),
            )

        fig.update_layout(
            paper_bgcolor="#090c10",
            plot_bgcolor="#0d1117",
            font=dict(family="Exo 2, sans-serif", color="#8b949e", size=11),
            title=dict(
                text=f"<b>{pname}</b>  ·  {asset['Name']}  ·  <span style='color:#00d9ff'>{ch_title}</span>",
                font=dict(family="Rajdhani, sans-serif", size=18, color="#e6edf3"),
                x=0.01,
            ),
            xaxis=dict(
                gridcolor="#21262d", zeroline=False,
                tickfont=dict(family="Share Tech Mono, monospace", size=10, color="#8b949e"),
                title=dict(text="Data / Hora (UTC)", font=dict(color="#8b949e", size=11)),
                rangeslider=dict(visible=True, bgcolor="#0d1117", thickness=0.06),
            ),
            yaxis=dict(
                gridcolor="#21262d", zeroline=False,
                tickfont=dict(family="Share Tech Mono, monospace", size=10, color="#8b949e"),
                title=dict(text=f"{ch_title}  [{unit}]", font=dict(color="#8b949e", size=11)),
            ),
            legend=dict(
                bgcolor="rgba(13,17,23,0.8)", bordercolor="#21262d", borderwidth=1,
                font=dict(family="Exo 2, sans-serif", size=11, color="#c9d1d9"),
                orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0,
            ),
            hovermode="x unified",
            margin=dict(l=60, r=60, t=70, b=60),
            height=500,
            **layout_extra,
        )

        st.plotly_chart(fig, use_container_width=True)

        # ── Tabela de dados brutos ───────────────
        with st.expander("🗃  Ver dados brutos"):
            df_show = df[["timestamp", "value", "unit", "channel_name",
                          "direction", "speed", "process"]].copy()
            df_show["timestamp"] = df_show["timestamp"].dt.strftime("%d/%m/%Y %H:%M:%S")
            df_show.columns = [
                "Data/Hora (UTC)", "Level", "Unidade",
                "Canal", "Direção", "Velocidade (RPM)", "Processo",
            ]
            st.dataframe(df_show, use_container_width=True, hide_index=True, height=300)

            csv = df_show.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇  Exportar CSV",
                data=csv,
                file_name=f"trend_{pid}_ch{selected_ch}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )


# ─────────────────────────────────────────────
# SPECTRUM PLOT
# ─────────────────────────────────────────────
if st.session_state.spectrum_data:
    channels_spec = st.session_state.spectrum_data
    point  = st.session_state.selected_point
    pname  = point.get("name", point.get("Name", "—")) if point else "—"
    pid    = point.get("id",   point.get("ID",   "—")) if point else "—"

    st.markdown(f'<div class="section-title">Espectro de Vibração — {pname}</div>',
                unsafe_allow_html=True)

    # ── Info cards do espectro ──────────────────
    first = channels_spec[0]
    speed_val = first.get("speed", 0.0)
    n_ch = len(channels_spec)

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="label">Canais</div>
            <div class="value">{n_ch}</div>
            <div class="unit">direções medidas</div>
        </div>
        <div class="metric-card">
            <div class="label">Faixa de Frequência</div>
            <div class="value">{first['end_freq']:.0f}</div>
            <div class="unit">{first['start_freq']:.0f} – {first['end_freq']:.0f} Hz</div>
        </div>
        <div class="metric-card">
            <div class="label">Taxa de Amostragem</div>
            <div class="value">{first['sample_rate']:.0f}</div>
            <div class="unit">Hz · {first['samples']} amostras</div>
        </div>
        <div class="metric-card">
            <div class="label">Unidade</div>
            <div class="value" style="font-size:1.3rem;margin-top:6px;">{first['eu']}</div>
            <div class="unit">amplitude</div>
        </div>
        {"" if speed_val == 0.0 else f'''
        <div class="metric-card">
            <div class="label">Velocidade</div>
            <div class="value">{speed_val:.1f}</div>
            <div class="unit">{first["speed_units"]}</div>
        </div>'''}
    </div>
    """, unsafe_allow_html=True)

    # ── Seletor de canal (se múltiplos) ────────
    DIRECTION_MAP = {0: "X", 1: "Y", 2: "Z", 3: "H", 4: "V", 5: "A", -1: "—"}
    MTYPE_MAP     = {0: "Waveform", 1: "Espectro (velocidade)", 2: "Espectro", 3: "Cepstrum"}

    ch_labels = []
    for i, ch in enumerate(channels_spec):
        dir_str  = DIRECTION_MAP.get(ch["direction"], str(ch["direction"]))
        mtype_str = MTYPE_MAP.get(ch["mtype"], f"Tipo {ch['mtype']}")
        ch_labels.append(f"Canal {i+1}  [{dir_str}]  — {mtype_str}")

    if len(ch_labels) > 1:
        sel_ch_label = st.selectbox("Canal do espectro", options=ch_labels, key="spec_ch_sel")
        sel_ch_idx = ch_labels.index(sel_ch_label)
    else:
        sel_ch_idx = 0

    ch = channels_spec[sel_ch_idx]
    freqs  = ch["freqs"]
    values = ch["values"]
    eu     = ch["eu"]
    dir_str = DIRECTION_MAP.get(ch["direction"], str(ch["direction"]))

    # ── Picos principais (top 10) ───────────────
    peak_indices = np.argsort(values)[::-1][:10]
    peak_freqs   = freqs[peak_indices]
    peak_vals    = values[peak_indices]

    # ── Frequência de rotação (1X, 2X, 3X) ──────
    harmonic_lines = []
    if speed_val and speed_val > 0:
        rpm_hz = speed_val / 60.0
        for h in range(1, 6):
            hf = rpm_hz * h
            if ch["start_freq"] <= hf <= ch["end_freq"]:
                harmonic_lines.append((hf, f"{h}X  {hf:.1f} Hz"))

    # ── Plotly ──────────────────────────────────
    fig_spec = go.Figure()

    # Área preenchida sob o espectro
    fig_spec.add_trace(go.Scatter(
        x=freqs, y=values,
        fill="tozeroy",
        fillcolor="rgba(0,217,255,0.06)",
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=False, hoverinfo="skip",
    ))

    # Linha do espectro
    fig_spec.add_trace(go.Scatter(
        x=freqs, y=values,
        mode="lines",
        name=f"Espectro [{dir_str}]",
        line=dict(color="#00d9ff", width=1.5),
        hovertemplate="<b>%{x:.2f} Hz</b><br>%{y:.4f} " + eu + "<extra></extra>",
    ))

    # Marcadores de picos
    fig_spec.add_trace(go.Scatter(
        x=peak_freqs, y=peak_vals,
        mode="markers+text",
        name="Picos",
        marker=dict(size=8, color="#f0a500", symbol="triangle-up",
                    line=dict(color="#f0a500", width=1)),
        text=[f"{f:.1f}" for f in peak_freqs],
        textposition="top center",
        textfont=dict(family="Share Tech Mono, monospace", size=9, color="#f0a500"),
        hovertemplate="<b>%{x:.2f} Hz</b><br>%{y:.5f} " + eu + "<extra>Pico</extra>",
    ))

    # Linhas harmônicas de rotação
    for hf, hlabel in harmonic_lines:
        fig_spec.add_vline(
            x=hf,
            line=dict(color="rgba(168,85,247,0.6)", width=1, dash="dot"),
            annotation_text=hlabel,
            annotation_font=dict(family="Share Tech Mono, monospace", size=9, color="#a855f7"),
            annotation_position="top",
        )

    fig_spec.update_layout(
        paper_bgcolor="#090c10",
        plot_bgcolor="#0d1117",
        font=dict(family="Exo 2, sans-serif", color="#8b949e", size=11),
        title=dict(
            text=(f"<b>{pname}</b>  ·  Espectro  ·  "
                  f"<span style='color:#00d9ff'>Direção {dir_str}</span>  ·  "
                  f"<span style='color:#8b949e'>{eu}</span>"),
            font=dict(family="Rajdhani, sans-serif", size=18, color="#e6edf3"),
            x=0.01,
        ),
        xaxis=dict(
            gridcolor="#21262d", zeroline=False,
            tickfont=dict(family="Share Tech Mono, monospace", size=10, color="#8b949e"),
            title=dict(text="Frequência [Hz]", font=dict(color="#8b949e", size=11)),
            rangeslider=dict(visible=True, bgcolor="#0d1117", thickness=0.06),
        ),
        yaxis=dict(
            gridcolor="#21262d", zeroline=False,
            tickfont=dict(family="Share Tech Mono, monospace", size=10, color="#8b949e"),
            title=dict(text=f"Amplitude  [{eu}]", font=dict(color="#8b949e", size=11)),
        ),
        legend=dict(
            bgcolor="rgba(13,17,23,0.8)", bordercolor="#21262d", borderwidth=1,
            font=dict(family="Exo 2, sans-serif", size=11, color="#c9d1d9"),
            orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0,
        ),
        hovermode="x",
        margin=dict(l=60, r=40, t=70, b=60),
        height=450,
    )

    st.plotly_chart(fig_spec, use_container_width=True)

    # ── Tabela de picos ──────────────────────────
    with st.expander("📊  Top 10 picos do espectro"):
        df_peaks = pd.DataFrame({
            "Frequência (Hz)": [f"{f:.3f}" for f in peak_freqs],
            f"Amplitude ({eu})": [f"{v:.5f}" for v in peak_vals],
            "Rank": [f"#{i+1}" for i in range(len(peak_freqs))],
        })
        st.dataframe(df_peaks, use_container_width=True, hide_index=True)

        csv_spec = df_peaks.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇  Exportar picos CSV",
            data=csv_spec,
            file_name=f"spectrum_peaks_{pid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )

    # ── Exportar espectro completo ───────────────
    with st.expander("🗃  Ver espectro completo (dados brutos)"):
        df_full_spec = pd.DataFrame({
            "Frequência (Hz)": np.round(freqs, 4),
            f"Amplitude ({eu})": np.round(values, 6),
        })
        st.dataframe(df_full_spec, use_container_width=True, hide_index=True, height=300)

        csv_full = df_full_spec.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇  Exportar espectro completo CSV",
            data=csv_full,
            file_name=f"spectrum_full_{pid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )
