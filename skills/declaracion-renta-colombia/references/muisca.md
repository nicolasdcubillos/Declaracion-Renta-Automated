# El portal MUISCA

Comportamientos del SI de Diligenciamiento que no están documentados en ninguna
resolución y que bloquean el avance si no se conocen.

---

## Bloqueante antes de empezar

**Responsabilidad «05 — Impuesto de renta y complementario régimen ordinario»
en el RUT.** Sin ella el sistema **no habilita** el Formulario 210. Es el
tropiezo más frecuente y se resuelve actualizando el RUT en el mismo portal.

También: **firma electrónica vigente**. Si está vencida hay que renovarla antes,
y el trámite no es inmediato.

Verificar además que nombres, apellidos y código de dirección seccional del RUT
coincidan con lo que se va a digitar.

---

## El aviso de las casillas 304 a 334

Al llegar a una casilla calculada, el aplicativo muestra:

> *«Para diligenciar el valor de la casilla N debe incluir valores de 304, 305,
> 307, 308, 310, 311, 313, 314… en la siguiente pestaña.»*

**Qué significa:** esa casilla es un **campo calculado**. No se digita: se
alimenta de un anexo en una pestaña aparte.

**Las casillas 304 a 334 no existen en ninguna norma publicada.** Se verificó su
ausencia en la Resolución 000044/2024, la 000120/2024, la 000227/2025, el
Formulario 210 oficial de 2026 y el Programa Ayuda Renta. El formulario impreso
llega hasta la 141.

**Cómo proceder:** no intentes mapear renglón por renglón. Carga el detalle en
el anexo y **verifica el resultado contra los totales de control** que sí están
normados. Si los totales cuadran, el anexo quedó bien.

### Caso: anexo de dividendos del exterior (casilla 109)

| Casilla de control | Debe quedar en |
|:--:|---|
| 109 | Total de dividendos del exterior a la TRM promedio |
| 120 | 35 % de (109 − 110), art. 245 ET |
| 122 | Impuesto efectivamente pagado en el exterior, art. 254 |

Si el anexo pide **«porcentaje»** y **«monto base»**, se refiere al impuesto
pagado afuera: el **dividendo bruto** (antes de la retención) y la tarifa del
agente retenedor — típicamente **30 %** para EE.UU. (art. 871(a) IRC, visible en
la casilla 3b del 1042-S).

> ⚠️ Si el aplicativo calcula el impuesto como *base × porcentaje*, puede dar un
> valor distinto al efectivamente pagado. El art. 254 solo permite descontar lo
> **pagado**. Si el campo es editable, corrígelo.

**El monto base es el dividendo bruto, no el valor del portafolio.** Las hojas
`Impuestos_Exteriordiv` y `Dividendos_Participaciones` del Programa Ayuda Renta
piden concepto, valor del impuesto, razón social, NIT, gravados y no gravados —
en ninguna se pide el valor de la inversión ni el rendimiento.

---

## La casilla 297

Es la única casilla auxiliar que el instructivo reconoce: «Valor compras con
factura electrónica». El propio instructivo dice que «se habilitará» si el
contribuyente responde afirmativamente a la pregunta del sistema.

Confirma que el aplicativo usa casillas no documentadas de forma rutinaria.

---

## Lo que el sistema NO calcula solo

| Casilla | Hay que liquidarla y digitarla |
|:--:|---|
| **135** | Sanciones. Incluida la de extemporaneidad |
| **138** | Número de dependientes — y de ella depende que se habilite la 139 |
| **130** | Anticipo del año anterior (viene de la casilla 133 de esa declaración) |
| **131** | Saldo a favor del año anterior (de su casilla 137) |

---

## Secciones contiguas que se confunden

| Casillas | Sección |
|---|---|
| 104 – 111 | Cédula de **dividendos** |
| 112 – 115 | **Ganancias ocasionales** |

Un aviso que aparece «al poner ganancia ocasional» puede ser en realidad de la
cédula de dividendos. **Confirma siempre a qué casilla corresponde el mensaje
antes de actuar.**

---

## Orden de presentación

1. Verificar RUT (responsabilidad 05) y firma electrónica
2. **Diligenciar / Presentar → Declaración de Renta Personas Naturales →
   Formulario 210**, seleccionando el año gravable
3. Digitar las casillas (el archivo `F210-casillas.txt` que genera la skill trae
   la lista completa)
4. Firmar y presentar
5. Si aplica, presentar el **Formulario 160** (activos en el exterior)
6. Si hay saldo a pagar, generar el **Formulario 490** y pagarlo por PSE
7. Descargar y archivar los acuses

> **Hay que presentar aunque no haya pago.** Con saldo a favor o impuesto cero,
> la sanción mínima del art. 639 (10 UVT) sigue aplicando si se presenta tarde.

---

## Qué hacer con un saldo a favor (art. 850)

| Opción | Cómo | Plazo |
|---|---|---|
| **Imputarlo** al año siguiente | Pasa a la casilla 131 de la declaración siguiente | automático, sin trámite |
| **Solicitar devolución** | Portal DIAN → Devoluciones y Compensaciones | 2 años desde el vencimiento |
| **Compensarlo** | Contra otras obligaciones con la DIAN | ídem |

Lo más sencillo es imputarlo. La devolución exige radicar solicitud con soportes
y la DIAN dispone de 50 días hábiles.
