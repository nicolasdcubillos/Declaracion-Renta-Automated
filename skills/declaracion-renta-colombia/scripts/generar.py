# -*- coding: utf-8 -*-
"""
GENERADOR DE FORMULARIOS DILIGENCIADOS

    python generar.py

Produce en ./salida/ :
    F210-AG2025.html   Formulario 210 diligenciado (imprimible / PDF)
    F160-AG2025.html   Declaracion anual de activos en el exterior
    F490-AG2025.html   Recibo oficial de pago
    F210-casillas.csv  Casilla;Valor  (para digitar o cargar en el MUISCA)
    F210-casillas.txt  Formato plano para copiar y pegar
    RESUMEN.md         Resumen ejecutivo y memoria de calculo

Antes de generar, corre la validacion independiente. Si falla, no genera nada.
"""
import os, csv, sys, datetime
from decimal import Decimal as D
from motor import liquidar, CASILLAS, SECCIONES, peso, mil
from validar import validar

RUTA = os.path.dirname(os.path.abspath(__file__))
SAL = os.path.join(RUTA, "salida")

CSS = """
:root{--b:#0b3d68;--g:#f4f6f8;--l:#c9d3dc}
*{box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
     margin:0;padding:24px;background:#eef1f4;color:#14202b;font-size:12px}
.hoja{max-width:940px;margin:0 auto 28px;background:#fff;padding:26px 30px;
      box-shadow:0 1px 4px rgba(0,0,0,.14);border-radius:3px}
.enc{display:flex;justify-content:space-between;align-items:flex-start;
     border-bottom:3px solid var(--b);padding-bottom:12px;margin-bottom:16px}
.enc h1{margin:0;font-size:19px;color:var(--b);letter-spacing:-.3px}
.enc h2{margin:3px 0 0;font-size:12px;font-weight:500;color:#5a6b7a}
.sello{text-align:right;font-size:10px;color:#5a6b7a;line-height:1.5}
.sello b{display:block;font-size:22px;color:var(--b);letter-spacing:1px}
table{width:100%;border-collapse:collapse;margin-bottom:14px}
th{background:var(--b);color:#fff;padding:6px 9px;text-align:left;font-size:10px;
   text-transform:uppercase;letter-spacing:.6px;font-weight:600}
td{padding:5px 9px;border-bottom:1px solid #e9edf1;vertical-align:top}
td.n{text-align:center;width:52px;font-weight:700;color:var(--b);font-variant-numeric:tabular-nums}
td.v{text-align:right;width:150px;font-variant-numeric:tabular-nums;white-space:nowrap}
tr.sec td{background:var(--b);color:#fff;font-weight:700;font-size:10px;
          text-transform:uppercase;letter-spacing:.8px;padding:5px 9px}
tr.tot td{background:#fdf3d4;font-weight:700;border-top:2px solid #d9b93c}
tr.res td{background:var(--b);color:#fff;font-weight:700;font-size:14px;padding:9px}
tr.cero td{color:#9aa7b2}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:9px;margin-bottom:16px}
.campo{background:var(--g);border:1px solid var(--l);border-radius:3px;padding:6px 9px}
.campo span{display:block;font-size:9px;color:#5a6b7a;text-transform:uppercase;
            letter-spacing:.5px;margin-bottom:2px}
.campo b{font-size:13px;letter-spacing:.3px}
.nota{background:#fff8e1;border-left:4px solid #e0a800;padding:9px 13px;
      margin:14px 0;font-size:11px;line-height:1.6}
.nota.ok{background:#e8f6ec;border-left-color:#2e7d43}
.nota.al{background:#fdecea;border-left-color:#c0392b}
.pie{margin-top:20px;padding-top:11px;border-top:1px solid var(--l);
     font-size:10px;color:#5a6b7a;line-height:1.6}
.firma{display:grid;grid-template-columns:1fr 1fr;gap:26px;margin-top:26px}
.firma div{border-top:1px solid #333;padding-top:5px;font-size:10px;text-align:center}
h3{color:var(--b);font-size:13px;margin:20px 0 7px;padding-bottom:4px;
   border-bottom:1px solid var(--l);text-transform:uppercase;letter-spacing:.5px}
@media print{body{background:#fff;padding:0;font-size:10.5px}
  .hoja{box-shadow:none;max-width:none;margin:0;padding:0 0 18px}
  .nota{break-inside:avoid} tr{break-inside:avoid}}
"""


