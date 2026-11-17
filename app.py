import math

import streamlit as st

# ---------------------------------------------------------------------------
# Configuración de la página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Calculadora 3D Colombia",
    page_icon="🖨️",
    layout="centered",
)

PRECIO_KWH_DEFECTO = 990.53  # COP/kWh (tarifa Enel Bogotá, nov 2026)


# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------
def formatear_cop(valor: float) -> str:
    """Formatea un número como pesos colombianos: $1.234.567"""
    return "$" + f"{round(valor):,}".replace(",", ".")


def redondear_arriba(valor: float, multiplo: int = 100) -> float:
    """Redondea hacia arriba al múltiplo indicado (precios más limpios)."""
    return math.ceil(valor / multiplo) * multiplo


def calcular_costos(
    gramos: float,
    horas: float,
    precio_kg: float,
    precio_kwh: float,
    potencia_w: float,
    precio_impresora: float,
    repuestos: float,
    vida_util_h: float,
    porc_fallas: float,
    minutos_trabajo: float,
    valor_hora_trabajo: float,
    insumos: float,
) -> dict:
    """Calcula cada componente del costo de producir la pieza."""
    material = (gramos / 1000) * precio_kg
    luz = (potencia_w / 1000) * horas * precio_kwh
    maquina = ((precio_impresora + repuestos) / vida_util_h) * horas
    base = material + luz + maquina
    fallas = base * (porc_fallas / 100)
    mano_obra = (minutos_trabajo / 60) * valor_hora_trabajo
    costo_total = base + fallas + mano_obra + insumos

    return {
        "Material (filamento)": material,
        "Electricidad": luz,
        "Desgaste de la máquina": maquina,
        "Margen por impresiones fallidas": fallas,
        "Mano de obra (post-proceso)": mano_obra,
        "Insumos / empaque": insumos,
        "total": costo_total,
    }


def calcular_precio(
    costo_total: float,
    margen_deseado: float,
    porc_impuestos: float,
    porc_comision: float = 0.0,
    cargo_fijo: float = 0.0,
):
    """
    Precio de venta para que, después de comisión, impuestos y costos,
    te quede el margen neto deseado SOBRE EL PRECIO.

    precio = (costo + cargo_fijo) / (1 - margen - impuestos - comisión)
    """
    denominador = 1 - margen_deseado - porc_impuestos - porc_comision
    if denominador <= 0:
        return None
    return (costo_total + cargo_fijo) / denominador


def ganancia_neta(
    precio: float,
    costo_total: float,
    porc_impuestos: float,
    porc_comision: float = 0.0,
    cargo_fijo: float = 0.0,
) -> float:
    """Lo que realmente te queda después de todo."""
    return precio * (1 - porc_impuestos - porc_comision) - cargo_fijo - costo_total


