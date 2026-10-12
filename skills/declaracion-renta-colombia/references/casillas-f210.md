# Formulario 210 — casillas e identidades

Estructura oficial según la **Resolución 000044 del 14-03-2024**, que lo
prescribe para el año gravable 2023 **y siguientes** (sigue vigente para
AG2025). La Resolución 000120 de 2024 modificó el instructivo y la 000227 de
2025 las compiló, sin cambiar la estructura.

> Descargable en
> `https://www.dian.gov.co/normatividad/Normatividad/Resoluci%C3%B3n%20000044%20de%2014-03-2024.pdf`
> El formulario oficial publicado cada año está en
> `https://www.dian.gov.co/atencionciudadano/formulariosinstructivos/Formularios/<año>/Formulario_210_<año>.pdf`
> (viene cifrado; `pikepdf` lo abre sin contraseña y permite re-guardarlo).

---

## Mapa de secciones

| Casillas | Sección |
|---|---|
| 29 – 31 | Patrimonio |
| 32 – 42 | Rentas de trabajo |
| 43 – 57 | Rentas de trabajo sin relación laboral (honorarios) |
| 58 – 73 | Rentas de capital |
| 74 – 90 | Rentas no laborales |
| 91 – 98 | Cédula general (consolidación) |
| 99 – 103 | **Cédula de pensiones** |
| 104 – 111 | **Cédula de dividendos** |
| 112 – 115 | **Ganancias ocasionales** |
| 116 – 137 | Liquidación privada |
| 138 – 141 | Datos informativos |

> Las secciones de dividendos y ganancias ocasionales son **contiguas**: es la
> confusión más frecuente. La casilla 107 es de dividendos, no de GO.

---

## Identidades que deben cerrar

El validador comprueba todas estas. Si alguna falla, hay un error de modelado.

```
 31 = 29 − 30
 34 = 32 − 33
 37 = 35 + 36
 40 = 38 + 39
 42 = 34 − 41
 61 = 58 − 59 − 60
 73 = 61 − 69                 (renta líquida neta de lo imputado)
 78 = 74 − 75 − 76 − 77
 90 = 78 − 86
 91 = 41 + 42 + 53 + 57 + 69 + 73 + 86 + 90
 92 = 28 + 41 + 53 + 69 + 86 + 139
 93 = 91 − 92
 97 = 93 + 96 − 94 − 95
101 = 99 − 100
103 = 101 − 102
111 = max(97, 98) + 103 + 107 + 108 − 118
115 = 112 − 113 − 114
121 = 116 + 117 + 118 + 119 + 120
125 = 122 + 123 + 124
126 = 121 − 125
129 = 126 + 127 − 128
134 = 129 + 133 − 130 − 131 − 132      (mínimo 0)
136 = 129 + 133 + 135 − 130 − 131 − 132
137 = 130 + 131 + 132 − 129 − 133 − 135
```

**Las casillas 136 y 137 nunca pueden ser ambas mayores que cero.**

### Por qué 91 suma las exentas y 92 las resta

La casilla 91 **reconstituye** la renta líquida bruta de cada cédula, porque las
casillas 42, 73 y 90 vienen **netas** de la parte imputada:

```
41 + 42 = 34      (trabajo)
69 + 73 = 61      (capital)
86 + 90 = 78      (no laborales)
```

Luego la 92 resta el total limitado de una sola vez. Si se modela la 73 como
igual a la 61 cuando la 69 es mayor que cero, la deducción **no tiene efecto**.

---

## Casillas que se confunden

