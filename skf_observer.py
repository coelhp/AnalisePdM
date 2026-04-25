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
# CSS GLOBAL — LDC Brand Theme
# ─────────────────────────────────────────────
# Paleta principal LDC
#   --accent  : LDC Blue    #32556E  (tom de comando, destaque primário)
#   --accent2 : #007CAA     (azul vivo — hover, links)
#   --accent3 : #A7C5E2     (azul claro — fills suaves)
#   --ok      : LDC Green   #4E9D2D  (sucesso / normal)
#   --ok-deep : #247F3B     (verde escuro — ênfase de sucesso)
#   --warn    : #BA944B     (âmbar LDC — alertas)
#   --danger  : #F06A22     (laranja LDC — crítico)
#   --teal    : #379A8D     (saúde / secundário)
#   --bg-base : derivado do LDC Blue escurecido
#   --grey    : LDC Grey    #5C6670
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&family=Exo+2:wght@300;400;600&display=swap');

:root {
    /* ── Backgrounds ── */
    --bg-base:      #0e1820;        /* LDC Blue escurecido */
    --bg-card:      #162130;        /* card principal */
    --bg-panel:     #1c2b3a;        /* painéis internos */

    /* ── Bordas ── */
    --border:       #2a3f52;
    --border-glow:  #32556E;

    /* ── Paleta LDC ── */
    --accent:       #A7C5E2;        /* LDC Blue claro — destaque primário */
    --accent-solid: #32556E;        /* LDC Blue sólido */
    --accent-deep:  #007CAA;        /* azul vivo — hover */
    --accent-glow:  rgba(50,85,110,0.25);

    --ok:           #4E9D2D;        /* LDC Green */
    --ok-deep:      #247F3B;        /* verde escuro */
    --ok-light:     #B9C966;        /* verde claro */

    --warn:         #BA944B;        /* âmbar */
    --warn-light:   #CEC4B0;

    --danger:       #F06A22;        /* laranja crítico */
    --danger-deep:  #504937;

    --teal:         #379A8D;        /* teal — saúde/info */
    --teal-light:   #98C0B8;

    --grey:         #5C6670;        /* LDC Grey */
    --purple:       #5E699E;        /* eixo secundário */

    /* ── Texto ── */
    --text-hi:      #EEF4F9;
    --text-mid:     #98C0B8;
    --text-lo:      #4a5a6a;

    /* ── Tipografia ── */
    --font-head:    'Rajdhani', sans-serif;
    --font-mono:    'Share Tech Mono', monospace;
    --font-body:    'Exo 2', sans-serif;
}

/* ── Base ──────────────────────────────────── */
html, body, [class*="css"] {
    font-family: var(--font-body) !important;
    background-color: var(--bg-base) !important;
    color: var(--text-hi) !important;
}

#MainMenu, footer, header { visibility: hidden; }

