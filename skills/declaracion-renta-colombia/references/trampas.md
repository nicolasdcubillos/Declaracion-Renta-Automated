# Trampas

Errores reales cometidos y corregidos preparando declaraciones. Cada uno costó
tiempo o dinero.

---

## 1. Cesantías: la tabla se aplica por empleador

**El error:** aplicar la tabla del art. 206 num. 4 al promedio consolidado de
los últimos 6 meses de todos los empleadores.

**Lo correcto:** se aplica al promedio de **cada empleador por separado** y
después se suman los resultados.

**Cómo se descubrió:** la hoja `renta exenta` del Programa Ayuda Renta oficial
calcula `N14 = LOOKUP(M14, tabla) × L14` fila por fila, una por empleador.

En un caso real: Microsoft con promedio de 511,82 UVT → 60 % exento; Javeriana
con 75,95 UVT → 100 % exento. Consolidados habrían dado un porcentaje único y
peor.

---

## 2. Dependientes: las dos deducciones son acumulables

**El error:** aplicar solo una de las dos deducciones por dependiente.

**Lo correcto:** con relación laboral proceden **ambas** sobre la misma persona:

| Deducción | Norma | Dónde |
|---|---|---|
| 72 UVT | Art. 336 num. 3 | casilla 139, **fuera** del límite del 40 % |
| 10 % de ingresos laborales, tope 32 UVT/mes | Art. 387 par. 2 | dentro de la casilla 39 |

El instructivo de la Res. 000044/2024 lo dice expresamente, con la palabra
«excepto».

**Valió $2.661.792** en un caso: convirtió un pago de $1.693.000 en una
devolución de $969.000.

> Parte del beneficio viene de que al bajar el impuesto **desaparece el
> anticipo** del art. 807.

---

## 3. La base del 1 % de compras

**El error:** tomar los consumos con tarjeta de crédito.

**Lo correcto:** el renglón **«Monto total de facturación electrónica
susceptible de beneficio»** de la exógena.

En un caso las tres cifras eran $63.369.444 (consumo TC), $26.507.408 (compras)
y **$25.745.832** (la correcta). El art. 336 num. 5 exige factura electrónica con
el NIT del adquirente y pago electrónico: la DIAN ya aplicó ese filtro.

---

## 4. Pensiones: el tope es mensual

**El error:** leer las 1.000 UVT del art. 206 num. 5 como tope anual.

**Lo correcto:** son **1.000 UVT mensuales** ($49.799.000/mes en 2025). Casi
cualquier pensión colombiana queda exenta al 100 %.

Se calcula sobre la porción **efectivamente recibida**, después de los aportes a
salud. Usar **13 mesadas** en el régimen de prima media.

---

## 5. La cédula de pensiones no admite deducciones

**El error:** restar medicina prepagada y GMF contra la pensión.

**Lo correcto:** la cédula de pensiones (99–103) solo acepta el ingreso no
constitutivo por aportes a salud y la renta exenta del art. 206 num. 5. Las
deducciones son de la **cédula general**.

**Consecuencia:** si el contribuyente es pensionado y su cédula general es
pequeña, el límite del 40 % se calcula sobre esa base pequeña y **las
deducciones se pierden**. En un caso se perdieron $3.282.000 de $4.232.000
solicitados.

---

## 6. El orden de imputación del art. 336

**El error:** poner todas las deducciones en la casilla 41 (rentas de trabajo).

**Lo correcto:** el instructivo ordena distribuirlas en cascada — trabajo (41),
trabajo sin relación laboral (53), capital (69), no laborales (86) — hasta
agotar el total limitado.

**Síntoma del error:** la casilla 42 queda **negativa**. Si no hay rentas de
trabajo, la 41 debe ser cero.

Además, las casillas 42, 73 y 90 van **netas** de lo imputado:

```
41 + 42 = 34      69 + 73 = 61      86 + 90 = 78
```

Si se modela `73 = 61` con `69 > 0`, la deducción se cancela sola entre las
casillas 91 y 92, y **no tiene ningún efecto**.

---

## 7. La retención del 39 % sobre RSU no es impuesto de EE.UU.

**El error:** tratarla como impuesto pagado en el exterior y descontarla por el
art. 254.

**Lo correcto:** es **retención en la fuente colombiana** del art. 383 ET,
practicada por el empleador local sobre el valor de las acciones entregadas.
Va a la casilla 132, no a la 122.

> EE.UU. **no grava las ganancias de capital de no residentes** (IRC §871(a)).
> Lo que sí retiene es el 30 % sobre dividendos, y eso consta en el 1042-S.

---

