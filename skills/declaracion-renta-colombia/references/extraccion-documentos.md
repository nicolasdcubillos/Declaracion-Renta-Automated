# Extracción de documentos

Los soportes llegan en formatos hostiles: PDF cifrados, escaneos sin texto,
hojas de cálculo con el dato enterrado. Esto es lo que funciona.

---

## 1. Diagnóstico inicial

Antes de leer nada, clasifica cada archivo:

```python
import pdfplumber

for f in archivos:
    try:
        d = pdfplumber.open(f)
        t = "".join((p.extract_text() or "") for p in d.pages)
        print(f, len(d.pages), "TEXTO" if t.strip() else "IMAGEN")
    except Exception:
        print(f, "CIFRADO")
```

Tres casos, tres tratamientos distintos.

---

## 2. PDF cifrados

**La contraseña casi siempre es el número de cédula sin dígito de
verificación.** Lo usan Lulo, Nequi, Nu, Davivienda, Colpensiones, Falabella y
la mayoría de entidades financieras colombianas.

```python
import pikepdf

for clave in [cedula, cedula + dv, cedula[:-1]]:
    try:
        pikepdf.open(f, password=clave).save("D_" + f)
        break
    except Exception:
        pass
```

Si no se conoce la cédula todavía, **empieza por un documento sin cifrar** —
normalmente la exógena o el certificado de ingresos — para obtenerla.

> Algunos PDF «cifrados» solo tienen restricciones de permisos:
> `pikepdf.open()` los abre sin contraseña y emite un *warning* si se le pasa
> una. El formulario 210 oficial de la DIAN es uno de esos.

---

## 3. Escaneos sin capa de texto

`pdfplumber` devuelve cadena vacía y `page.chars` está en cero. Renderiza la
página y **léela visualmente**:

```python
page = pdfplumber.open(f).pages[0]
page.to_image(resolution=200).save("pagina.png")
```

Después abre el PNG con la herramienta de visión y transcribe casilla por
casilla.

**Nunca adivines una cifra de un escaneo.** Si la imagen no es legible, pide una
mejor copia. Un dígito mal leído se propaga a toda la liquidación.

**Control obligatorio:** la suma de los renglones transcritos debe reproducir el
total impreso en el propio documento. En un certificado de ingresos (form. 220):

```
casilla 36 + 37 + 42 + 46 (+ los demás)  ==  casilla 52
```

Si no cuadra, se transcribió mal.

---

## 4. La información exógena — el documento clave

Es la consulta «Información reportada por terceros» del portal DIAN, en XLSX.
Vale más que cualquier otro soporte porque:

- Trae **los cinco topes del art. 592** ya calculados
- Mapea cada dato al **renglón sugerido del F210** (`R29`, `R58`, `R132`…)
- Contiene información que **no está en ningún otro documento**: avalúos
  catastrales, avalúos de vehículos, cuentas por cobrar, saldos a favor de años
  anteriores, patrimonio bruto declarado el año anterior

```python
import openpyxl
wb = openpyxl.load_workbook("reporteExogena.xlsx", data_only=True)
for nm in wb.sheetnames:
    for row in wb[nm].iter_rows(values_only=True):
        v = [str(c).strip() for c in row if c not in (None, "")]
        if v:
            print(nm, "|", "  |".join(v))
```

### Columnas que importan

| Columna | Para qué |
|---|---|
| NIT y nombre de quien reporta | Identifica la fuente |
| Detalle | El concepto y su **código DIAN** (1476 avalúo catastral, 1480 vehículo, 2276 pensión…) |
| Valor | La cifra |
| **Uso declaración sugerida** | **El renglón del F210 al que va** |
| Información adicional | Número de cuenta, placa, matrícula, **porcentaje de participación** |

### Las tres cifras de compras que NO son intercambiables

