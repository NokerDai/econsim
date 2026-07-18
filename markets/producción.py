def producción(estado):
    duracion = estado.config.duración_contrato

    for trabajador in estado.trabajadores:
        if trabajador.contrato is not None:
            empresa = trabajador.contrato.empresa
            
            # Salario diario proporcional
            if trabajador.contrato.tipo == "formal":
                salario_diario = empresa.salario / duracion
            else:
                salario_diario = empresa.salario_informal / duracion

            # Intentar pagar la jornada
            if empresa.presupuesto >= salario_diario:
                empresa.presupuesto -= salario_diario
                trabajador.presupuesto += salario_diario
                
                # El trabajador produce porque cobró su día
                empresa.stock += 2 / duracion
                
                # El presupuesto disponible se va liberando progresivamente en la misma
                # medida que el compromiso futuro se convierte en gasto real ejecutado.
                empresa.presupuesto_disponible += salario_diario
            else:
                # Si la empresa quiebra/no puede pagar, se rescinde el contrato.
                # Devolvemos el presupuesto comprometido de los días que faltaban por cumplir.
                días_restantes = max(0, trabajador.contrato.vence - estado.día)
                compromiso_restante = salario_diario * días_restantes
                
                empresa.presupuesto_disponible += compromiso_restante
                
                empresa.empleados -= 1
                trabajador.contrato = None