## 8. Bajar el impuesto puede costar el beneficio de auditoría

El art. 689-3 exige que el impuesto neto **crezca un 35 %** frente al año
anterior para la firmeza en 6 meses. Es un umbral **relativo**.

Si se optimiza y el impuesto de este año baja, el del año anterior tiene que
haber sido aún más bajo para cumplir. En un caso el umbral pasó de «AG2024 menor
a $56.070.370» a «menor a $46.780.740» — y el contribuyente podía quedar en el
rango intermedio, perdiendo la firmeza anticipada.

**Siempre advertirlo al presentar un escenario optimizado.**

---

## 9. La sanción mínima casi siempre manda

Art. 639: **10 UVT del año de presentación**. Para 2026, $523.740.

En declaraciones pequeñas, el cálculo del art. 641 (0,5 % de los ingresos brutos
por mes sin impuesto a cargo) suele quedar muy por debajo. En un caso: $141.594
calculados contra $523.740 de mínima.

Aplica **aunque no haya impuesto a cargo**. Y si hay saldo a favor, la sanción
se compensa dentro de la misma liquidación: no exige desembolso.

---

## 10. El anticipo desaparece, no se vuelve negativo

```
anticipo = 75 % × impuesto neto − retenciones
```

Si da negativo, la casilla 133 es **cero** (art. 807). Por eso bajar el impuesto
produce un ahorro mayor al del impuesto mismo: elimina el anticipo completo.

**Y revisa si es la primera declaración**: ahí el porcentaje es 25 %, no 75 %.

---

## 11. Archivos obsoletos en disco

**El error:** el generador omitió el Formulario 490 porque ya no había saldo a
pagar, pero **dejó en disco el archivo de la corrida anterior**, que anunciaba
«TOTAL A PAGAR $1.693.000».

**La corrección:** cuando un formulario deja de aplicar, hay que **borrarlo**,
no solo dejar de generarlo.

Mismo cuidado con los PDF y los ZIP: regenerarlos todos después de cada cambio.

---

## 12. El redondeo al millar no aplica a los conteos

**El error:** la casilla 138 (número de dependientes) pasó por la función de
redondeo del art. 577 y `1` se convirtió en `0`, dejando un formulario
contradictorio: cero dependientes con $3.586.000 de deducción por dependientes.

**Lo correcto:** las casillas 138, 140 y 141 no son valores monetarios. Van sin
redondeo y sin símbolo de peso.

---

## 13. Vehículos: la retención del 1 % no revela el precio

**El error:** dividir la retención entre 1 % para deducir el precio de venta.

**Lo correcto:** la base de retención es el **mayor** entre el precio pactado y
el avalúo del Ministerio de Transporte (art. 398 con art. 90 ET; Concepto DIAN
12330 de 2025). Si el precio real fue superior al avalúo, la retención resulta
proporcionalmente menor.

El cociente da un **piso**, no el precio. Hay que pedir el contrato de
compraventa.

---

## 14. Ventas y recompras del mismo título

Vender y volver a comprar **sí** realiza el ingreso: son operaciones
independientes. La ganancia de la venta se declara aunque el dinero se haya
reinvertido inmediatamente.

Y distingue en los extractos: **una compra no es una venta**. Confundirlas infla
los ingresos.

---

## 15. Bienes a nombre de terceros

Un inmueble cuya escritura está a nombre de otro **sí se declara** si el
contribuyente tiene el aprovechamiento económico (art. 263 ET: *«el
aprovechamiento económico, potencial o real, de cualquier bien en beneficio del
contribuyente»*).

Señal típica: paga el predial pero el paz y salvo registra otro propietario.

Pedir siempre escritura o promesa de compraventa **y** certificado de tradición.
Y si el bien es familiar, **coordinar los porcentajes entre las declaraciones de
los parientes** para que sumen 100 % sin doble conteo ni omisión.

---

## 16. Omitir ingresos reportados por terceros

Es la causal más frecuente de requerimiento. El cruce es automático.

Art. 648: sanción del **100 %** de la diferencia, **agravada al 200 % cuando hay
omisión de ingresos**.

Si un tercero reportó un ingreso y se decide no declararlo, tiene que haber un
fundamento escrito y sólido. «No me acuerdo» no lo es.

---

## 17. Conciliar la variación patrimonial

El art. 236 faculta a la DIAN a presumir renta cuando el patrimonio crece sin
justificación. Una **caída** inexplicada levanta la pregunta inversa: ¿se omitió
un activo?

La exógena reporta el patrimonio bruto declarado el año anterior. Úsalo como
control y explica la diferencia.
