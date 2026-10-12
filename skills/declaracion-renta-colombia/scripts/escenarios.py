#!/usr/bin/env python3
"""
Comparador de escenarios para la declaracion de renta.

Recalcula la liquidacion completa variando los supuestos abiertos, para
cuantificar cuanto vale resolver cada uno ANTES de presentar.

Cada escenario es una funcion que recibe el dict de datos.json y lo muta.
Edite la lista ESCENARIOS al final del archivo segun el caso concreto:
los que vienen son los que aparecen una y otra vez en la practica.

Uso:  python escenarios.py
"""
import json
import os
import sys
from decimal import Decimal as D

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from motor import liquidar                                     # noqa: E402

BASE = os.path.join(AQUI, "datos.json")


# --------------------------------------------------------------- utilidades
def correr(mut=None):
    dat = json.load(open(BASE, encoding="utf-8"))
    if mut:
        mut(dat)
    tmp = os.path.join(AQUI, ".escenario.json")
    json.dump(dat, open(tmp, "w", encoding="utf-8"))
    try:
        return liquidar(tmp)
    finally:
        os.remove(tmp)


def cop(v):
    return "$" + format(int(v), ",d").replace(",", ".")


def ingresos_laborales(d):
    return sum(e["salarios"] + e["prestaciones"] + e["otros_pagos"]
               + e.get("cesantias_pagadas", 0) for e in d.get("empleadores", []))


# -------------------------------------------------------------- escenarios
def base(d):
    """Lo que esta documentado hoy."""


def con_dependiente(d):
    """Con relacion laboral proceden LAS DOS deducciones sobre el mismo
    dependiente (instructivo Res. 000044/2024): 72 UVT del art. 336 num.3
    -fuera del limite del 40%- mas el 10% de los ingresos brutos laborales
    del art. 387 par.2, con tope de 32 UVT mensuales."""
    d["opciones"]["numero_dependientes"] = 1
    uvt = d["parametros"]["uvt_ano_gravable"]
    d["deducciones"]["dependientes_art387"] = int(
        min(D(ingresos_laborales(d)) * D("0.10"), D(384 * uvt)))


def sin_dependiente(d):
    d["opciones"]["numero_dependientes"] = 0
    d["deducciones"]["dependientes_art387"] = 0


def con_factura_electronica(d):
    """1% de compras con factura electronica (art. 336 num.5 ET).
    La base correcta es el renglon 'facturacion electronica susceptible de
    beneficio' de la exogena, NO los consumos con tarjeta."""
    d["deducciones"]["base_factura_electronica"] = 20_000_000


def sin_factura_electronica(d):
    d["deducciones"]["base_factura_electronica"] = 0


def primera_declaracion(d):
    """Art. 807 ET: el anticipo es del 25% -no del 75%- en la primera."""
    d["parametros"]["pct_anticipo"] = "0.25"


ESCENARIOS = [
    (base,                    "A. Base (lo documentado)"),
    (con_dependiente,         "B. + deduccion por dependiente"),
    (con_factura_electronica, "C. + 1% compras con factura electronica"),
    (primera_declaracion,     "D. si es su primera declaracion (anticipo 25%)"),
]


# ------------------------------------------------------------------- salida
def main():
    L0 = correr()
    c = L0.dat["contribuyente"]
    nombre = " ".join(x for x in (c.get("primer_nombre"), c.get("otros_nombres"),
                                  c.get("primer_apellido"), c.get("segundo_apellido"))
                      if x)
    print("=" * 88)
    print(f"ESCENARIOS  ·  {nombre}  ·  AG{c['anio_gravable']}")
    print("=" * 88)
    print(f"{'Escenario':<46}{'Cas.111':>14}{'Cas.129':>12}{'Resultado':>16}")
    print("-" * 88)

    filas, ref = [], None
    for fn, etiqueta in ESCENARIOS:
        L = correr(fn)
        saldo = L.M[136] if L.M[136] else -L.M[137]
        if ref is None:
            ref = saldo
        filas.append((etiqueta, saldo))
        txt = cop(saldo) if saldo >= 0 else "a favor " + cop(-saldo)
        print(f"{etiqueta:<46}{cop(L.M[111]):>14}{cop(L.M[129]):>12}{txt:>16}")

    print("-" * 88)
    print("\nDiferencia frente al escenario base:")
    for etiqueta, s in filas[1:]:
        dif = s - ref
        if dif == 0:
            print(f"  {etiqueta:<46}sin efecto en el impuesto")
        else:
            print(f"  {etiqueta:<46}{'ahorra' if dif < 0 else 'cuesta'} {cop(abs(dif))}")

    techo = L0.M[130] + L0.M[131] + L0.M[132]
    print(f"\nTecho del saldo a favor: {cop(techo)}")
    print("  (retenciones + anticipo y saldo a favor del ano anterior). Por encima")
    print("  de ese valor, mas deducciones no devuelven nada.")


if __name__ == "__main__":
    main()
