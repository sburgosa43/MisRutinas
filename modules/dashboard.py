import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date

import utils.estado as estado
from utils.sheets import leer_df
from utils.calculos import calcular_imc, clasificar_imc, calcular_rcc, clasificar_rcc_mujer


def gauge(valor, minimo, maximo, titulo, rangos):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=valor,
        title={"text": titulo, "font": {"size": 13}},
        gauge={"axis": {"range": [minimo, maximo]}, "bar": {"color": "#6366f1"},
               "steps": rangos,
               "threshold": {"line": {"color": "#1e293b", "width": 3}, "thickness": 0.75, "value": valor}},
    ))
    fig.update_layout(height=200, margin=dict(t=40, b=10, l=20, r=20))
    return fig


def mostrar():
    estado.cargar_perfil()
    nombre = estado.get("nombre_usuario", "")
    st.title(f"🏠 Dashboard {f'— {nombre}' if nombre and nombre != 'Mi Rutina' else ''}")

    try:
        df = leer_df("medidas")
    except Exception as e:
        st.error(f"Error conectando a Google Sheets: {e}")
        st.info("Configura la conexión en el módulo 🔧 Diagnóstico.")
        return

    if df.empty:
        st.info("📋 Aún no hay registros. Ve a **📊 Mis Medidas** para agregar tu primer registro.")
        return

    u = df.iloc[-1]
    peso = float(u.get("peso_lbs", 0))
    cintura = float(u.get("cintura_cm", 0))
    cadera = float(u.get("cadera_cm", 0))
    imc_v = float(u.get("imc", 0)) if u.get("imc") else None
    rcc_v = float(u.get("rcc", 0)) if u.get("rcc") else None

    st.subheader("📌 Último registro")
    c1, c2, c3, c4 = st.columns(4)
    delta = round(peso - float(df.iloc[-2].get("peso_lbs", peso)), 1) if len(df) >= 2 else None
    c1.metric("⚖️ Peso", f"{peso} lbs", f"{delta:+.1f} lbs" if delta else None, delta_color="inverse")
    c2.metric("📏 Cintura", f"{cintura} cm")
    c3.metric("🍑 Cadera", f"{cadera} cm")
    c4.metric("📅 Fecha", str(u.get("fecha", "—")))

    st.divider()
    st.subheader("🎯 Indicadores clave")
    g1, g2 = st.columns(2)
    with g1:
        if imc_v:
            cat, _ = clasificar_imc(imc_v)
            st.plotly_chart(gauge(imc_v, 14, 40, f"IMC — {cat}",
                [{"range":[14,18.5],"color":"#fef9c3"},{"range":[18.5,25],"color":"#dcfce7"},
                 {"range":[25,30],"color":"#fef3c7"},{"range":[30,40],"color":"#fee2e2"}]),
                use_container_width=True)
    with g2:
        if rcc_v:
            cat, _ = clasificar_rcc_mujer(rcc_v)
            st.plotly_chart(gauge(rcc_v, 0.6, 1.1, f"RCC — {cat}",
                [{"range":[0.6,0.80],"color":"#dcfce7"},{"range":[0.80,0.85],"color":"#fef3c7"},
                 {"range":[0.85,1.1],"color":"#fee2e2"}]),
                use_container_width=True)

    if len(df) >= 2:
        st.divider()
        st.subheader("📈 Tendencia de peso")
        df_p = df.copy()
        df_p["peso_lbs"] = pd.to_numeric(df_p["peso_lbs"], errors="coerce")
        df_p = df_p.dropna(subset=["peso_lbs"])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_p["fecha"], y=df_p["peso_lbs"],
            mode="lines+markers", line=dict(color="#6366f1", width=2), marker=dict(size=7)))
        fig.update_layout(height=250, margin=dict(t=10,b=30,l=40,r=20),
            xaxis_title="Fecha", yaxis_title="Peso (lbs)",
            plot_bgcolor="white", paper_bgcolor="white")
        fig.update_yaxes(showgrid=True, gridcolor="#f1f5f9")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    obj = estado.get("eval_objetivo", "")
    if obj:
        st.caption(f"🎯 Objetivo: {obj}")
    st.caption(f"📊 {len(df)} registro(s) · Primer: {df.iloc[0].get('fecha','—')} · Último: {df.iloc[-1].get('fecha','—')}")
