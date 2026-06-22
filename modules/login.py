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
    st.markdown("""
    <div style="text-align:center;padding:40px 0 20px;">
      <p style="font-size:40px;margin:0;">🏋️</p>
      <h1 style="font-size:28px;font-weight:600;margin:8px 0 4px;">Mis Rutinas</h1>
      <p style="color:#64748b;margin:0;">Fitness & Bienestar Personal</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        df = leer_df("usuarios")
    except Exception as e:
        st.error(f"Error conectando a Google Sheets: {e}")
        return False

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:

        # ── Sin usuarios: solo mostrar registro ──────────────────────────
        if df.empty:
            st.info("¡Bienvenido! Crea el primer usuario para comenzar.")
            st.subheader("Crear usuario")
            nombre = st.text_input("Tu nombre", key="reg_nombre")
            pin    = st.text_input("PIN de 4 dígitos", type="password",
                                    max_chars=4, key="reg_pin")
            pin2   = st.text_input("Confirmar PIN", type="password",
                                    max_chars=4, key="reg_pin2")
            if st.button("Crear y entrar", type="primary", use_container_width=True):
                if not nombre.strip():
                    st.error("Ingresa un nombre.")
                elif len(pin) != 4 or not pin.isdigit():
                    st.error("El PIN debe ser exactamente 4 dígitos numéricos.")
                elif pin != pin2:
                    st.error("Los PINs no coinciden.")
                elif _crear_usuario(nombre, pin):
                    st.success("✅ Usuario creado. Iniciando sesión...")
                    uid = nombre.lower().strip().replace(" ", "_")
                    estado.set("user_id", uid)
                    estado.set("nombre_usuario", nombre.strip())
                    st.session_state["autenticado"] = True
                    st.rerun()
            return False

        # ── Con usuarios: tabs Login / Nuevo usuario ──────────────────────
        tab_login, tab_nuevo = st.tabs(["🔑 Iniciar sesión", "➕ Nuevo usuario"])

        with tab_login:
            usuarios_activos = df[df["activo"].astype(str).str.lower() == "si"]
            if usuarios_activos.empty:
                st.warning("No hay usuarios activos.")
            else:
                nombre_sel = st.selectbox("¿Quién eres?",
                                           usuarios_activos["nombre"].tolist(),
                                           key="login_nombre")
                pin_input  = st.text_input("PIN", type="password",
                                            max_chars=4, key="login_pin",
                                            placeholder="4 dígitos")
                if st.button("Entrar →", type="primary", use_container_width=True):
                    fila = usuarios_activos[usuarios_activos["nombre"] == nombre_sel].iloc[0]
                    if str(pin_input) == str(fila["pin"]):
                        estado.set("user_id",       str(fila["id"]))
                        estado.set("nombre_usuario", fila["nombre"])
                        st.session_state["autenticado"] = True
                        estado.refrescar()
                        st.rerun()
                    else:
                        st.error("❌ PIN incorrecto")

        with tab_nuevo:
            st.caption(f"Usuarios registrados: {len(df)} / 5")
            if len(df) >= 5:
                st.warning("Se alcanzó el límite de 5 usuarios.")
            else:
                n2  = st.text_input("Nombre del nuevo usuario", key="new_nombre")
                p2  = st.text_input("PIN de 4 dígitos", type="password",
                                     max_chars=4, key="new_pin")
                p2c = st.text_input("Confirmar PIN", type="password",
                                     max_chars=4, key="new_pin2")
                if st.button("Crear usuario", type="primary", use_container_width=True):
                    if not n2.strip():
                        st.error("Ingresa un nombre.")
                    elif len(p2) != 4 or not p2.isdigit():
                        st.error("El PIN debe ser exactamente 4 dígitos numéricos.")
                    elif p2 != p2c:
                        st.error("Los PINs no coinciden.")
                    elif n2.lower().strip() in df["nombre"].str.lower().tolist():
                        st.error(f"Ya existe un usuario con el nombre '{n2}'.")
                    elif _crear_usuario(n2, p2):
                        st.success(f"✅ Usuario '{n2}' creado. Ahora puede iniciar sesión.")
                        st.rerun()

    return False
