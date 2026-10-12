# Declaración de Renta Automated

Skill de [Claude](https://claude.com/claude-code) para preparar la **declaración
de renta de personas naturales en Colombia** (Formulario 210), la declaración de
activos en el exterior (Formulario 160) y el recibo de pago (Formulario 490).

Nace de preparar declaraciones reales: un asalariado con ingresos y acciones en
el exterior, una asalariada con dependiente, y una pensionada con patrimonio
inmobiliario. Cada caso dejó una lección que está codificada aquí.

---

## Qué hace

- **Lee los documentos** del contribuyente: certificados de ingresos, bancarios,
  de pensión, prediales, información exógena de la DIAN. Incluidos los PDF
  cifrados y los escaneos sin capa de texto.
- **Liquida** las cinco cédulas del Formulario 210 con la normativa vigente.
- **Valida** por una vía independiente: ~70 controles aritméticos y normativos
  que se recalculan sin reutilizar el motor.
- **Compara escenarios** para cuantificar en pesos cuánto vale resolver cada
  dato faltante.
- **Genera** los formularios en HTML y PDF, más la lista casilla → valor lista
  para digitar en el MUISCA.
- **Documenta** cada decisión en una memoria de cálculo que un contador puede
  auditar.

## Qué no hace

No presenta la declaración ante la DIAN ni reemplaza a un contador en posiciones
discutibles: las identifica, las cuantifica y las deja explícitas para que
alguien decida. Tampoco cubre personas jurídicas, régimen simple ni IVA.

---

## Instalación

```bash
git clone https://github.com/nicolasdcubillos/Declaracion-Renta-Automated.git
cp -r Declaracion-Renta-Automated/skills/declaracion-renta-colombia ~/.claude/skills/
```

Para un proyecto concreto, en `.claude/skills/` del repositorio.

**Dependencias de los scripts:**

```bash
pip install pdfplumber openpyxl pikepdf markdown
```

Para generar PDF hace falta Google Chrome (se usa en modo *headless*).

---

## Uso

La skill se activa sola cuando el usuario pide algo como:

> *«Ayúdame a hacer mi declaración de renta, los documentos están en Downloads»*

También responde a preguntas puntuales: cuándo vence el plazo, qué significa una
casilla, por qué la DIAN reporta un valor distinto, cómo se tratan las cesantías
con dos empleadores.

### Flujo típico

```bash
python scripts/plazos.py 1000077617     # cuándo vence
cp scripts/datos.ejemplo.json datos.json # rellenar con los datos del caso
python scripts/validar.py                # controles independientes
python scripts/generar.py                # F210 / F160 / F490
python scripts/escenarios.py             # cuánto vale cada pendiente
python scripts/pdf.py                    # todo a PDF
```

**`datos.json` es el único archivo que se edita.** Todo lo demás se recalcula.

---

## Estructura

```
skills/declaracion-renta-colombia/
├── SKILL.md                        instrucciones y flujo de trabajo
├── references/
│   ├── normativa.md                parámetros, topes, tarifas, artículos
│   ├── casillas-f210.md            qué va en cada casilla y las identidades
│   ├── extraccion-documentos.md    PDF cifrados, escaneos, exógena
│   ├── trampas.md                  17 errores reales y cómo evitarlos
│   └── muisca.md                   mensajes del portal y anexos no documentados
└── scripts/
    ├── motor.py                    liquidación de las cinco cédulas
    ├── validar.py                  ~70 controles independientes
    ├── generar.py                  F210 / F160 / F490 + CSV + TXT
    ├── escenarios.py               comparador de supuestos
    ├── plazos.py                   calculadora de vencimiento
    ├── pdf.py                      conversión a PDF
    └── datos.ejemplo.json          plantilla comentada
```

---

## El motor

Implementa las cinco cédulas del artículo 330 del Estatuto Tributario:

| Cédula | Casillas |
|---|---|
| General — rentas de trabajo | 32 – 42 |
| General — trabajo sin relación laboral | 43 – 57 |
| General — rentas de capital | 58 – 73 |
| General — rentas no laborales | 74 – 90 |
| Pensiones | 99 – 103 |
| Dividendos | 104 – 111 |
| Ganancias ocasionales | 112 – 115 |

Y resuelve correctamente lo que suele salir mal:

- **Cesantías por empleador**, no consolidadas (criterio del Programa Ayuda
  Renta oficial de la DIAN)
- **Orden de imputación** del artículo 336: trabajo → capital → no laborales,
  sin dejar ninguna cédula en negativo
- **Doble deducción por dependiente** cuando hay relación laboral
- **Exención de pensiones** con el tope de 1.000 UVT *mensuales*
- **Redondeo al millar** del artículo 577, recalculando las derivadas para que
  todas las identidades cierren exactas — y sin tocar los conteos

### Verificación

El validador **no reutiliza** el cálculo del motor: lo recalcula por otra vía y
compara. Los tres casos reales con los que se construyó reproducen sus cifras
exactas: 63, 66 y 69 controles en verde respectivamente.

---

## Advertencia

Herramienta de apoyo. **La responsabilidad de la declaración es del
contribuyente** (art. 746 ET). Verifique siempre contra la normativa vigente y
consulte a un contador en posiciones discutibles.

Los parámetros tributarios **cambian cada año**: UVT, componente inflacionario,
TRM y calendario de plazos deben actualizarse antes de cada temporada. Están
centralizados en `references/normativa.md` y en el bloque `CALENDARIOS` de
`scripts/plazos.py`.

## Licencia

MIT — ver [LICENSE](LICENSE).
