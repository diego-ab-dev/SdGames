from django import template

register = template.Library()

@register.filter
def formato_chileno(valor):
    """
    Formatea un número al estilo chileno:
    - Punto para los miles
    - Coma para los decimales (si corresponde)
    """
    if not isinstance(valor, (int, float)):
        return valor  # Devolver el valor original si no es un número
    return f"{valor:,.0f}".replace(",", ".")


@register.filter
def multiply(value, arg):
    return value * arg