import streamlit as st
from datetime import date
from utils.sheets import get_worksheet, leer_df


def mostrar_login():
    st.markdown("""
    <div style="text-align:center;padding:40px 0 24px;">
      <div style="font-size:48px;">🏋️</div>
      <h1 style="font-size:26px;font-weight:600;margin:10px 0 4px;">Mis Rutinas</h1>
      <p style="color:#64748b;margin:0;font-size:14px;">Fitness & Bienestar Personal</p>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.2, 1])

    with col:
        try:
            df = leer_df("usuarios")
        except Exception as e:
            st.error(f"Error conectando: {e}")
            return

        # ── Sin usuarios → crear primero ─────────────────────────────────
        if df.empty:
            st.subheader("Crear primer usuario")
            nombre = st.text_input("Tu nombre")
            pin    = st.text_input("PIN (4 dígitos)", type="password", max_chars=4)
            pin2   = st.text_input("Confirmar PIN",   type="password", max_chars=4)

            if st.button("Crear y entrar", type="primary", use_container_width=True):
                err = _validar_pin(nombre, pin, pin2)
                if err:
                    st.error(err)
                else:
                    uid = nombre.lower().strip().replace(" ", "_")
                    ok  = _guardar_usuario(uid, nombre.strip(), pin)
                    if ok:
                        st.session_state["autenticado"]    = True
                        st.session_state["user_id"]        = uid
                        st.session_state["nombre_usuario"] = nombre.strip()
                        st.rerun()
            return

        # ── Con usuarios → login ──────────────────────────────────────────
        activos = df[df["activo"].astype(str).str.lower() == "si"]

        st.subheader("Iniciar sesión")
        nombre_sel = st.selectbox("¿Quién eres?", activos["nombre"].tolist())
        pin_input  = st.text_input("PIN", type="password", max_chars=4,
                                    placeholder="4 dígitos")

        if st.button("Entrar →", type="primary", use_container_width=True):
            fila = activos[activos["nombre"] == nombre_sel].iloc[0]
            if str(pin_input).strip() == str(fila["pin"]).strip():
                st.session_state["autenticado"]    = True
                st.session_state["user_id"]        = str(fila["id"])
                st.session_state["nombre_usuario"] = str(fila["nombre"])
                st.rerun()
            else:
                st.error("❌ PIN incorrecto")

        st.divider()

        # ── Agregar nuevo usuario (visible, sin expander) ─────────────────
        st.subheader("Registrar nuevo usuario")
        st.caption(f"Usuarios actuales: {len(df)} / 5")

        if len(df) >= 5:
            st.warning("Límite de 5 usuarios alcanzado.")
        else:
            n2  = st.text_input("Nombre del nuevo usuario", key="new_n")
            p2  = st.text_input("PIN (4 dígitos)",  type="password",
                                 max_chars=4, key="new_p")
            p2c = st.text_input("Confirmar PIN", type="password",
                                 max_chars=4, key="new_pc")

            if st.button("Registrar usuario", type="secondary",
                          use_container_width=True):
                err = _validar_pin(n2, p2, p2c)
                if err:
                    st.error(err)
                elif n2.lower().strip() in df["nombre"].str.lower().tolist():
                    st.error(f"Ya existe un usuario llamado '{n2}'.")
                else:
                    uid2 = n2.lower().strip().replace(" ", "_")
                    if _guardar_usuario(uid2, n2.strip(), p2):
                        st.success(f"✅ Usuario '{n2}' registrado. Ya puede iniciar sesión.")
                        st.rerun()


def _validar_pin(nombre, pin, pin2):
    if not nombre or not nombre.strip():
        return "Ingresa un nombre."
    if len(pin) != 4 or not pin.isdigit():
        return "El PIN debe ser exactamente 4 dígitos numéricos."
    if pin != pin2:
        return "Los PINs no coinciden."
    return None


def _guardar_usuario(uid, nombre, pin):
    try:
        ws = get_worksheet("usuarios")
        ws.append_row([uid, nombre, pin, str(date.today()), "si"])
        return True
    except Exception as e:
        st.error(f"Error guardando usuario: {e}")
        return False
