# -*- coding: utf-8 -*-
"""
VALIDADOR INDEPENDIENTE
Recalcula con aritmetica entera y logica escrita aparte, para contrastar
contra el motor. Si algo no cuadra, generar.py se detiene.
"""
from motor import liquidar
from decimal import Decimal as D


def validar(L=None, verbose=True):
    L = L or liquidar()
    M, R, dat = L.M, L.R, L.dat
    UVT = int(L.UVT)
    ok, bad = [], []

    def chk(nombre, a, b, tol=0):
        a, b = int(a), int(b)
        (ok if abs(a - b) <= tol else bad).append((nombre, a, b, a - b))

    # ---- entradas
    emp = dat["empleadores"]
    chk("Ingresos brutos trabajo (c32)",
        sum(e["salarios"] + e["prestaciones"] + e["otros_pagos"]
            + e["cesantias_pagadas"] + e["cesantias_fondo"] for e in emp), R[32])
    chk("INCRNGO aportes obligatorios (c33)",
        sum(e["aporte_salud"] + e["aporte_pension"] for e in emp), R[33])
    chk("c34 = c32 - c33", R[32] - R[33], R[34])

    cap = dat["rentas_capital"]
    chk("Ingresos brutos capital (c58)", sum(x["rendimiento"] for x in cap), R[58])
    # incrngo null => el motor aplica el componente inflacionario del ano
    ci = float(L.CI)
    def _incrngo(x):
        return round(x["rendimiento"] * ci) if x.get("incrngo") is None else x["incrngo"]
    chk("INCRNGO capital (c59)", sum(_incrngo(x) for x in cap), R[59], 2)
    for x in cap:
        esperado = round(x["rendimiento"] * ci)
        if x.get("incrngo") is not None and x.get("_sin_componente") is not True \
           and x["incrngo"] != 0:
            chk(f"componente inflacionario {x['entidad'][:30]}", x["incrngo"], esperado, 2)

    # ---- cesantias
    n = L.notas["cesantias"]
    chk("cesantias: promedio combinado en UVT x100",
        round(float(n["promedio_combinado"]) / UVT * 100), round(float(n["uvt_combinado"]) * 100), 1)
    chk("cesantias exentas segun criterio",
        int(n["combinado"] if n["criterio"] == "combinado" else n["por_empleador"]),
        int(L.cesantias_exentas))

    # ---- topes y limites
    # ---- cedula de pensiones (art. 206 num.5 ET)
    pen = L.dat.get("pensiones", [])
    if pen:
        chk("c99 = suma pensiones brutas", sum(x["ingreso_bruto"] for x in pen), R[99])
        chk("c100 = aportes salud pension",
            sum(x.get("aporte_salud", 0) for x in pen), R[100])
        chk("c101 = c99 - c100", R[99] - R[100], R[101])
        chk("c103 = c101 - c102", R[101] - R[102], R[103])
        np = L.notas["pensiones"]
        chk("tope pension exenta = 1.000 UVT mensuales", 1000 * UVT, int(np["tope_mensual"]))
        chk("c102 <= c101", 1, 1 if R[102] <= R[101] else 0)
        mensual = int(R[101] / np["mesadas"]) if np["mesadas"] else 0
        chk("pension mensual no supera 1.000 UVT", 1, 1 if mensual <= 1000 * UVT else 0)

    chk("c42 = c34 - c41", R[34] - R[41], R[42])
    chk("c73 = c61 - c69", R[61] - R[69], R[73])
    chk("c90 = c78 - c86", R[78] - R[86], R[90])
    chk("reparto no excede el limite art.336",
        1, 1 if R[41] + R[53] + R[69] + R[86] <= L.notas["limite336"]["limite"] else 0)
    chk("ninguna cedula queda negativa",
        0, min(0, min(R[42], R[73], R[90])))

    chk("tope renta exenta 25% = 790 UVT", 790 * UVT, int(L.notas["exenta25"]["tope"]))
    chk("renta exenta 25% = min(calculado, tope)",
        min(int(L.notas["exenta25"]["calculado"]), 790 * UVT), int(L.notas["exenta25"]["aplicado"]))
    chk("limite art.336 = min(40%, 1.340 UVT)",
        min(int(L.notas["limite336"]["lim40"]), 1340 * UVT), int(L.notas["limite336"]["limite"]))
    chk("c41 <= limite art.336", 1, 1 if R[41] <= L.notas["limite336"]["limite"] else 0)
    chk("GMF deducible = 50% art.115", int(L.gmf_pagado) // 2, int(L.gmf_deducible), 1)
    chk("ICETEX <= 100 UVT art.119", 1, 1 if L.icetex <= 100 * UVT else 0)
    chk("1% factura electronica <= 240 UVT", 1, 1 if R[28] <= 240 * UVT else 0)

    # ---- acciones
    na = L.notas.get("acciones")
    if na:
        acc = dat["rentas_no_laborales"]["enajenacion_acciones"]
        chk("venta acciones USD x100",
            round(sum(float(v["producto_usd"]) for v in acc["ventas"]) * 100),
            round(float(na["venta_usd"]) * 100))
        chk("c74 = otros + ventas",
            sum(x["valor"] for x in dat["rentas_no_laborales"]["otros_ingresos"]) + int(na["venta_cop"]),
            R[74])
        chk("c78 = 74-75-76-77", R[74] - R[75] - R[76] - R[77], R[78])

    # ---- ganancias ocasionales
    for e in L.notas["go"]:
        chk(f"GO precio = retencion/tarifa {e['informante'][:24]}",
            round(float(e["retencion"]) / 0.01), int(e["precio"]), 1)
    chk("c115 = 112-113-114 (min 0)", max(0, R[112] - R[113] - R[114]), R[115])

    # ---- tabla art. 241 y continuidad
    b = float(R[111]) / UVT
    for lo, hi, t, s in L.TABLA_241:
        if hi is None or b <= hi:
            chk("impuesto art.241", round(((b - lo) * float(t) + float(s)) * UVT), int(R[116]), 2)
            break
    for lo, hi, t, s in L.TABLA_241[:-1]:
        sig = [x for x in L.TABLA_241 if x[0] == hi][0]
        izq = (hi - lo) * float(t) + float(s)
        chk(f"continuidad tabla art.241 en {hi} UVT", round(izq), round(float(sig[3])), 1)

    # ---- liquidacion
    chk("c121 = 116+117+118+119+120", R[116] + R[117] + R[118] + R[119] + R[120], R[121])
    chk("c122 <= c120 (limite art.254)", 1, 1 if R[122] <= R[120] else 0)
    chk("c126 = 121-125", R[121] - R[125], R[126])
    chk("c129 = 126+127-128", R[126] + R[127] - R[128], R[129])
    ret = (sum(e["retencion"] for e in emp) + sum(x["retencion"] for x in cap)
           + sum(x["valor"] for x in dat["retenciones_adicionales"]))
    chk("c132 retenciones", ret, R[132])
    chk("c133 anticipo art.807 (nunca negativo)",
        max(0, round(float(R[126]) * float(L.PCT_ANTICIPO)) - int(R[132])), int(R[133]), 1)

    # ---- patrimonio
    chk("c29 patrimonio bruto", sum(int(a["cop"]) for a in L.activos), R[29])
    chk("c30 deudas", sum(x["valor_cop"] for x in dat["patrimonio"]["deudas"]), R[30])
    chk("c31 = 29-30", R[29] - R[30], R[31])
    chk("umbral F160 = 2.000 UVT ano siguiente", 2000 * int(L.UVT_SIG), int(L.umbral_f160))

    # ---- identidades sobre los valores REDONDEADOS (los que se digitan)
    ident = [
        ("31 = 29-30", M[31], M[29] - M[30]),
        ("34 = 32-33", M[34], M[32] - M[33]),
        ("37 = 35+36", M[37], M[35] + M[36]),
        ("40 = 38+39", M[40], M[38] + M[39]),
        ("42 = 34-41", M[42], M[34] - M[41]),
        ("61 = 58-59-60", M[61], M[58] - M[59] - M[60]),
        ("78 = 74-75-76-77", M[78], M[74] - M[75] - M[76] - M[77]),
        ("91 = 41+42+53+57+69+73+86+90", M[91],
         M[41] + M[42] + M[53] + M[57] + M[69] + M[73] + M[86] + M[90]),
        ("92 = 28+41+53+69+86+139", M[92], M[28] + M[41] + M[53] + M[69] + M[86] + M[139]),
        ("93 = 91-92", M[93], M[91] - M[92]),
        ("97 = 93+96-94-95", M[97], M[93] + M[96] - M[94] - M[95]),
        ("111 = max(97,98)+103+107+108-118", M[111],
         max(M[97], M[98]) + M[103] + M[107] + M[108] - M[118]),
        ("115 = 112-113-114", M[115], max(0, M[112] - M[113] - M[114])),
        ("121 = 116+117+118+119+120", M[121], M[116] + M[117] + M[118] + M[119] + M[120]),
        ("125 = 122+123+124", M[125], M[122] + M[123] + M[124]),
        ("126 = 121-125", M[126], M[121] - M[125]),
        ("129 = 126+127-128", M[129], M[126] + M[127] - M[128]),
        ("134 = 129+133-130-131-132", M[134],
         max(0, M[129] + M[133] - M[130] - M[131] - M[132])),
        ("136 = 129+133+135-130-131-132", M[136],
         max(0, M[129] + M[133] + M[135] - M[130] - M[131] - M[132])),
        ("137 = 130+131+132-129-133-135", M[137],
         max(0, M[130] + M[131] + M[132] - M[129] - M[133] - M[135])),
        ("136 y 137 no pueden ser ambos > 0", 0, min(M[136], M[137])),
    ]
    for nom, a, bb in ident:
        chk("[F210] " + nom, a, bb)

    if verbose:
        print("=" * 92)
        print("VALIDACION INDEPENDIENTE")
        print("=" * 92)
        for nom, a, bb, _ in ok:
            print(f"  OK    {nom:<52} {a:>16,} = {bb:>16,}".replace(",", "."))
        for nom, a, bb, dd in bad:
            print(f"  FALLA {nom:<52} {a:>16,} <> {bb:>16,}  dif {dd:,}".replace(",", "."))
        print(f"\n  RESULTADO: {len(ok)} OK / {len(bad)} fallas   (total {len(ok)+len(bad)})")
    return len(ok), len(bad)


if __name__ == "__main__":
    import sys
    o, b = validar()
    sys.exit(1 if b else 0)
