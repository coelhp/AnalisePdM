"""
SKF Observer Phoenix API v2.0 - Extração e Plot de Dados de Tendência
======================================================================
Fluxo:
  1. Autenticação  → POST /token
  2. Listar Assets → GET  /v2/assets
  3. Listar Points → GET  /v2/points?machine_id={asset_id}
  4. Trend Data    → GET  /v2/trend?pointId={point_id}
  5. Plot          → matplotlib

Configuração:
  Ajuste as variáveis da seção CONFIG antes de executar.
"""

import sys
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timezone, timedelta

# ─────────────────────────────────────────────
# CONFIG  ← edite aqui
# ─────────────────────────────────────────────
BASE_URL   = "http://services.repcenter.skf.com:21236"   # URL base do Observer Phoenix
USERNAME   = "patrick.coelho"
PASSWORD   = "REMOVIDO"
GRANT_TYPE = "password"

# Filtros opcionais para o trend (None = sem filtro)
FROM_DATE_UTC = None   # ex: "2024-01-01T00:00:00Z"
TO_DATE_UTC   = None   # ex: "2024-12-31T23:59:59Z"
MAX_READINGS  = 500    # máximo de leituras retornadas
# ─────────────────────────────────────────────


# ── Helpers ──────────────────────────────────

def get_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json; v=2.0",
    }


def handle_response(resp: requests.Response, context: str) -> dict | list:
    if resp.status_code == 204:
        print(f"[AVISO] {context}: sem conteúdo (204).")
        return []
    if not resp.ok:
        print(f"[ERRO] {context}: HTTP {resp.status_code}")
        try:
            print("       Detalhe:", resp.json())
        except Exception:
            print("       Body:", resp.text[:300])
        sys.exit(1)
    return resp.json()


# ── Etapa 1: Autenticação ────────────────────

def autenticar() -> str:
    print("\n[1/4] Autenticando...")
    resp = requests.post(
        f"{BASE_URL}/token",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
        data={
            "grant_type": GRANT_TYPE,
            "username": USERNAME,
            "password": PASSWORD,
        },
        timeout=15,
    )
    data = handle_response(resp, "Autenticação")
    token = data.get("access_token")
    if not token:
        print("[ERRO] Token não encontrado na resposta:", data)
        sys.exit(1)
    print(f"       Token obtido com sucesso. Expira em {data.get('expires_in', '?')}s")
    return token


# ── Etapa 2: Listar Assets ───────────────────

def listar_assets(token: str) -> list[dict]:
    print("\n[2/4] Listando Assets (máquinas)...")
    resp = requests.get(
        f"{BASE_URL}/v2/assets",
        headers=get_headers(token),
        params={"includeAcknowledged": "true"},
        timeout=15,
    )
    assets = handle_response(resp, "GET /v2/assets")
    if not assets:
        print("[ERRO] Nenhum asset encontrado.")
        sys.exit(1)

    print(f"\n       {'ID':>8}  {'Nome':<30}  {'Status':<12}  Path")
    print("       " + "-" * 75)
    for a in assets:
        status_list = a.get("Status", [])
        status_str  = str(status_list[0]) if status_list else "-"
        print(f"       {a['ID']:>8}  {a['Name']:<30}  {status_str:<12}  {a.get('Path','')}")

    return assets


def selecionar_asset(assets: list[dict]) -> dict:
    ids_validos = [str(a["ID"]) for a in assets]
    while True:
        escolha = input("\n>>> Informe o ID do Asset desejado: ").strip()
        if escolha in ids_validos:
            asset = next(a for a in assets if str(a["ID"]) == escolha)
            print(f"    Asset selecionado: [{asset['ID']}] {asset['Name']}")
            return asset
        print(f"    ID inválido. Escolha entre: {', '.join(ids_validos)}")


# ── Etapa 3: Listar Points ───────────────────

def listar_points(token: str, machine_id: int) -> list[dict]:
    print(f"\n[3/4] Listando Points para machine_id={machine_id}...")
    resp = requests.get(
        f"{BASE_URL}/v2/points",
        headers=get_headers(token),
        params={"machine_id": machine_id},
        timeout=15,
    )
    points = handle_response(resp, "GET /v2/points")
    if not points:
        print("[ERRO] Nenhum ponto encontrado para este asset.")
        sys.exit(1)

    print(f"\n       {'ID':>8}  {'Nome':<35}  {'Tipo':<20}  Unidade")
    print("       " + "-" * 80)
    for p in points:
        unit = p.get("unit", p.get("Unit", "-"))
        ptype = p.get("type", p.get("Type", "-"))
        print(f"       {p['id']:>8}  {p['name']:<35}  {str(ptype):<20}  {unit}")

    return points


def selecionar_point(points: list[dict]) -> dict:
    ids_validos = [str(p["id"]) for p in points]
    while True:
        escolha = input("\n>>> Informe o ID do Point desejado: ").strip()
        if escolha in ids_validos:
            point = next(p for p in points if str(p["id"]) == escolha)
            print(f"    Point selecionado: [{point['id']}] {point['name']}")
            return point
        print(f"    ID inválido. Escolha entre: {', '.join(ids_validos)}")


# ── Etapa 4: Buscar Trend Data ───────────────

