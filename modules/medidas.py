import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import base64
from pathlib import Path
from datetime import date, timedelta

import utils.estado as estado
from utils.sheets import get_worksheet, leer_df_usuario, guardar_fila_usuario, eliminar_fila_sheets, actualizar_fila_sheets
from utils.ui_helpers import seccion_eliminar
from utils.calculos import (calcular_imc, clasificar_imc,
                             calcular_rcc, clasificar_rcc_mujer,
                             calcular_rel_hombros_cintura)

LBS_A_KG = 0.453592


def calcular_edad(fecha_nac: date) -> int:
    hoy = date.today()
    return hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))


def _cargar_silueta() -> str | None:
    """Carga la imagen de siluetas desde assets/ como base64."""
    ruta = Path(__file__).parent.parent / "assets" / "siluetas.jpg"
    if not ruta.exists():
        ruta = Path(__file__).parent.parent / "assets" / "siluetas.png"
    if ruta.exists():
        with open(ruta, "rb") as f:
            ext = ruta.suffix.lstrip(".")
            return f"data:image/{ext};base64," + base64.b64encode(f.read()).decode()
    return None


def silhoueta_html(genero: str) -> str:
    """
    Muestra la imagen de siluetas. 
    La imagen tiene mujer a la izquierda y hombre a la derecha.
    Recorta el lado correcto según el género.
    """
    img_src = _cargar_silueta()

    if not img_src:
        return """<div style="padding:20px;background:#f1f5f9;border-radius:8px;text-align:center;color:#64748b;font-family:sans-serif;">
            <p style="margin:0;font-size:13px;">⚠️ Imagen no encontrada.<br>
            Sube <code>siluetas.jpg</code> a la carpeta <code>assets/</code> del repo.</p>
        </div>"""

    return f"""<div style="background:white;border-radius:10px;padding:8px;border:1px solid #e5e7eb;">
  <p style="margin:0 0 6px 0;font-size:11px;font-weight:600;color:#6b7280;font-family:sans-serif;text-align:center;">Guía de medición</p>
  <div style="width:100%;border-radius:6px;">
    <img src="{img_src}" style="width:100%;display:block;height:auto;border-radius:6px;"/>
  </div>
</div>"""


def calcular_edad(fecha_nac: date) -> int:
    hoy = date.today()
    return hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))



def calcular_edad(fecha_nac: date) -> int:
    hoy = date.today()
    return hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))


def _cargar_silueta() -> str | None:
    """Carga la imagen de siluetas desde assets/ como base64."""
    ruta = Path(__file__).parent.parent / "assets" / "siluetas.jpg"
    if not ruta.exists():
        ruta = Path(__file__).parent.parent / "assets" / "siluetas.png"
    if ruta.exists():
        with open(ruta, "rb") as f:
            ext = ruta.suffix.lstrip(".")
            return f"data:image/{ext};base64," + base64.b64encode(f.read()).decode()
    return None


def silhoueta_html(genero: str) -> str:
    """
    Muestra la imagen de siluetas. 
    La imagen tiene mujer a la izquierda y hombre a la derecha.
    Recorta el lado correcto según el género.
    """
    img_src = _cargar_silueta()

    if not img_src:
        return """<div style="padding:20px;background:#f1f5f9;border-radius:8px;text-align:center;color:#64748b;font-family:sans-serif;">
            <p style="margin:0;font-size:13px;">⚠️ Imagen no encontrada.<br>
            Sube <code>siluetas.jpg</code> a la carpeta <code>assets/</code> del repo.</p>
        </div>"""

    return f"""<div style="background:white;border-radius:10px;padding:8px;border:1px solid #e5e7eb;">
  <p style="margin:0 0 6px 0;font-size:11px;font-weight:600;color:#6b7280;font-family:sans-serif;text-align:center;">Guía de medición</p>
  <div style="width:100%;border-radius:6px;">
    <img src="{img_src}" style="width:100%;display:block;height:auto;border-radius:6px;"/>
  </div>
</div>"""


def calcular_edad(fecha_nac: date) -> int:
    hoy = date.today()
    return hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))


