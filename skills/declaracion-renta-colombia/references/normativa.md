# Normativa y parámetros

Fuente: Estatuto Tributario (ET), resoluciones de la DIAN y decretos
reglamentarios. **Verificar los valores del año cada temporada.**

---

## Parámetros por año

| Parámetro | 2024 | 2025 | 2026 |
|---|---:|---:|---:|
| UVT | $47.065 | **$49.799** | **$52.374** |
| Resolución que la fija | 000187/2023 | 000193/2024 | 000238/2025 |
| Componente inflacionario | — | **55,43 %** | — |
| TRM de cierre (31-dic) | — | **$3.757,08** | — |
| TRM promedio del año | — | **$4.052,86** | — |

El componente inflacionario de 2025 lo fijó el **Decreto 0898 de 2026**. Es el
porcentaje de los rendimientos financieros que **no** constituye renta para
personas naturales no obligadas a llevar contabilidad (art. 38 ET).

Las TRM las certifica la Superintendencia Financiera. La **de cierre** se usa
para activos en moneda extranjera (art. 288 ET); la **promedio** para ingresos
del exterior.

---

## ¿Quién está obligado a declarar? (art. 592 ET)

Se exonera quien cumple **todos** los topes. Basta con superar **uno** para
quedar obligado. Valores para AG2025:

| Criterio | UVT | Valor 2025 |
|---|---:|---:|
| Ingresos brutos | 1.400 | $69.718.600 |
| Patrimonio bruto a 31-dic | 4.500 | $224.095.500 |
| Consumos con tarjeta de crédito | 1.400 | $69.718.600 |
| Compras y consumos totales | 1.400 | $69.718.600 |
| Consignaciones, depósitos e inversiones | 1.400 | $69.718.600 |

> Los cinco valores vienen calculados en la consulta de información exógena,
> bajo los rótulos «Tope 1 - Ingresos» a «Tope 5 - Compras».

El certificado de ingresos y retenciones (form. 220) trae al pie una leyenda
preimpresa donde el trabajador manifiesta **no** estar obligado. Si sí lo está,
esa casilla se deja en blanco.

---

## Tarifa del impuesto (art. 241 ET)

Sobre la casilla 111, expresada en UVT:

| Desde (UVT) | Hasta (UVT) | Tarifa marginal | Suma (UVT) |
|---:|---:|---:|---:|
| 0 | 1.090 | 0 % | 0 |
| 1.090 | 1.700 | 19 % | 0 |
| 1.700 | 4.100 | 28 % | 116 |
| 4.100 | 8.670 | 33 % | 788 |
| 8.670 | 18.970 | 35 % | 2.296 |
| 18.970 | 31.000 | 37 % | 5.901 |
| 31.000 | en adelante | 39 % | 10.352 |

**Fórmula:** `(base_UVT − límite_inferior) × tarifa + suma`, todo × UVT.

Otras tarifas:

| Concepto | Tarifa | Norma |
|---|---:|---|
| Ganancia ocasional | 15 % | Art. 314 ET |
| Loterías, rifas y apuestas | 20 % | Art. 317 ET |
| Dividendos recibidos del exterior | 35 % | Art. 245 ET |

---

## Rentas exentas y deducciones

### Límite global (art. 336 num. 3)

El **menor** entre el **40 %** de la renta líquida de la cédula general y
**1.340 UVT** ($66.730.660 en 2025).

**Orden de imputación** (instructivo Res. 000044/2024): primero rentas de
trabajo (casilla 41), segundo rentas de trabajo sin relación laboral (53),
después rentas de capital (69) y por último no laborales (86), hasta agotar el
total. Ninguna cédula puede quedar en negativo.

**Quedan FUERA del límite:**
- El 1 % de compras con factura electrónica (casilla 28)
- Los 72 UVT por dependiente (casilla 139)

### Renta exenta del 25 % (art. 206 num. 10)

Tope de **790 UVT** = $39.341.210 en 2025 (lo bajó la Ley 2277 de 2022).

```
base = ingresos brutos − INCRNGO − cesantías exentas − deducciones
exenta = min(25 % × base, 790 UVT)
```

> La base se calcula **después** de restar las deducciones: al subir estas, la
> renta exenta baja. Cada peso de deducción adicional rinde el 75 %.

### Pensiones (art. 206 num. 5)