# casillas que NO son valores en pesos: no llevan signo ni separador de miles
NO_MONETARIAS = {138, 140, 141}


def cop(v, casilla=None):
    if isinstance(v, str):
        return v
    if casilla in NO_MONETARIAS:
        return str(int(v))
    return "$" + f"{int(v):,}".replace(",", ".")


def trm(v):
    e, d = str(v).split(".")
    return "$" + f"{int(e):,}".replace(",", ".") + "," + d


def usd(v):
    return "US$ " + f"{float(v):,.2f}".replace(",", "@").replace(".", ",").replace("@", ".")


def html(titulo, cuerpo):
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{titulo}</title><style>{CSS}</style></head><body>{cuerpo}</body></html>"""


def encabezado(L, num, nombre, subtitulo):
    c = L.dat["contribuyente"]
    return f"""<div class="enc">
  <div><h1>{nombre}</h1><h2>{subtitulo}</h2></div>
  <div class="sello">Formulario<b>{num}</b>DIAN &middot; Colombia<br>Año gravable {c['anio_gravable']}</div>
</div>
<div class="grid">
  <div class="campo"><span>4. Número de formulario</span><b>&nbsp;</b></div>
  <div class="campo"><span>5. NIT</span><b>{c['nit']}</b></div>
  <div class="campo"><span>6. DV</span><b>{c['dv']}</b></div>
  <div class="campo"><span>12. Dirección seccional</span><b>{c['direccion_seccional_codigo']}</b></div>
  <div class="campo"><span>7. Primer apellido</span><b>{c['primer_apellido']}</b></div>
  <div class="campo"><span>8. Segundo apellido</span><b>{c['segundo_apellido']}</b></div>
  <div class="campo"><span>9. Primer nombre</span><b>{c['primer_nombre']}</b></div>
  <div class="campo"><span>10. Otros nombres</span><b>{c['otros_nombres']}</b></div>
</div>"""


# ----------------------------------------------------------------- F210
def gen_f210(L):
    M = L.M
    c = L.dat["contribuyente"]
    filas = []
    for sec, casillas in SECCIONES:
        filas.append(f'<tr class="sec"><td colspan="3">{sec}</td></tr>')
        for k in casillas:
            v = M.get(k, 0)
            nom = CASILLAS.get(k, "")
            cls = ""
            if k in (31, 42, 73, 90, 97, 111, 115, 126, 129):
                cls = "tot"
            if k in (136, 137):
                cls = "res"
            if v == 0 and not cls:
                cls = "cero"
            filas.append(f'<tr class="{cls}"><td class="n">{k}</td><td>{nom}</td>'
                         f'<td class="v">{cop(v, k)}</td></tr>')
    n = L.notas
    alertas = f"""
<div class="nota al"><b>Antes de presentar:</b> actualice el RUT agregando la responsabilidad
<b>&laquo;05 - Impuesto de renta y complementario regimen ordinario&raquo;</b>. Sin ella el sistema
de la DIAN no habilita este formulario. Habilite también el instrumento de firma electrónica.</div>
<div class="nota"><b>Vencimiento:</b> {c['fecha_vencimiento']} (NIT terminado en
{c['nit'][-2:]}). Presentación 100% virtual (Res. DIAN 000227 de 2025).</div>"""
    if M[136] > 0:
        alertas += (f'<div class="nota"><b>Pago:</b> liquide el Formulario 490 por '
                    f'<b>{cop(M[136])}</b> y páguelo a más tardar el {c["fecha_vencimiento"]}.</div>')

    cn = n["cesantias"]
    if cn["criterio"] == "por_empleador":
        filas_ces = " &middot; ".join(
            f"{nom[:34]}: {cop(prom)} = "
            f"{('%.2f' % float(u)).replace('.', ',')} UVT &rarr; {int(pc*100)}%"
            for nom, prom, u, pc in cn["detalle"])
        ces_nota = (f"Criterio <b>por empleador</b>, el mismo que aplica el Programa Ayuda Renta "
                    f"oficial de la DIAN. {filas_ces}. Total exento: "
                    f"<b>{cop(cn['por_empleador'])}</b>. "
                    f"Criterio alternativo (sumando ambos empleadores): {cop(cn['combinado'])}")
    else:
        ces_nota = (f"Criterio <b>combinado</b>: promedio {cop(cn['promedio_combinado'])} = "
                    f"{('%.2f' % float(cn['uvt_combinado'])).replace('.', ',')} UVT &rarr; {int(cn['pct_combinado']*100)}% "
                    f"exento = <b>{cop(cn['combinado'])}</b>. "
                    f"Alternativa por empleador: {cop(cn['por_empleador'])}")

    detalle = f"""
