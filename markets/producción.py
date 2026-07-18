# --- producción.py ---

def producción(estado):
    duracion = estado.config.duración_contrato

    for trabajador in estado.trabajadores:
        if trabajador.contrato is not None:
            empresa = trabajador.contrato.empresa
            
            if trabajador.contrato.tipo == "formal":
                salario_diario = empresa.salario / duracion
            else:
                salario_diario = empresa.salario_informal / duracion

            if empresa.presupuesto >= salario_diario:
                empresa.presupuesto -= salario_diario
                trabajador.presupuesto += salario_diario
                empresa.stock += 1
            else:
                empresa.empleados -= 1
                trabajador.contrato = None