| Casilla | Qué es realmente |
|:--:|---|
| **28** | 1 % de compras con factura electrónica. Va **fuera** del límite del 40 % y suma directo a la 92 |
| **36** | Rentas exentas de trabajo: cesantías exentas **+** el 25 % del art. 206 num. 10 |
| **39** | Deducciones: GMF 50 %, ICETEX, salud, dependientes del art. 387 par. 2, vivienda |
| **41** | Lo anterior **ya limitado** por el art. 336 e imputado a rentas de trabajo |
| **69** | Lo mismo, pero imputado a rentas de capital (cuando no alcanza en trabajo) |
| **99–103** | Cédula de **pensiones**. La 102 es la exención del art. 206 num. 5 |
| **107** | 1.ª subcédula de **dividendos nacionales** (art. 49 num. 3). No es ganancia ocasional |
| **109** | Dividendos recibidos del **exterior**. Gravados al 35 % en la casilla 120 |
| **122** | Descuento por impuestos pagados en el exterior (art. 254). **Descuento, no deducción** |
| **130** | Anticipo liquidado en la declaración del **año anterior** (su casilla 133) |
| **131** | Saldo a favor del año anterior no solicitado en devolución (su casilla 137) |
| **133** | Anticipo para el año **siguiente**. Nunca negativo |
| **135** | Sanciones. **El sistema no las calcula**: hay que liquidarlas y digitarlas |
| **138** | Número de dependientes. Es un **conteo**, no un valor en pesos |
| **139** | 72 UVT por dependiente. Va **fuera** del límite del 40 % |
| **140** | Marca de superación del tope indicativo del art. 336-1 (costos > 60 % en honorarios) |

---

## Redondeo (art. 577)

**Todos los valores van en múltiplos de mil**, aproximando al más cercano.

**Excepciones**: las casillas que no son valores monetarios — 138 (número de
dependientes), 140 y 141 (marcas) — van sin redondeo ni símbolo de peso.

Consecuencia práctica: hay que redondear **y después recalcular las casillas
derivadas**, no al revés. Si se redondea cada casilla por separado, las
identidades dejan de cerrar por diferencias de a mil pesos.

---

## Casillas auxiliares del aplicativo (200 – 400)

El formulario impreso llega hasta la **141**. El SI de Diligenciamiento del
MUISCA usa además casillas internas de numeración alta que **no figuran en
ninguna norma publicada**.

Se verificó la ausencia de las casillas 304 a 334 en: Resolución 000044/2024,
Resolución 000120/2024, Resolución 000227/2025, el Formulario 210 oficial
publicado para 2026 y el Programa Ayuda Renta. Cero apariciones.

El instructivo solo reconoce **una**: la **297** (valor de compras con factura
electrónica), y la describe como algo que «se habilitará» según las respuestas
del contribuyente — admitiendo que el aplicativo usa casillas no documentadas.

Ver `muisca.md` para cómo manejarlas.

---

## Formulario 160 — activos en el exterior

### Hoja 1

| Casilla | Contenido |
|:--:|---|
| 1 | Año (el de la **fecha de corte**: activos a 1-ene-2026 → año 2026) |
| 5 / 6 | NIT / DV |
| 7 – 10 | Apellidos y nombres |
| 12 | Código de dirección seccional |
| 25 / 26 | Corrección (código y formulario anterior) |
| **27** | **¿Valor patrimonial superior a 3.580 UVT?** — define qué pide la hoja 2 |
| 28 – 30 | Bloque > 3.580 UVT *(automáticas)* |
| 31 – 33 | Bloque ≤ 3.580 UVT *(automáticas)* |
| 34 | Sanción por extemporaneidad |
| 35 / 36 / 981 | Signatario y representación |
| 980 | Pago total (no se activa en declaraciones virtuales) |

### Hoja 2

Con la casilla 27 en **SÍ** pide: 37 (jurisdicción), 38 (naturaleza), 39 (tipo
de activo), 40 (identificación) y 41 (valor patrimonial).

Con la casilla 27 en **NO** pide solo: 37, 38 y 41 — y los activos se declaran
**agregados por jurisdicción**, un renglón por país.

**Naturaleza** (art. 60 ET): *Fijo* si no se enajena dentro del giro ordinario
del negocio; *Movible* en caso contrario. Acciones y depósitos de un particular
son **Fijos**.

Las casillas 28 a 33 **no se digitan**: el sistema las calcula desde la hoja 2.

---

## Formulario 490 — recibo de pago

Solo se genera si la casilla 136 es mayor que cero. Concepto **01** (declaración
privada), formulario asociado **210**.

> Si una corrección deja el saldo en cero o a favor, hay que **eliminar** el
> F490 generado antes: un recibo obsoleto induce a pagar algo que ya no se debe.