def buscar_trend(token: str, point_id: int) -> pd.DataFrame:
    print(f"\n[4/4] Buscando dados de tendência para pointId={point_id}...")

    params: dict = {
        "pointId": point_id,
        "maxNumberOfReadings": MAX_READINGS,
        "descending": "false",
    }
    if FROM_DATE_UTC:
        params["fromDateUTC"] = FROM_DATE_UTC
    if TO_DATE_UTC:
        params["toDateUTC"] = TO_DATE_UTC

    resp = requests.get(
        f"{BASE_URL}/v2/trend",
        headers=get_headers(token),
        params=params,
        timeout=30,
    )
    data = handle_response(resp, "GET /v2/trend")

    if not data:
        print("[AVISO] Nenhum dado de tendência retornado.")
        return pd.DataFrame()

    # Normaliza o formato (lista de leituras)
    rows = []
    for item in data:
        # Timestamp pode vir em campo "timestamp" ou "dateUTC" etc.
        ts_raw  = item.get("timestamp") or item.get("dateUTC") or item.get("date")
        val_obj = item.get("value") or {}

        if isinstance(val_obj, dict):
            value = val_obj.get("value")
            unit  = val_obj.get("unit", "")
        else:
            value = val_obj
            unit  = item.get("unit", "")

        rows.append({"timestamp": ts_raw, "value": value, "unit": unit})

    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df["value"]     = pd.to_numeric(df["value"], errors="coerce")
    df.dropna(subset=["timestamp", "value"], inplace=True)
    df.sort_values("timestamp", inplace=True)
    df.reset_index(drop=True, inplace=True)

    print(f"       {len(df)} leituras carregadas  |  "
          f"de {df['timestamp'].min()}  até {df['timestamp'].max()}")
    return df


# ── Plot ─────────────────────────────────────

def plotar_tendencia(df: pd.DataFrame, asset: dict, point: dict) -> None:
    if df.empty:
        print("[AVISO] Sem dados para plotar.")
        return

    unit      = df["unit"].iloc[-1] if "unit" in df.columns else ""
    ponto_str = f"{point['name']}  (ID {point['id']})"
    asset_str = f"{asset['Name']}  (ID {asset['ID']})"

    # Calcular estatísticas básicas
    media   = df["value"].mean()
    desvio  = df["value"].std()
    lim_alerta = media + 2 * desvio   # linha de referência simples (2σ)
    lim_alarme = media + 3 * desvio

    fig, ax = plt.subplots(figsize=(14, 5))
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#16213e")

    # Linha de tendência
    ax.plot(df["timestamp"], df["value"],
            color="#00d4ff", linewidth=1.5, label="Leitura", zorder=3)
    ax.scatter(df["timestamp"], df["value"],
               color="#00d4ff", s=14, zorder=4, alpha=0.7)

    # Linhas de referência
    ax.axhline(media,       color="#a8e063", linewidth=1, linestyle="--",
               label=f"Média  {media:.3f} {unit}", alpha=0.8)
    ax.axhline(lim_alerta,  color="#f9c74f", linewidth=1, linestyle=":",
               label=f"Alerta  (μ+2σ)  {lim_alerta:.3f} {unit}", alpha=0.8)
    ax.axhline(lim_alarme,  color="#f94144", linewidth=1, linestyle=":",
               label=f"Alarme  (μ+3σ)  {lim_alarme:.3f} {unit}", alpha=0.8)

    # Eixo X – formatação de datas adaptativa
    span_days = (df["timestamp"].max() - df["timestamp"].min()).days
    if span_days > 365:
        fmt = mdates.DateFormatter("%b %Y")
        loc = mdates.MonthLocator(interval=3)
    elif span_days > 60:
        fmt = mdates.DateFormatter("%d/%m/%y")
        loc = mdates.WeekdayLocator(interval=2)
    else:
        fmt = mdates.DateFormatter("%d/%m %H:%M")
        loc = mdates.AutoDateLocator()

    ax.xaxis.set_major_formatter(fmt)
    ax.xaxis.set_major_locator(loc)
    plt.xticks(rotation=35, ha="right", color="#c9d1d9", fontsize=8)
    plt.yticks(color="#c9d1d9", fontsize=9)

    # Labels e título
    ax.set_xlabel("Data / Hora (UTC)", color="#c9d1d9", fontsize=10)
    ax.set_ylabel(f"Valor  [{unit}]", color="#c9d1d9", fontsize=10)
    ax.set_title(
        f"Gráfico de Tendência\n{asset_str}  ›  {ponto_str}",
        color="#e6edf3", fontsize=13, fontweight="bold", pad=12,
    )

    # Grade e bordas
    ax.grid(color="#263859", linestyle="--", linewidth=0.5, alpha=0.7)
    for spine in ax.spines.values():
        spine.set_edgecolor("#263859")

    # Legenda
    legend = ax.legend(
        loc="upper left", framealpha=0.3,
        labelcolor="#c9d1d9", fontsize=8.5,
        facecolor="#1a1a2e", edgecolor="#263859",
    )

    # Anotação de informações extras
    info_txt = (
        f"Leituras: {len(df)}\n"
        f"Mín: {df['value'].min():.4f}  |  Máx: {df['value'].max():.4f}"
    )
    ax.text(0.99, 0.97, info_txt,
            transform=ax.transAxes, ha="right", va="top",
            color="#8b949e", fontsize=8,
            bbox=dict(facecolor="#1a1a2e", alpha=0.5, edgecolor="none"))

    plt.tight_layout()

    filename = (
        f"trend_{asset['ID']}_{point['id']}_"
        f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.png"
    )
    plt.savefig(filename, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"\n    Gráfico salvo em: {filename}")
    plt.show()


# ── Main ─────────────────────────────────────

def main():
    print("=" * 60)
    print("  SKF Observer Phoenix API v2.0 – Trend Plot")
    print("=" * 60)

    token  = autenticar()
    assets = listar_assets(token)
    asset  = selecionar_asset(assets)

    points = listar_points(token, asset["ID"])
    point  = selecionar_point(points)

    df = buscar_trend(token, point["id"])
    plotar_tendencia(df, asset, point)

    print("\nConcluído.")


if __name__ == "__main__":
    main()