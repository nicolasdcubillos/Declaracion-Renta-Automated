---
name: declaracion-renta-colombia
description: Prepara la declaración de renta de personas naturales en Colombia (Formulario 210), la declaración de activos en el exterior (Formulario 160) y el recibo de pago (Formulario 490). Úsala cuando el usuario pida hacer, revisar, liquidar o corregir su declaración de renta colombiana, calcular cuánto debe pagar a la DIAN, interpretar certificados de ingresos y retenciones, leer su información exógena, saber cuándo vence su plazo, entender una casilla del formulario, o resolver mensajes del portal MUISCA. Cubre asalariados, pensionados, rentistas de capital, ingresos y activos en el exterior, ventas de acciones y vehículos, y beneficio de auditoría.
license: MIT
---

# Declaración de renta de personas naturales — Colombia

Prepara una declaración completa, auditable y reproducible a partir de los
documentos del contribuyente, usando la normativa de la DIAN como fuente de
verdad.

**La regla que ordena todo el trabajo: cada cifra se verifica al menos dos
veces, contra fuentes independientes.** Un error aquí le cuesta dinero real al
usuario y puede acarrear sanciones del 100 % o 200 % del valor omitido.

---

## Flujo de trabajo

### 1. Recolectar y extraer

Los documentos suelen estar en una carpeta (`~/Downloads/...`). Espera encontrar:

| Documento | Aporta |
|---|---|
| Certificado de ingresos y retenciones (**formulario 220**) | Rentas de trabajo, aportes, retención |
| Certificado de pensión | Cédula de pensiones |
| Certificados bancarios | Saldos, rendimientos, retenciones, GMF |
| **Información exógena** (XLSX del portal DIAN) | Lo que terceros reportaron: es el cruce |
| Certificados de medicina prepagada, ICETEX, AFC/FVP | Deducciones |
| Prediales, facturas de impuesto vehicular | Patrimonio |
| Certificados de brókers extranjeros, 1042-S | Rentas y activos del exterior |

**Problemas constantes al extraer** — ver `references/extraccion-documentos.md`:

- **PDF protegidos con contraseña.** La clave casi siempre es el **número de
  cédula sin dígito de verificación**. Usa `pikepdf.open(f, password=...)`.
- **PDF que son escaneos sin capa de texto.** `pdfplumber` devuelve vacío.
  Renderiza la página a PNG (`page.to_image(resolution=200).save(...)`) y
  **léela visualmente**. No adivines cifras.
- **La exógena es el documento más valioso.** Trae los cinco topes del art. 592,
  el mapeo sugerido a cada renglón del F210 y datos que no están en ningún otro
  soporte.

### 2. Determinar si está obligado a declarar y cuándo vence

```bash
python scripts/plazos.py <cedula>
```

El plazo depende de los **dos últimos dígitos** del documento. El script trae un
calendario verificado contra pares de control reales; si cambias de año hay que
actualizarlo con el decreto de plazos y **volver a verificarlo**.

Obligado si supera **cualquiera** de los cinco topes del art. 592 ET (todos en
UVT del año gravable): ingresos brutos 1.400, patrimonio bruto 4.500, consumos
con tarjeta 1.400, compras 1.400, consignaciones 1.400. Los cinco valores están
en la exógena.

### 3. Modelar en `datos.json`

Copia `scripts/datos.ejemplo.json` a la carpeta de trabajo como `datos.json` y
rellénalo. **Es el único archivo que se edita**: todo lo demás se recalcula.

Documenta cada decisión no trivial con una clave `_nota_*` dentro del propio
JSON. Cuando un dato falta o hay contradicción entre fuentes, deja una
`_alerta_*` — esas alertas se convierten después en la sección de pendientes
de la memoria.

### 4. Validar, liquidar, generar

```bash
python scripts/validar.py     # controles aritméticos y normativos independientes
python scripts/generar.py     # F210, F160, F490 + casillas en CSV/TXT
python scripts/escenarios.py  # cuánto vale resolver cada supuesto abierto
python scripts/pdf.py         # todo a PDF (Chrome headless)
```

`validar.py` **no reutiliza** el cálculo del motor: lo recalcula por otra vía y
compara. Si algo no cuadra, se detiene. Nunca presentes resultados con
validaciones en rojo.

### 5. Escribir la memoria de cálculo

Un archivo `DECLARACION-RENTA-AG<año>-<NOMBRE>.md` en la raíz, que `pdf.py`
convierte automáticamente. Debe permitir que un contador reconstruya cada cifra
sin volver a abrir los soportes. Estructura que funciona:

