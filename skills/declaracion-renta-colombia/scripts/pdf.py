# -*- coding: utf-8 -*-
"""
CONVERSION DE LOS FORMULARIOS A PDF

    python pdf.py

Usa Google Chrome en modo headless, que respeta el CSS de impresion del HTML.
Genera los PDF en salida/pdf/ listos para enviar al contador.
"""
import os, subprocess, shutil, glob, datetime

RUTA = os.path.dirname(os.path.abspath(__file__))
SAL = os.path.join(RUTA, "salida")
PDF = os.path.join(SAL, "pdf")

NAVEGADORES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
]

DOCS = [
    ("F210-AG2025.html", "Formulario-210-Renta-AG2025.pdf",
     "Formulario 210 - Declaracion de renta"),
    ("F160-AG2025.html", "Formulario-160-Activos-Exterior-AG2025.pdf",
     "Formulario 160 - Activos en el exterior"),
    ("F490-AG2025.html", "Formulario-490-Recibo-Pago.pdf",
     "Formulario 490 - Recibo oficial de pago"),
]


def navegador():
    for n in NAVEGADORES:
        if n and os.path.exists(n):
            return n
    return None


def convertir(nav, origen, destino):
    cmd = [nav, "--headless", "--disable-gpu", "--no-sandbox",
           "--no-pdf-header-footer",
           "--virtual-time-budget=4000",
           f"--print-to-pdf={destino}",
           f"file://{origen}"]
    r = subprocess.run(cmd, capture_output=True, timeout=120)
    return os.path.exists(destino) and os.path.getsize(destino) > 5000


def paginas(ruta):
    """Cuenta las paginas del PDF sin dependencias externas."""
    try:
        with open(ruta, "rb") as f:
            data = f.read()
        n = data.count(b"/Type /Page") - data.count(b"/Type /Pages")
        return n if n > 0 else data.count(b"/Type/Page") - data.count(b"/Type/Pages")
    except Exception:
        return "?"



# ---------------------------------------------------------------- markdown
CSS_MD = """
@page { size: Letter; margin: 16mm 14mm; }
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
     font-size:10pt;line-height:1.55;color:#14202b;max-width:none;margin:0}
h1{color:#0b3d68;font-size:20pt;border-bottom:3px solid #0b3d68;padding-bottom:6px;margin:0 0 4px}
h2{color:#0b3d68;font-size:13pt;margin:20px 0 7px;padding-bottom:3px;border-bottom:1px solid #c9d3dc;
   page-break-after:avoid}
h3{color:#0b3d68;font-size:11pt;margin:14px 0 5px;page-break-after:avoid}
h4{font-size:10pt;margin:10px 0 4px}
table{width:100%;border-collapse:collapse;margin:9px 0;font-size:8.6pt;page-break-inside:avoid}
th{background:#0b3d68;color:#fff;padding:5px 7px;text-align:left;font-size:8pt;
   text-transform:uppercase;letter-spacing:.4px}
td{padding:4px 7px;border-bottom:1px solid #e9edf1;vertical-align:top}
tr:nth-child(even) td{background:#f7f9fb}
blockquote{background:#fff8e1;border-left:4px solid #e0a800;margin:10px 0;padding:8px 13px;
           font-size:9pt;page-break-inside:avoid}
code{background:#eef1f4;padding:1px 4px;border-radius:3px;font-size:8.5pt}
pre{background:#f4f6f8;border-left:3px solid #0b3d68;padding:9px 12px;overflow-x:auto;
    font-size:8.2pt;line-height:1.4;page-break-inside:avoid}
pre code{background:none;padding:0}
hr{border:none;border-top:1px solid #c9d3dc;margin:18px 0}
a{color:#0b3d68}
strong{color:#0b2b48}
ul,ol{margin:6px 0;padding-left:20px}
li{margin:2px 0}
"""


def md_a_pdf(nav, md_path, pdf_path, titulo):
    """Convierte un .md a PDF con el mismo estilo de los formularios."""
    try:
        import markdown
    except ImportError:
        return False, "falta el paquete 'markdown' (pip install markdown)"
    with open(md_path, encoding="utf-8") as f:
        cuerpo = markdown.markdown(f.read(), extensions=["tables", "fenced_code", "sane_lists"])
    html = (f"<!DOCTYPE html><html lang='es'><head><meta charset='utf-8'>"
            f"<title>{titulo}</title><style>{CSS_MD}</style></head><body>{cuerpo}</body></html>")
    tmp = pdf_path + ".tmp.html"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(html)
    ok = convertir(nav, tmp, pdf_path)
    os.remove(tmp)
    return ok, ""


def main():
    nav = navegador()
    if not nav:
        print("  ✗ No se encontro Chrome, Edge ni Brave.")
        print("    Alternativa: abra los .html y use Imprimir -> Guardar como PDF.")
        return
    print(f"  Motor: {nav.split(chr(47))[2] if nav.startswith(chr(47)+chr(65)+chr(112)) else os.path.basename(nav)}")
    os.makedirs(PDF, exist_ok=True)
    ok = 0
    for html, salida, titulo in DOCS:
        org = os.path.join(SAL, html)
        if not os.path.exists(org):
            print(f"  – {html} no existe (ejecute primero: python generar.py)")
            continue
        dst = os.path.join(PDF, salida)
        if convertir(nav, org, dst):
            kb = os.path.getsize(dst) // 1024
            print(f"  ✓ {salida:<46} {paginas(dst)} pag  {kb} KB")
            ok += 1
        else:
            print(f"  ✗ Fallo la conversion de {html}")
    # memoria de calculo: cualquier .md de la raiz que empiece por DECLARACION-RENTA
    RAIZ = os.path.dirname(RUTA)
    memorias = sorted(f for f in os.listdir(RAIZ)
                      if f.startswith("DECLARACION-RENTA") and f.endswith(".md"))
    otros = [f for f in ("RECOMENDACIONES.md", "COMPARATIVO.md") 
             if os.path.exists(os.path.join(RAIZ, f))]
    trabajos = [(m, "00-Memoria-de-calculo.pdf" if i == 0 else f"00-{m[:-3]}.pdf",
                 "Memoria de calculo - " + m[:-3].replace("-", " ").title())
                for i, m in enumerate(memorias)]
    trabajos += [(o, o[:-3] + ".pdf", o[:-3].title()) for o in otros]
    for md, salida, titulo in trabajos:
        org = os.path.join(RAIZ, md)
        if not os.path.exists(org):
            continue
        dst = os.path.join(PDF, salida)
        hecho, err = md_a_pdf(nav, org, dst, titulo)
        if hecho:
            kb = os.path.getsize(dst) // 1024
            print(f"  ✓ {salida:<46} {paginas(dst)} pag  {kb} KB")
            ok += 1
        else:
            print(f"  ✗ {salida}: {err}")

    print(f"\n  {ok} PDF generados en salida/pdf/")


if __name__ == "__main__":
    main()
