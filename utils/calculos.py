def calcular_imc(peso_kg: float, altura_cm: float):
    if altura_cm <= 0 or peso_kg <= 0:
        return None
    altura_m = altura_cm / 100
    return round(peso_kg / (altura_m ** 2), 1)


def clasificar_imc(imc: float):
    if imc < 18.5:
        return "Bajo peso", "#f59e0b"
    elif imc < 25.0:
        return "Peso normal ✅", "#10b981"
    elif imc < 30.0:
        return "Sobrepeso", "#f59e0b"
    elif imc < 35.0:
        return "Obesidad I", "#ef4444"
    else:
        return "Obesidad II+", "#dc2626"


def calcular_rcc(cintura_cm: float, cadera_cm: float):
    if cadera_cm <= 0 or cintura_cm <= 0:
        return None
    return round(cintura_cm / cadera_cm, 3)


def clasificar_rcc_mujer(rcc: float):
    if rcc < 0.80:
        return "Bajo riesgo ✅", "#10b981"
    elif rcc < 0.85:
        return "Riesgo moderado", "#f59e0b"
    else:
        return "Riesgo alto", "#ef4444"


def calcular_rel_hombros_cintura(hombros_cm: float, cintura_cm: float):
    if cintura_cm <= 0 or hombros_cm <= 0:
        return None
    return round(hombros_cm / cintura_cm, 3)
