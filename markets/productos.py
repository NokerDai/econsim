# --- productos.py ---
from collections import deque

def mercado_productos(estado):
    productos_disponibles = []
    
    for empresa in estado.empresas:
        empresa.inventario = empresa.empleados_formales * estado.config.productividad_formal + empresa.empleados_informales * estado.config.productividad_informal
        empresa.unidades_vendidas = 0
        
        productos_disponibles.extend([empresa] * int(unidades_producidas))
        
    productos_disponibles.sort(key=lambda e: e.precio)
    cola_productos = deque(productos_disponibles)
    
    for trabajador in estado.trabajadores:
        
        while cola_productos and not comprado:
            siguiente_producto_mas_barato = cola_productos[0]
            
            if trabajador.presupuesto >= siguiente_producto_mas_barato.precio:
                empresa_vendedora = cola_productos.popleft()

                trabajador.presupuesto -= empresa_vendedora.precio
                empresa_vendedora.presupuesto += empresa_vendedora.precio

                empresa.inventario -= 1
                empresa_vendedora.unidades_vendidas += 1
            else:
                break

    for empresa in estado.empresas:
        empresa.precio *= estado.config.aumento_precio ** empresa.unidades_vendidas
        empresa.precio *= estado.config.reducción_precio ** empresa.inventario