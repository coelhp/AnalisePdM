import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="SKF Observer Dashboard", layout="wide")

st.title("📊 SKF Observer - Dashboard de Monitoramento")

# =========================
# INPUTS DE CONEXÃO
# =========================

st.sidebar.header("🔐 Conexão API")

base_url = st.sidebar.text_input(
    "URL da API",
    "http://services.repcenter.skf.com"
)

port = st.sidebar.text_input(
    "Porta da planta",
    "21221"
)

username = st.sidebar.text_input("Usuário")
password = st.sidebar.text_input("Senha", type="password")

timeout = 60


# =========================
# FUNÇÕES API
# =========================

def get_token():

    token_url = f"{base_url}:{port}/token"

    payload = {
        "grant_type": "password",
        "username": username,
        "password": password
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        r = requests.post(token_url, data=payload, headers=headers, timeout=timeout)

        if r.status_code == 200:
            return r.json().get("access_token")
        else:
            return None

    except:
        return None


def get_data(endpoint, token):

    try:

        url = f"{base_url}:{port}{endpoint}"

        headers = {
            "Authorization": f"Bearer {token}"
        }

        r = requests.get(url, headers=headers, timeout=timeout)

        if r.status_code == 200:
            return r.json()
        else:
            return None

    except:
        return None


# =========================
# AUTENTICAÇÃO
# =========================

if st.sidebar.button("Conectar"):

    token = get_token()

    if token:

        st.success("Conectado com sucesso!")

        # =========================
        # ASSETS
        # =========================

        assets = get_data("/v2/assets", token)

        if assets:

            df_assets = pd.DataFrame(assets)

            asset_options = df_assets[["ID", "Name"]].copy()
            asset_options["label"] = asset_options["Name"] + " (ID: " + asset_options["ID"].astype(str) + ")"

            selected_asset = st.selectbox(
                "Selecione o Asset",
                asset_options["label"]
            )

            asset_id = asset_options.loc[
                asset_options["label"] == selected_asset, "ID"
            ].values[0]

            st.write("Asset selecionado:", asset_id)

            # =========================
            # POINTS
            # =========================

            points = get_data(f"/v1/machines/{asset_id}/points", token)

            if points:

                df_points = pd.DataFrame(points)

                point_options = df_points[["ID", "Name"]].copy()
                point_options["label"] = point_options["Name"] + " (ID: " + point_options["ID"].astype(str) + ")"

                selected_point = st.selectbox(
                    "Selecione o Point",
                    point_options["label"]
                )

                point_id = point_options.loc[
                    point_options["label"] == selected_point, "ID"
                ].values[0]

                st.write("Point selecionado:", point_id)

                # =========================
                # TREND MEASUREMENTS
                # =========================

                trend = get_data(f"/v1/points/{point_id}/trendMeasurements", token)

                if trend:

                    df_trend = pd.DataFrame(trend)

                    if "TimeStamp" in df_trend.columns:
                        df_trend["TimeStamp"] = pd.to_datetime(df_trend["TimeStamp"])

                    st.subheader("📈 Trend Measurements")

                    st.dataframe(df_trend)

                    # Detecta coluna de valor automaticamente
                    value_columns = df_trend.select_dtypes(include="number").columns

                    if len(value_columns) > 0:

                        value_col = value_columns[0]

                        fig = px.line(
                            df_trend,
                            x="TimeStamp",
                            y=value_col,
                            title=f"Trend - Point {point_id}"
                        )

                        st.plotly_chart(fig, use_container_width=True)

                    else:
                        st.warning("Nenhuma coluna numérica encontrada para plot.")

                else:
                    st.warning("TrendMeasurements não encontrados.")

            else:
                st.warning("Points não encontrados.")

        else:
            st.warning("Assets não encontrados.")

    else:
        st.error("Falha ao autenticar na API.")