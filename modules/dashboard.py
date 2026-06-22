import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta

from utils.sheets import get_worksheet
from utils.calculos import calcular_imc, clasificar_imc, calcular_rcc, clasificar_rcc_mujer


def gauge_chart(valor, minimo, maximo, titulo, rangos_color):
    """Crea un gauge chart con Plotly."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor,
        title={"text": titulo, "font": {"size": 13}},
        gauge={
            "axis": {"range": [minimo, maximo], "tickwidth": 1},
            "bar": {"color": "#6366f1"},
            "steps": rangos_color,
            "threshold": {
                "line": {"color": "#1e293b", "width": 3},
                "thickness": 0.75,
                "value": valor,
            },
        },
    ))
    fig.update_layout(height=200, margin=dict(t=40, b=10, l=20, r=20))
    return fig


def mostrar():
    st.title("🏠 Dashboard")

    # ── Cargar datos ───────────────────────────────────────────────────────
    try:
        ws  = get_worksheet("medidas")
        data = ws.get_all_records()
        df  = pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error conectando a Google Sheets: {e}")
        st.info("Configura la conexión en el módulo de Diagnóstico.")
        return

    tiene_datos = not df.empty

    # ── Bienvenida ─────────────────────────────────────────────────────────
    hoy = date.today()
    hora = hoy.strftime("%A %d de %B")
    st.markdown(f"### 👋 ¡Hola! Hoy es {hora}")
    st.divider()

    if not tiene_datos:
        st.info("📋 Aún no hay registros. Ve a **📊 Mis Medidas** para agregar tu primer registro.")
        return

    # ── Último registro ────────────────────────────────────────────────────
    ultimo = df.iloc[-1]

    st.subheader("📌 Último registro")
    c1, c2, c3, c4 = st.columns(4)

    peso     = float(ultimo.get("peso_lbs", 0))
    altura   = float(ultimo.get("altura_cm", 0))
    cintura  = float(ultimo.get("cintura_cm", 0))
    cadera   = float(ultimo.get("cadera_cm", 0))
    imc_val  = float(ultimo.get("imc", 0)) if ultimo.get("imc") else None
    rcc_val  = float(ultimo.get("rcc", 0)) if ultimo.get("rcc") else None

    with c1:
        delta_peso = None
        if len(df) >= 2:
            delta_peso = round(peso - float(df.iloc[-2].get("peso_lbs", peso)), 1)
        st.metric("⚖️ Peso", f"{peso} lbs",
                  delta=f"{delta_peso:+.1f} lbs" if delta_peso is not None else None,
                  delta_color="inverse")
    with c2:
        st.metric("📏 Cintura", f"{cintura} cm")
    with c3:
        st.metric("🍑 Cadera", f"{cadera} cm")
    with c4:
        st.metric("📅 Fecha", str(ultimo.get("fecha", "—")))

    st.divider()

    # ── Gauges ────────────────────────────────────────────────────────────
    st.subheader("🎯 Indicadores clave")
    g1, g2 = st.columns(2)

    with g1:
        if imc_val:
            cat_imc, _ = clasificar_imc(imc_val)
            fig_imc = gauge_chart(
                imc_val, 14, 40, f"IMC — {cat_imc}",
                [
                    {"range": [14, 18.5], "color": "#fef9c3"},
                    {"range": [18.5, 25],  "color": "#dcfce7"},
                    {"range": [25, 30],    "color": "#fef3c7"},
                    {"range": [30, 40],    "color": "#fee2e2"},
                ]
            )
            st.plotly_chart(fig_imc, use_container_width=True)

    with g2:
        if rcc_val:
            cat_rcc, _ = clasificar_rcc_mujer(rcc_val)
            fig_rcc = gauge_chart(
                rcc_val, 0.6, 1.1, f"RCC — {cat_rcc}",
                [
                    {"range": [0.6, 0.80],  "color": "#dcfce7"},
                    {"range": [0.80, 0.85], "color": "#fef3c7"},
                    {"range": [0.85, 1.1],  "color": "#fee2e2"},
                ]
            )
            st.plotly_chart(fig_rcc, use_container_width=True)

    st.divider()

    # ── Tendencia de peso ──────────────────────────────────────────────────
    if len(df) >= 2:
        st.subheader("📈 Tendencia de peso")
        df_plot = df[df["peso_lbs"] != ""].copy()
        df_plot["peso_lbs"] = pd.to_numeric(df_plot["peso_lbs"], errors="coerce")
        df_plot = df_plot.dropna(subset=["peso_lbs"])

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_plot["fecha"],
            y=df_plot["peso_lbs"],
            mode="lines+markers",
            name="Peso (lbs)",
            line=dict(color="#6366f1", width=2),
            marker=dict(size=7),
        ))
        fig.update_layout(
            height=250,
            margin=dict(t=10, b=30, l=40, r=20),
            xaxis_title="Fecha",
            yaxis_title="Peso (lbs)",
            plot_bgcolor="white",
            paper_bgcolor="white",
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="#f1f5f9")
        st.plotly_chart(fig, use_container_width=True)

    # ── Total registros ────────────────────────────────────────────────────
    st.divider()
    st.caption(f"📊 Total de registros: {len(df)}  |  Primer registro: {df.iloc[0].get('fecha', '—')}  |  Último: {df.iloc[-1].get('fecha', '—')}")