# ---------------------------------------------------------------------------
# Barra lateral: parámetros del negocio (se configuran una sola vez)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Parámetros del negocio")

    st.subheader("Electricidad")
    precio_kwh = st.number_input(
        "Precio del kWh (COP)",
        min_value=0.0,
        value=PRECIO_KWH_DEFECTO,
        step=10.0,
        help="Míralo en tu factura. Si consumes más de 130 kWh/mes "
        "(estrato 3), el kWh extra se paga a la tarifa completa.",
    )
    potencia_w = st.number_input(
        "Consumo promedio de la impresora (W)",
        min_value=1.0,
        value=120.0,
        step=10.0,
        help="Mídelo con un enchufe inteligente con medidor de energía.",
    )

    st.subheader("Máquina")
    precio_impresora = st.number_input(
        "Precio de la impresora (COP)",
        min_value=0.0,
        value=0.0,
        step=100000.0,
        help="Para recuperar la inversión. Si lo dejas en 0, no la recuperas.",
    )
    repuestos = st.number_input(
        "Costo de repuestos durante su vida útil (COP)",
        min_value=0.0,
        value=600000.0,
        step=50000.0,
        help="Boquillas, cama, correas, ventiladores, etc.",
    )
    vida_util_h = st.number_input(
        "Vida útil de la máquina (horas)",
        min_value=1.0,
        value=4320.0,
        step=100.0,
    )

    st.subheader("Riesgos y trabajo")
    porc_fallas = st.number_input(
        "Margen por impresiones fallidas (%)",
        min_value=0.0,
        max_value=100.0,
        value=10.0,
        step=1.0,
        help="Recomendado 10-15 % mientras aprendes.",
    )
    minutos_trabajo = st.number_input(
        "Tiempo de trabajo por pieza (min)",
        min_value=0.0,
        value=10.0,
        step=5.0,
        help="Preparar el archivo, quitar soportes, lijar, empacar, atender al cliente.",
    )
    valor_hora_trabajo = st.number_input(
        "Valor de tu hora de trabajo (COP)",
        min_value=0.0,
        value=10000.0,
        step=1000.0,
    )
    insumos = st.number_input(
        "Insumos / empaque por pieza (COP)",
        min_value=0.0,
        value=0.0,
        step=500.0,
        help="Caja, bolsa, cinta, tarjeta, etc.",
    )

    st.subheader("Ventas")
    margen_deseado_pct = st.slider(
        "Ganancia neta deseada (% del precio)",
        min_value=10,
        max_value=80,
        value=40,
        help="Es el porcentaje del precio de venta que quieres que te quede "
        "limpio, después de todos los costos.",
    )
    porc_impuestos_pct = st.number_input(
        "Reserva para impuestos (% del precio)",
        min_value=0.0,
        max_value=50.0,
        value=0.0,
        step=0.5,
        help="Si ya declaras renta/IVA, aparta un porcentaje aquí. "
        "Consulta con un contador.",
    )
    porc_comision_pct = st.number_input(
        "Comisión de MercadoLibre (%)",
        min_value=0.0,
        max_value=50.0,
        value=15.0,
        step=0.5,
        help="Varía por categoría. Revisa la tuya en MercadoLibre.",
    )
    cargo_fijo_ml = st.number_input(
        "Cargo fijo / envío que asumes en MercadoLibre (COP)",
        min_value=0.0,
        value=0.0,
        step=500.0,
    )

# ---------------------------------------------------------------------------
# Pantalla principal: datos de la pieza
# ---------------------------------------------------------------------------
st.title("🖨️ Calculadora 3D Colombia")
st.caption("Calcula cuánto cobrar para que cada pieza deje ganancia real.")

st.subheader("Datos de la pieza")

precio_kg = st.number_input(
    "Precio del filamento (COP por kg)",
    min_value=0.0,
    value=60000.0,
    step=1000.0,
)

col_h, col_m = st.columns(2)
with col_h:
    horas_imp = st.number_input("Horas de impresión", min_value=0, value=2, step=1)
with col_m:
    minutos_imp = st.number_input(
        "Minutos adicionales", min_value=0, max_value=59, value=24, step=5
    )

gramos = st.number_input(
    "Gramos de filamento usados (incluye soportes)",
    min_value=0.0,
    value=49.0,
    step=1.0,
    help="Tu laminador (Bambu Studio) te lo muestra al cortar la pieza.",
)

cantidad = st.number_input(
    "Cantidad de piezas del pedido", min_value=1, value=1, step=1
)

# ---------------------------------------------------------------------------
# Cálculos
# ---------------------------------------------------------------------------
horas_totales = horas_imp + minutos_imp / 60
margen_deseado = margen_deseado_pct / 100
porc_impuestos = porc_impuestos_pct / 100
porc_comision = porc_comision_pct / 100

if gramos <= 0 or horas_totales <= 0:
    st.info("Ingresa los gramos y el tiempo de impresión para ver el resultado.")
    st.stop()

costos = calcular_costos(
    gramos=gramos,
    horas=horas_totales,
    precio_kg=precio_kg,
    precio_kwh=precio_kwh,
    potencia_w=potencia_w,
    precio_impresora=precio_impresora,
    repuestos=repuestos,
    vida_util_h=vida_util_h,
    porc_fallas=porc_fallas,
    minutos_trabajo=minutos_trabajo,
    valor_hora_trabajo=valor_hora_trabajo,
    insumos=insumos,
)
costo_total = costos["total"]