Exentas en la parte del pago **MENSUAL** que no exceda **1.000 UVT**
($49.799.000 mensuales en 2025). Es mensual, no anual — por eso casi todas las
pensiones colombianas quedan exentas al 100 %.

Se calcula sobre la **porción efectivamente recibida**, es decir después de
restar los aportes obligatorios a salud.

Usar **13 mesadas** en el régimen de prima media (incluye la mesada adicional).

> **La cédula de pensiones no admite deducciones imputables.** Solo el ingreso
> no constitutivo (aportes a salud, art. 56) y esta renta exenta.

### Cesantías (art. 206 num. 4)

Según el **promedio mensual de ingresos de los últimos 6 meses**, en UVT:

| Promedio (UVT) | Porción exenta |
|---:|---:|
| ≤ 350 | 100 % |
| 350 – 410 | 90 % |
| 410 – 470 | 80 % |
| 470 – 530 | 60 % |
| 530 – 590 | 40 % |
| 590 – 650 | 20 % |
| > 650 | 0 % |

> **Se aplica POR EMPLEADOR, no al consolidado.** Lo confirma la hoja
> `renta exenta` del Programa Ayuda Renta oficial de la DIAN, cuya fórmula es
> `N14 = LOOKUP(M14, tabla) × L14` por cada fila de empleador, y luego suma.

### Deducciones

| Concepto | Tope | Norma |
|---|---|---|
| Pagos por salud (medicina prepagada) | 16 UVT mensuales | Art. 387 num. 1 |
| Dependientes — 10 % de ingresos laborales | 32 UVT mensuales (384 UVT/año) | Art. 387 par. 2 |
| Dependientes — 72 UVT (fuera del límite del 40 %) | 72 UVT | Art. 336 num. 3 |
| Intereses de vivienda | 1.200 UVT | Art. 119 |
| Intereses de crédito ICETEX | 100 UVT | Art. 119 inc. 3 |
| GMF (4×1.000) | 50 % de lo pagado | Art. 115 |
| 1 % de compras con factura electrónica | 240 UVT | Art. 336 num. 5 |
| Aportes voluntarios y AFC | 30 % del ingreso, máx. 3.800 UVT | Art. 126-1 y 126-4 |

**Dependientes: las dos deducciones son acumulables** cuando hay relación
laboral. El instructivo lo dice expresamente:

> *«Cuando se tengan ingresos provenientes de rentas de trabajo y un mismo
> dependiente solo dará lugar a una de estas dos deducciones, **excepto cuando
> se tenga rentas provenientes de una relación laboral o legal y reglamentaria,
> caso en el cual se podrá aplicar ambas deducciones por un mismo
> dependiente**.»*

Califican como dependientes (art. 387 par. 2):
1. Hijos hasta 18 años
2. Hijos de 18 a 23 si el contribuyente financia su educación superior (ICFES/SENA)
3. Hijos mayores de 23 con dependencia certificada por Medicina Legal
4. Cónyuge o compañero(a) sin ingresos o con ingresos < 260 UVT
5. Padres y hermanos en las mismas condiciones

**El 1 % de compras**: exige factura electrónica **con el NIT del adquirente** y
pago por medios electrónicos. La DIAN ya publica la base depurada en la exógena
bajo «Monto total de facturación electrónica susceptible de beneficio».

---

## Patrimonio

| Activo | Valor patrimonial | Norma |
|---|---|---|
| Inmuebles | El **mayor** entre costo de adquisición, costo fiscal, autoavalúo y avalúo catastral | Art. 277 |
| Cuentas bancarias | Saldo a 31-dic | Art. 268 |
| Acciones y aportes | Costo fiscal | Art. 272 |
| Cuentas por cobrar | Valor nominal | Art. 270 |
| Vehículos y demás | Costo fiscal | Art. 267 |
| Moneda extranjera | TRM de cierre | Art. 288 |

**Posesión** (art. 263): *«el aprovechamiento económico, potencial o real, de
cualquier bien en beneficio del contribuyente»*. Un bien cuya escritura está a
nombre de un tercero **sí** se declara si hay aprovechamiento económico.

**Renta presuntiva: 0 % desde 2021** (art. 188, modificado por la Ley 2010/2019).

---

## Ganancias ocasionales

