import math

import streamlit as st

# ---------------------------------------------------------------------------
# Configuración de la página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Francia · Calculadora 3D",
    page_icon="🖨️",
    layout="centered",
    initial_sidebar_state="expanded",
)

PRECIO_KWH_DEFECTO = 990.53  # COP/kWh (tarifa Enel Bogotá, nov 2026)

# ---------------------------------------------------------------------------
# Estilos (CSS)
# ---------------------------------------------------------------------------
ESTILOS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,800&family=DM+Sans:wght@400;500;700&display=swap');

:root{
  --bg:#0E0B13; --card:#181321; --card2:#1F1829; --borde:#2E2540;
  --texto:#F4F0FA; --suave:#A79CBA;
  --rosa:#FF5A7A; --ambar:#FFB020; --violeta:#7C5CFF; --menta:#2DD4BF;
}
html, body, .stApp, [class*="css"]{ font-family:'DM Sans', sans-serif; }
.stApp{
  background:
    radial-gradient(1100px 500px at 85% -10%, rgba(255,90,122,.18), transparent 60%),
    radial-gradient(900px 500px at -10% 10%, rgba(124,92,255,.16), transparent 55%),
    var(--bg);
}
#MainMenu, footer{ visibility:hidden; }
header[data-testid="stHeader"]{ background:transparent; }
.block-container{ padding-top:1.4rem; max-width:760px; }
section[data-testid="stSidebar"]{ background:#120E1A; border-right:1px solid var(--borde); }

/* Campos de texto y números */
div[data-baseweb="input"] > div, div[data-baseweb="base-input"]{
  background:var(--card2) !important; border-radius:12px !important;
}
button[data-baseweb="tab"]{ font-weight:700; font-size:15px; }

/* Encabezado */
.hero{
  position:relative; overflow:hidden; border-radius:26px; padding:28px 26px;
  margin-bottom:10px; border:1px solid var(--borde);
  background:linear-gradient(135deg, rgba(255,90,122,.18), rgba(124,92,255,.16)), var(--card);
}
.hero::before{
  content:""; position:absolute; inset:0; pointer-events:none;
  background-image:repeating-linear-gradient(0deg, rgba(255,255,255,.06) 0 1px, transparent 1px 7px);
  -webkit-mask-image:linear-gradient(90deg, transparent 25%, #000);
  mask-image:linear-gradient(90deg, transparent 25%, #000);
}
.marca{ position:relative; display:flex; align-items:center; gap:16px; }
.logo{
  width:64px; height:64px; border-radius:20px; display:grid; place-items:center;
  font-family:'Fraunces',serif; font-weight:800; font-size:38px; color:#fff;
  background:linear-gradient(135deg, var(--rosa), var(--violeta));
  box-shadow:0 10px 30px rgba(255,90,122,.40);
}
.nombre{ font-family:'Fraunces',serif; font-weight:800; font-size:42px; line-height:1; letter-spacing:-.5px; color:var(--texto); }
.lema{ color:var(--suave); font-size:14px; margin-top:7px; }

/* Títulos de sección */
.seccion{
  display:flex; align-items:center; gap:12px; margin:28px 0 12px;
  font-family:'Fraunces',serif; font-weight:600; font-size:24px; color:var(--texto);
}
.seccion .num{
  width:30px; height:30px; border-radius:50%; display:grid; place-items:center;
  font-family:'DM Sans',sans-serif; font-weight:700; font-size:14px; color:#fff;
  background:linear-gradient(135deg, var(--rosa), var(--violeta));
}

/* Tarjeta de precio */
.precio-card{
  border-radius:26px; padding:26px; color:#fff;
  background:linear-gradient(135deg, #FF5A7A 0%, #B04CFF 60%, #7C5CFF 100%);
  box-shadow:0 20px 50px rgba(124,92,255,.30);
}
.precio-etq{ font-size:12px; text-transform:uppercase; letter-spacing:.16em; opacity:.88; font-weight:700; }
.precio-valor{ font-family:'Fraunces',serif; font-weight:800; font-size:58px; line-height:1.05; margin:8px 0 14px; }
.chips{ display:flex; flex-wrap:wrap; gap:8px; }
.chip{ background:rgba(255,255,255,.20); border-radius:999px; padding:6px 13px; font-size:13px; font-weight:500; }

/* Métricas */
.rejilla{ display:grid; grid-template-columns:repeat(auto-fit, minmax(160px, 1fr)); gap:12px; margin-top:14px; }
.metrica{ background:var(--card); border:1px solid var(--borde); border-radius:18px; padding:14px 16px; }
.metrica .t{ color:var(--suave); font-size:12px; }
.metrica .v{ font-family:'Fraunces',serif; font-weight:600; font-size:25px; margin-top:4px; color:var(--texto); }

/* Precio mínimo */
.piso{
  margin-top:14px; border-radius:16px; padding:14px 16px; color:var(--texto);
  border:1px solid rgba(255,90,122,.45); background:rgba(255,90,122,.08); font-size:14px;
}
.piso b{ color:#FF8FA5; font-size:16px; }

/* Desglose */
.panel{ background:var(--card); border:1px solid var(--borde); border-radius:20px; padding:18px 18px 8px; }
.barra{ display:flex; height:16px; border-radius:999px; overflow:hidden; background:var(--card2); margin-bottom:12px; }
.barra div{ height:100%; }
.item{
  display:grid; grid-template-columns:14px 1fr auto 52px; gap:10px; align-items:center;
  padding:9px 0; border-bottom:1px solid var(--borde); font-size:14px; color:var(--texto);
}
.item:last-child{ border-bottom:none; }
.item .punto{ width:10px; height:10px; border-radius:50%; display:inline-block; }
.item .v{ font-weight:700; }
.item .p{ color:var(--suave); text-align:right; font-size:13px; }
.item.total{ font-weight:700; }
.nota{ color:var(--suave); font-size:13px; margin:10px 2px 0; }
.aviso{
  border-radius:14px; padding:12px 14px; font-size:14px; margin:12px 0;
  border:1px solid rgba(255,176,32,.5); background:rgba(255,176,32,.09); color:var(--texto);
}
.pie{ text-align:center; color:var(--suave); font-size:12px; margin:34px 0 8px; }
.pie b{ font-family:'Fraunces',serif; color:var(--texto); font-size:15px; }
</style>
"""
st.markdown(ESTILOS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------
def formatear_cop(valor: float, para_html: bool = False) -> str:
    """Formatea pesos colombianos ($1.234.567). En HTML usa &#36; para que
    Streamlit no interprete el signo $ como fórmula matemática."""
    signo = "&#36;" if para_html else "$"
    return signo + f"{round(valor):,}".replace(",", ".")


def redondear_arriba(valor: float, multiplo: int = 100) -> float:
    """Redondea hacia arriba al múltiplo indicado (precios más limpios)."""
    return math.ceil(valor / multiplo) * multiplo


def mostrar_html(texto: str) -> None:
    """Muestra HTML sin que el markdown lo trate como bloque de código."""
    compacto = "".join(linea.strip() for linea in texto.strip().splitlines())
    st.markdown(compacto, unsafe_allow_html=True)


def etiqueta_margen(porcentaje: float) -> str:
    if porcentaje < 15:
        return "Muy ajustado"
    if porcentaje < 30:
        return "Competitivo"
    if porcentaje < 45:
        return "Saludable"
    return "Premium"


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
    """Calcula cada componente del costo de producir UNA pieza."""
    material = (gramos / 1000) * precio_kg
    luz = (potencia_w / 1000) * horas * precio_kwh
    maquina = ((precio_impresora + repuestos) / vida_util_h) * horas
    base = material + luz + maquina
    fallas = base * (porc_fallas / 100)
    mano_obra = (minutos_trabajo / 60) * valor_hora_trabajo
    total = base + fallas + mano_obra + insumos
    return {
        "material": material,
        "luz": luz,
        "maquina": maquina,
        "fallas": fallas,
        "mano_obra": mano_obra,
        "insumos": insumos,
        "total": total,
    }


def calcular_precio(
    costo_total: float,
    margen_deseado: float,
    porc_impuestos: float,
    porc_comision: float = 0.0,
    cargo_fijo: float = 0.0,
):
    """
    Precio para que, después de comisión, impuestos y costos, te quede el
    margen neto deseado SOBRE EL PRECIO:
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


def tarjeta_resultado(
    etiqueta: str,
    precio: float,
    ganancia: float,
    horas_pieza: float,
    costo_total: float,
    piso: float,
    cantidad: int,
) -> None:
    """Dibuja la tarjeta grande de precio, las métricas y el precio mínimo."""
    margen_real = ganancia / precio * 100 if precio else 0
    extra_pedido = ""
    if cantidad > 1:
        extra_pedido = (
            '<div class="metrica"><div class="t">Total del pedido (' + str(cantidad) + ' piezas)</div>'
            '<div class="v">' + formatear_cop(precio * cantidad, True) + "</div></div>"
            '<div class="metrica"><div class="t">Ganancia del pedido</div>'
            '<div class="v">' + formatear_cop(ganancia * cantidad, True) + "</div></div>"
        )
    mostrar_html(
        f"""
        <div class="precio-card">
          <div class="precio-etq">{etiqueta}</div>
          <div class="precio-valor">{formatear_cop(precio, True)}</div>
          <div class="chips">
            <span class="chip">Ganancia {formatear_cop(ganancia, True)} por pieza</span>
            <span class="chip">{margen_real:.0f} % del precio</span>
            <span class="chip">{etiqueta_margen(margen_real)}</span>
          </div>
        </div>
        <div class="rejilla">
          <div class="metrica"><div class="t">Costo de producción</div>
            <div class="v">{formatear_cop(costo_total, True)}</div></div>
          <div class="metrica"><div class="t">Ganancia por hora de impresora</div>
            <div class="v">{formatear_cop(ganancia / horas_pieza, True)}</div></div>
          {extra_pedido}
        </div>
        <div class="piso">⛔ Precio mínimo para no perder: <b>{formatear_cop(piso, True)}</b>.
          Por debajo de este valor, la pieza te cuesta plata.</div>
        """
    )


# ---------------------------------------------------------------------------
# Barra lateral: configuración del negocio (se ajusta una sola vez)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Configuración de Francia")
    st.caption("Ajusta esto una vez; la calculadora lo usa en cada pieza.")

    st.markdown("**⚡ Electricidad**")
    precio_kwh = st.number_input(
        "Precio del kWh (COP)",
        min_value=0.0,
        value=PRECIO_KWH_DEFECTO,
        step=10.0,
        help="Míralo en tu factura. Si pasas de 130 kWh al mes (estrato 3), "
        "el kWh extra se paga a la tarifa completa.",
    )
    potencia_w = st.number_input(
        "Consumo promedio de la impresora (W)",
        min_value=1.0,
        value=120.0,
        step=10.0,
        help="Mídelo con un enchufe inteligente con medidor de energía. "
        "Con la cámara caliente (ABS, ASA, nylon) el consumo sube.",
    )

    st.markdown("**🖨️ Máquina (Bambu Lab X2D)**")
    precio_impresora = st.number_input(
        "Precio de la impresora (COP)",
        min_value=0.0,
        value=4400000.0,
        step=100000.0,
        help="Lo que pagaste por ella. Con 0 no recuperas la inversión.",
    )
    repuestos = st.number_input(
        "Repuestos durante su vida útil (COP)",
        min_value=0.0,
        value=1000000.0,
        step=50000.0,
        help="Boquillas y hotends, láminas PEI, ventiladores, correas, "
        "tubos PTFE, filtros. Estimado: 800.000 a 1.400.000.",
    )
    vida_util_h = st.number_input(
        "Vida útil de la máquina (horas)",
        min_value=1.0,
        value=6000.0,
        step=500.0,
        help="Las X1 y P1S de Bambu Lab superan las 10.000 h según usuarios. "
        "La X2D es nueva, así que 6.000 h es una cifra prudente.",
    )

    st.markdown("**🛡️ Riesgos y trabajo**")
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
        value=0.0,
        step=5.0,
        help="Quitar soportes, lijar, empacar, atender al cliente.",
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

    st.markdown("**💰 Ventas**")
    margen_deseado_pct = st.slider(
        "Ganancia neta deseada (% del precio)",
        min_value=10,
        max_value=80,
        value=25,
        help="Lo que quieres que te quede limpio de cada venta, "
        "después de todos los costos.",
    )
    st.caption(f"Nivel: **{etiqueta_margen(margen_deseado_pct)}**")
    porc_impuestos_pct = st.number_input(
        "Reserva para impuestos (% del precio)",
        min_value=0.0,
        max_value=50.0,
        value=0.0,
        step=0.5,
        help="Si declaras renta o IVA, aparta un porcentaje. Consulta con un contador.",
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
        "Cargo fijo / envío en MercadoLibre (COP)",
        min_value=0.0,
        value=0.0,
        step=500.0,
    )

# ---------------------------------------------------------------------------
# Encabezado
# ---------------------------------------------------------------------------
mostrar_html(
    """
    <div class="hero">
      <div class="marca">
        <div class="logo">F</div>
        <div>
          <div class="nombre">Francia</div>
          <div class="lema">Impresión 3D · Cada pieza, hecha con cariño.</div>
        </div>
      </div>
    </div>
    """
)

# ---------------------------------------------------------------------------
# Paso 1: datos de la pieza
# ---------------------------------------------------------------------------
mostrar_html('<div class="seccion"><span class="num">1</span>Tu pieza</div>')

precio_kg = st.number_input(
    "Precio del filamento (COP por kg)",
    min_value=0.0,
    value=60000.0,
    step=1000.0,
    key="precio_kg",
)

col_h, col_m = st.columns(2)
with col_h:
    horas_imp = st.number_input(
        "Horas de impresión", min_value=0, value=2, step=1, key="horas"
    )
with col_m:
    minutos_imp = st.number_input(
        "Minutos adicionales", min_value=0, max_value=59, value=24, step=5, key="minutos"
    )

gramos = st.number_input(
    "Gramos de filamento (incluye soportes y purga)",
    min_value=0.0,
    value=49.0,
    step=1.0,
    help="Tu laminador (Bambu Studio) te lo muestra al cortar la pieza.",
    key="gramos",
)

cantidad = st.number_input(
    "Cantidad de piezas del pedido", min_value=1, value=1, step=1, key="cantidad"
)

base_datos = "Una sola pieza"
if cantidad > 1:
    base_datos = st.radio(
        "Los gramos y el tiempo que ingresaste son de…",
        ["Una sola pieza", "Todo el pedido"],
        horizontal=True,
        key="base_datos",
        help="Si Bambu Studio te dio el total de la cama con varias piezas, "
        "elige «Todo el pedido» y se reparte entre las piezas.",
    )

# ---------------------------------------------------------------------------
# Cálculos
# ---------------------------------------------------------------------------
horas_totales = horas_imp + minutos_imp / 60

if gramos <= 0 or horas_totales <= 0:
    st.info("Ingresa los gramos y el tiempo de impresión para ver el precio.")
    st.stop()

if base_datos == "Todo el pedido":
    gramos_pieza = gramos / cantidad
    horas_pieza = horas_totales / cantidad
else:
    gramos_pieza = gramos
    horas_pieza = horas_totales

margen_deseado = margen_deseado_pct / 100
porc_impuestos = porc_impuestos_pct / 100
porc_comision = porc_comision_pct / 100

costos = calcular_costos(
    gramos=gramos_pieza,
    horas=horas_pieza,
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

precio_directo_bruto = calcular_precio(costo_total, margen_deseado, porc_impuestos)
precio_ml_bruto = calcular_precio(
    costo_total, margen_deseado, porc_impuestos, porc_comision, cargo_fijo_ml
)

if precio_directo_bruto is None or precio_ml_bruto is None:
    st.error(
        "La suma de ganancia deseada, impuestos y comisión llega a 100 % o más. "
        "Baja alguno de esos porcentajes en la barra lateral."
    )
    st.stop()

precio_directo = redondear_arriba(precio_directo_bruto)
precio_ml = redondear_arriba(precio_ml_bruto)

piso_directo = redondear_arriba(costo_total / (1 - porc_impuestos))
piso_ml = redondear_arriba(
    (costo_total + cargo_fijo_ml) / (1 - porc_impuestos - porc_comision)
)

ganancia_directo = ganancia_neta(precio_directo, costo_total, porc_impuestos)
ganancia_ml = ganancia_neta(
    precio_ml, costo_total, porc_impuestos, porc_comision, cargo_fijo_ml
)

# ---------------------------------------------------------------------------
# Paso 2: precio
# ---------------------------------------------------------------------------
mostrar_html('<div class="seccion"><span class="num">2</span>Tu precio</div>')

if precio_impresora == 0:
    mostrar_html(
        '<div class="aviso">⚠️ No pusiste el precio de la impresora: el cálculo '
        "no incluye recuperar su inversión.</div>"
    )

tab_directo, tab_ml = st.tabs(["💬 Venta directa", "🛒 MercadoLibre"])

with tab_directo:
    tarjeta_resultado(
        "Cobra por pieza",
        precio_directo,
        ganancia_directo,
        horas_pieza,
        costo_total,
        piso_directo,
        int(cantidad),
    )

with tab_ml:
    tarjeta_resultado(
        "Publica en MercadoLibre a",
        precio_ml,
        ganancia_ml,
        horas_pieza,
        costo_total,
        piso_ml,
        int(cantidad),
    )

# ---------------------------------------------------------------------------
# Paso 3: desglose
# ---------------------------------------------------------------------------
mostrar_html('<div class="seccion"><span class="num">3</span>¿En qué se va el costo?</div>')

segmentos = [
    ("Material (filamento)", costos["material"], "#FF5A7A"),
    ("Electricidad", costos["luz"], "#FFB020"),
    ("Desgaste de la máquina", costos["maquina"], "#7C5CFF"),
    ("Impresiones fallidas", costos["fallas"], "#2DD4BF"),
    ("Mano de obra", costos["mano_obra"], "#60A5FA"),
    ("Insumos / empaque", costos["insumos"], "#94A3B8"),
]

barra = "".join(
    f'<div style="width:{valor / costo_total * 100:.2f}%;background:{color}"></div>'
    for _, valor, color in segmentos
    if valor > 0
)
leyenda = "".join(
    f'<div class="item"><span class="punto" style="background:{color}"></span>'
    f"<span>{nombre}</span><span class=\"v\">{formatear_cop(valor, True)}</span>"
    f'<span class="p">{valor / costo_total * 100:.0f} %</span></div>'
    for nombre, valor, color in segmentos
    if valor > 0
)
energia_kwh = potencia_w / 1000 * horas_pieza

mostrar_html(
    f"""
    <div class="panel">
      <div class="barra">{barra}</div>
      {leyenda}
      <div class="item total"><span></span><span>Costo total por pieza</span>
        <span class="v">{formatear_cop(costo_total, True)}</span><span class="p">100 %</span></div>
    </div>
    <div class="nota">Energía por pieza: {energia_kwh:.2f} kWh
      ({horas_pieza:.2f} h a {potencia_w:.0f} W).</div>
    """
)

mostrar_html(
    """
    <div class="pie"><b>Francia</b> · Impresión 3D<br>
    Guía de costeo: no reemplaza la asesoría de un contador. Compara con el mercado antes de publicar.</div>
    """
)
