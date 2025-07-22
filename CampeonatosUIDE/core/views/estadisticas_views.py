from django.shortcuts import render



# ========================
# ESTADÍSTICAS
# ========================

def estadisticas_futbol(request):
    # Renderiza la plantilla 'estadisticas_futbol.html' para mostrar las estadísticas de fútbol
    return render(request, 'estadisticas/estadisticas_futbol.html')

def estadisticas_basquet(request):
    # Renderiza la plantilla 'estadisticas_basquet.html' para mostrar las estadísticas de baloncesto
    return render(request, 'estadisticas/estadisticas_basquet.html')

def estadisticas_ecuaboly(request):
    # Renderiza la plantilla 'estadisticas_ecuaboly.html' para mostrar las estadísticas de Ecuaboly
    return render(request, 'estadisticas/estadisticas_ecuaboly.html')

def estadisticas_ajedrez(request):
    # Renderiza la plantilla 'estadisticas_ajedrez.html' para mostrar las estadísticas de ajedrez
    return render(request, 'estadisticas/estadisticas_ajedrez.html')

def estadisticas_futbolin(request):
    # Renderiza la plantilla 'estadisticas_futbolin.html' para mostrar las estadísticas de futbolín
    return render(request, 'estadisticas/estadisticas_futbolin.html')

def estadisticas_pingpong(request):
    # Renderiza la plantilla 'estadisticas_pingpong.html' para mostrar las estadísticas de ping pong
    return render(request, 'estadisticas/estadisticas_pingpong.html')

def estadisticas_tenis(request):
    # Renderiza la plantilla 'estadisticas_tenis.html' para mostrar las estadísticas de tenis
    return render(request, 'estadisticas/estadisticas_tenis.html')

def estadisticas_videojuegos(request):
    # Renderiza la plantilla 'estadisticas_videojuegos.html' para mostrar las estadísticas de videojuegos
    return render(request, 'estadisticas/estadisticas_videojuegos.html')
