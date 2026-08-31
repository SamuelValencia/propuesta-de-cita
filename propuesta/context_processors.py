PASOS = [
    (1, "Datos"),
    (2, "Fecha"),
    (3, "Actividad"),
    (4, "Cena"),
    (5, "Cita"),
]


def pasos_progreso(request):
    return {"pasos": PASOS}