def silhoueta_svg(genero: str) -> str:
    """SVG silhouette inspired by flat body measurement diagrams."""

    if genero == "Mujer":
        cc = "#f4b8b0"   # body color salmon
        ch = "#c47560"   # hair color

        hair = f"""
        <path d="M58,34 C54,16 62,4 74,2 C68,10 66,22 68,32 Z" fill="{ch}"/>
        <path d="M68,30 C66,14 72,2 82,2 C90,0 100,6 104,16
                 C108,8 112,2 120,4 C114,12 112,24 112,36
                 C116,28 120,18 120,10 C122,22 120,36 116,48
                 C120,42 122,32 120,24 C120,38 116,54 110,66
                 C114,58 116,46 114,36 C108,56 100,70 94,80
                 L80,76 C72,62 66,46 62,32 Z" fill="{ch}"/>"""

        head = f'<ellipse cx="80" cy="38" rx="27" ry="30" fill="{cc}"/>'
        neck = f'<path d="M73,66 L73,82 L87,82 L87,66 C87,72 84,76 80,76 C76,76 73,72 73,66 Z" fill="{cc}"/>'

        body = f"""
        <path d="
          M73,80 C61,80 45,84 37,94 C29,104 28,116 30,126
          C32,134 38,140 42,142 C38,154 38,164 40,172
          C42,180 46,186 44,194 C42,202 36,206 36,214
          L40,214 C40,228 42,268 42,280 L42,355
          C42,364 46,370 52,372 C58,374 64,370 66,364
          C68,358 68,352 68,345 L68,280
          C72,272 76,268 80,268 C84,268 88,272 92,280
          L92,345 C92,352 92,358 94,364 C96,370 102,374 108,372
          C114,370 118,364 118,355 L118,280
          C118,268 120,228 120,214 L124,214
          C124,206 118,202 116,194 C114,186 118,180 120,172
          C122,164 122,154 118,142 C122,140 128,134 130,126
          C132,116 131,104 123,94 C115,84 99,80 87,80 Z
        " fill="{cc}"/>"""

        arms = f"""
        <path d="M37,96 C28,102 22,114 20,128 L15,192 C14,202 16,208 20,210
                 L28,208 C26,202 26,194 28,184 L33,128 C35,116 40,106 44,100 Z" fill="{cc}"/>
        <path d="M123,96 C132,102 138,114 140,128 L145,192 C146,202 144,208 140,210
                 L132,208 C134,202 134,194 132,184 L127,128 C125,116 120,106 116,100 Z" fill="{cc}"/>"""

        feet = f"""
        <path d="M42,370 C40,374 38,378 40,382 L70,382 C72,378 70,372 68,370 Z" fill="{cc}"/>
        <path d="M92,370 C90,374 88,378 90,382 L120,382 C122,378 120,372 118,370 Z" fill="{cc}"/>"""

        puntos = [(92,"Hombros"),(130,"Brazos"),(165,"Cintura"),(196,"Cadera"),(300,"Muslos")]

    else:  # Hombre
        cc = "#86c9e8"
        ch = "#5aabb8"

        hair = f"""
        <path d="M52,24 C50,8 58,0 72,0 C82,-2 94,0 102,6 C110,12 114,22 112,32
                 C114,22 112,10 106,4 C114,12 116,24 114,36
                 C118,26 118,14 112,6 C120,16 120,30 116,44 L52,44 Z" fill="{ch}"/>"""

        head = f'<ellipse cx="80" cy="36" rx="27" ry="28" fill="{cc}"/>'
        neck = f'<path d="M72,62 L72,78 L88,78 L88,62 C88,68 85,72 80,72 C75,72 72,68 72,62 Z" fill="{cc}"/>'

        body = f"""
        <path d="
          M72,76 C58,76 38,80 28,92 C18,104 18,118 22,128
          C26,138 32,142 38,144 C34,156 34,166 36,176
          C38,184 40,190 38,198 C36,204 30,208 30,216
          L36,216 C36,230 38,268 38,280 L38,355
          C38,364 42,370 48,372 C54,374 60,370 62,364
          C64,358 64,350 64,344 L64,280
          C70,272 76,268 80,268 C84,268 90,272 96,280
          L96,344 C96,350 96,358 98,364 C100,370 106,374 112,372
          C118,370 122,364 122,355 L122,280
          C122,268 124,230 124,216 L130,216
          C130,208 124,204 122,198 C120,190 122,184 124,176
          C126,166 126,156 122,144 C128,142 134,138 138,128
          C142,118 142,104 132,92 C122,80 102,76 88,76 Z
        " fill="{cc}"/>"""

        arms = f"""
        <path d="M27,94 C16,100 10,114 8,130 L3,196 C2,206 4,213 8,215
                 L18,213 C16,207 16,198 18,188 L23,130 C25,118 30,106 36,98 Z" fill="{cc}"/>
        <path d="M133,94 C144,100 150,114 152,130 L157,196 C158,206 156,213 152,215
                 L142,213 C144,207 144,198 142,188 L137,130 C135,118 130,106 124,98 Z" fill="{cc}"/>"""

        feet = f"""
        <path d="M38,370 C36,374 34,378 36,382 L66,382 C68,378 66,372 64,370 Z" fill="{cc}"/>
        <path d="M96,370 C94,374 92,378 94,382 L124,382 C126,378 124,372 122,370 Z" fill="{cc}"/>"""

        puntos = [(90,"Hombros"),(116,"Pecho"),(132,"Brazos"),(168,"Cintura"),(198,"Cadera"),(300,"Muslos")]

    # Build measurement lines with numbered circles
    lc = "#9ca3af"
    lines_svg = ""
    for i, (y, label) in enumerate(puntos, 1):
        lines_svg += f"""
        <line x1="22" y1="{y}" x2="138" y2="{y}"
              stroke="{lc}" stroke-width="1.1" stroke-dasharray="5,4"/>
        <circle cx="22" cy="{y}" r="9" fill="#f3f4f6" stroke="{lc}" stroke-width="1"/>
        <text x="22" y="{y+4}" text-anchor="middle"
              font-size="8" fill="#374151" font-family="sans-serif" font-weight="600">{i}</text>
        <circle cx="138" cy="{y}" r="9" fill="#f3f4f6" stroke="{lc}" stroke-width="1"/>
        <text x="138" y="{y+4}" text-anchor="middle"
              font-size="8" fill="#374151" font-family="sans-serif" font-weight="600">{i}</text>"""

    # Legend
    legend = ""
    for i, (y, label) in enumerate(puntos, 1):
        legend += f'<text x="10" y="{22 + (i-1)*18}" font-size="10" fill="#374151" font-family="sans-serif"><tspan font-weight="600" fill="#6366f1">{i}.</tspan> {label}</text>'

    emoji = "👩 Mujer" if genero == "Mujer" else "👨 Hombre"

    return f"""<!DOCTYPE html>
<html><body style="margin:0;padding:0;background:#f9fafb;font-family:sans-serif;">
<div style="display:flex;align-items:flex-start;gap:12px;padding:12px;
            background:#f9fafb;border-radius:12px;border:1px solid #e5e7eb;">
  <div style="text-align:center;">
    <p style="font-size:11px;color:#6b7280;margin:0 0 6px 0;font-weight:600;">{emoji}</p>
    <svg viewBox="0 0 160 395" xmlns="http://www.w3.org/2000/svg"
         style="width:160px;height:auto;display:block;">
      {hair}
      {head}
      {neck}
      {body}
      {arms}
      {feet}
      {lines_svg}
    </svg>
  </div>
  <div style="padding-top:28px;">
    <p style="font-size:11px;color:#6b7280;margin:0 0 8px 0;font-weight:600;">Puntos de medición</p>
    <svg viewBox="0 0 120 {len(puntos)*18+10}" xmlns="http://www.w3.org/2000/svg"
         style="width:120px;height:auto;display:block;">
      {legend}
    </svg>
  </div>
</div>
</body></html>"""