/* ── Sidebar ─────────────────────────────── */
section[data-testid="stSidebar"] {
    background: var(--bg-card) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * {
    font-family: var(--font-body) !important;
}

/* ── Header banner ────────────────────────── */
.top-banner {
    background: linear-gradient(135deg, #0e1820 0%, #1c2b3a 50%, #0e1820 100%);
    border-bottom: 2px solid var(--accent-solid);
    box-shadow: 0 4px 24px rgba(50,85,110,0.35);
    padding: 18px 32px;
    margin: -1rem -1rem 2rem -1rem;
    display: flex;
    align-items: center;
    gap: 18px;
}
.top-banner .logo-box {
    width: 48px; height: 48px;
    background: var(--accent-solid);
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

/* ── Metric cards ─────────────────────────── */
.metric-row { display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }

.metric-card {
    flex: 1; min-width: 150px;
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-top: 3px solid var(--accent-solid);
    border-radius: 8px;
    padding: 16px 20px;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    opacity: 0.4;
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

/* Card — estados semânticos */
.metric-card.ok     { border-top-color: var(--ok); }
.metric-card.ok     .value { color: var(--ok); }

.metric-card.warn   { border-top-color: var(--warn); }
.metric-card.warn   .value { color: var(--warn); }

.metric-card.danger { border-top-color: var(--danger); }
.metric-card.danger .value { color: var(--danger); }

.metric-card.teal   { border-top-color: var(--teal); }
.metric-card.teal   .value { color: var(--teal); }

/* ── Badges ───────────────────────────────── */
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
.badge-ok      { background: rgba(78,157,45,0.15);   color: var(--ok);      border: 1px solid rgba(78,157,45,0.35); }
.badge-warn    { background: rgba(186,148,75,0.15);  color: var(--warn);    border: 1px solid rgba(186,148,75,0.35); }
.badge-danger  { background: rgba(240,106,34,0.15);  color: var(--danger);  border: 1px solid rgba(240,106,34,0.35); }
.badge-offline { background: rgba(92,102,112,0.15);  color: var(--grey);    border: 1px solid rgba(92,102,112,0.3); }

/* ── Section titles ───────────────────────── */
.section-title {
    font-family: var(--font-head);
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--teal-light);
    border-left: 3px solid var(--accent-solid);
    padding-left: 10px;
    margin: 24px 0 14px 0;
}

/* ── Tabelas ──────────────────────────────── */
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
.data-table tr:hover td { background: rgba(50,85,110,0.12); }

.id-chip {
    font-family: var(--font-mono);
    font-size: 0.78rem;
    color: var(--accent);
    background: rgba(50,85,110,0.2);
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid rgba(167,197,226,0.25);
}

/* ── Inputs / Selects ─────────────────────── */
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
    border-color: var(--accent-deep) !important;
    box-shadow: 0 0 0 2px var(--accent-glow) !important;
}

/* ── Botões ───────────────────────────────── */
.stButton > button {
    background: transparent !important;
    border: 1px solid var(--accent-solid) !important;
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
    border-color: var(--accent-deep) !important;
    box-shadow: 0 0 16px var(--accent-glow) !important;
}
.stButton > button[kind="primary"] {
    background: var(--accent-solid) !important;
    border-color: var(--accent-solid) !important;
    color: #EEF4F9 !important;
}
.stButton > button[kind="primary"]:hover {
    background: var(--accent-deep) !important;
    border-color: var(--accent-deep) !important;
}

/* ── Expander ─────────────────────────────── */
.streamlit-expanderHeader {
    background: var(--bg-panel) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    font-family: var(--font-head) !important;
    color: var(--text-hi) !important;
}

/* ── Sidebar labels ───────────────────────── */
.sidebar-label {
    font-family: var(--font-mono);
    font-size: 0.68rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text-mid);
    margin-bottom: 4px;
}

/* ── Divider ──────────────────────────────── */
.hline {
    border: none;
    border-top: 1px solid var(--border);
    margin: 20px 0;
}

/* ── Alert boxes ──────────────────────────── */
.alert-box {
    padding: 12px 16px;
    border-radius: 6px;
    font-family: var(--font-body);
    font-size: 0.88rem;
    margin: 12px 0;
}
.alert-warn   { background: rgba(186,148,75,0.1);   border-left: 3px solid var(--warn);    color: #CEC4B0; }
.alert-danger { background: rgba(240,106,34,0.12);  border-left: 3px solid var(--danger);  color: #F06A22; }
.alert-info   { background: rgba(55,154,141,0.1);   border-left: 3px solid var(--teal);    color: var(--teal-light); }
.alert-ok     { background: rgba(78,157,45,0.1);    border-left: 3px solid var(--ok);      color: var(--ok-light); }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
for key, default in {
    "token":          None,
    "token_ts":       None,
    "assets":         [],
    "points":         [],
    "trend_df":       None,
    "spectrum_data":  None,
    "selected_asset": None,
    "selected_point": None,
    "imx_df":         None,
    "imx_log":        [],
    "fleet_data":     None,
    "fleet_log":      [],
    "username":       "patrick.coelho",
    "_password":      "",
    "selected_unit":  None,
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
        params={"machine_id": machine_id},
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
    """GET /v1/points/{pointId}/dynamicMeasurements — retorna última medição dinâmica (espectro)."""
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
# IMx-1 SCAN — HELPERS DE API
# ─────────────────────────────────────────────

# NodeTypes que identificam sensores IMx-1
IMX1_NODE_TYPES = {11101, 11102, 11103, 11104}
# NodeType do ponto de temperatura (prioridade máxima)
IMX1_TEMP_NODE_TYPE = 11104
# EUType do ponto de temperatura
IMX1_TEMP_EU_TYPE = 10905
# Data de corte para varredura
IMX1_FROM_DATE = "2024-05-01T00:00:00"


def _ensure_token(base_url: str, username: str, password: str) -> str:
    """
    Retorna o token atual. Renova automaticamente se tiver mais de 18 minutos.
    """
    import time
    now = time.time()
    ts  = st.session_state.get("token_ts") or 0
    if st.session_state.token and (now - ts) < 18 * 60:
        return st.session_state.token
    token = autenticar(base_url, username, password)
    st.session_state.token    = token
    st.session_state.token_ts = now
    return token


def get_points_v1(base_url: str, token: str, machine_id) -> list:
    """GET /v1/machines/{machineId}/points — retorna points com NodeType."""
    resp = requests.get(
        f"{base_url}/v1/machines/{machine_id}/points",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        timeout=15,
    )
    if resp.status_code in (204, 404):
        return []
    resp.raise_for_status()
    data = resp.json()
    return data if isinstance(data, list) else []


def get_trend_first_reading(base_url: str, token: str, point_id) -> dict | None:
    """
    GET /v1/points/{pointId}/trendMeasurements — retorna APENAS a primeira
    leitura a partir de 01/05/2024 (descending=false, numReadings=1).
    """
    resp = requests.get(
        f"{base_url}/v1/points/{point_id}/trendMeasurements",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        params={
            "fromDateUTC":  IMX1_FROM_DATE,
            "descending":   "false",
            "numReadings":  1,
        },
        timeout=15,
    )
    if resp.status_code in (204, 404):
        return None
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, list) and data:
        return data[0]
    if isinstance(data, dict):
        return data
    return None


def get_imx_sensors(base_url: str, token: str) -> dict:
    """
    GET /v1/nextgensensor — retorna dict {IDNode: {...}} apenas para sensores
    comissionados (Commissioned == 1), ou seja, instalados e ativos em campo.
    """
    resp = requests.get(
        f"{base_url}/v1/nextgensensor",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        timeout=15,
    )
    if resp.status_code in (204, 404):
        return {}
    resp.raise_for_status()
    data = resp.json()
    sensors = data if isinstance(data, list) else data.get("value", data.get("items", []))
    index = {}
    for s in (sensors if isinstance(sensors, list) else []):
        # Ignora sensores não comissionados (Commissioned = 0 ou ausente)
        commissioned = s.get("Commissioned") if s.get("Commissioned") is not None \
                       else s.get("commissioned")
        if not commissioned:
            continue
        nid = s.get("IDNode") or s.get("idNode") or s.get("NodeID")
        if nid is not None:
            index[int(nid)] = s
    return index


def run_imx_scan(base_url: str, username: str, password: str,
                 progress_cb=None, log_cb=None) -> pd.DataFrame:
    """
    Varredura completa de sensores IMx-1:
      1. Lista todos os assets
      2. Para cada asset, lista points via v1 e filtra NodeType IMx-1
      3. Prioriza ponto de temperatura; usa qualquer IMx-1 se não houver
      4. Busca primeira leitura de tendência (≥ 01/05/2024)
      5. Cruza com /v1/nextgensensor para Hardware ID e bateria
      6. Monta DataFrame final com colunas de BI
    """
    import time

    def log(msg: str):
        if log_cb:
            log_cb(msg)

    def prog(val: float, text: str = ""):
        if progress_cb:
            progress_cb(val, text)

    today = datetime.now(timezone.utc)
    rows  = []

    # ── 1. Token inicial ──────────────────────────
    token = _ensure_token(base_url, username, password)
    log("🔑 Token obtido.")

    # ── 2. Assets ────────────────────────────────
    assets_list = get_assets(base_url, token)
    total = len(assets_list)
    log(f"🏭 {total} asset(s) encontrado(s).")
    prog(0.02, f"0 / {total} assets processados")

    # ── 3. Sensores IMx (metadados) ───────────────
    token = _ensure_token(base_url, username, password)
    try:
        sensor_index = get_imx_sensors(base_url, token)
        log(f"📡 {len(sensor_index)} sensor(es) IMx comissionados indexados.")
    except Exception as e:
        sensor_index = {}
        log(f"⚠ /v1/nextgensensor indisponível: {e}")

    # ── 4. Iterar assets → points → trend ────────
    for i, asset in enumerate(assets_list):
        machine_id   = asset.get("ID") or asset.get("id")
        machine_name = asset.get("Name") or asset.get("name", "—")
        sys_created  = asset.get("SystemCreatedDate") or asset.get("Created") or ""

        token = _ensure_token(base_url, username, password)

        try:
            points_v1 = get_points_v1(base_url, token, machine_id)
        except Exception as e:
            log(f"  ↳ [{machine_id}] {machine_name}: erro ao listar points — {e}")
            time.sleep(0.1)
            continue

        # Filtra apenas pontos IMx-1
        imx_points = [
            p for p in points_v1
            if int(p.get("NodeType", 0)) in IMX1_NODE_TYPES
        ]

        if not imx_points:
            prog((i + 1) / total, f"{i+1} / {total}: {machine_name} — sem IMx-1")
            time.sleep(0.05)
            continue

        # ── Agrupa points por IDNode (= sensor físico) ───────────────
        # Cada IDNode representa um sensor distinto instalado na máquina.
        # Um mesmo sensor pode ter múltiplos points (vibração, temperatura, etc.).
        nodes: dict[int, list] = {}
        for p in imx_points:
            nid = (
                p.get("ParentID")
                or p.get("IDNode")
                or p.get("NodeID")
            )
            try:
                nid = int(nid)
            except (TypeError, ValueError):
                nid = None
            if nid is None:
                continue
            nodes.setdefault(nid, []).append(p)

        if not nodes:
            prog((i + 1) / total, f"{i+1} / {total}: {machine_name} — IDNode indisponível")
            time.sleep(0.05)
            continue

        log(f"  ↳ [{machine_id}] {machine_name}: {len(nodes)} sensor(es) IMx-1")

        # ── Itera cada sensor (IDNode) individualmente ───────────────
        for id_node, node_points in nodes.items():

            # Pula sensores não comissionados — se o IDNode não consta no
            # sensor_index, foi filtrado por Commissioned == 0
            if id_node not in sensor_index:
                log(f"    ⊘ IDNode {id_node} — não comissionado, ignorado.")
                continue

            # Escolhe o melhor point para buscar a 1ª leitura:
            # prioridade: temperatura (NodeType 11104 / EUType 10905),
            # depois qualquer outro ponto IMx-1 do nó.
            temp_points = [
                p for p in node_points
                if int(p.get("NodeType", 0)) == IMX1_TEMP_NODE_TYPE
                or int(p.get("EUType",   0)) == IMX1_TEMP_EU_TYPE
            ]
            target_point = temp_points[0] if temp_points else node_points[0]
            point_id     = (
                target_point.get("ID")
                or target_point.get("id")
                or target_point.get("PointID")
            )

            log(f"    · IDNode {id_node} — point {point_id} "
                f"(NodeType {target_point.get('NodeType')}, {len(node_points)} point(s) no nó)")

            # Busca primeira leitura
            token = _ensure_token(base_url, username, password)
            try:
                first = get_trend_first_reading(base_url, token, point_id)
            except Exception as e:
                log(f"      ⚠ trend error: {e}")
                first = None
            time.sleep(0.15)

            if first is None:
                commissioning_dt = None
            else:
                ts_raw = (
                    first.get("ReadingTimeUTC")
                    or first.get("readingTimeUTC")
                    or first.get("timestamp")
                    or first.get("dateUTC")
                )
                try:
                    commissioning_dt = pd.to_datetime(ts_raw, utc=True)
                except Exception:
                    commissioning_dt = None

            # ── Metadados do sensor (nextgensensor) ──────────────────
            sensor_meta = sensor_index.get(id_node, {})
            hardware_id = (
                sensor_meta.get("SensorIdentifier")
                or sensor_meta.get("sensorIdentifier")
                or sensor_meta.get("HardwareID")
                or "—"
            )
            battery_lvl = sensor_meta.get("BatteryLevel") or sensor_meta.get("batteryLevel")
            if battery_lvl is not None:
                try:
                    battery_lvl = float(battery_lvl)
                except Exception:
                    battery_lvl = None

            # ── Validação da data de comissionamento ─────────────────
            # ClearedDate = ano ≤ 1940 é sentinela de campo vazio na API.
            # Regra:
            #   • ClearedDate ausente ou ano ≤ 1940  →  usa 1ª leitura de tendência
            #   • ClearedDate válido (ano > 1940)    →  usa ClearedDate
            sensor_created_raw = (
                sensor_meta.get("ClearedDate")
                or sensor_meta.get("clearedDate")
                or sensor_meta.get("Cleared")
                or sensor_meta.get("cleared")
            )
            try:
                sensor_created_dt = pd.to_datetime(sensor_created_raw, utc=True) if sensor_created_raw else None
            except Exception:
                sensor_created_dt = None

            if sensor_created_dt is not None and sensor_created_dt.year <= 1940:
                log(f"      ⚠ IDNode {id_node}: ClearedDate sentinela "
                    f"({sensor_created_dt.year}) — ignorado.")
                sensor_created_dt = None

            if sensor_created_dt is not None:
                effective_dt = sensor_created_dt
                fonte        = "ClearedDate (sensor)"
            elif commissioning_dt is not None:
                effective_dt = commissioning_dt
                fonte        = "1ª Leitura Tendência"
            else:
                effective_dt = None
                fonte        = "—"

            dias_uso = (today - effective_dt).days if effective_dt else None

            if dias_uso and dias_uso > 0 and battery_lvl is not None:
                taxa_bateria = round((100.0 - battery_lvl) / dias_uso, 4)
            else:
                taxa_bateria = None

            rows.append({
                "HardwareID":                  hardware_id,
                "IDNode":                      id_node,
                "MachineID":                   machine_id,
                "MachineName":                 machine_name,
                "BatteryLevel":                battery_lvl,
                "SystemCreatedDate":           sys_created,
                "DataPrimeiraLeitura":         commissioning_dt.strftime("%Y-%m-%d %H:%M:%S") if commissioning_dt else None,
                "DataClearedSensor":           sensor_created_dt.strftime("%Y-%m-%d %H:%M:%S") if sensor_created_dt else None,
                "ProvavelDataComissionamento": effective_dt.strftime("%Y-%m-%d %H:%M:%S") if effective_dt else None,
                "FonteComissionamento":        fonte,
                "DiasDeUso":                   dias_uso,
                "TaxaConsumoBateria":          taxa_bateria,
            })

        prog((i + 1) / total, f"{i+1} / {total}: {machine_name}")

    log(f"✅ Varredura concluída — {len(rows)} sensor(es) IMx-1 identificado(s).")
    prog(1.0, "Concluído")

    if not rows:
        return pd.DataFrame(columns=[
            "HardwareID", "IDNode", "MachineID", "MachineName", "BatteryLevel",
            "SystemCreatedDate", "DataPrimeiraLeitura", "DataClearedSensor",
            "ProvavelDataComissionamento", "FonteComissionamento",
            "DiasDeUso", "TaxaConsumoBateria",
        ])
    return pd.DataFrame(rows)
 
# ─────────────────────────────────────────────
# FLEET MONITORING — HELPERS DE API
# ─────────────────────────────────────────────

# Dicionário de synchronizationstatus
SYNC_STATUS = {
    0:   ("Não Sincronizado", "warn"),
    1:   ("Sincronizado",     "ok"),
    2:   ("Pendente",         "warn"),
    100: ("Falha",            "danger"),
}

# Autodiagnóstico IMx-1 (bitwise)
DIAG_BITS = {
    1:   "Bateria Baixa",
    512: "Instabilidade de Rede",
}


def get_gateways(base_url: str, token: str) -> list:
    """GET /v1/gateways — lista gateways Enlight Collect."""
    resp = requests.get(
        f"{base_url}/v1/gateways",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        timeout=15,
    )
    if resp.status_code in (204, 404):
        return []
    resp.raise_for_status()
    data = resp.json()
    return data if isinstance(data, list) else data.get("value", data.get("items", []))


def get_wired_devices(base_url: str, token: str) -> list:
    """GET /v1/device — lista dispositivos cabeados (IMx-8/16, DADs)."""
    resp = requests.get(
        f"{base_url}/v1/device",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        timeout=15,
    )
    if resp.status_code in (204, 404):
        return []
    resp.raise_for_status()
    data = resp.json()
    return data if isinstance(data, list) else data.get("value", data.get("items", []))


def get_system_check(base_url: str, token: str) -> list:
    """GET /v1/systemcheck — identificação rápida de falhas de config/dados."""
    resp = requests.get(
        f"{base_url}/v1/systemcheck",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        timeout=20,
    )
    if resp.status_code in (204, 404):
        return []
    resp.raise_for_status()
    data = resp.json()
    return data if isinstance(data, list) else data.get("value", data.get("items", []))


def _parse_dt(raw) -> "pd.Timestamp | None":
    """Parse datetime string → UTC Timestamp, or None."""
    if not raw:
        return None
    try:
        return pd.to_datetime(raw, utc=True)
    except Exception:
        return None


def run_fleet_scan(base_url: str, username: str, password: str,
                   progress_cb=None, log_cb=None) -> dict:
    """
    Coleta e estrutura todos os dados de frota:
      gateways   → DataFrame de gateways com status online/offline
      sensors    → DataFrame de sensores sem fio (IMx-1) com saúde
      devices    → DataFrame de dispositivos cabeados
      syscheck   → DataFrame de itens com falha no system check
    Retorna dict com as quatro chaves.
    """
    import time

    def log(msg):
        if log_cb:
            log_cb(msg)

    def prog(val, text=""):
        if progress_cb:
            progress_cb(val, text)

    today = datetime.now(timezone.utc)
    result = {}

    # ── 1. Token ──────────────────────────────────────────────────
    token = _ensure_token(base_url, username, password)
    log("🔑 Token obtido.")
    prog(0.05, "Autenticado")

    # ── 2. Gateways ───────────────────────────────────────────────
    log("📡 Coletando gateways…")
    try:
        gw_raw = get_gateways(base_url, token)
        gw_rows = []
        for g in gw_raw:
            updated = _parse_dt(g.get("statusLastUpdated") or g.get("StatusLastUpdated"))
            dias_sem_update = (today - updated).days if updated else None
            connected = g.get("connected") if g.get("connected") is not None else g.get("Connected")
            gw_rows.append({
                "GatewayID":          g.get("id") or g.get("ID"),
                "Nome":               g.get("name") or g.get("Name") or "—",
                "Conectado":          bool(connected),
                "StatusLastUpdated":  updated.strftime("%Y-%m-%d %H:%M:%S") if updated else None,
                "DiasSemUpdate":      dias_sem_update,
                "Status":             "🟢 Online" if connected else "🔴 Offline",
            })
        result["gateways"] = pd.DataFrame(gw_rows)
        log(f"  ✓ {len(gw_rows)} gateway(s) encontrado(s).")
    except Exception as e:
        log(f"  ⚠ Erro em /v1/gateways: {e}")
        result["gateways"] = pd.DataFrame()
    prog(0.25, "Gateways coletados")
    time.sleep(0.2)

    # ── 3. Sensores sem fio (nextgensensor) ───────────────────────
    log("📶 Coletando sensores sem fio…")
    token = _ensure_token(base_url, username, password)
    try:
        resp = requests.get(
            f"{base_url}/v1/nextgensensor",
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            timeout=15,
        )
        ns_data = resp.json() if resp.status_code not in (204, 404) else []
        ns_list_raw = ns_data if isinstance(ns_data, list) else ns_data.get("value", ns_data.get("items", []))

        # Filtra apenas sensores comissionados (Commissioned == 1)
        ns_list = [
            s for s in ns_list_raw
            if (s.get("Commissioned") if s.get("Commissioned") is not None
                else s.get("commissioned"))
        ]
        log(f"  ✓ {len(ns_list)} comissionado(s) de {len(ns_list_raw)} sensor(es) total.")

        sensor_rows = []
        for s in ns_list:
            updated      = _parse_dt(s.get("StatusLastUpdated") or s.get("statusLastUpdated"))
            dias_offline = (today - updated).days if updated else None
            bat          = s.get("BatteryLevel") or s.get("batteryLevel")
            try:
                bat = float(bat)
            except Exception:
                bat = None

            # Decodifica bits de autodiagnóstico
            diag_code = s.get("DiagnosticCode") or s.get("diagnosticCode") or 0
            try:
                diag_code = int(diag_code)
            except Exception:
                diag_code = 0
            diag_flags = [label for bit, label in DIAG_BITS.items() if diag_code & bit]

            conn_state_raw = s.get("ConnectionState") or s.get("connectionState")
            try:
                conn_state_code = int(conn_state_raw) if conn_state_raw is not None else None
            except (ValueError, TypeError):
                conn_state_code = None

            # OPC UA ConnectionState codes (nextgensensor):
            #   0 → Desconectado / Não Comissionado  (crítico)
            #   1 → Conectado                        (normal)
            #   2 → Sem Medição                      (aviso)
            #   3 → Conectado — Sem Medição           (aviso)
            CONN_STATE_LABELS = {
                0: "Desconectado",
                1: "Conectado",
                2: "Sem Medição",
                3: "Conectado — Sem Medição",
            }
            conn_state = CONN_STATE_LABELS.get(conn_state_code, f"Desconhecido ({conn_state_raw})")

            # Nível de alerta
            if conn_state_code == 0 or (dias_offline and dias_offline > 2):
                alert_level = "danger"
            elif bat is not None and bat < 20:
                alert_level = "danger"
            elif conn_state_code in (2, 3):
                alert_level = "warn"
            elif 512 in [b for b in DIAG_BITS if diag_code & b]:
                alert_level = "warn"
            elif bat is not None and bat < 40:
                alert_level = "warn"
            else:
                alert_level = "ok"

            sensor_rows.append({
                "IDNode":            s.get("IDNode") or s.get("idNode"),
                "HardwareID":        s.get("SensorIdentifier") or s.get("sensorIdentifier") or "—",
                "GatewayID":         s.get("IDSmartGateway") or s.get("idSmartGateway"),
                "ConnectionState":   conn_state,
                "BatteryLevel":      bat,
                "StatusLastUpdated": updated.strftime("%Y-%m-%d %H:%M:%S") if updated else None,
                "DiasOffline":       dias_offline,
                "DiagnosticCode":    diag_code,
                "DiagFlags":         ", ".join(diag_flags) if diag_flags else "—",
                "AlertLevel":        alert_level,
            })

        result["sensors"] = pd.DataFrame(sensor_rows)
        log(f"  ✓ {len(sensor_rows)} sensor(es) sem fio encontrado(s).")
    except Exception as e:
        log(f"  ⚠ Erro em /v1/nextgensensor: {e}")
        result["sensors"] = pd.DataFrame()
    prog(0.50, "Sensores sem fio coletados")
    time.sleep(0.2)

    # ── 4. Dispositivos cabeados ──────────────────────────────────
    log("🔌 Coletando dispositivos cabeados…")
    token = _ensure_token(base_url, username, password)
    try:
        dev_raw  = get_wired_devices(base_url, token)
        dev_rows = []
        for d in dev_raw:
            updated      = _parse_dt(d.get("lastupdate") or d.get("LastUpdate"))
            dias_offline = (today - updated).days if updated else None
            sync_code    = d.get("synchronizationstatus")
            try:
                sync_code = int(sync_code)
            except Exception:
                sync_code = None
            sync_label, sync_cls = SYNC_STATUS.get(sync_code, ("Desconhecido", "warn"))

            # Alerta para Pendente > 30 min
            if sync_code == 100:
                alert_level = "danger"
            elif sync_code == 2 and updated:
                mins_pending = (today - updated).seconds // 60
                alert_level  = "warn" if mins_pending > 30 else "ok"
            elif sync_code == 0:
                alert_level = "warn"
            else:
                alert_level = "ok"

            dev_rows.append({
                "DeviceID":    d.get("id") or d.get("ID"),
                "Nome":        d.get("name") or d.get("Name") or "—",
                "Ativo":       bool(d.get("active") or d.get("Active")),
                "LastUpdate":  updated.strftime("%Y-%m-%d %H:%M:%S") if updated else None,
                "DiasOffline": dias_offline,
                "SyncStatus":  sync_label,
                "SyncCode":    sync_code,
                "AlertLevel":  alert_level,
            })

        result["devices"] = pd.DataFrame(dev_rows)
        log(f"  ✓ {len(dev_rows)} dispositivo(s) cabeado(s) encontrado(s).")
    except Exception as e:
        log(f"  ⚠ Erro em /v1/device: {e}")
        result["devices"] = pd.DataFrame()
    prog(0.75, "Dispositivos cabeados coletados")
    time.sleep(0.2)

    # ── 5. System Check ───────────────────────────────────────────
    log("🔍 Executando system check…")
    token = _ensure_token(base_url, username, password)
    try:
        sc_raw  = get_system_check(base_url, token)
        sc_rows = []
        for item in sc_raw:
            last_recv = _parse_dt(item.get("DateDataReceived") or item.get("dateDataReceived"))
            dias_sem  = (today - last_recv).days if last_recv else None
            sc_rows.append({
                "Nome":             item.get("name") or item.get("Name") or "—",
                "Tipo":             item.get("type") or item.get("Type") or "—",
                "Falha":            item.get("error") or item.get("Error") or item.get("message") or "—",
                "DateDataReceived": last_recv.strftime("%Y-%m-%d %H:%M:%S") if last_recv else None,
                "DiasSemDados":     dias_sem,
            })
        result["syscheck"] = pd.DataFrame(sc_rows)
        log(f"  ✓ {len(sc_rows)} item(ns) com falha no system check.")
    except Exception as e:
        log(f"  ⚠ Erro em /v1/systemcheck: {e}")
        result["syscheck"] = pd.DataFrame()
    prog(1.0, "✅ Coleta concluída")

    log(f"✅ Fleet scan concluído.")
    return result


def run_imx_scan(base_url: str, username: str, password: str,
                 progress_cb=None, log_cb=None) -> pd.DataFrame:
    """
    Varredura completa de sensores IMx-1:
      1. Lista todos os assets
      2. Para cada asset, lista points via v1 e filtra NodeType IMx-1
      3. Prioriza ponto de temperatura; usa qualquer IMx-1 se não houver
      4. Busca primeira leitura de tendência (≥ 01/05/2024)
      5. Cruza com /v1/nextgensensor para Hardware ID e bateria
      6. Monta DataFrame final com colunas de BI
    """
    import time

    def log(msg: str):
        if log_cb:
            log_cb(msg)

    def prog(val: float, text: str = ""):
        if progress_cb:
            progress_cb(val, text)

    today = datetime.now(timezone.utc)
    rows  = []

    # ── 1. Token inicial ──────────────────────────
    token = _ensure_token(base_url, username, password)
    log("🔑 Token obtido.")

    # ── 2. Assets ────────────────────────────────
    assets_list = get_assets(base_url, token)
    total = len(assets_list)
    log(f"🏭 {total} asset(s) encontrado(s).")
    prog(0.02, f"0 / {total} assets processados")

    # ── 3. Sensores IMx (metadados) ───────────────
    token = _ensure_token(base_url, username, password)
    try:
        sensor_index = get_imx_sensors(base_url, token)
        log(f"📡 {len(sensor_index)} sensor(es) IMx comissionados indexados.")
    except Exception as e:
        sensor_index = {}
        log(f"⚠ /v1/nextgensensor indisponível: {e}")

    # ── 4. Iterar assets → points → trend ────────
    for i, asset in enumerate(assets_list):
        machine_id   = asset.get("ID") or asset.get("id")
        machine_name = asset.get("Name") or asset.get("name", "—")
        sys_created  = asset.get("SystemCreatedDate") or asset.get("Created") or ""

        token = _ensure_token(base_url, username, password)

        try:
            points_v1 = get_points_v1(base_url, token, machine_id)
        except Exception as e:
            log(f"  ↳ [{machine_id}] {machine_name}: erro ao listar points — {e}")
            time.sleep(0.1)
            continue

        # Filtra apenas pontos IMx-1
        imx_points = [
            p for p in points_v1
            if int(p.get("NodeType", 0)) in IMX1_NODE_TYPES
        ]

        if not imx_points:
            prog((i + 1) / total, f"{i+1} / {total}: {machine_name} — sem IMx-1")
            time.sleep(0.05)
            continue

        # ── Agrupa points por IDNode (= sensor físico) ───────────────
        # Cada IDNode representa um sensor distinto instalado na máquina.
        # Um mesmo sensor pode ter múltiplos points (vibração, temperatura, etc.).
        nodes: dict[int, list] = {}
        for p in imx_points:
            nid = (
                p.get("ParentID")
                or p.get("IDNode")
                or p.get("NodeID")
            )
            try:
                nid = int(nid)
            except (TypeError, ValueError):
                nid = None
            if nid is None:
                continue
            nodes.setdefault(nid, []).append(p)

        if not nodes:
            prog((i + 1) / total, f"{i+1} / {total}: {machine_name} — IDNode indisponível")
            time.sleep(0.05)
            continue

        log(f"  ↳ [{machine_id}] {machine_name}: {len(nodes)} sensor(es) IMx-1")

        # ── Itera cada sensor (IDNode) individualmente ───────────────
        for id_node, node_points in nodes.items():

            # Pula sensores não comissionados — se o IDNode não consta no
            # sensor_index, foi filtrado por Commissioned == 0
            if id_node not in sensor_index:
                log(f"    ⊘ IDNode {id_node} — não comissionado, ignorado.")
                continue

            # Escolhe o melhor point para buscar a 1ª leitura:
            # prioridade: temperatura (NodeType 11104 / EUType 10905),
            # depois qualquer outro ponto IMx-1 do nó.
            temp_points = [
                p for p in node_points
                if int(p.get("NodeType", 0)) == IMX1_TEMP_NODE_TYPE
                or int(p.get("EUType",   0)) == IMX1_TEMP_EU_TYPE
            ]
            target_point = temp_points[0] if temp_points else node_points[0]
            point_id     = (
                target_point.get("ID")
                or target_point.get("id")
                or target_point.get("PointID")
            )

            log(f"    · IDNode {id_node} — point {point_id} "
                f"(NodeType {target_point.get('NodeType')}, {len(node_points)} point(s) no nó)")

            # Busca primeira leitura
            token = _ensure_token(base_url, username, password)
            try:
                first = get_trend_first_reading(base_url, token, point_id)
            except Exception as e:
                log(f"      ⚠ trend error: {e}")
                first = None
            time.sleep(0.15)

            if first is None:
                commissioning_dt = None
            else:
                ts_raw = (
                    first.get("ReadingTimeUTC")
                    or first.get("readingTimeUTC")
                    or first.get("timestamp")
                    or first.get("dateUTC")
                )
                try:
                    commissioning_dt = pd.to_datetime(ts_raw, utc=True)
                except Exception:
                    commissioning_dt = None

            # ── Metadados do sensor (nextgensensor) ──────────────────
            sensor_meta = sensor_index.get(id_node, {})
            hardware_id = (
                sensor_meta.get("SensorIdentifier")
                or sensor_meta.get("sensorIdentifier")
                or sensor_meta.get("HardwareID")
                or "—"
            )
            battery_lvl = sensor_meta.get("BatteryLevel") or sensor_meta.get("batteryLevel")
            if battery_lvl is not None:
                try:
                    battery_lvl = float(battery_lvl)
                except Exception:
                    battery_lvl = None

            # ── Validação da data de comissionamento ─────────────────
            # ClearedDate = ano ≤ 1940 é sentinela de campo vazio na API.
            # Regra:
            #   • ClearedDate ausente ou ano ≤ 1940  →  usa 1ª leitura de tendência
            #   • ClearedDate válido (ano > 1940)    →  usa ClearedDate
            sensor_created_raw = (
                sensor_meta.get("ClearedDate")
                or sensor_meta.get("clearedDate")
                or sensor_meta.get("Cleared")
                or sensor_meta.get("cleared")
            )
            try:
                sensor_created_dt = pd.to_datetime(sensor_created_raw, utc=True) if sensor_created_raw else None
            except Exception:
                sensor_created_dt = None

            if sensor_created_dt is not None and sensor_created_dt.year <= 1940:
                log(f"      ⚠ IDNode {id_node}: ClearedDate sentinela "
                    f"({sensor_created_dt.year}) — ignorado.")
                sensor_created_dt = None

            if sensor_created_dt is not None:
                effective_dt = sensor_created_dt
                fonte        = "ClearedDate (sensor)"
            elif commissioning_dt is not None:
                effective_dt = commissioning_dt
                fonte        = "1ª Leitura Tendência"
            else:
                effective_dt = None
                fonte        = "—"

            dias_uso = (today - effective_dt).days if effective_dt else None

            if dias_uso and dias_uso > 0 and battery_lvl is not None:
                taxa_bateria = round((100.0 - battery_lvl) / dias_uso, 4)
            else:
                taxa_bateria = None

            rows.append({
                "HardwareID":                  hardware_id,
                "IDNode":                      id_node,
                "MachineID":                   machine_id,
                "MachineName":                 machine_name,
                "BatteryLevel":                battery_lvl,
                "SystemCreatedDate":           sys_created,
                "DataPrimeiraLeitura":         commissioning_dt.strftime("%Y-%m-%d %H:%M:%S") if commissioning_dt else None,
                "DataClearedSensor":           sensor_created_dt.strftime("%Y-%m-%d %H:%M:%S") if sensor_created_dt else None,
                "ProvavelDataComissionamento": effective_dt.strftime("%Y-%m-%d %H:%M:%S") if effective_dt else None,
                "FonteComissionamento":        fonte,
                "DiasDeUso":                   dias_uso,
                "TaxaConsumoBateria":          taxa_bateria,
            })

        prog((i + 1) / total, f"{i+1} / {total}: {machine_name}")

    log(f"✅ Varredura concluída — {len(rows)} sensor(es) IMx-1 identificado(s).")
    prog(1.0, "Concluído")

    if not rows:
        return pd.DataFrame(columns=[
            "HardwareID", "IDNode", "MachineID", "MachineName", "BatteryLevel",
            "SystemCreatedDate", "DataPrimeiraLeitura", "DataClearedSensor",
            "ProvavelDataComissionamento", "FonteComissionamento",
            "DiasDeUso", "TaxaConsumoBateria",
        ])
    return pd.DataFrame(rows)

# ─────────────────────────────────────────────
# SIDEBAR — Conexão
# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# MESH GRAPH — HELPERS E CONSTRUÇÃO
with st.sidebar:
    st.markdown("""
    <div style="padding:16px 0 8px;">
        <div style="font-family:'Rajdhani',sans-serif;font-size:1.4rem;font-weight:700;
                    letter-spacing:3px;text-transform:uppercase;color:#EEF4F9;">
            ⚙ SKF Observer
        </div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.68rem;
                    color:#A7C5E2;letter-spacing:2px;">PHOENIX API v2.0</div>
    </div>
    <hr style="border-color:#2a3f52;margin:8px 0 16px 0;">
    """, unsafe_allow_html=True)

    # ── Seletor de Unidade ───────────────────────
    UNITS = {
        "Alto Araguaia":      ("21221", "http://services.repcenter.skf.com:21221"),
        "Itumbiara":          ("21236", "http://services.repcenter.skf.com:21236"),
        "Jataí":              ("21226", "http://services.repcenter.skf.com:21226"),
        "Paraguaçu Paulista": ("21246", "http://services.repcenter.skf.com:21246"),
        "Ponta Grossa":       ("21241", "http://services.repcenter.skf.com:21241"),
    }

    st.markdown('<div class="sidebar-label">Unidade</div>', unsafe_allow_html=True)

    for unit_name, (port, unit_url) in UNITS.items():
        is_active = st.session_state.selected_unit == unit_name
        # Botão com estilo diferenciado quando selecionado
        btn_style = (
            "background:var(--accent-solid) !important;"
            "color:#EEF4F9 !important;"
            "border-color:var(--accent-solid) !important;"
        ) if is_active else ""
        # Injetar estilo via chave única
        btn_key = f"unit_{port}"
        if is_active:
            st.markdown(
                f'<style>div[data-testid="stButton"] '
                f'button[kind="secondary"]#{btn_key}'
                f'{{background:var(--accent-solid)!important;'
                f'color:#EEF4F9!important;}}</style>',
                unsafe_allow_html=True,
            )
        if st.button(
            f"{'▶ ' if is_active else '   '}{unit_name}  ·  :{port}",
            key=btn_key,
            use_container_width=True,
        ):
            if st.session_state.selected_unit != unit_name:
                # Troca de unidade: limpa todo o estado de dados
                st.session_state.selected_unit  = unit_name
                st.session_state.base_url       = unit_url
                st.session_state.token          = None
                st.session_state.token_ts       = None
                st.session_state.assets         = []
                st.session_state.points         = []
                st.session_state.trend_df       = None
                st.session_state.spectrum_data  = None
                st.session_state.selected_asset = None
                st.session_state.selected_point = None
                st.session_state.imx_df         = None
                st.session_state.imx_log        = []
                st.session_state.fleet_data     = None
                st.session_state.fleet_log      = []
                st.rerun()

    # URL ativa — exibe apenas, sem campo editável por padrão
    _active_url = st.session_state.get("base_url", "—")
    st.markdown(
        f'<div style="font-family:Share Tech Mono,monospace;font-size:0.68rem;'
        f'color:#4a5a6a;word-break:break-all;margin:4px 0 12px 0;padding:6px 8px;'
        f'background:#162130;border-radius:4px;border:1px solid #2a3f52;">'
        f'{_active_url}</div>',
        unsafe_allow_html=True,
    )


    # ── Credenciais ──────────────────────────────
    st.markdown('<div class="sidebar-label">Usuário</div>', unsafe_allow_html=True)
    username = st.text_input("", value=st.session_state.username, label_visibility="collapsed",
                              key="sidebar_username")

    st.markdown('<div class="sidebar-label" style="margin-top:12px;">Senha</div>', unsafe_allow_html=True)
    password = st.text_input("", type="password", placeholder="••••••••", label_visibility="collapsed",
                              key="sidebar_password")

    # Mostra qual unidade está selecionada
    if st.session_state.selected_unit:
        st.markdown(
            f'<div style="font-family:Share Tech Mono,monospace;font-size:0.7rem;'
            f'color:#98C0B8;margin:8px 0 4px;letter-spacing:1px;">'
            f'📍 {st.session_state.selected_unit}</div>',
            unsafe_allow_html=True,
        )

    if st.button("🔌  Conectar", use_container_width=True, key="btn_connect"):
        with st.spinner("Autenticando..."):
            try:
                base_url = st.session_state.base_url
                token = autenticar(base_url, username, password)
                import time as _time
                st.session_state.token     = token
                st.session_state.token_ts  = _time.time()
                st.session_state.username  = username
                st.session_state._password = password
                assets = get_assets(base_url, token)
                st.session_state.assets         = assets
                st.session_state.points         = []
                st.session_state.trend_df       = None
                st.session_state.selected_asset = None
                st.session_state.selected_point = None
                st.success(f"✅ Conectado! {len(assets)} asset(s) encontrado(s).")
            except requests.exceptions.ConnectionError:
                st.error("❌ Servidor inacessível.")
            except requests.exceptions.HTTPError as e:
                st.error(f"❌ Erro HTTP {e.response.status_code}")
            except Exception as e:
                st.error(f"❌ {e}")

    st.markdown('<div class="section-title">Fleet Monitoring — Conectividade e Saúde da Rede</div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div class="alert-info">
        ℹ  Coleta dados de <strong>gateways</strong>, <strong>sensores sem fio IMx-1</strong>,
        <strong>dispositivos cabeados</strong> e <strong>system check</strong> em uma única varredura.
        Interpreta estados de conectividade, bateria, sincronização e diagnósticos automáticos
        para oferecer visibilidade completa da frota de hardware.
    </div>
    """, unsafe_allow_html=True)

    # ── Botões ────────────────────────────────────────────────────
    col_fs, col_fc = st.columns([2, 1])
    with col_fs:
        run_fleet = st.button("🛰  Iniciar Coleta de Frota", use_container_width=True, type="primary",
                              key="btn_fleet_scan")
    with col_fc:
        if st.button("🗑  Limpar", use_container_width=True, key="btn_fleet_clear"):
            st.session_state.fleet_data = None
            st.session_state.fleet_log  = []
            st.rerun()

    # ── Execução ──────────────────────────────────────────────────
    if run_fleet:
        pw = st.session_state.get("_password", "")
        if not pw:
            st.error("❌ Senha não disponível — reconecte na barra lateral.")
        else:
            st.session_state.fleet_data = None
            st.session_state.fleet_log  = []

            fleet_prog = st.progress(0.0, text="Iniciando…")
            fleet_log_box = st.empty()
            fleet_lines   = []

            def _fp(val, text=""):
                fleet_prog.progress(min(val, 1.0), text=text)

            def _fl(msg):
                fleet_lines.append(msg)
                fleet_log_box.markdown(
                    "<br>".join(
                        f"<span style='font-family:Share Tech Mono,monospace;"
                        f"font-size:0.75rem;color:#8b949e;'>{l}</span>"
                        for l in fleet_lines[-10:]
                    ),
                    unsafe_allow_html=True,
                )

            try:
                data = run_fleet_scan(
                    st.session_state.base_url,
                    st.session_state.username,
                    pw,
                    progress_cb=_fp,
                    log_cb=_fl,
                )
                st.session_state.fleet_data = data
                st.session_state.fleet_log  = fleet_lines
                fleet_prog.progress(1.0, text="✅ Coleta concluída")
                fleet_log_box.empty()
            except Exception as e:
                st.error(f"❌ Erro durante coleta: {e}")

    # ── Dashboard ─────────────────────────────────────────────────
    if st.session_state.fleet_data:
        fd       = st.session_state.fleet_data
        df_gw    = fd.get("gateways",  pd.DataFrame())
        df_sens  = fd.get("sensors",   pd.DataFrame())
        df_dev   = fd.get("devices",   pd.DataFrame())
        df_sc    = fd.get("syscheck",  pd.DataFrame())
        now_utc  = datetime.now(timezone.utc)

        # ══════════════════════════════════════════
        # NÍVEL 1 — VISÃO GERAL DE FROTA
        # ══════════════════════════════════════════
        st.markdown('<div class="section-title">Nível 1 — Visão Geral de Frota</div>',
                    unsafe_allow_html=True)

        # KPIs de gateway
        n_gw_total   = len(df_gw)
        n_gw_online  = int(df_gw["Conectado"].sum()) if not df_gw.empty and "Conectado" in df_gw else 0
        n_gw_offline = n_gw_total - n_gw_online
        pct_online   = round(100 * n_gw_online / n_gw_total, 1) if n_gw_total > 0 else 0.0

        # KPIs de sensores
        n_sens       = len(df_sens)
        n_instab     = int((df_sens["DiagnosticCode"].fillna(0).astype(int) & 512 > 0).sum()) \
                       if not df_sens.empty and "DiagnosticCode" in df_sens else 0
        n_bat_crit   = int((df_sens["BatteryLevel"].dropna() < 20).sum()) \
                       if not df_sens.empty and "BatteryLevel" in df_sens else 0
        n_desconectados = int((df_sens["ConnectionState"] == "Desconectado").sum()) \
                        if not df_sens.empty and "ConnectionState" in df_sens else 0
        n_sem_medicao = int((df_sens["ConnectionState"].isin(
                                ["Sem Medição", "Conectado — Sem Medição"])).sum()) \
                        if not df_sens.empty and "ConnectionState" in df_sens else 0

        # KPIs de dispositivos
        n_dev        = len(df_dev)
        n_dev_fail   = int((df_dev["SyncCode"] == 100).sum()) \
                       if not df_dev.empty and "SyncCode" in df_dev else 0
        n_dev_pend   = int((df_dev["SyncCode"] == 2).sum()) \
                       if not df_dev.empty and "SyncCode" in df_dev else 0

        # System check
        n_sc_fail    = len(df_sc)

        gw_cls  = "ok" if pct_online >= 90 else ("warn" if pct_online >= 60 else "danger")
        bat_cls = "danger" if n_bat_crit > 0 else "ok"
        net_cls = "warn"   if n_instab > 0 else "ok"
        dev_cls = "danger" if n_dev_fail > 0 else ("warn" if n_dev_pend > 0 else "ok")

        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-card {gw_cls}">
                <div class="label">Gateways Online</div>
                <div class="value">{pct_online:.0f}%</div>
                <div class="unit">{n_gw_online} / {n_gw_total} · {n_gw_offline} offline</div>
            </div>
            <div class="metric-card {net_cls}">
                <div class="label">Instabilidade de Rede</div>
                <div class="value">{n_instab}</div>
                <div class="unit">sensores com erro 512 (mesh)</div>
            </div>
            <div class="metric-card {"danger" if n_desconectados > 0 else "ok"}">
                <div class="label">Desconectados</div>
                <div class="value">{n_desconectados}</div>
                <div class="unit">estado OPC UA 0</div>
            </div>
            <div class="metric-card {"warn" if n_sem_medicao > 0 else "ok"}">
                <div class="label">Sem Medição</div>
                <div class="value">{n_sem_medicao}</div>
                <div class="unit">estados OPC UA 2 e 3</div>
            </div>
            <div class="metric-card {bat_cls}">
                <div class="label">Bateria Crítica</div>
                <div class="value">{n_bat_crit}</div>
                <div class="unit">sensores abaixo de 20%</div>
            </div>
            <div class="metric-card {dev_cls}">
                <div class="label">Dispositivos Cabeados</div>
                <div class="value">{n_dev}</div>
                <div class="unit">{n_dev_fail} falha(s) · {n_dev_pend} pendente(s)</div>
            </div>
            <div class="metric-card {"warn" if n_sc_fail > 0 else "ok"}">
                <div class="label">System Check</div>
                <div class="value">{n_sc_fail}</div>
                <div class="unit">item(ns) com falha</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Alertas críticos de topo
        alertas = []
        if n_gw_offline > 0:
            alertas.append(("danger", f"🔴 {n_gw_offline} gateway(s) OFFLINE — verificar conectividade de rede."))
        if n_desconectados > 0:
            alertas.append(("danger", f"🚨 {n_desconectados} sensor(es) Desconectado(s) (OPC UA 0) — verificar comissionamento ou falha de hardware."))
        if n_sem_medicao > 0:
            alertas.append(("warn", f"⚠ {n_sem_medicao} sensor(es) Sem Medição (OPC UA 2/3) — comunicação presente mas sem dados."))
        if n_bat_crit > 0:
            alertas.append(("danger", f"🪫 {n_bat_crit} sensor(es) com bateria abaixo de 20% — substituição urgente."))
        if n_dev_fail > 0:
            alertas.append(("danger", f"⛔ {n_dev_fail} dispositivo(s) cabeado(s) com FALHA de sincronização."))
        if n_instab > 0:
            alertas.append(("warn",  f"⚠ {n_instab} sensor(es) com Instabilidade de Rede (código 512) — alto consumo de bateria."))
        if n_dev_pend > 0:
            alertas.append(("warn",  f"⏳ {n_dev_pend} dispositivo(s) com sincronização Pendente."))
        if not alertas:
            alertas.append(("ok", "✔ Frota operando dentro dos parâmetros normais."))

        for cls, msg in alertas:
            st.markdown(f'<div class="alert-{cls}">{msg}</div>', unsafe_allow_html=True)

        # ══════════════════════════════════════════
        # NÍVEL 2 — MAPA DE CONECTIVIDADE
        # ══════════════════════════════════════════
        st.markdown('<div class="section-title">Nível 2 — Mapa de Conectividade da Rede Mesh</div>',
                    unsafe_allow_html=True)

        if not df_gw.empty and not df_sens.empty:

            # Gráfico de pizza: status dos gateways
            col_pie, col_bar = st.columns([1, 2])

            with col_pie:
                fig_pie = go.Figure(go.Pie(
                    labels=["Online", "Offline"],
                    values=[n_gw_online, n_gw_offline],
                    hole=0.62,
                    marker=dict(colors=["#4E9D2D", "#F06A22"],
                                line=dict(color="#0e1820", width=3)),
                    textinfo="percent+label",
                    textfont=dict(family="Exo 2, sans-serif", size=12, color="#EEF4F9"),
                    hovertemplate="<b>%{label}</b><br>%{value} gateway(s)<extra></extra>",
                ))
                fig_pie.update_layout(
                    paper_bgcolor="#0e1820",
                    plot_bgcolor="#0e1820",
                    font=dict(family="Exo 2, sans-serif", color="#98C0B8"),
                    title=dict(text="<b>Gateways</b>",
                               font=dict(family="Rajdhani, sans-serif", size=16, color="#EEF4F9"),
                               x=0.5),
                    showlegend=False,
                    margin=dict(l=10, r=10, t=50, b=10),
                    height=260,
                    annotations=[dict(
                        text=f"<b>{pct_online:.0f}%</b><br>online",
                        x=0.5, y=0.5, font_size=16,
                        font=dict(family="Rajdhani, sans-serif", color="#A7C5E2"),
                        showarrow=False,
                    )],
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            with col_bar:
                # Distribuição de ConnectionState dos sensores
                if "ConnectionState" in df_sens.columns:
                    cs_counts = df_sens["ConnectionState"].value_counts().reset_index()
                    cs_counts.columns = ["Estado", "Qtd"]
                    color_map = {
                        "Conectado":              "#4E9D2D",
                        "Desconectado":           "#F06A22",
                        "Sem Medição":            "#BA944B",
                        "Conectado — Sem Medição": "#708EB4",
                    }
                    bar_colors = [color_map.get(s, "#BA944B") for s in cs_counts["Estado"]]

                    fig_cs = go.Figure(go.Bar(
                        x=cs_counts["Estado"],
                        y=cs_counts["Qtd"],
                        marker=dict(color=bar_colors,
                                    line=dict(color="rgba(255,255,255,0.1)", width=0.5)),
                        hovertemplate="<b>%{x}</b><br>%{y} sensor(es)<extra></extra>",
                    ))
                    fig_cs.update_layout(
                        paper_bgcolor="#0e1820",
                        plot_bgcolor="#162130",
                        font=dict(family="Exo 2, sans-serif", color="#98C0B8", size=11),
                        title=dict(text="<b>Estado de Conexão dos Sensores</b>",
                                   font=dict(family="Rajdhani, sans-serif", size=16, color="#EEF4F9"),
                                   x=0.01),
                        xaxis=dict(gridcolor="#2a3f52",
                                   tickfont=dict(family="Share Tech Mono, monospace", size=10, color="#98C0B8")),
                        yaxis=dict(gridcolor="#2a3f52", zeroline=False,
                                   tickfont=dict(family="Share Tech Mono, monospace", size=10, color="#98C0B8"),
                                   title=dict(text="Sensores", font=dict(color="#98C0B8", size=10))),
                        margin=dict(l=50, r=20, t=50, b=40),
                        height=260,
                    )
                    st.plotly_chart(fig_cs, use_container_width=True)

            # Scatter mesh: BatteryLevel × DiasOffline, colorido por alert level
            if "BatteryLevel" in df_sens.columns and "DiasOffline" in df_sens.columns:
                df_mesh = df_sens.dropna(subset=["BatteryLevel"]).copy()
                df_mesh["DiasOffline"] = df_mesh["DiasOffline"].fillna(0)

                ALERT_COLORS = {"ok": "#4E9D2D", "warn": "#BA944B", "danger": "#F06A22"}
                mesh_colors  = [ALERT_COLORS.get(a, "#98C0B8") for a in df_mesh.get("AlertLevel", [])]

                # Ícone de bateria no texto
                def _bat_icon(b):
                    if b is None:   return "?"
                    if b >= 70:     return "🔋"
                    if b >= 40:     return "🪫"
                    return "⚠"

                fig_mesh = go.Figure()

                # Zonas de fundo
                fig_mesh.add_hrect(y0=0,   y1=20,  fillcolor="rgba(240,106,34,0.08)",  line_width=0)
                fig_mesh.add_hrect(y0=20,  y1=40,  fillcolor="rgba(186,148,75,0.05)",  line_width=0)
                fig_mesh.add_hrect(y0=40,  y1=100, fillcolor="rgba(78,157,45,0.05)", line_width=0)

                fig_mesh.add_trace(go.Scatter(
                    x=df_mesh["DiasOffline"],
                    y=df_mesh["BatteryLevel"],
                    mode="markers+text",
                    marker=dict(
                        size=12,
                        color=mesh_colors,
                        line=dict(color="rgba(255,255,255,0.15)", width=1),
                        symbol="circle",
                    ),
                    text=[_bat_icon(b) for b in df_mesh["BatteryLevel"]],
                    textposition="middle center",
                    textfont=dict(size=10),
                    customdata=df_mesh[["HardwareID", "ConnectionState",
                                        "DiagFlags", "GatewayID"]].values,
                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>"
                        "Estado: %{customdata[1]}<br>"
                        "Bateria: <b>%{y:.1f}%</b><br>"
                        "Dias sem update: %{x}<br>"
                        "Diagnóstico: %{customdata[2]}<br>"
                        "Gateway: %{customdata[3]}<extra></extra>"
                    ),
                    showlegend=False,
                ))

                # Linhas de referência
                fig_mesh.add_vline(x=2, line=dict(color="rgba(255,71,87,0.4)", width=1, dash="dot"),
                                   annotation_text="2 dias offline",
                                   annotation_font=dict(color="#F06A22", size=9))
                fig_mesh.add_hline(y=20, line=dict(color="rgba(255,71,87,0.4)", width=1, dash="dot"),
                                   annotation_text="Bateria crítica 20%",
                                   annotation_font=dict(color="#F06A22", size=9),
                                   annotation_position="bottom right")

                fig_mesh.update_layout(
                    paper_bgcolor="#0e1820",
                    plot_bgcolor="#162130",
                    font=dict(family="Exo 2, sans-serif", color="#98C0B8", size=11),
                    title=dict(
                        text="<b>Saúde da Rede Mesh</b>  ·  Bateria × Dias sem Atualização",
                        font=dict(family="Rajdhani, sans-serif", size=18, color="#EEF4F9"),
                        x=0.01,
                    ),
                    xaxis=dict(
                        gridcolor="#2a3f52", zeroline=False,
                        tickfont=dict(family="Share Tech Mono, monospace", size=10, color="#98C0B8"),
                        title=dict(text="Dias sem Atualização de Status", font=dict(color="#98C0B8", size=11)),
                    ),
                    yaxis=dict(
                        gridcolor="#2a3f52", zeroline=False, range=[0, 105],
                        tickfont=dict(family="Share Tech Mono, monospace", size=10, color="#98C0B8"),
                        title=dict(text="Nível de Bateria [%]", font=dict(color="#98C0B8", size=11)),
                    ),
                    hovermode="closest",
                    margin=dict(l=60, r=40, t=70, b=60),
                    height=420,
                )
                st.plotly_chart(fig_mesh, use_container_width=True)

        # ── Gauge de gateways (barras empilhadas por status) ─────────
        if not df_gw.empty and "Nome" in df_gw.columns and "Conectado" in df_gw.columns:
            df_gw_sorted = df_gw.sort_values("Conectado", ascending=True)
            gw_colors    = ["#F06A22" if not c else "#4E9D2D" for c in df_gw_sorted["Conectado"]]

            fig_gw = go.Figure(go.Bar(
                x=[1] * len(df_gw_sorted),
                y=df_gw_sorted["Nome"],
                orientation="h",
                marker=dict(color=gw_colors, line=dict(color="rgba(0,0,0,0)", width=0)),
                customdata=df_gw_sorted[["StatusLastUpdated", "DiasSemUpdate"]].values,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Último update: %{customdata[0]}<br>"
                    "Dias sem update: %{customdata[1]}<extra></extra>"
                ),
                text=df_gw_sorted["Status"],
                textposition="inside",
                textfont=dict(family="Share Tech Mono, monospace", size=10, color="#0e1820"),
            ))
            fig_gw.update_layout(
                paper_bgcolor="#0e1820",
                plot_bgcolor="#162130",
                font=dict(family="Exo 2, sans-serif", color="#98C0B8", size=11),
                title=dict(text="<b>Status Individual dos Gateways</b>",
                           font=dict(family="Rajdhani, sans-serif", size=16, color="#EEF4F9"),
                           x=0.01),
                xaxis=dict(visible=False),
                yaxis=dict(tickfont=dict(family="Exo 2, sans-serif", size=11, color="#A7C5E2"),
                           gridcolor="rgba(0,0,0,0)"),
                margin=dict(l=180, r=20, t=50, b=20),
                height=max(200, len(df_gw_sorted) * 32 + 80),
                showlegend=False,
            )
            st.plotly_chart(fig_gw, use_container_width=True)

        # ══════════════════════════════════════════
        # NÍVEL 3 — DRILL-DOWN / DETALHES
        # ══════════════════════════════════════════
        st.markdown('<div class="section-title">Nível 3 — Detalhes do Ativo</div>',
                    unsafe_allow_html=True)

        # Sub-tabs por tipo de dispositivo
        dtab_sens, dtab_dev, dtab_sc = st.tabs([
            f"📶  Sensores Sem Fio ({len(df_sens)})",
            f"🔌  Dispositivos Cabeados ({len(df_dev)})",
            f"🔍  System Check ({len(df_sc)})",
        ])

        # ── Sensores sem fio ──────────────────────────────────────
        with dtab_sens:
            if df_sens.empty:
                st.markdown('<div class="alert-info">Nenhum sensor sem fio encontrado.</div>',
                            unsafe_allow_html=True)
            else:
                # Filtro de alerta
                filter_opts = ["Todos", "⛔ Crítico", "⚠ Aviso", "✔ Normal"]
                col_flt, col_srch = st.columns([2, 2])
                with col_flt:
                    sel_filter = st.selectbox("Filtrar por nível de alerta",
                                              filter_opts, key="fleet_sens_filter")
                with col_srch:
                    srch = st.text_input("Buscar por Hardware ID", "", key="fleet_sens_search")

                df_show_s = df_sens.copy()
                if sel_filter == "⛔ Crítico":
                    df_show_s = df_show_s[df_show_s["AlertLevel"] == "danger"]
                elif sel_filter == "⚠ Aviso":
                    df_show_s = df_show_s[df_show_s["AlertLevel"] == "warn"]
                elif sel_filter == "✔ Normal":
                    df_show_s = df_show_s[df_show_s["AlertLevel"] == "ok"]
                if srch:
                    df_show_s = df_show_s[
                        df_show_s["HardwareID"].str.contains(srch, case=False, na=False)
                    ]

                # Tabela principal
                st.dataframe(
                    df_show_s.drop(columns=["AlertLevel"], errors="ignore"),
                    use_container_width=True,
                    hide_index=True,
                    height=350,
                    column_config={
                        "IDNode":            st.column_config.NumberColumn("IDNode"),
                        "HardwareID":        st.column_config.TextColumn("Hardware ID"),
                        "GatewayID":         st.column_config.NumberColumn("Gateway ID"),
                        "ConnectionState":   st.column_config.TextColumn("Estado Conexão"),
                        "BatteryLevel":      st.column_config.ProgressColumn(
                                                "Bateria", min_value=0, max_value=100,
                                                format="%.1f%%"),
                        "StatusLastUpdated": st.column_config.TextColumn("Último Update"),
                        "DiasOffline":       st.column_config.NumberColumn("Dias Offline"),
                        "DiagnosticCode":    st.column_config.NumberColumn("Cód. Diagnóstico"),
                        "DiagFlags":         st.column_config.TextColumn("Diagnóstico"),
                    },
                )

                # Gráfico de distribuição de bateria
                df_bat_hist = df_show_s["BatteryLevel"].dropna()
                if not df_bat_hist.empty:
                    fig_bat_hist = go.Figure()
                    fig_bat_hist.add_trace(go.Histogram(
                        x=df_bat_hist,
                        nbinsx=20,
                        marker=dict(
                            color=df_bat_hist.apply(
                                lambda b: "#F06A22" if b < 20 else ("#BA944B" if b < 40 else "#4E9D2D")
                            ),
                            line=dict(color="#0e1820", width=0.5),
                        ),
                        hovertemplate="Bateria: %{x:.0f}%<br>Sensores: %{y}<extra></extra>",
                    ))
                    fig_bat_hist.add_vline(x=20, line=dict(color="#F06A22", width=1.5, dash="dot"),
                                          annotation_text="20% crítico",
                                          annotation_font=dict(color="#F06A22", size=9))
                    fig_bat_hist.add_vline(x=40, line=dict(color="#BA944B", width=1, dash="dot"),
                                          annotation_text="40% aviso",
                                          annotation_font=dict(color="#BA944B", size=9))
                    fig_bat_hist.update_layout(
                        paper_bgcolor="#0e1820", plot_bgcolor="#162130",
                        font=dict(family="Exo 2, sans-serif", color="#98C0B8", size=11),
                        title=dict(text="<b>Distribuição de Bateria — Sensores Sem Fio</b>",
                                   font=dict(family="Rajdhani, sans-serif", size=16, color="#EEF4F9"),
                                   x=0.01),
                        xaxis=dict(gridcolor="#2a3f52",
                                   title=dict(text="Nível de Bateria [%]", font=dict(color="#98C0B8")),
                                   tickfont=dict(family="Share Tech Mono, monospace", size=10, color="#98C0B8")),
                        yaxis=dict(gridcolor="#2a3f52", zeroline=False,
                                   title=dict(text="Nº de Sensores", font=dict(color="#98C0B8")),
                                   tickfont=dict(family="Share Tech Mono, monospace", size=10, color="#98C0B8")),
                        margin=dict(l=60, r=20, t=50, b=50),
                        height=300,
                    )
                    st.plotly_chart(fig_bat_hist, use_container_width=True)

                # Exportação
                csv_sens = df_show_s.to_csv(index=False).encode("utf-8")
                st.download_button("⬇  Exportar Sensores CSV", data=csv_sens,
                                   file_name=f"fleet_sensors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                   mime="text/csv", key="dl_sens")

        # ── Dispositivos cabeados ─────────────────────────────────
        with dtab_dev:
            if df_dev.empty:
                st.markdown('<div class="alert-info">Nenhum dispositivo cabeado encontrado.</div>',
                            unsafe_allow_html=True)
            else:
                # Gráfico de barras agrupado por SyncStatus
                sync_counts = df_dev["SyncStatus"].value_counts().reset_index()
                sync_counts.columns = ["Status", "Qtd"]
                SYNC_COLORS = {
                    "Sincronizado":     "#4E9D2D",
                    "Pendente":         "#BA944B",
                    "Não Sincronizado": "#BA944B",
                    "Falha":            "#F06A22",
                    "Desconhecido":     "#98C0B8",
                }
                sync_bar_colors = [SYNC_COLORS.get(s, "#98C0B8") for s in sync_counts["Status"]]

                fig_sync = go.Figure(go.Bar(
                    x=sync_counts["Status"],
                    y=sync_counts["Qtd"],
                    marker=dict(color=sync_bar_colors,
                                line=dict(color="rgba(255,255,255,0.1)", width=0.5)),
                    hovertemplate="<b>%{x}</b><br>%{y} dispositivo(s)<extra></extra>",
                    text=sync_counts["Qtd"],
                    textposition="outside",
                    textfont=dict(family="Share Tech Mono, monospace", size=11, color="#EEF4F9"),
                ))
                fig_sync.update_layout(
                    paper_bgcolor="#0e1820", plot_bgcolor="#162130",
                    font=dict(family="Exo 2, sans-serif", color="#98C0B8", size=11),
                    title=dict(text="<b>Status de Sincronização — Dispositivos Cabeados</b>",
                               font=dict(family="Rajdhani, sans-serif", size=16, color="#EEF4F9"),
                               x=0.01),
                    xaxis=dict(gridcolor="#2a3f52",
                               tickfont=dict(family="Share Tech Mono, monospace", size=10, color="#98C0B8")),
                    yaxis=dict(gridcolor="#2a3f52", zeroline=False,
                               tickfont=dict(family="Share Tech Mono, monospace", size=10, color="#98C0B8"),
                               title=dict(text="Qtd.", font=dict(color="#98C0B8", size=10))),
                    margin=dict(l=50, r=20, t=50, b=40),
                    height=280,
                )
                st.plotly_chart(fig_sync, use_container_width=True)

                # Tabela detalhada
                st.dataframe(
                    df_dev,
                    use_container_width=True,
                    hide_index=True,
                    height=300,
                    column_config={
                        "DeviceID":    st.column_config.NumberColumn("ID"),
                        "Nome":        st.column_config.TextColumn("Dispositivo"),
                        "Ativo":       st.column_config.CheckboxColumn("Ativo"),
                        "LastUpdate":  st.column_config.TextColumn("Último Update"),
                        "DiasOffline": st.column_config.NumberColumn("Dias Offline"),
                        "SyncStatus":  st.column_config.TextColumn("Sincronização"),
                        "SyncCode":    st.column_config.NumberColumn("Cód."),
                        "AlertLevel":  st.column_config.TextColumn("Alerta"),
                    },
                )

                csv_dev = df_dev.to_csv(index=False).encode("utf-8")
                st.download_button("⬇  Exportar Dispositivos CSV", data=csv_dev,
                                   file_name=f"fleet_devices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                   mime="text/csv", key="dl_dev")

        # ── System Check ──────────────────────────────────────────
        with dtab_sc:
            if df_sc.empty:
                st.markdown('<div class="alert-ok">✔ Nenhuma falha detectada no System Check.</div>',
                            unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert-danger">🔴 {len(df_sc)} item(ns) com falha detectado(s).</div>',
                            unsafe_allow_html=True)

                # Histograma de dias sem dados
                df_sc_dias = df_sc["DiasSemDados"].dropna()
                if not df_sc_dias.empty:
                    fig_sc = go.Figure(go.Histogram(
                        x=df_sc_dias, nbinsx=15,
                        marker=dict(color="#F06A22", line=dict(color="#0e1820", width=0.5)),
                        hovertemplate="Dias sem dados: %{x}<br>Itens: %{y}<extra></extra>",
                    ))
                    fig_sc.update_layout(
                        paper_bgcolor="#0e1820", plot_bgcolor="#162130",
                        font=dict(family="Exo 2, sans-serif", color="#98C0B8", size=11),
                        title=dict(text="<b>Distribuição — Dias sem Dados Recebidos</b>",
                                   font=dict(family="Rajdhani, sans-serif", size=16, color="#EEF4F9"),
                                   x=0.01),
                        xaxis=dict(gridcolor="#2a3f52",
                                   title=dict(text="Dias sem dados", font=dict(color="#98C0B8")),
                                   tickfont=dict(family="Share Tech Mono, monospace", size=10, color="#98C0B8")),
                        yaxis=dict(gridcolor="#2a3f52", zeroline=False,
                                   title=dict(text="Nº Itens", font=dict(color="#98C0B8")),
                                   tickfont=dict(family="Share Tech Mono, monospace", size=10, color="#98C0B8")),
                        margin=dict(l=60, r=20, t=50, b=50),
                        height=260,
                    )
                    st.plotly_chart(fig_sc, use_container_width=True)

                st.dataframe(
                    df_sc,
                    use_container_width=True,
                    hide_index=True,
                    height=320,
                    column_config={
                        "Nome":             st.column_config.TextColumn("Nome"),
                        "Tipo":             st.column_config.TextColumn("Tipo"),
                        "Falha":            st.column_config.TextColumn("Descrição da Falha"),
                        "DateDataReceived": st.column_config.TextColumn("Último Dado Recebido"),
                        "DiasSemDados":     st.column_config.NumberColumn("Dias sem Dados"),
                    },
                )

                csv_sc = df_sc.to_csv(index=False).encode("utf-8")
                st.download_button("⬇  Exportar System Check CSV", data=csv_sc,
                                   file_name=f"fleet_syscheck_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                   mime="text/csv", key="dl_sc")

        # ── Log da coleta ─────────────────────────────────────────
        if st.session_state.fleet_log:
            with st.expander("📋  Log da Coleta de Frota"):
                st.code("\n".join(st.session_state.fleet_log), language=None)
# ══════════════════════════════════════════════