<h3>Notas de cálculo</h3>
<table>
<tr><th>Concepto</th><th>Detalle</th></tr>
<tr><td>Cesantías exentas (art. 206 num. 4)</td><td>{ces_nota}</td></tr>
<tr><td>Renta exenta 25% (art. 206 num. 10)</td><td>Base {cop(n['exenta25']['base'])} &times; 25% =
    {cop(n['exenta25']['calculado'])}; tope 790 UVT = {cop(n['exenta25']['tope'])}
    &rarr; aplicado <b>{cop(n['exenta25']['aplicado'])}</b></td></tr>
<tr><td>Límite art. 336 num. 3</td><td>40% = {cop(n['limite336']['lim40'])} vs 1.340 UVT =
    {cop(n['limite336']['lim1340'])} &rarr; límite {cop(n['limite336']['limite'])}.
    Solicitado {cop(n['limite336']['solicitado'])} &rarr;
    <b>{'SE LIMITA' if n['limite336']['limita'] else 'no limita'}</b></td></tr>
<tr><td>Impuesto art. 241</td><td>Base {cop(M[111])} = {('%.2f' % float(L.base_uvt)).replace('.', ',')} UVT,
    tarifa marginal {int(L.tarifa_marginal*100)}% &rarr; {cop(M[116])}</td></tr>
<tr><td>Anticipo art. 807</td><td>{int(L.PCT_ANTICIPO*100)}% &times; {cop(M[126])} =
    {cop(int(D(M[126])*L.PCT_ANTICIPO))} &minus; retenciones {cop(M[132])}
    &rarr; <b>{cop(M[133])}</b> (no puede ser negativo)</td></tr>
<tr><td>Descuento art. 254</td><td>Impuesto pagado en EE.UU. {cop(L.impuesto_exterior)},
    limitado al impuesto colombiano sobre esas rentas {cop(M[120])} &rarr; <b>{cop(M[122])}</b></td></tr>
</table>"""

    cuerpo = f"""<div class="hoja">
{encabezado(L, "210", "Declaración de Renta y Complementarios",
            "Personas Naturales y Asimiladas Residentes y Sucesiones Ilíquidas")}
<div class="grid">
  <div class="campo"><span>1. Año</span><b>{c['anio_gravable']}</b></div>
  <div class="campo"><span>24. Actividad económica</span><b>{c['actividad_economica']}</b></div>
  <div class="campo"><span>25. Cód. corrección</span><b>&nbsp;</b></div>
  <div class="campo"><span>27. Fracción año gravable siguiente</span><b>&nbsp;</b></div>
</div>
{alertas}
<table><tr><th style="width:52px">Cas.</th><th>Concepto</th><th style="width:150px;text-align:right">Valor</th></tr>
{''.join(filas)}
</table>
{detalle}
<div class="firma">
  <div>981. Firma electrónica del declarante<br>{c['primer_nombre']} {c['otros_nombres']}
       {c['primer_apellido']} {c['segundo_apellido']} &middot; NIT {c['nit']}-{c['dv']}</div>
  <div>996. Espacio exclusivo para el número interno de la DIAN</div>
