def producción(estado):
    for empresa in estado.empresas:
        producción_hoy = empresa.empleados
        empresa.stock += producción_hoy