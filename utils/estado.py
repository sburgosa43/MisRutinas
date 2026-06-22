"""
Gestión de estado global del usuario.
Carga los datos desde Google Sheets UNA sola vez por sesión
y los comparte en todos los módulos via st.session_state.
"""
import streamlit as st

DEFAULTS = {
    "genero":           "Mujer",
    "fecha_nacimiento": "",
    "med_peso":     132.0,
    "med_altura":   165.0,
    "med_edad":     25,
    "med_hombros":  100.0,
    "med_pecho":    90.0,
    "med_cintura":  75.0,
    "med_cadera":   95.0,
    "med_muslo_der": 55.0,
    "med_muslo_izq": 55.0,
    "med_brazo_der": 28.0,
    "med_brazo_izq": 28.0,
    "eval_objetivo": "",
    "eval_nivel":    "",
    "eval_dias":     3,
    "eval_equipo":   "",
    "eval_lesiones": "",
    "eval_duracion": "60 min",
    "nombre_usuario": "Mi Rutina",
}


def cargar_perfil():
    """Carga el perfil del usuario desde Sheets la primera vez en la sesión."""
    if st.session_state.get("_perfil_cargado"):
        return
    for k, v in DEFAULTS.items():
        st.session_state.setdefault(k, v)
    try:
        from utils.sheets import get_worksheet
        # Última medida
        filas = get_worksheet("medidas").get_all_records()
        if filas:
            u = filas[-1]
            _s("med_peso",     _f(u, "peso_lbs",     132.0))
            _s("med_altura",   _f(u, "altura_cm",    165.0))
            _s("med_edad",     _i(u, "edad",         25))
            _s("med_cintura",  _f(u, "cintura_cm",   75.0))
            _s("med_cadera",   _f(u, "cadera_cm",    95.0))
            _s("med_hombros",  _f(u, "hombros_cm",   100.0))
            _s("med_muslo_der",_f(u, "muslo_der_cm", 55.0))
            _s("med_muslo_izq",_f(u, "muslo_izq_cm", 55.0))
            _s("med_brazo_der",_f(u, "brazo_der_cm", 28.0))
            _s("med_brazo_izq",_f(u, "brazo_izq_cm", 28.0))
        # Última evaluación
        filas_e = get_worksheet("evaluacion").get_all_records()
        if filas_e:
            u = filas_e[-1]
            _s("eval_objetivo", u.get("objetivo", ""))
            _s("eval_nivel",    u.get("nivel", ""))
            _s("eval_dias",     _i(u, "dias_semana", 3))
            _s("eval_equipo",   u.get("equipo", ""))
            _s("eval_lesiones", u.get("lesiones", ""))
            _s("eval_duracion", u.get("duracion_sesion", "60 min"))
        # Config
        filas_c = get_worksheet("config").get_all_records()
        for row in filas_c:
            if row.get("clave") == "nombre_usuario":
                _s("nombre_usuario", row.get("valor", "Mi Rutina"))
    except Exception:
        pass
    st.session_state["_perfil_cargado"] = True


def refrescar():
    """Fuerza recarga del perfil desde Sheets en el próximo render."""
    st.session_state.pop("_perfil_cargado", None)


def get(key: str, default=None):
    return st.session_state.get(key, default if default is not None else DEFAULTS.get(key))


def set(key: str, value):
    if value is not None:
        st.session_state[key] = value


def _s(key, value):
    if value is not None:
        st.session_state[key] = value

def _f(d, k, default):
    try: return float(d.get(k, default) or default)
    except: return default

def _i(d, k, default):
    try: return int(d.get(k, default) or default)
    except: return default