</div>
<div class="pie">Valores expresados en pesos colombianos, aproximados al múltiplo de mil más cercano
(art. 577 E.T.). Estructura de casillas conforme al instructivo oficial de la Resolución DIAN 000044
del 14-03-2024. Documento preparatorio generado el {datetime.date.today().strftime('%d/%m/%Y')};
no sustituye la presentación oficial ante la DIAN.</div>
</div>"""
    return html(f"Formulario 210 - AG{c['anio_gravable']}", cuerpo)


# ----------------------------------------------------------------- F160
def gen_f160(L):
    c = L.dat["contribuyente"]
    ext = [a for a in L.activos if a.get("exterior")]
    if not ext:
        return None
    anio = c["anio_gravable"] + 1                      # activos a 1-ene del ano siguiente
    supera = L.patrimonio_exterior > L.umbral_detalle_f160
    c27 = "SI" if supera else "NO"
    tot = D(mil(L.patrimonio_exterior))

    juris = {}
    for a in ext:
        k = a.get("jurisdiccion", "-")
        juris[k] = juris.get(k, D(0)) + D(a["cop"])

    if supera:                                          # hoja 2 pide 37,38,39,40,41
        fh2 = "".join(
            f'<tr><td class="n">{i}</td><td>{a.get("jurisdiccion","")}</td><td>Fijo</td>'
            f'<td>Acciones y demas derechos financieros</td>'
            f'<td>{a.get("custodio","")}</td><td class="v">{cop(mil(a["cop"]))}</td></tr>'
            for i, a in enumerate(ext, 1))
        cab2 = ('<th style="width:34px">#</th><th>37. Jurisdicción</th><th style="width:78px">38. Naturaleza</th>'
                '<th>39. Tipo de activo</th><th>40. Identificación del activo</th>'
                '<th style="width:130px;text-align:right">41. Valor patrimonial</th>')
    else:                                               # hoja 2 pide solo 37,38,41
        fh2 = "".join(
            f'<tr><td class="n">{i}</td><td>{k}</td><td>Fijo</td><td class="v">{cop(mil(v))}</td></tr>'
            for i, (k, v) in enumerate(juris.items(), 1))
        cab2 = ('<th style="width:34px">#</th><th>37. Jurisdicción</th><th style="width:110px">38. Naturaleza</th>'
                '<th style="width:150px;text-align:right">41. Valor patrimonial</th>')

    def f(n, concepto, valor, auto=False):
        cls = ' class="cero"' if auto else ""
        v = f'<b>{valor}</b>' if not auto else valor
        return f'<tr{cls}><td class="n">{n}</td><td>{concepto}</td><td class="v">{v}</td></tr>'

    h1 = "".join([
        f(1,  "Año", str(anio)),
        f(4,  "Número de formulario", "lo asigna la DIAN", True),
        f(5,  "Número de Identificación Tributaria (NIT)", c["nit"]),
        f(6,  "DV", c["dv"]),
        f(7,  "Primer apellido", c["primer_apellido"]),
        f(8,  "Segundo apellido", c["segundo_apellido"]),
        f(9,  "Primer nombre", c["primer_nombre"]),
        f(10, "Otros nombres", c["otros_nombres"]),
        f(11, "Razón social", "no aplica &mdash; dejar en blanco", True),
        f(12, "Código Dirección Seccional",
             c["direccion_seccional_codigo"] + " &mdash; " + c["direccion_seccional_nombre"]),
        f(25, "Cód. corrección", "no aplica &mdash; dejar en blanco", True),
        f(26, "No. formulario anterior", "no aplica &mdash; dejar en blanco", True),
        f(27, "¿Valor patrimonial superior a 3.580 UVT?", "marcar <b>" + c27 + "</b>"),
        f(28, "Activos fijos con valor &gt; 3.580 UVT",
             cop(tot) if supera else "0", not supera),
        f(29, "Activos movibles con valor &gt; 3.580 UVT", "0", True),
        f(30, "Total activos con valores &gt; 3.580 UVT", cop(tot) if supera else "0", True),
        f(31, "Activos fijos con valor &le; 3.580 UVT", "0" if supera else cop(tot), supera),
        f(32, "Activos movibles con valor &le; 3.580 UVT", "0", True),
        f(33, "Total activos con valores &le; 3.580 UVT", "0" if supera else cop(tot), True),
        f(34, "Sanción por extemporaneidad", "0", True),
        f(35, "No. Identificación signatario", "no aplica &mdash; firma el declarante", True),
        f(36, "DV del signatario", "no aplica", True),
        f(981, "Código de representación", "no aplica", True),
        f(980, "Pago total", "no se activa en declaraciones virtuales", True),
    ])

    cuerpo = f"""<div class="hoja">
{encabezado(L, "160", "Declaración Anual de Activos en el Exterior", "Artículo 607 del Estatuto Tributario")}
<div class="nota ok"><b>Obligado a presentar.</b> Los activos poseídos en el exterior a
<b>1 de enero de {anio}</b> suman <b>{cop(tot)}</b> y superan el umbral de 2.000 UVT
({cop(L.umbral_f160)}). Plazo: <b>{c['fecha_vencimiento']}</b>, el mismo de la declaración de renta.
Todos los valores van <b>aproximados al múltiplo de mil más cercano</b>.</div>

