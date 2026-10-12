#!/usr/bin/env python3
"""
Calculadora del plazo para declarar renta de personas naturales (DIAN).

El decreto anual de plazos asigna a cada contribuyente un dia habil segun
los DOS ULTIMOS DIGITOS del NIT o la cedula, en pares: 01-02, 03-04, ...
99-00. El primer par vence el primer dia habil del calendario y a partir
de ahi se avanza un dia habil por par.

Uso:
    python plazos.py 79123456
    python plazos.py 79123456 --anio 2026
    python plazos.py --tabla

IMPORTANTE: verifique SIEMPRE el resultado contra el decreto de plazos del
ano o contra un par ya conocido. El inicio del calendario y los festivos se
configuran abajo y cambian cada ano.
"""
import argparse
import datetime
import sys

# --------------------------------------------------------------------------
# Configuracion por ano de presentacion. ACTUALIZAR CADA ANO con el decreto.
#   inicio   : fecha del primer dia habil del calendario (par 01-02)
#   festivos : festivos nacionales que caen dentro de la ventana
# --------------------------------------------------------------------------
CALENDARIOS = {
    2026: {
        "inicio": datetime.date(2026, 8, 12),
        "festivos": [
            datetime.date(2026, 8, 17),    # Asuncion de la Virgen
            datetime.date(2026, 10, 12),   # Dia de la Raza
            datetime.date(2026, 11, 2),    # Todos los Santos
            datetime.date(2026, 11, 16),   # Independencia de Cartagena
        ],
        "decreto": "Decreto de plazos AG2025",
        "controles": {                     # pares verificados contra la DIAN
            "17-18": datetime.date(2026, 8, 25),
            "63-64": datetime.date(2026, 9, 25),
            "83-84": datetime.date(2026, 10, 9),
        },
    },
}


def par_de(documento):
    """Devuelve el par 'NN-MM' que corresponde a los dos ultimos digitos."""
    dig = "".join(ch for ch in str(documento) if ch.isdigit())
    if not dig:
        raise ValueError("el documento no contiene digitos")
    ult = int(dig[-2:]) if len(dig) >= 2 else int(dig)
    if ult == 0:
        ult = 100
    idx = (ult + 1) // 2                       # 1..50
    ini = 2 * idx - 1
    fin = 2 * idx
    return f"{ini:02d}-{fin % 100:02d}", idx


def calendario(anio):
    cfg = CALENDARIOS.get(anio)
    if cfg is None:
        raise SystemExit(
            f"No hay calendario cargado para {anio}.\n"
            f"Agreguelo en CALENDARIOS leyendo el decreto de plazos y "
            f"verifiquelo contra al menos un par conocido."
        )
    festivos = set(cfg["festivos"])
    fechas, d, n = {}, cfg["inicio"], 0
    while n < 50:
        if d.weekday() < 5 and d not in festivos:
            n += 1
            fechas[f"{2*n-1:02d}-{(2*n) % 100:02d}"] = d
        d += datetime.timedelta(days=1)
    return cfg, fechas


def verificar(cfg, fechas):
    """Contrasta el calendario generado contra los pares de control."""
    fallas = []
    for par, esperada in cfg.get("controles", {}).items():
        obtenida = fechas.get(par)
        if obtenida != esperada:
            fallas.append((par, esperada, obtenida))
    return fallas


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("documento", nargs="?", help="NIT o cedula del contribuyente")
    ap.add_argument("--anio", type=int, default=2026,
                    help="ano de PRESENTACION (no el gravable)")
    ap.add_argument("--tabla", action="store_true", help="imprime los 50 pares")
    args = ap.parse_args()

    cfg, fechas = calendario(args.anio)

    fallas = verificar(cfg, fechas)
    if fallas:
        print("AVISO: el calendario generado no reproduce los pares de control:")
        for par, esp, obt in fallas:
            print(f"   {par}: esperado {esp}, obtenido {obt}")
        print("   Revise 'inicio' y 'festivos' en CALENDARIOS antes de confiar.\n")
    elif cfg.get("controles"):
        print(f"Calendario {args.anio} verificado contra "
              f"{len(cfg['controles'])} pares de control.\n")

    if args.tabla:
        for par, f in fechas.items():
            marca = "  <-- control" if par in cfg.get("controles", {}) else ""
            print(f"  {par}   {f:%A %d-%b-%Y}{marca}")
        return

    if not args.documento:
        ap.error("indique el documento, o use --tabla")

    par, _ = par_de(args.documento)
    venc = fechas[par]
    hoy = datetime.date.today()

    print(f"Documento      : {args.documento}")
    print(f"Dos ultimos    : {par}")
    print(f"VENCIMIENTO    : {venc:%A %d de %B de %Y}")

    if hoy < venc:
        print(f"Faltan         : {(venc - hoy).days} dia(s)")
    elif hoy == venc:
        print("VENCE HOY")
    else:
        dias = (hoy - venc).days
        meses = -(-dias // 30)                 # techo
        print(f"VENCIDO hace   : {dias} dia(s)  ->  {meses} mes(es) o fraccion")
        print("\nLiquide sancion de extemporaneidad (art. 641 ET) y, si hay")
        print("impuesto a cargo, intereses de mora (art. 635 ET).")
        print("Recuerde la sancion minima del art. 639: 10 UVT del ano de")
        print("presentacion.")


if __name__ == "__main__":
    sys.exit(main())