| Rótulo | Qué es |
|---|---|
| Tope 3 — Consumo TC | Todo lo pasado por tarjeta |
| Tope 5 — Compras | Compras en factura electrónica |
| **Monto total de facturación electrónica susceptible de beneficio** | **La base del 1 % del art. 336 num. 5** |

Solo la tercera sirve para la casilla 28: es la que ya pasó el filtro de factura
electrónica con el NIT del adquirente **y** pago por medios electrónicos.

### Las notas al final

La exógena suele traer **notas manuscritas** del contribuyente o su contador en
las últimas filas («Incluir los honorarios pagados por X», «Incluir las CxC a
socios»). **Léelas**: señalan documentos que faltan y que la DIAN no reporta.

---

## 5. Hojas de trabajo del contribuyente

Si el usuario aporta su propio Excel de activos, suele contener el histórico de
avalúos y los **porcentajes de participación** en bienes compartidos.

Vale como fuente, pero **conciliala contra la exógena**. En un caso real el
papel de trabajo usaba 70 % de participación en un inmueble y la exógena
reportaba 50 %: una diferencia de $97 millones en el patrimonio.

Cuando las dos fuentes difieren:
1. No escojas en silencio.
2. Adopta la que reconcilie con el histórico declarado, y dilo.
3. Deja el punto como pendiente, cuantificado, pidiendo la escritura o el
   certificado de tradición.

---

## 6. Documentos del exterior

| Documento | Qué acredita |
|---|---|
| **1042-S** | Dividendos de fuente estadounidense y la retención. Casilla 1 = income code (06 = dividendos), 2 = gross income, 3b = tax rate, 7a = federal tax withheld |
| Estado de cuenta anual del bróker | Saldo a 31-dic, dividendos, «securities transferred out» |
| Reporte de operaciones | Fechas, cantidades y precios de cada venta |

**Para reconstruir el costo fiscal de acciones** cuando el bróker no lo informa:
busca el valor de las acciones transferidas y divídelo entre la cantidad. Después
**verifica con el saldo**: `acciones iniciales − vendidas == saldo final`.

> Cuidado con confundir **compras** con **ventas** en los extractos: ambas
> aparecen como movimientos. Un error así infla los ingresos.

---

## 7. El Programa Ayuda Renta oficial

Es la herramienta en Excel que publica la DIAN cada año. Sirve como **árbitro**
en interpretaciones dudosas: sus fórmulas son la posición oficial.

```
https://storagecdndian.blob.core.windows.net/site/Transaccional/PREVALIDADORES/Programa-Ayuda-Renta-DIAN-<año>.zip
```

Hojas útiles: `renta exenta` (cesantías), `TOPES`, `tarifa imporenta`,
`cesantias`, `descuentos`, `Impuestos_Exteriordiv`, `Dividendos_Participaciones`.

Para leer las fórmulas sin ejecutarlo:

```python
wb = openpyxl.load_workbook(archivo, data_only=False)  # fórmulas
wb = openpyxl.load_workbook(archivo, data_only=True)   # valores
```

> **Si necesitas modificar el .xlsm, no uses openpyxl**: destruye los dibujos y
> rompe el archivo. Tampoco `ElementTree`, que renombra los namespaces. La única
> vía segura es editar el XML como **texto plano** dentro del ZIP, preservando
> todas las partes.

---

## 8. Checklist de verificación cruzada

Antes de dar por buena la extracción:

- [ ] La suma de renglones de cada certificado reproduce su propio total
- [ ] Cada ingreso declarado aparece en la exógena, y viceversa
- [ ] Los saldos bancarios coinciden entre certificado y exógena
- [ ] Las retenciones suman lo mismo en ambas fuentes
- [ ] El componente inflacionario está al porcentaje del año
- [ ] El patrimonio bruto se puede conciliar contra el del año anterior
- [ ] Toda nota o anotación manual del contribuyente quedó atendida
- [ ] Los documentos que faltan están listados y cuantificados