<h3>Hoja 1 &mdash; casilla por casilla</h3>
<table><tr><th style="width:52px">Cas.</th><th>Concepto</th>
<th style="width:230px;text-align:right">Qué digitar</th></tr>
{h1}</table>
<div class="nota">Las casillas <b>28 a 33</b> las calcula el sistema a partir de la hoja 2; no se digitan.
La casilla <b>34</b> queda en cero si se presenta dentro del plazo &mdash; de lo contrario la sanción es del
<b>0,5&nbsp;% mensual</b> del valor de los activos ({cop(mil(D(L.patrimonio_exterior)*D("0.005")))} por mes o fracción),
con tope del 10&nbsp;% ({cop(mil(D(L.patrimonio_exterior)*D("0.10")))}).</div>

<h3>Hoja 2 &mdash; relación de activos en el exterior</h3>
<table><tr>{cab2}</tr>
{fh2}
<tr class="tot"><td colspan="{6 if supera else 3}">TOTAL</td><td class="v">{cop(tot)}</td></tr></table>
<div class="nota">Como la casilla 27 se marca <b>{c27}</b>, el sistema despliega en la hoja 2
únicamente las casillas <b>{'37, 38, 39, 40 y 41' if supera else '37, 38 y 41'}</b>.
{'' if supera else 'El art. 607 num. 4 E.T. ordena declararlos <b>de forma agregada por jurisdicción</b>, por eso va un solo renglón.'}
<b>Naturaleza «Fijo»</b> (art. 60 E.T.): son bienes que no se enajenan dentro del giro ordinario del negocio.</div>

<h3>De dónde sale el valor</h3>
<table><tr><th>Custodio</th><th>Jurisdicción</th>
<th style="width:120px;text-align:right">Valor USD</th><th style="width:150px;text-align:right">Valor COP</th></tr>
{"".join(f'<tr><td>{a.get("custodio","")}</td><td>{a.get("jurisdiccion","")}</td>'
         f'<td class="v">{usd(a["valor_usd"])}</td><td class="v">{cop(mil(a["cop"]))}</td></tr>' for a in ext)}
<tr class="tot"><td colspan="3">TOTAL PATRIMONIO EN EL EXTERIOR</td><td class="v">{cop(tot)}</td></tr></table>
<div class="nota"><b>Conversión:</b> art. 288 E.T. &mdash; los activos en moneda extranjera se reexpresan a la
<b>TRM de cierre: {trm(L.TRM_CIERRE)}</b> por dólar, certificada por la Superintendencia Financiera al
31 de diciembre de {c['anio_gravable']} y vigente para el 1 de enero de {anio}.</div>
<div class="nota"><b>Umbrales (UVT {anio} = {cop(L.UVT_SIG)}):</b> obligación de declarar, 2.000 UVT =
{cop(L.umbral_f160)} &mdash; se supera. Detalle individualizado, 3.580 UVT =
{cop(L.umbral_detalle_f160)} &mdash; {'se supera' if supera else 'no se supera'}.</div>
<div class="firma">
  <div>Firma electrónica del declarante<br>{c['primer_nombre']} {c['otros_nombres']}
       {c['primer_apellido']} {c['segundo_apellido']} &middot; NIT {c['nit']}-{c['dv']}</div>
  <div>Espacio exclusivo para el número interno de la DIAN</div>
</div>
<div class="pie">Documento preparatorio generado el {datetime.date.today().strftime('%d/%m/%Y')}.</div>
</div>"""
    return html(f"Formulario 160 - año {anio}", cuerpo)

def gen_f490(L):
    c = L.dat["contribuyente"]
    M = L.M
    if M[136] <= 0:
        return None
    cuerpo = f"""<div class="hoja">
{encabezado(L, "490", "Recibo Oficial de Pago Impuestos Nacionales", "Concepto 01 – Declaración privada")}
<div class="grid">
  <div class="campo"><span>Año gravable</span><b>{c['anio_gravable']}</b></div>
  <div class="campo"><span>Periodo</span><b>Anual</b></div>
  <div class="campo"><span>Cód. concepto</span><b>01</b></div>
  <div class="campo"><span>Formulario asociado</span><b>210</b></div>
