def resolver_valor_salario(salario_automático, salario_slider, salario_input, salario_config):
    if salario_automático:
        return int(salario_config or 0)

    return max(
        int(salario_slider or 0),
        int(salario_input or 0),
        int(salario_config or 0),
    )