Se causan por la venta de activos fijos poseídos **2 años o más** (art. 300 ET).
Si se poseyeron menos de 2 años, la utilidad es **renta ordinaria** y va a la
cédula correspondiente — lo que suele ser peor, porque la tarifa marginal supera
al 15 %.

**Retención en la venta de vehículos e inmuebles: 1 %.** La base es el **mayor**
entre el precio pactado y el avalúo oficial (art. 398 con art. 90 ET; DIAN,
Concepto 12330 de 2025). Dividir la retención entre 1 % da un **piso** del precio,
no el precio exacto.

---

## Impuestos pagados en el exterior (art. 254)

Descuento **directo del impuesto**, no deducción. Limitado al impuesto
colombiano sobre esas mismas rentas.

Para dividendos del exterior la base del límite es: casilla 107 + casilla 108 −
casilla 118 (art. 254-1).

> **EE.UU. no grava las ganancias de capital de extranjeros no residentes**
> (IRC §871(a)). La venta de acciones de un no residente tributa solo en
> Colombia. Lo que sí se retiene allá es el **30 % sobre dividendos**, que
> consta en la casilla 3b del formulario **1042-S**.

---

## Anticipo (art. 807)

```
anticipo = porcentaje × impuesto neto − retenciones del año
```

| Situación | Porcentaje |
|---|---:|
| Primera declaración | 25 % |
| Segunda declaración | 50 % |
| Tercera en adelante | 75 % |

**Nunca es negativo**: si el cálculo da menos que cero, la casilla 133 es cero.
Alternativamente puede calcularse sobre el promedio de los dos últimos años y
escoger el menor.

---

## Sanciones

### Extemporaneidad (art. 641)

| Situación | Sanción por mes o fracción | Tope |
|---|---|---|
| Con impuesto a cargo | 5 % del impuesto | 100 % del impuesto |
| **Sin impuesto a cargo** | **0,5 % de los ingresos brutos** | el menor entre 5 % de los ingresos, el doble del saldo a favor, o 2.500 UVT |
| Sin ingresos ni impuesto | 1 % del patrimonio líquido del año anterior | el menor entre 10 % del patrimonio, el doble del saldo a favor, o 2.500 UVT |

### Sanción mínima (art. 639)

**10 UVT del año en que se presenta.** Para una declaración presentada en 2026:
10 × $52.374 = **$523.740**.

> Aplica aunque no haya impuesto a cargo, y en la práctica **casi siempre supera
> al cálculo del art. 641** en declaraciones pequeñas. No la olvides.

### Inexactitud (art. 648)

100 % de la diferencia, **agravada al 200 % cuando hay omisión de ingresos**.
Es la causal más frecuente de requerimiento cuando lo declarado no cruza con lo
que reportaron terceros.

### Intereses de mora (art. 635)

A la tasa de usura vigente menos dos puntos, por cada día de retraso en el pago.

---

## Beneficio de auditoría (art. 689-3)

Vigente para los años gravables **2022 a 2026**.

| Si el impuesto neto crece frente al año anterior | La declaración queda en firme en |
|---|---|
| ≥ 35 % | **6 meses** |
| ≥ 25 % y < 35 % | **12 meses** |

**Requisitos:** presentación oportuna, pago total dentro del plazo, y que la
retención en la fuente declarada sea la real.

**No hay casilla en el F210**: opera *ope legis*. El contribuyente solo debe
poder demostrarlo.

> ⚠️ **Bajar el impuesto endurece el umbral.** El requisito es relativo al año
> anterior: si el impuesto neto de este año baja, el del año pasado tiene que
> haber sido aún menor para cumplir el 35 %. Una optimización agresiva puede
> costar la firmeza anticipada.

---

## Declaración de activos en el exterior (Formulario 160, art. 607)

**Obligado** si el valor patrimonial de los activos en el exterior a 1 de enero
supera **2.000 UVT del año de presentación**.

Si el total supera **3.580 UVT** hay que individualizar cada activo; si no, se
declaran **agregados por jurisdicción**.

El año que se declara es el de la **fecha de corte**: los activos a 1-ene-2026
se declaran en el formulario del año **2026**, que se presenta junto con la renta
del año gravable 2025.

**Sanción de extemporaneidad propia:** 0,5 % mensual del valor de los activos
(1 % después del emplazamiento), con tope del 10 %. Es autónoma: aplica aunque
no haya impuesto.