1. Resultado y alerta de plazo
2. ¿Está obligado? (los cinco topes contra sus valores reales)
3. Una sección por cédula (trabajo, pensiones, capital, no laborales)
4. Deducciones, con el tope de cada una y si limita o no
5. Rentas exentas y el límite global del art. 336
6. Liquidación paso a paso, mostrando la aritmética
7. Patrimonio, con la norma de valoración de cada activo
8. **Puntos pendientes**, cuantificados en pesos
9. Verificaciones realizadas (tabla de controles)
10. Qué hacer antes de presentar, priorizado
11. Documentos utilizados y parámetros normativos

### 6. Entregar

- Di el saldo y **qué lo mueve**, no solo el número.
- Cuantifica cada pendiente: *«conseguir este certificado vale $2.661.792»*.
- Si hay riesgo, dilo sin rodeos y cita el artículo.
- Recuerda el bloqueante operativo: **responsabilidad «05» en el RUT** y firma
  electrónica vigente, o el MUISCA no habilita el formulario.

---

## Referencias

Cárgalas cuando las necesites, no antes:

| Archivo | Cuándo |
|---|---|
| `references/normativa.md` | Parámetros del año, topes, tarifas, artículos |
| `references/casillas-f210.md` | Qué va en cada casilla y las identidades que deben cerrar |
| `references/extraccion-documentos.md` | Descifrar PDF, leer escaneos, interpretar la exógena |
| `references/trampas.md` | Los errores que ya se cometieron y cómo evitarlos |
| `references/muisca.md` | Mensajes del portal y anexos no documentados |

---

## Reglas que no se negocian

**Verifica dos veces, con fuentes independientes.** La suma de los renglones de
un certificado debe reproducir su propio total. Lo declarado debe cruzar con la
exógena. Si no cruza, investiga antes de seguir.

**Nunca inventes una cifra.** Si un dato falta, déjalo en cero, márcalo como
pendiente y cuantifica cuánto vale conseguirlo. Es preferible un saldo
conservador y una lista clara de pendientes.

**La DIAN es la fuente de verdad.** Ante cualquier duda interpretativa, el orden
es: Estatuto Tributario → instructivo del formulario (Resolución 000044 de 2024
y sus modificaciones) → Programa Ayuda Renta oficial → conceptos DIAN. Las guías
de terceros no son fuente.

**Todo valor va en múltiplos de mil** (art. 577 ET), *excepto* los conteos como
el número de dependientes (casilla 138).

**Distingue lo cierto de lo supuesto.** En la memoria, lo verificado va como
hecho; lo inferido va marcado como tal, con lo que haría falta para confirmarlo.

**No optimices a costa del riesgo sin decirlo.** Si una posición es agresiva,
explica el tope legal que se está excediendo y la sanción asociada.

---

## Errores caros que ya ocurrieron

Están desarrollados en `references/trampas.md`. Los más costosos:

- **Cesantías**: la tabla del art. 206-4 se aplica al promedio de **cada
  empleador por separado**, no al consolidado. Lo confirma la hoja
  `renta exenta` del Programa Ayuda Renta oficial.
- **Deducción por dependiente**: con relación laboral proceden **las dos**
  (72 UVT del art. 336 num. 3 *más* el 10 % del art. 387 par. 2) sobre el mismo
  dependiente. En un caso real valió **$2,66 millones**.
- **Base del 1 % de compras**: es el renglón «facturación electrónica
  susceptible de beneficio» de la exógena, **no** los consumos con tarjeta. En
  un caso la diferencia fue de $63 M contra $25,7 M.
- **Pensiones**: el tope del art. 206 num. 5 es de 1.000 UVT **mensuales**, no
  anuales. Casi siempre la pensión queda exenta al 100 %.
- **Cédula de pensiones**: no admite deducciones imputables. Si el contribuyente
  solo tiene pensión, el límite del 40 % se calcula sobre una cédula general
  minúscula y las deducciones **se pierden**.
- **Orden de imputación** (instructivo Res. 000044/2024): trabajo → trabajo sin
  relación laboral → capital → no laborales. Si no hay rentas de trabajo, poner
  las deducciones en la casilla 41 deja la 42 **en negativo**.
- **Retención del 39 % sobre acciones RSU**: es retención **colombiana** del
  art. 383, no impuesto de EE.UU. No es descontable por el art. 254.
- **Bajar el impuesto endurece el beneficio de auditoría**: el umbral del art.
  689-3 es relativo al impuesto neto del año anterior.
- **Sanción mínima** (art. 639): 10 UVT **del año de presentación**. Aplica
  aunque no haya impuesto a cargo, y casi siempre supera al cálculo del art. 641.

---

## Qué NO hace esta skill

- No presenta la declaración ante la DIAN. Genera el insumo; el contribuyente
  firma y presenta.
- No reemplaza a un contador en posiciones discutibles. Las identifica,
  las cuantifica y las deja explícitas para que alguien decida.
- No cubre personas jurídicas, régimen simple, IVA ni retención en la fuente
  como agente retenedor.