</div>
<table>
<tr><th>Concepto</th><th style="width:170px;text-align:right">Valor</th></tr>
<tr><td>Total impuesto a cargo (casilla 129 del Formulario 210)</td><td class="v">{cop(M[129])}</td></tr>
<tr><td>Anticipo renta ano gravable siguiente (casilla 133)</td><td class="v">{cop(M[133])}</td></tr>
<tr><td>Sanciones (casilla 135)</td><td class="v">{cop(M[135])}</td></tr>
<tr><td>Menos: anticipo liquidado año anterior (casilla 130)</td><td class="v">-{cop(M[130])}</td></tr>
<tr><td>Menos: saldo a favor año anterior (casilla 131)</td><td class="v">-{cop(M[131])}</td></tr>
<tr><td>Menos: retenciones practicadas en el año (casilla 132)</td><td class="v">-{cop(M[132])}</td></tr>
<tr class="tot"><td>Subtotal &mdash; valor a pagar por impuesto</td><td class="v">{cop(M[136])}</td></tr>
<tr><td>Intereses de mora (si paga después del vencimiento)</td><td class="v">$0</td></tr>
<tr class="res"><td>TOTAL A PAGAR</td><td class="v">{cop(M[136])}</td></tr>
</table>
<div class="nota"><b>Fecha límite de pago: {c['fecha_vencimiento']}.</b>
Puede pagar por PSE desde el portal transaccional de la DIAN o en cualquier banco autorizado.
Si paga después del vencimiento se causan intereses de mora a la tasa vigente (art. 635 E.T.).</div>
<div class="firma">
  <div>Firma del contribuyente<br>{c['primer_nombre']} {c['otros_nombres']}
       {c['primer_apellido']} {c['segundo_apellido']} &middot; NIT {c['nit']}-{c['dv']}</div>
  <div>Sello y firma de la entidad recaudadora</div>
