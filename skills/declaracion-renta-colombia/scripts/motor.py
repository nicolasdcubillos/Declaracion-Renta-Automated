# -*- coding: utf-8 -*-
"""
MOTOR DE LIQUIDACION - Formulario 210 (Declaracion de renta personas naturales residentes)
Colombia - DIAN

Lee datos.json y calcula las 141 casillas del Formulario 210, mas los datos
del Formulario 160 (activos en el exterior) y del Formulario 490 (recibo de pago).

Estructura y numeracion de casillas conforme al INSTRUCTIVO OFICIAL de la
Resolucion DIAN 000044 del 14-03-2024.

No editar este archivo para cambiar cifras: editar datos.json.
"""
import json, os
from decimal import Decimal as D, ROUND_HALF_UP

RUTA = os.path.dirname(os.path.abspath(__file__))


def d(x):
    """Convierte a Decimal de forma segura (acepta int, str, None)."""
    if x is None:
        return D(0)
    return D(str(x))


def mil(x):
    """Art. 577 ET: aproximar al multiplo de mil mas cercano."""
    return int((d(x) / 1000).quantize(D("1"), rounding=ROUND_HALF_UP) * 1000)


def peso(x):
    return d(x).quantize(D("1"), rounding=ROUND_HALF_UP)


class Liquidacion:
    """Calcula la declaracion completa a partir del diccionario de datos."""

    TABLA_CESANTIAS = [(350, "1.00"), (410, "0.90"), (470, "0.80"),
                       (530, "0.60"), (590, "0.40"), (650, "0.20")]

    # art. 241 ET: (desde UVT, hasta UVT, tarifa marginal, suma en UVT)
    TABLA_241 = [(0, 1090, "0", "0"), (1090, 1700, "0.19", "0"),
                 (1700, 4100, "0.28", "116"), (4100, 8670, "0.33", "788"),
                 (8670, 18970, "0.35", "2296"), (18970, 31000, "0.37", "5901"),
                 (31000, None, "0.39", "10352")]

    def __init__(self, datos):
        self.dat = datos
        p = datos["parametros"]
        self.UVT = d(p["uvt_ano_gravable"])
        self.UVT_SIG = d(p["uvt_ano_siguiente"])
        self.TRM_CIERRE = d(p["trm_cierre"])
        self.TRM_PROM = d(p["trm_promedio"])
        self.CI = d(p["componente_inflacionario"])
        self.PCT_ANTICIPO = d(p["pct_anticipo"])
        self.R = {}          # casillas exactas
        self.notas = {}      # trazabilidad de cada bloque
        self._calcular()

    def uvt(self, n, siguiente=False):
        base = self.UVT_SIG if siguiente else self.UVT
        return peso(d(n) * base)

    # ------------------------------------------------------------------ 1
    def _rentas_trabajo(self):
        emp = self.dat["empleadores"]
        c32 = sum(d(e["salarios"]) + d(e["prestaciones"]) + d(e["otros_pagos"])
                  + d(e["cesantias_pagadas"]) + d(e["cesantias_fondo"]) for e in emp)
        c33 = sum(d(e["aporte_salud"]) + d(e["aporte_pension"]) for e in emp)
        self.R[32], self.R[33] = c32, c33
        self.R[34] = c32 - c33

    def pct_cesantias(self, promedio):
        u = d(promedio) / self.UVT
        for tope, pct in self.TABLA_CESANTIAS:
            if u <= tope:
                return d(pct), u
        return D(0), u

    def _cesantias(self):
        emp = self.dat["empleadores"]
        total = sum(d(e["cesantias_pagadas"]) + d(e["cesantias_fondo"]) for e in emp)
        prom_comb = sum(d(e["promedio_6_meses"]) for e in emp)
        pct_comb, uvt_comb = self.pct_cesantias(prom_comb)
        combinado = peso(total * pct_comb)
        por_emp = peso(sum((d(e["cesantias_pagadas"]) + d(e["cesantias_fondo"]))
                           * self.pct_cesantias(e["promedio_6_meses"])[0] for e in emp))
        criterio = self.dat["opciones"]["criterio_cesantias"]
        self.cesantias_exentas = combinado if criterio == "combinado" else por_emp
        self.notas["cesantias"] = dict(total=total, promedio_combinado=prom_comb,
                                       uvt_combinado=uvt_comb, pct_combinado=pct_comb,
                                       combinado=combinado, por_empleador=por_emp,
                                       criterio=criterio,
                                       detalle=[(e["nombre"], d(e["promedio_6_meses"]),
                                                 self.pct_cesantias(e["promedio_6_meses"])[1],
                                                 self.pct_cesantias(e["promedio_6_meses"])[0])
                                                for e in emp])

    # ------------------------------------------------------------------ 2
    def _rentas_capital(self):
        cap = self.dat["rentas_capital"]
        self.R[58] = sum(d(x["rendimiento"]) for x in cap)
        self.R[59] = sum(d(x["incrngo"]) for x in cap)
        self.R[60] = D(0)
        self.R[61] = self.R[58] - self.R[59] - self.R[60]
        self.gmf_pagado = sum(d(x["gmf"]) for x in cap)
        self.gmf_deducible = peso(self.gmf_pagado / 2)          # art. 115 ET
        for k in (62, 63, 64, 65, 66, 67, 68, 69, 71, 72):
            self.R[k] = D(0)
        self.R[70] = self.R[61]
        self.R[73] = self.R[61]

    # ------------------------------------------------------------------ 3
    def _rentas_no_laborales(self):
        nl = self.dat["rentas_no_laborales"]
        otros = sum(d(x["valor"]) for x in nl.get("otros_ingresos", []))
        acc = nl.get("enajenacion_acciones", {})
        venta_cop = costo_cop = D(0)
        self.notas["acciones"] = None
        if acc.get("activar"):
            cu = d(acc["costo_unitario_usd"])
            venta_usd = sum(d(v["producto_usd"]) for v in acc["ventas"])
            costo_usd = D(0)
            det = []
            for v in acc["ventas"]:
                c = d(v["costo_usd"]) if v.get("costo_usd") else cu * d(v["cantidad"])
                costo_usd += c
                det.append(dict(fecha=v["fecha"], titulo=v["titulo"], cantidad=v["cantidad"],
                                precio=v["precio_usd"], producto=d(v["producto_usd"]), costo=c))
            venta_cop = peso(venta_usd * self.TRM_PROM)
            costo_cop = peso(costo_usd * self.TRM_PROM)
            self.notas["acciones"] = dict(ventas=det, venta_usd=venta_usd, costo_usd=costo_usd,
                                          venta_cop=venta_cop, costo_cop=costo_cop,
                                          costo_unitario=cu,
                                          utilidad_usd=venta_usd - costo_usd)
        self.R[74] = otros + venta_cop
        self.R[75] = D(0)
        self.R[76] = D(0)
        self.R[77] = costo_cop
        self.R[78] = self.R[74] - self.R[75] - self.R[76] - self.R[77]
        for k in (79, 80, 81, 82, 83, 84, 85, 86, 88, 89):
            self.R[k] = D(0)
        self.R[87] = self.R[78]
        self.R[90] = self.R[78]

    # ------------------------------------------------------------------ 4
    def _deducciones_y_exentas(self):
        ded = self.dat["deducciones"]
        # casilla 28: 1% factura electronica, tope 240 UVT, FUERA del limite del 40%
        self.R[28] = min(peso(d(ded["base_factura_electronica"]) * D("0.01")), self.uvt(240))
        # casilla 139: 72 UVT por dependiente, FUERA del limite del 40%
        self.R[139] = self.uvt(72) * d(self.dat["opciones"]["numero_dependientes"])
        self.R[138] = d(self.dat["opciones"]["numero_dependientes"])
        # ICETEX art. 119 inciso 3: tope 100 UVT
        self.icetex = min(d(ded["icetex_intereses_pagados"]), self.uvt(100))

        self.R[35] = d(ded["aportes_afc_fvp"])
        self.R[38] = d(ded["intereses_vivienda"])
        self.R[39] = (self.gmf_deducible + self.icetex
                      + d(ded["dependientes_art387"]) + d(ded["medicina_prepagada"]))
        self.R[40] = self.R[38] + self.R[39]

        # renta exenta 25% art. 206 num.10, tope 790 UVT (nunca negativa)
        base = max(D(0), self.R[32] - self.R[33] - self.cesantias_exentas - self.R[40])
        tope = self.uvt(790)
        exenta = min(peso(base * D("0.25")), tope)
        self.R[36] = self.cesantias_exentas + exenta
        self.R[37] = self.R[35] + self.R[36]
        self.notas["exenta25"] = dict(base=base, calculado=peso(base * D("0.25")),
                                      tope=tope, aplicado=exenta)

        # limite global art. 336 num.3: 40% de la renta liquida, maximo 1.340 UVT
        renta_liquida = self.R[34] + self.R[61] + self.R[78]
        lim40 = peso(renta_liquida * D("0.40"))
        lim1340 = self.uvt(1340)
        limite = min(lim40, lim1340)
        solicitado = self.R[37] + self.R[40]
        total_imputable = min(solicitado, limite)

        # Instructivo Res. 000044/2024: el total imputable se distribuye en orden
        # -trabajo, trabajo sin relacion laboral, capital, no laborales- hasta
        # agotarlo, sin que ninguna cedula pueda quedar en negativo.
        for k in range(43, 58):
            self.R.setdefault(k, D(0))
        resto = total_imputable
        self.R[41] = min(resto, self.R[34]); resto -= self.R[41]
        self.R[53] = min(resto, self.R[57]); resto -= self.R[53]
        self.R[69] = min(resto, self.R[61]); resto -= self.R[69]
        self.R[86] = min(resto, self.R[78]); resto -= self.R[86]
        # las casillas 42, 70/73 y 87/90 van netas de su parte imputada, de modo
        # que 41+42, 69+73 y 86+90 reconstituyan la renta liquida de cada cedula
        self.R[42] = self.R[34] - self.R[41]
        self.R[70] = self.R[73] = self.R[61] - self.R[69]
        self.R[87] = self.R[90] = self.R[78] - self.R[86]
        self.notas["limite336"] = dict(renta_liquida=renta_liquida, lim40=lim40,
                                       lim1340=lim1340, limite=limite,
                                       solicitado=solicitado, limita=solicitado > limite,
                                       imputable=total_imputable, sin_imputar=resto,
                                       reparto={41: self.R[41], 53: self.R[53],
                                                69: self.R[69], 86: self.R[86]})


    # ------------------------------------------------------------------ 5
    def _cedula_general(self):
        self.R[91] = (self.R[41] + self.R[42] + self.R[53] + self.R[57]
                      + self.R[69] + self.R[73] + self.R[86] + self.R[90])
        self.R[92] = self.R[28] + self.R[41] + self.R[53] + self.R[69] + self.R[86] + self.R[139]
        self.R[93] = self.R[91] - self.R[92]
        self.R[94] = self.R[95] = self.R[96] = D(0)
        self.R[97] = self.R[93] + self.R[96] - self.R[94] - self.R[95]
        self.R[98] = D(0)                      # renta presuntiva 0% desde 2021

    # ------------------------------------------------------------- 5-bis
    def _pensiones(self):
        """Cedula de pensiones (casillas 99 a 103).

        Art. 206 num. 5 ET: la pension esta exenta en la parte del pago
        MENSUAL que no exceda 1.000 UVT; el exceso es gravado. La exencion
        se calcula sobre la porcion efectivamente recibida, es decir
        despues de restar los aportes obligatorios a salud (instructivo de
        la Res. 000044/2024, casilla 102).
        """
        pen = [x for x in self.dat.get("pensiones", []) if d(x.get("ingreso_bruto", 0))]
        if not pen:
            for k in range(99, 104):
                self.R[k] = D(0)
            return
        bruto = sum(d(x["ingreso_bruto"]) for x in pen)
        salud = sum(d(x.get("aporte_salud", 0)) for x in pen)
        self.R[99] = bruto
        self.R[100] = salud
        self.R[101] = self.R[99] - self.R[100]

        # tope mensual de 1.000 UVT; mesadas = 12 o 13 segun el regimen
        mesadas = sum(d(x.get("mesadas", 12)) for x in pen) / D(len(pen))
        tope_anual = self.uvt(1000) * mesadas
        self.R[102] = min(self.R[101], tope_anual)
        self.R[103] = self.R[101] - self.R[102]
        self.notas["pensiones"] = dict(
            bruto=bruto, salud=salud, exenta=self.R[102], gravada=self.R[103],
            tope_mensual=self.uvt(1000), mesadas=mesadas, detalle=pen)

    # ------------------------------------------------------------------ 6
    def _dividendos(self):
        div = self.dat["dividendos_exterior"]
        usd = sum(d(x["dividendo_usd"]) for x in div)
        imp = sum(d(x["impuesto_usa_usd"]) for x in div)
        for k in (104, 105, 106, 107, 108):
            self.R[k] = D(0)
        self.R[109] = peso(usd * self.TRM_PROM)          # dividendos del exterior
        self.R[110] = D(0)                               # exentos solo si son de la CAN
        self.impuesto_exterior = peso(imp * self.TRM_PROM)
        self.notas["dividendos"] = dict(usd=usd, imp_usd=imp, detalle=div)
        self.R[111] = max(self.R[97], self.R[98]) + self.R[103] + self.R[107] + self.R[108]

    # ------------------------------------------------------------------ 7
    def _ganancias_ocasionales(self):
        go = self.dat["ganancias_ocasionales"]
        ing = cos = D(0)
        det = []
        for e in go["enajenaciones"]:
            precio = peso(d(e["retencion"]) / d(e["tarifa_retencion"]))
            costo = d(e["costo_fiscal"]) if e.get("costo_fiscal") is not None else precio
            ing += precio
            cos += costo
            det.append(dict(concepto=e["concepto"], informante=e["informante"],
                            retencion=d(e["retencion"]), precio=precio, costo=costo))
        self.R[112] = ing
        self.R[113] = cos
        self.R[114] = d(go["no_gravadas_exentas"])
        self.R[115] = max(D(0), self.R[112] - self.R[113] - self.R[114])
        self.notas["go"] = det

    # ------------------------------------------------------------------ 8
    def art241(self, base):
        b = d(base) / self.UVT
        for lo, hi, t, s in self.TABLA_241:
            if hi is None or b <= hi:
                return peso(((b - lo) * d(t) + d(s)) * self.UVT), b, d(t)
        return D(0), b, D(0)

    def _liquidacion(self):
        lp = self.dat["liquidacion_previa"]
        self.R[116], self.base_uvt, self.tarifa_marginal = self.art241(self.R[111])
        self.R[117] = self.R[118] = self.R[119] = D(0)
        self.R[120] = peso((self.R[109] - self.R[110]) * D("0.35"))   # tarifa 35%
        self.R[121] = self.R[116] + self.R[117] + self.R[118] + self.R[119] + self.R[120]
        self.R[122] = min(self.impuesto_exterior, self.R[120])        # art. 254 ET
        self.R[123] = self.R[124] = D(0)
        self.R[125] = self.R[122] + self.R[123] + self.R[124]
        self.R[126] = self.R[121] - self.R[125]
        self.R[127] = peso(self.R[115] * d(self.dat["opciones"]["tarifa_ganancia_ocasional"]))
        self.R[128] = D(0)
        self.R[129] = self.R[126] + self.R[127] - self.R[128]

        ret = sum(d(e["retencion"]) for e in self.dat["empleadores"])
        ret += sum(d(x["retencion"]) for x in self.dat["rentas_capital"])
        ret += sum(d(x["valor"]) for x in self.dat["retenciones_adicionales"])
        self.R[130] = d(lp["anticipo_ano_anterior"])
        self.R[131] = d(lp["saldo_favor_ano_anterior"])
        self.R[132] = ret
        # art. 807 ET: nunca negativo
        self.R[133] = max(D(0), peso(self.R[126] * self.PCT_ANTICIPO) - self.R[132])
        self.R[135] = d(lp["sanciones"])
        self.R[141] = d(lp["aporte_voluntario_art244_1"])
        neto = self.R[129] + self.R[133] + self.R[135] - self.R[130] - self.R[131] - self.R[132]
        self.R[134] = max(D(0), neto)
        self.R[136] = max(D(0), neto)
        self.R[137] = max(D(0), -neto)
        self.R[140] = "No"

    # ------------------------------------------------------------------ 9
    def _patrimonio(self):
        act = self.dat["patrimonio"]["activos"]
        self.activos = []
        for a in act:
            if a.get("exterior"):
                v = peso(d(a["valor_usd"]) * self.TRM_CIERRE)
            else:
                v = d(a["valor_cop"])
            self.activos.append(dict(a, cop=v))
        self.R[29] = sum(a["cop"] for a in self.activos)
        self.R[30] = sum(d(x["valor_cop"]) for x in self.dat["patrimonio"]["deudas"])
        self.R[31] = self.R[29] - self.R[30]
        self.patrimonio_exterior = sum(a["cop"] for a in self.activos if a.get("exterior"))
        self.umbral_f160 = self.uvt(2000, siguiente=True)
        self.umbral_detalle_f160 = self.uvt(3580, siguiente=True)
        self.obligado_f160 = self.patrimonio_exterior > self.umbral_f160

    def _calcular(self):
        self._rentas_trabajo()
        self._cesantias()
        self._rentas_capital()
        self._rentas_no_laborales()
        self._deducciones_y_exentas()
        self._cedula_general()
        self._pensiones()
        self._dividendos()
        self._ganancias_ocasionales()
        self._liquidacion()
        self._patrimonio()
        self.M = self._redondear()

    # --------------------------------------------------- capa de presentacion
    def _redondear(self):
        """Art. 577 ET: valores en multiplos de mil, recalculando las casillas
        derivadas para que TODAS las identidades del formulario cierren exactas."""
        M = {k: (mil(v) if isinstance(v, D) else v) for k, v in self.R.items()}
        M[31] = M[29] - M[30]
        M[34] = M[32] - M[33]
        M[37] = M[35] + M[36]
        M[40] = M[38] + M[39]
        M[61] = M[58] - M[59] - M[60]
        M[70] = M[73] = M[61] - M[69]
        M[78] = M[74] - M[75] - M[76] - M[77]
        M[87] = M[90] = M[78] - M[86]
        renta_liquida = M[34] + M[61] + M[78]
        limite = min(mil(d(renta_liquida) * D("0.40")), mil(self.uvt(1340)))
        # mismo reparto en cascada que en self.R: trabajo, trabajo sin relacion
        # laboral, capital y no laborales, sin dejar ninguna cedula en negativo
        resto = min(M[37] + M[40], limite)
        M[41] = min(resto, M[34]); resto -= M[41]
        M[53] = min(resto, M[57]); resto -= M[53]
        M[69] = min(resto, M[61]); resto -= M[69]
        M[86] = min(resto, M[78]); resto -= M[86]
        M[42] = M[34] - M[41]
        M[70] = M[73] = M[61] - M[69]
        M[87] = M[90] = M[78] - M[86]
        M[91] = M[41] + M[42] + M[53] + M[57] + M[69] + M[73] + M[86] + M[90]
        M[92] = M[28] + M[41] + M[53] + M[69] + M[86] + M[139]
        M[93] = M[91] - M[92]
        M[97] = M[93] + M[96] - M[94] - M[95]
        M[101] = M[99] - M[100]
        M[103] = M[101] - M[102]
        M[111] = max(M[97], M[98]) + M[103] + M[107] + M[108] - M[118]
        M[115] = max(0, M[112] - M[113] - M[114])
        M[116] = mil(self.art241(M[111])[0])
        M[120] = mil(d(M[109] - M[110]) * D("0.35"))
        M[121] = M[116] + M[117] + M[118] + M[119] + M[120]
        M[122] = min(M[122], M[120])
        M[125] = M[122] + M[123] + M[124]
        M[126] = M[121] - M[125]
        M[127] = mil(d(M[115]) * d(self.dat["opciones"]["tarifa_ganancia_ocasional"]))
        M[129] = M[126] + M[127] - M[128]
        M[133] = max(0, mil(d(M[126]) * self.PCT_ANTICIPO) - M[132])
        neto = M[129] + M[133] + M[135] - M[130] - M[131] - M[132]
        M[134] = max(0, neto)
        M[136] = max(0, neto)
        M[137] = max(0, -neto)
        M[140] = "No"
        # la casilla 138 es un CONTEO de personas, no un valor en pesos:
        # el redondeo al multiplo de mil del art. 577 no le aplica.
        M[138] = int(self.R[138])
        return M