precio_directo_bruto = calcular_precio(
    costo_total, margen_deseado, porc_impuestos
)
precio_ml_bruto = calcular_precio(
    costo_total, margen_deseado, porc_impuestos, porc_comision, cargo_fijo_ml
)

if precio_directo_bruto is None or precio_ml_bruto is None:
    st.error(
        "La suma de ganancia deseada, impuestos y comisión es 100 % o más. "
        "Baja alguno de esos porcentajes en la barra lateral."
    )
    st.stop()

precio_directo = redondear_arriba(precio_directo_bruto)
precio_ml = redondear_arriba(precio_ml_bruto)
punto_equilibrio = redondear_arriba(costo_total / (1 - porc_impuestos))

ganancia_directo = ganancia_neta(precio_directo, costo_total, porc_impuestos)
ganancia_ml = ganancia_neta(
    precio_ml, costo_total, porc_impuestos, porc_comision, cargo_fijo_ml
)

# ---------------------------------------------------------------------------
# Resultados
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Resultado")

if precio_impresora == 0:
    st.warning(
        "No pusiste el precio de la impresora: el cálculo no incluye "
        "recuperar la inversión de la máquina."
    )

tab_directo, tab_ml = st.tabs(["💬 Venta directa", "🛒 MercadoLibre"])

with tab_directo:
    st.metric("Cobra por pieza", formatear_cop(precio_directo))
    c1, c2 = st.columns(2)
    c1.metric("Ganancia neta por pieza", formatear_cop(ganancia_directo))
    c2.metric(
        "Ganancia por hora de impresora",
        formatear_cop(ganancia_directo / horas_totales),
    )
    if cantidad > 1:
        st.success(
            f"Pedido de {cantidad} piezas: cobra **{formatear_cop(precio_directo * cantidad)}** "
            f"(ganancia neta {formatear_cop(ganancia_directo * cantidad)})."
        )

with tab_ml:
    st.metric("Publica en MercadoLibre a", formatear_cop(precio_ml))
    c1, c2 = st.columns(2)
    c1.metric("Ganancia neta por pieza", formatear_cop(ganancia_ml))
    c2.metric(
        "Ganancia por hora de impresora",
        formatear_cop(ganancia_ml / horas_totales),
    )
    if cantidad > 1:
        st.success(
            f"Pedido de {cantidad} piezas: {formatear_cop(precio_ml * cantidad)} "
            f"(ganancia neta {formatear_cop(ganancia_ml * cantidad)})."
        )

st.error(
    f"⛔ **Precio mínimo (punto de equilibrio): {formatear_cop(punto_equilibrio)}**. "
    "Por debajo de esto pierdes dinero."
)

st.caption(
    f"El precio de venta directa equivale a {precio_directo / costo_total:.1f} veces "
    f"el costo de producción."
)

# ---------------------------------------------------------------------------
# Desglose de costos
# ---------------------------------------------------------------------------
with st.expander("📊 Ver desglose de costos"):
    filas = []
    for concepto, valor in costos.items():
        if concepto == "total":
            continue
        filas.append(
            {
                "Concepto": concepto,
                "Valor": formatear_cop(valor),
                "% del costo": f"{valor / costo_total * 100:.1f} %",
            }
        )
    filas.append(
        {
            "Concepto": "COSTO TOTAL",
            "Valor": formatear_cop(costo_total),
            "% del costo": "100 %",
        }
    )
    st.table(filas)

    st.write(
        f"Energía consumida: **{potencia_w / 1000 * horas_totales:.2f} kWh** "
        f"({horas_totales:.2f} h a {potencia_w:.0f} W)."
    )

st.caption(
    "Esta herramienta es una guía de costeo y no reemplaza la asesoría de un contador. "
    "Revisa los precios de piezas similares en el mercado antes de publicar."
)