def mostrar():
    estado.cargar_perfil()

    st.title("📊 Mis Medidas")
    st.caption("Los campos se pre-llenan con tu último registro guardado.")
    st.divider()

    # ── Datos generales ───────────────────────────────────────────────────
    st.subheader("Datos generales")
    g1, g2, g3, g4 = st.columns(4)

    with g1:
        genero = st.radio("Género", ["Mujer", "Hombre"],
                          index=0 if estado.get("genero","Mujer") == "Mujer" else 1,
                          horizontal=True)
        estado.set("genero", genero)

    with g2:
        hoy = date.today()
        fn_def = estado.get("fecha_nacimiento", None)
        if fn_def and isinstance(fn_def, str):
            try: fn_def = date.fromisoformat(fn_def)
            except: fn_def = None
        fn_def = fn_def or date(hoy.year-25, 1, 1)
        fecha_nac = st.date_input("Fecha de nacimiento", value=fn_def,
                                   min_value=date(1980, 1, 1),
                                   max_value=hoy-timedelta(days=365*10), format="DD/MM/YYYY")
        st.caption(f"Edad: **{calcular_edad(fecha_nac)} años**")

    with g3:
        peso_lbs = st.number_input("Peso (lbs)", 66.0, 440.0,
                                    estado.get("med_peso", 132.0), 0.5, format="%.1f")

    with g4:
        altura = st.number_input("Altura (cm)", 100.0, 220.0,
                                  estado.get("med_altura", 165.0), 0.5, format="%.1f")

    st.divider()

    # ── Silueta + Medidas ─────────────────────────────────────────────────
    col_sil, col_med = st.columns([1, 1], gap="large")

    with col_sil:
        st.subheader("Guía de medición")
        components.html(silhoueta_html(genero), height=480, scrolling=False)

    with col_med:
        st.subheader("Medidas corporales (cm)")

        # 2 por fila
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            hombros = st.number_input("Hombros", 50.0, 200.0,
                estado.get("med_hombros",100.0), 0.5, format="%.1f")
        with r1c2:
            label_pecho = "Pecho / Busto" if genero == "Mujer" else "Pecho"
            pecho = st.number_input(label_pecho, 50.0, 200.0,
                estado.get("med_pecho",90.0), 0.5, format="%.1f")

        r2c1, r2c2 = st.columns(2)
        with r2c1:
            brazo_der = st.number_input("Brazo derecho", 15.0, 60.0,
                estado.get("med_brazo_der",28.0), 0.5, format="%.1f")
        with r2c2:
            brazo_izq = st.number_input("Brazo izquierdo", 15.0, 60.0,
                estado.get("med_brazo_izq",28.0), 0.5, format="%.1f")

        r3c1, r3c2 = st.columns(2)
        with r3c1:
            cintura = st.number_input("Cintura", 40.0, 200.0,
                estado.get("med_cintura",75.0), 0.5, format="%.1f")
        with r3c2:
            cadera = st.number_input("Cadera", 50.0, 200.0,
                estado.get("med_cadera",95.0), 0.5, format="%.1f")

        r4c1, r4c2 = st.columns(2)
        with r4c1:
            muslo_der = st.number_input("Muslo derecho", 20.0, 100.0,
                estado.get("med_muslo_der",55.0), 0.5, format="%.1f")
        with r4c2:
            muslo_izq = st.number_input("Muslo izquierdo", 20.0, 100.0,
                estado.get("med_muslo_izq",55.0), 0.5, format="%.1f")

        notas = st.text_area("Notas", placeholder="Observaciones opcionales...", height=60)

    # ── Cálculos ──────────────────────────────────────────────────────────
    peso_kg = peso_lbs * LBS_A_KG
    imc     = calcular_imc(peso_kg, altura)
    rcc     = calcular_rcc(cintura, cadera)
    rel_hc  = calcular_rel_hombros_cintura(hombros, cintura)

    st.divider()
    st.subheader("Cálculos automáticos")
    m1, m2, m3 = st.columns(3)
    with m1:
        if imc:
            cat, _ = clasificar_imc(imc)
            st.metric("IMC", f"{imc}", cat)
    with m2:
        if rcc:
            cat, _ = clasificar_rcc_mujer(rcc)
            st.metric("Relación Cintura-Cadera", f"{rcc}", cat)
    with m3:
        if rel_hc:
            ref = "✅ Figura atlética" if rel_hc >= 1.4 else "Por mejorar"
            st.metric("Hombros / Cintura", f"{rel_hc}", ref)

    st.divider()

    # ── Guardar ───────────────────────────────────────────────────────────
    if st.button("💾 Guardar registro", type="primary", use_container_width=True):
        with st.spinner("Guardando..."):
            try:
                uid = estado.get("user_id", "")
                guardar_fila_usuario("medidas", [
                    str(date.today()), genero, str(fecha_nac), calcular_edad(fecha_nac),
                    float(peso_lbs), float(altura),
                    float(hombros), float(pecho),
                    float(cintura), float(cadera),
                    float(muslo_der), float(muslo_izq),
                    float(brazo_der), float(brazo_izq),
                    imc, rcc, rel_hc, notas.strip()
                ], uid)
                estado.set("genero", genero)
                estado.set("fecha_nacimiento", str(fecha_nac))
                estado.set("med_peso",     peso_lbs)
                estado.set("med_altura",   altura)
                estado.set("med_hombros",  hombros)
                estado.set("med_pecho",    pecho)
                estado.set("med_cintura",  cintura)
                estado.set("med_cadera",   cadera)
                estado.set("med_muslo_der", muslo_der)
                estado.set("med_muslo_izq", muslo_izq)
                estado.set("med_brazo_der", brazo_der)
                estado.set("med_brazo_izq", brazo_izq)
                st.success("✅ Registro guardado.")
                st.balloons()
            except Exception as e:
                st.error(f"Error al guardar: {e}")
                st.exception(e)


    # ── Historial ─────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("Registros")
    df = None
    try:
        uid = estado.get("user_id", "")
        df  = leer_df_usuario("medidas", uid)
        if not df.empty:
            cols = [c for c in df.columns if not c.startswith("_") and c != "user_id"]
            st.dataframe(df[cols].iloc[::-1].reset_index(drop=True),
                         use_container_width=True, hide_index=True)
            st.divider()
            seccion_eliminar("medidas", df, "registros de medidas")
        else:
            st.info("Aún no hay registros. ¡Agrega el primero arriba! 💪")
    except Exception as e:
        st.error(f"Error al cargar historial: {e}")
        st.exception(e)

    # ── Editar registro ────────────────────────────────────────────────────────
    if df is not None and not df.empty:
        st.divider()
        with st.expander("✏️ Editar un registro existente"):
            fechas    = df["fecha"].astype(str).tolist()
            fecha_sel = st.selectbox("Selecciona la fecha a editar", fechas, key="edit_fecha")
            fila_e    = df[df["fecha"].astype(str) == fecha_sel].iloc[0]
            fn_s      = int(fila_e["_fila_sheets"])

            st.caption(f"Editando registro del {fecha_sel}")
            e1, e2 = st.columns(2)
            with e1:
                eg  = st.radio("Género", ["Mujer","Hombre"],
                                index=0 if str(fila_e.get("genero","Mujer")) == "Mujer" else 1,
                                key="eg", horizontal=True)
                ep  = st.number_input("Peso (lbs)", 66.0, 440.0,
                                       float(fila_e.get("peso_lbs") or 132), 0.5, key="ep", format="%.1f")
                ea  = st.number_input("Altura (cm)", 100.0, 220.0,
                                       float(fila_e.get("altura_cm") or 165), 0.5, key="ea", format="%.1f")
                eh  = st.number_input("Hombros (cm)", 50.0, 200.0,
                                       float(fila_e.get("hombros_cm") or 100), 0.5, key="eh", format="%.1f")
                epc = st.number_input("Pecho/Busto (cm)", 50.0, 200.0,
                                       float(fila_e.get("pecho_cm") or 90), 0.5, key="epc", format="%.1f")
            with e2:
                ec  = st.number_input("Cintura (cm)", 40.0, 200.0,
                                       float(fila_e.get("cintura_cm") or 75), 0.5, key="ec", format="%.1f")
                eca = st.number_input("Cadera (cm)", 50.0, 200.0,
                                       float(fila_e.get("cadera_cm") or 95), 0.5, key="eca", format="%.1f")
                emd = st.number_input("Muslo derecho (cm)", 20.0, 100.0,
                                       float(fila_e.get("muslo_der_cm") or 55), 0.5, key="emd", format="%.1f")
                emi = st.number_input("Muslo izquierdo (cm)", 20.0, 100.0,
                                       float(fila_e.get("muslo_izq_cm") or 55), 0.5, key="emi", format="%.1f")
                ebd = st.number_input("Brazo derecho (cm)", 15.0, 60.0,
                                       float(fila_e.get("brazo_der_cm") or 28), 0.5, key="ebd", format="%.1f")
                ebi = st.number_input("Brazo izquierdo (cm)", 15.0, 60.0,
                                       float(fila_e.get("brazo_izq_cm") or 28), 0.5, key="ebi", format="%.1f")

            e_imc = calcular_imc(ep * LBS_A_KG, ea)
            e_rcc = calcular_rcc(ec, eca)
            e_rel = calcular_rel_hombros_cintura(eh, ec)

            if st.button("💾 Guardar cambios", type="primary", key="btn_edit"):
                uid2 = estado.get("user_id", "")
                valores = [
                    uid2, str(fila_e.get("fecha","")), eg,
                    str(fila_e.get("fecha_nacimiento","")),
                    fila_e.get("edad_calculada",""),
                    ep, ea, eh, epc, ec, eca, emd, emi, ebd, ebi,
                    e_imc, e_rcc, e_rel, str(fila_e.get("notas",""))
                ]
                try:
                    actualizar_fila_sheets("medidas", fn_s, valores)
                    st.success("✅ Registro actualizado.")
                    st.rerun()
                except Exception as ex:
                    st.error(f"Error al actualizar: {ex}")
