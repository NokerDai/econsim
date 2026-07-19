# --- productos.py ---
from collections import deque

def mercado_productos(estado):
    productos_disponibles = []
    
    for empresa in estado.empresas:
        unidades_producidas = empresa.empleados_formales + empresa.empleados_informales
        
        empresa.inventario = unidades_producidas
        empresa.unidades_vendidas = 0
        
        productos_disponibles.extend([empresa] * unidades_producidas)
        
    productos_disponibles.sort(key=lambda e: e.precio)
    cola_productos = deque(productos_disponibles)
    
    
    for trabajador in estado.trabajadores:
        comprado = False
        
        while cola_productos and not comprado:
            siguiente_producto_mas_barato = cola_productos[0]
            
            if trabajador.presupuesto >= siguiente_producto_mas_barato.precio:
                empresa_vendedora = cola_productos.popleft()
                
                trabajador.presupuesto -= empresa_vendedora.precio
                empresa_vendedora.presupuesto += empresa_vendedora.precio
                
                empresa_vendedora.unidades_vendidas += 1
                comprado = True
            else:
                break

    for empresa in estado.empresas:
        if empresa.inventario > 0 and empresa.unidades_vendidas == empresa.inventario:
            empresa.precio *= estado.config.aumento_precio
        elif empresa.unidades_vendidas < (empresa.inventario / 2):
            empresa.precio *= estado.config.reducción_precio