def cargar(ruta=None):
    ruta = ruta or os.path.join(RUTA, "datos.json")
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def liquidar(ruta=None):
    return Liquidacion(cargar(ruta))


# Nombres oficiales de las casillas (Res. DIAN 000044 de 2024)
CASILLAS = {
    28: "Uno por ciento (1%) de compras con factura electrónica",
    29: "Total patrimonio bruto", 30: "Deudas", 31: "Total patrimonio líquido (29 - 30)",
    32: "Ingresos brutos de las Rentas de trabajo",
    33: "Ingresos no constitutivos de renta de las Rentas de trabajo",
    34: "Renta líquida de las Rentas de trabajo (32 - 33)",
    35: "Rentas exentas de las Rentas de trabajo – Aportes voluntarios AFC, FVP y/o AVC",
    36: "Rentas exentas de las Rentas de trabajo – Otras rentas exentas",
    37: "Total rentas exentas de las Rentas de trabajo",
    38: "Deducciones imputables a las Rentas de trabajo – Intereses de vivienda",
    39: "Deducciones imputables a las Rentas de trabajo – Otras deducciones",
    40: "Total deducciones imputables a las Rentas de trabajo",
    41: "Rentas exentas y/o deducciones imputables a las Rentas de trabajo (Limitadas)",
    42: "Renta líquida ordinaria de las Rentas de trabajo",
    43: "Ingresos brutos rentas de trabajo sin relación laboral (honorarios)",
    53: "Rentas exentas y/o deducciones imputables honorarios (Limitadas)",
    57: "Renta líquida ordinaria de las Rentas de trabajo por honorarios",
    58: "Ingresos brutos de las Rentas de capital",
    59: "Ingresos no constitutivos de renta de las Rentas de capital",
    60: "Costos y deducciones procedentes de las Rentas de capital",
    61: "Renta líquida de las Rentas de capital",
    65: "Total rentas exentas de las Rentas de capital",
    68: "Total deducciones imputables a las Rentas de capital",
    69: "Rentas exentas y/o deducciones imputables a las Rentas de capital (Limitadas)",
    70: "Renta líquida ordinaria del ejercicio de las Rentas de capital",
    73: "Renta líquida ordinaria de las Rentas de capital",
    74: "Ingresos brutos de las Rentas no laborales",
    75: "Devoluciones, rebajas y descuentos de las Rentas no laborales",
    76: "Ingresos no constitutivos de renta de las Rentas no laborales",
    77: "Costos y deducciones procedentes de las Rentas no laborales",
    78: "Renta líquida de las Rentas no laborales",
    82: "Total rentas exentas de las Rentas no laborales",
    85: "Total deducciones imputables a las Rentas no laborales",
    86: "Rentas exentas y/o deducciones imputables (Limitadas) de las Rentas no laborales",
    87: "Renta líquida ordinaria del ejercicio de las Rentas no laborales",
    90: "Renta líquida ordinaria de las Rentas no laborales",
    91: "Renta líquida cédula general (41 + 42 + 53 + 57 + 69 + 73 + 86 + 90)",
    92: "Rentas exentas y deducciones imputables limitadas (28 + 41 + 53 + 69 + 86 + 139)",
    93: "Renta líquida ordinaria cédula general (91 - 92)",
    94: "Compensaciones por pérdidas año gravable 2018 y anteriores",
    95: "Compensaciones por exceso de renta presuntiva",
    96: "Rentas gravables",
    97: "Renta líquida gravable cédula general (93 + 96 - 94 - 95)",
    98: "Renta presuntiva",
    99: "Ingresos brutos por rentas de pensiones del país y del exterior",
    100: "Ingresos no constitutivos de renta (pensiones)",
    101: "Renta líquida (99 - 100)", 102: "Rentas exentas de pensiones",
    103: "Renta líquida gravable cédula de pensiones (101 - 102)",
    104: "Dividendos, participaciones año 2016 y anteriores, y otros",
    105: "Ingresos no constitutivos de renta (dividendos)",
    106: "Renta líquida ordinaria año 2016 y anteriores (104 - 105)",
    107: "1a. Subcédula años 2017 y siguientes numeral 3 art. 49 del E.T.",
    108: "2a. Subcédula años 2017 y siguientes, parágrafo 2° art. 49 del E.T.",
    109: "Dividendos y participaciones recibidas del exterior",
    110: "Rentas exentas de la casilla 109",
    111: "Renta líquida gravable (cédula general o renta presuntiva, de pensiones y de dividendos, art. 241 E.T.)",
    112: "Ingresos por ganancias ocasionales del país y del exterior",
    113: "Costos por ganancias ocasionales",
    114: "Ganancias ocasionales no gravadas y exentas",
    115: "Ganancias ocasionales gravables (112 - 113 - 114)",
    116: "Cédula general, de pensiones y de dividendos y participaciones (base casilla 111)",
    117: "Renta presuntiva, de pensiones y de dividendos y participaciones",
    118: "Por dividendos y participaciones año 2017 y siguientes, 2a subcédula (art. 240 E.T.)",
    119: "Por dividendos y participaciones año 2016 (base casilla 106)",
    120: "Por dividendos y participaciones recibidas del exterior (base casillas 109 - 110)",
    121: "Total impuesto sobre las rentas líquidas gravables (116 + 117 + 118 + 119 + 120)",
    122: "Impuestos pagados en el exterior", 123: "Donaciones",
    124: "Dividendos, participaciones y otros",
    125: "Total descuentos tributarios (122 + 123 + 124)",
    126: "Impuesto neto de renta (121 - 125)",
    127: "Impuesto de ganancias ocasionales (casilla 115 por tarifa)",
    128: "Descuento por impuestos pagados en el exterior por ganancias ocasionales",
    129: "Total impuesto a cargo (126 + 127 - 128)",
    130: "Anticipo renta liquidado año gravable anterior",
    131: "Saldo a favor del año gravable anterior sin solicitud de devolución y/o compensación",
    132: "Retenciones año gravable a declarar",
    133: "Anticipo renta para el año gravable siguiente",
    134: "Saldo a pagar por impuesto (129 + 133 - 130 - 131 - 132)",
    135: "Sanciones",
    136: "Total saldo a pagar (129 + 133 + 135 - 130 - 131 - 132)",
    137: "Total saldo a favor (130 + 131 + 132 - 129 - 133 - 135)",
    138: "Número de dependientes económicos",
    139: "Adición por dependientes a la casilla 92",
    140: "Ud. superó tope indicativo art. 336-1 del E.T., marque X",
    141: "Aporte voluntario (art. 244-1 E.T.)",
}

# Casillas que se imprimen en el formulario, en orden y por seccion
SECCIONES = [
    ("PATRIMONIO", [28, 29, 30, 31]),
    ("RENTAS DE TRABAJO", [32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42]),
    ("RENTAS DE CAPITAL", [58, 59, 60, 61, 65, 68, 69, 70, 73]),
    ("RENTAS NO LABORALES", [74, 75, 76, 77, 78, 82, 85, 86, 87, 90]),
    ("CÉDULA GENERAL", [91, 92, 93, 94, 95, 96, 97, 98]),
    ("CÉDULA DE PENSIONES", [99, 100, 101, 102, 103]),
    ("CÉDULA DE DIVIDENDOS Y PARTICIPACIONES", [104, 105, 106, 107, 108, 109, 110]),
    ("RENTA LÍQUIDA GRAVABLE", [111]),
    ("GANANCIAS OCASIONALES", [112, 113, 114, 115]),
    ("LIQUIDACIÓN PRIVADA", [116, 117, 118, 119, 120, 121, 122, 123, 124, 125,
                             126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137]),
    ("DATOS INFORMATIVOS", [138, 139, 140, 141]),
]
