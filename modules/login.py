import streamlit as st
import pandas as pd
from datetime import date
from utils.sheets import get_worksheet, leer_df
import utils.estado as estado


def _crear_usuario(nombre: str, pin: str) -> bool:
    try:
        ws  = get_worksheet("usuarios")
        uid = nombre.lower().strip().replace(" ", "_")
        ws.append_row([uid, nombre.strip(), pin, str(date.today()), "si"])
        return True
    except Exception as e:
        st.error(f"Error creando usuario: {e}")
        return False


def mostrar_login() -> bool:
    """Muestra la pantalla de login. Retorna True si el usuario está autenticado."""

    st.markdown("""
    <div style="text-align:center;padding:40px 0 20px;">
      <p style="font-size:36px;margin:0;">🏋️</p>
      <h1 style="font-size:28px;font-weight:600;margin:8px 0 4px;">Mis Rutinas</h1>
      <p style="color:#64748b;margin:0;">Fitness & Bienestar Personal</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        df = leer_df("usuarios")
    except Exception as e:
        st.error(f"Error conectando a Google Sheets: {e}")
        return False

    # ── Primer uso: no hay usuarios ──────────────────────────────────────
    if df.empty:
        st.info("¡Bienvenido! Crea el primer usuario para comenzar.")
        with st.form("form_primer_usuario"):
            st.subheader("Crear primer usuario")
            nombre = st.text_input("Tu nombre")
            pin    = st.text_input("Elige un PIN de 4 dígitos", type="password", max_chars=4)
            pin2   = st.text_input("Confirma el PIN", type="password", max_chars=4)
            if st.form_submit_button("Crear usuario", type="primary", use_container_width=True):
                if not nombre.strip():
                    st.error("Ingresa un nombre.")
                elif len(pin) != 4 or not pin.isdigit():
                    st.error("El PIN debe ser exactamente 4 dígitos.")
                elif pin != pin2:
                    st.error("Los PINs no coinciden.")
                elif _crear_usuario(nombre, pin):
                    st.success("✅ Usuario creado. Ahora inicia sesión.")
                    st.rerun()
        return False

    # ── Login normal ──────────────────────────────────────────────────────
    usuarios_activos = df[df.get("activo", pd.Series(["si"]*len(df))).str.lower() == "si"]

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        with st.form("form_login"):
            st.subheader("Iniciar sesión")
            nombre_sel = st.selectbox("¿Quién eres?", usuarios_activos["nombre"].tolist())
            pin_input  = st.text_input("PIN", type="password", max_chars=4,
                                        placeholder="4 dígitos")
            submitted  = st.form_submit_button("Entrar →", type="primary",
                                                use_container_width=True)
            if submitted:
                user_row = usuarios_activos[usuarios_activos["nombre"] == nombre_sel].iloc[0]
                if str(pin_input) == str(user_row["pin"]):
                    estado.set("user_id",        str(user_row["id"]))
                    estado.set("nombre_usuario",  user_row["nombre"])
                    st.session_state["autenticado"] = True
                    estado.refrescar()
                    st.rerun()
                else:
                    st.error("❌ PIN incorrecto")

        # Agregar usuario nuevo (expandible)
        with st.expander("➕ Agregar nuevo usuario"):
            with st.form("form_nuevo_usuario"):
                n2   = st.text_input("Nombre del nuevo usuario")
                p2   = st.text_input("PIN", type="password", max_chars=4)
                p2c  = st.text_input("Confirmar PIN", type="password", max_chars=4)
                if st.form_submit_button("Crear", type="secondary", use_container_width=True):
                    if not n2.strip():
                        st.error("Ingresa un nombre.")
                    elif len(p2) != 4 or not p2.isdigit():
                        st.error("El PIN debe ser 4 dígitos.")
                    elif p2 != p2c:
                        st.error("Los PINs no coinciden.")
                    elif n2.lower().strip() in df["nombre"].str.lower().tolist():
                        st.error("Ese nombre ya existe.")
                    elif _crear_usuario(n2, p2):
                        st.success(f"✅ Usuario '{n2}' creado.")
                        st.rerun()

    return False