</div>
<div class="pie">Documento preparatorio generado el {datetime.date.today().strftime('%d/%m/%Y')}.
El recibo oficial debe generarse desde el sistema de la DIAN.</div>
</div>"""
    return html(f"Formulario 490 - AG{c['anio_gravable']}", cuerpo)


# ----------------------------------------------------------------- planos
def gen_csv(L, ruta):
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["casilla", "concepto", "valor"])
        for _, casillas in SECCIONES:
            for k in casillas:
                w.writerow([k, CASILLAS.get(k, ""), L.M.get(k, 0)])


def gen_txt(L):
    out = [f"FORMULARIO 210 - AÑO GRAVABLE {L.dat['contribuyente']['anio_gravable']}",
           f"NIT {L.dat['contribuyente']['nit']}-{L.dat['contribuyente']['dv']}",
           "Valores en múltiplos de mil (art. 577 E.T.)", ""]
    for sec, casillas in SECCIONES:
        out.append(f"--- {sec} ---")
        for k in casillas:
            v = L.M.get(k, 0)
            out.append(f"  {k:>4}  {CASILLAS.get(k,'')[:62]:<64} {cop(v, k):>16}")
        out.append("")
    return "\n".join(out)


def gen_resumen(L):
    M, c, n = L.M, L.dat["contribuyente"], L.notas
    l = []
    a = l.append
    a(f"# Resumen — Declaración de renta AG{c['anio_gravable']}")
    a("")
    a(f"> Generado automáticamente el {datetime.date.today().strftime('%d/%m/%Y')} "
      f"a partir de `datos.json`. Para recalcular: `python generar.py`.")
    a("")
    a("| Concepto | Valor |")
    a("|---|---:|")
    a(f"| Patrimonio bruto (29) | {cop(M[29])} |")
    a(f"| Patrimonio líquido (31) | {cop(M[31])} |")
    a(f"| Renta líquida gravable (111) | {cop(M[111])} |")
    a(f"| Impuesto neto de renta (126) | {cop(M[126])} |")
    a(f"| Ganancias ocasionales gravables (115) | {cop(M[115])} |")
    a(f"| Total impuesto a cargo (129) | {cop(M[129])} |")
    a(f"| Retenciones (132) | {cop(M[132])} |")
    a(f"| Anticipo año siguiente (133) | {cop(M[133])} |")
    a(f"| **TOTAL SALDO A PAGAR (136)** | **{cop(M[136])}** |")
    a(f"| Total saldo a favor (137) | {cop(M[137])} |")
    a("")
    a(f"**Vencimiento:** {c['fecha_vencimiento']}")
    a("")
    a("## Formularios a presentar")
    a("")
    a("| Formulario | ¿Obligatorio? | Fundamento |")
    a("|---|---|---|")
    a("| **210** Renta personas naturales | SÍ | Art. 592 E.T. |")
    a(f"| **160** Activos en el exterior | {'SÍ' if L.obligado_f160 else 'NO'} | "
      f"Art. 607 E.T.: {cop(L.patrimonio_exterior)} vs umbral {cop(L.umbral_f160)} |")
    a(f"| **490** Recibo de pago | {'SÍ' if M[136] > 0 else 'NO'} | "
      f"{'Hay saldo a pagar' if M[136] > 0 else 'No hay saldo a pagar'} |")
    a("")
    if n.get("acciones"):
        na = n["acciones"]
        a("## Enajenación de acciones (rentas no laborales)")
        a("")
        a("| Fecha | Título | Cantidad | Precio | Producto | Costo fiscal |")
        a("|---|---|---:|---:|---:|---:|")
        for v in na["ventas"]:
            a(f"| {v['fecha']} | {v['titulo']} | {v['cantidad']} | {usd(v['precio'])} | "
              f"{usd(v['producto'])} | {usd(v['costo'])} |")
        a(f"| | **Total** | | | **{usd(na['venta_usd'])}** | **{usd(na['costo_usd'])}** |")
        a("")
        a(f"Utilidad: **{usd(na['utilidad_usd'])}** → TRM {L.TRM_PROM} → "
          f"**{cop(na['venta_cop'] - na['costo_cop'])}**")
        a("")
    a("## Escenario alternativo de cesantías")
    a("")
    dif = n["cesantias"]["por_empleador"] - n["cesantias"]["combinado"]
    ahorro = int(D(dif) * L.tarifa_marginal)
    a(f"- Criterio aplicado: **{n['cesantias']['criterio']}** → exentas {cop(n['cesantias']['combinado'] if n['cesantias']['criterio']=='combinado' else n['cesantias']['por_empleador'])}")
    a(f"- Criterio alternativo → exentas {cop(n['cesantias']['por_empleador'] if n['cesantias']['criterio']=='combinado' else n['cesantias']['combinado'])}")
    a(f"- Diferencia en impuesto: aproximadamente **{cop(abs(ahorro))}**")
    a("")
    a("Para cambiarlo, edite `opciones.criterio_cesantias` en `datos.json` y vuelva a generar.")
    return "\n".join(l)


# ----------------------------------------------------------------- main
def main():
    os.makedirs(SAL, exist_ok=True)
    L = liquidar()
    print("Validando…")
    o, b = validar(L, verbose=False)
    if b:
        print(f"  ✗ {b} validaciones fallaron. Ejecute: python validar.py")
        sys.exit(1)
    print(f"  ✓ {o}/{o} validaciones correctas\n")

    generados = []
    for nombre, contenido in [("F210-AG%d.html" % L.dat["contribuyente"]["anio_gravable"], gen_f210(L)),
                              ("F160-AG%d.html" % L.dat["contribuyente"]["anio_gravable"], gen_f160(L)),
                              ("F490-AG%d.html" % L.dat["contribuyente"]["anio_gravable"], gen_f490(L))]:
        if contenido is None:
            obsoleto = os.path.join(SAL, nombre)
            if os.path.exists(obsoleto):
                os.remove(obsoleto)
                print(f"  – {nombre} omitido (no aplica) — se eliminó la versión anterior")
            else:
                print(f"  – {nombre} omitido (no aplica)")
            continue
        p = os.path.join(SAL, nombre)
        with open(p, "w", encoding="utf-8") as f:
            f.write(contenido)
        generados.append(p)

    p = os.path.join(SAL, "F210-casillas.csv"); gen_csv(L, p); generados.append(p)
    p = os.path.join(SAL, "F210-casillas.txt")
    with open(p, "w", encoding="utf-8") as f:
        f.write(gen_txt(L))
    generados.append(p)
    p = os.path.join(SAL, "RESUMEN.md")
    with open(p, "w", encoding="utf-8") as f:
        f.write(gen_resumen(L))
    generados.append(p)

    for g in generados:
        print(f"  ✓ salida/{os.path.basename(g)}")
    print(f"\n  SALDO A PAGAR (casilla 136): {cop(L.M[136])}")
    print(f"  Vencimiento: {L.dat['contribuyente']['fecha_vencimiento']}")
    print(f"\n  Abra los .html en el navegador y use Imprimir → Guardar como PDF.")


if __name__ == "__main__":
    main()
