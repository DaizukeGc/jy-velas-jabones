# -*- coding: utf-8 -*-
"""Genera el informe de la semana 5 en formato APA 7 (DOCX).

El documento se construye con python-docx. Después se convierte a PDF con
Microsoft Word (ver el comando de PowerShell en el README o en la bitácora).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

RAIZ = Path(__file__).resolve().parents[1]
DOCS = RAIZ / "docs"
SALIDA_DOCX = DOCS / "Informe_Semana_5.docx"

FUENTE = "Times New Roman"
FUENTE_CODIGO = "Consolas"

TITULO = (
    "Primera funcionalidad del proyecto final con pruebas y bitácora de "
    "inteligencia artificial: registro de compras de materiales para "
    "JY Velas y Jabones"
)

RESUMEN = (
    "Este informe documenta la primera funcionalidad del proyecto final del seminario: "
    "el registro de compras de materiales del sistema de inventario, pedidos y ventas de "
    "JY Velas y Jabones. Se tomó la historia de usuario HU-01, de prioridad Must, y su "
    "criterio de aceptación del documento de requisitos de la semana 3. Siguiendo el ciclo "
    "de pruebas primero, se escribió el contrato en el README y nueve pruebas automatizadas "
    "con pytest antes de la implementación: tres casos normales, tres casos límite y tres "
    "casos de error. El asistente de código del IDE (OpenCode) apoyó la implementación y el "
    "refactor, y cada sugerencia se registró en una bitácora con su decisión y verificación. "
    "Las pruebas descubrieron un error de orden en las validaciones que dejaba el inventario "
    "modificado ante una compra negativa; se corrigió y el conjunto quedó en verde. El "
    "refactor extrajo constantes y un método de búsqueda para eliminar duplicación, sin "
    "modificar las pruebas. El resultado cumple el contrato, respeta la decisión de usar solo "
    "la biblioteca estándar y deja evidencia del proceso en el historial de Git."
)

PALABRAS_CLAVE = (
    "pruebas primero; pruebas automatizadas; asistente de código; inventario; Python"
)


def configurar_documento(doc: Document) -> None:
    seccion = doc.sections[0]
    seccion.page_width = Inches(8.5)
    seccion.page_height = Inches(11)
    seccion.top_margin = Inches(1)
    seccion.bottom_margin = Inches(1)
    seccion.left_margin = Inches(1)
    seccion.right_margin = Inches(1)

    normal = doc.styles["Normal"]
    normal.font.name = FUENTE
    normal.font.size = Pt(12)
    normal.paragraph_format.line_spacing = 2.0
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(0)
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

    rpr = normal.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), FUENTE)
    rfonts.set(qn("w:hAnsi"), FUENTE)


def numerar_paginas(seccion) -> None:
    encabezado = seccion.header
    encabezado.is_linked_to_previous = False
    parrafo_encabezado = encabezado.paragraphs[0]
    parrafo_encabezado.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    parrafo_encabezado.paragraph_format.first_line_indent = Inches(0)
    campo = OxmlElement("w:fldSimple")
    campo.set(qn("w:instr"), "PAGE")
    corrida = OxmlElement("w:r")
    texto = OxmlElement("w:t")
    texto.text = "1"
    corrida.append(texto)
    campo.append(corrida)
    parrafo_encabezado._p.append(campo)


def _fuente(run, nombre: str, tamano: int) -> None:
    run.font.name = nombre
    run.font.size = Pt(tamano)
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), nombre)
    rfonts.set(qn("w:hAnsi"), nombre)


def parrafo(
    doc: Document,
    texto: str = "",
    *,
    bold: bool = False,
    italic: bool = False,
    align=WD_ALIGN_PARAGRAPH.LEFT,
    indent: bool = False,
    size: int = 12,
    font: str = FUENTE,
    spacing: float = 2.0,
    space_after: int = 0,
    space_before: int = 0,
    keep_with_next: bool = False,
):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.alignment = align
    pf.line_spacing = spacing
    pf.space_after = Pt(space_after)
    pf.space_before = Pt(space_before)
    pf.first_line_indent = Inches(0.5) if indent else Inches(0)
    pf.keep_with_next = keep_with_next
    if texto:
        run = p.add_run(texto)
        run.bold = bold
        run.italic = italic
        _fuente(run, font, size)
    return p


def h1(doc: Document, texto: str):
    return parrafo(doc, texto, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, keep_with_next=True)


def h2(doc: Document, texto: str):
    return parrafo(doc, texto, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, keep_with_next=True)


def h3(doc: Document, texto: str):
    return parrafo(
        doc, texto, bold=True, italic=True, align=WD_ALIGN_PARAGRAPH.LEFT, keep_with_next=True
    )


def sombrear(p, relleno: str = "F2F2F2") -> None:
    ppr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), relleno)
    ppr.append(shd)


def bloque_codigo(doc: Document, texto: str):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing = 1.0
    pf.space_after = Pt(8)
    pf.space_before = Pt(4)
    pf.first_line_indent = Inches(0)
    pf.left_indent = Inches(0)
    lineas = texto.rstrip("\n").split("\n")
    for indice, linea in enumerate(lineas):
        run = p.add_run(linea)
        _fuente(run, FUENTE_CODIGO, 9)
        if indice < len(lineas) - 1:
            run.add_break()
    sombrear(p)
    return p


def _borde_celda(celda, borde: str = "bottom", sz: int = 8) -> None:
    tcpr = celda._tc.get_or_add_tcPr()
    tcbordes = tcpr.find(qn("w:tcBorders"))
    if tcbordes is None:
        tcbordes = OxmlElement("w:tcBorders")
        tcpr.append(tcbordes)
    el = tcbordes.find(qn(f"w:{borde}"))
    if el is None:
        el = OxmlElement(f"w:{borde}")
        tcbordes.append(el)
    el.set(qn("w:val"), "single")
    el.set(qn("w:sz"), str(sz))
    el.set(qn("w:space"), "0")
    el.set(qn("w:color"), "000000")


def _bordes_tabla(tabla) -> None:
    tbl = tabla._tbl
    tblpr = tbl.tblPr
    bordes = OxmlElement("w:tblBorders")
    especificaciones = [
        ("top", "single", "8"),
        ("left", "nil", "0"),
        ("bottom", "single", "8"),
        ("right", "nil", "0"),
        ("insideH", "nil", "0"),
        ("insideV", "nil", "0"),
    ]
    for borde, valor, sz in especificaciones:
        el = OxmlElement(f"w:{borde}")
        el.set(qn("w:val"), valor)
        el.set(qn("w:sz"), sz)
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "000000")
        bordes.append(el)
    tblpr.append(bordes)


def tabla_apa(
    doc: Document,
    numero: int,
    titulo: str,
    encabezados,
    filas,
    *,
    anchos=None,
    tamano: int = 11,
) -> None:
    parrafo(doc, f"Tabla {numero}", bold=True, spacing=2.0, keep_with_next=True)
    parrafo(doc, titulo, italic=True, spacing=2.0, keep_with_next=True)
    tabla = doc.add_table(rows=1, cols=len(encabezados))
    tabla.alignment = WD_TABLE_ALIGNMENT.CENTER
    tabla.autofit = True
    _bordes_tabla(tabla)

    for indice, texto in enumerate(encabezados):
        celda = tabla.rows[0].cells[indice]
        celda.text = ""
        p = celda.paragraphs[0]
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.space_before = Pt(2)
        run = p.add_run(str(texto))
        run.bold = True
        _fuente(run, FUENTE, tamano)
        _borde_celda(celda, "bottom")

    for fila in filas:
        celdas = tabla.add_row().cells
        for indice, valor in enumerate(fila):
            celdas[indice].text = ""
            p = celdas[indice].paragraphs[0]
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(2)
            run = p.add_run(str(valor))
            _fuente(run, FUENTE, tamano)

    if anchos:
        for fila in tabla.rows:
            for indice, ancho in enumerate(anchos):
                fila.cells[indice].width = Inches(ancho)

    tr = tabla.rows[0]._tr
    trpr = tr.get_or_add_trPr()
    cabecera = OxmlElement("w:tblHeader")
    cabecera.set(qn("w:val"), "true")
    trpr.append(cabecera)


def nota(doc: Document, texto: str) -> None:
    p = parrafo(doc, "", size=10, spacing=1.0, space_after=8)
    run = p.add_run("Nota. ")
    run.italic = True
    _fuente(run, FUENTE, 10)
    run2 = p.add_run(texto)
    _fuente(run2, FUENTE, 10)


def referencia(doc: Document, texto: str) -> None:
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pf.line_spacing = 2.0
    pf.space_after = Pt(0)
    pf.left_indent = Inches(0.5)
    pf.first_line_indent = Inches(-0.5)
    run = p.add_run(texto)
    _fuente(run, FUENTE, 12)


def leer(relativa: str) -> str:
    return (RAIZ / relativa).read_text(encoding="utf-8")


def historial_commits() -> str:
    resultado = subprocess.run(
        ["git", "log", "--format=%h %ad %s", "--date=short"],
        cwd=RAIZ,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return resultado.stdout.strip()


def portada(doc: Document) -> None:
    for _ in range(3):
        parrafo(doc, "")
    parrafo(doc, TITULO, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    parrafo(doc, "")
    parrafo(doc, "Jhonier Santiago García Coqueco", align=WD_ALIGN_PARAGRAPH.CENTER)
    parrafo(
        doc,
        "Fundación Escuela Tecnológica de Neiva «Jesús Oviedo Pérez»",
        align=WD_ALIGN_PARAGRAPH.CENTER,
    )
    parrafo(
        doc,
        "Seminario Inteligencia Artificial Aplicada al Ciclo de Vida del Software",
        align=WD_ALIGN_PARAGRAPH.CENTER,
    )
    parrafo(doc, "Ing. Jorge Luis Trujillo Artunduaga", align=WD_ALIGN_PARAGRAPH.CENTER)
    parrafo(doc, "7 de noviembre de 2026", align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_page_break()


def resumen(doc: Document) -> None:
    parrafo(doc, TITULO, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    h1(doc, "Resumen")
    parrafo(doc, RESUMEN, indent=False)
    p = parrafo(doc, "", indent=False)
    run = p.add_run("Palabras clave: ")
    run.italic = True
    _fuente(run, FUENTE, 12)
    run2 = p.add_run(PALABRAS_CLAVE)
    _fuente(run2, FUENTE, 12)
    doc.add_page_break()


def cuerpo(doc: Document) -> None:
    parrafo(doc, TITULO, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)

    parrafo(
        doc,
        "JY Velas y Jabones es un emprendimiento familiar que fabrica y vende velas y "
        "jabones artesanales por WhatsApp, Instagram y ferias. En la semana 3 se elaboró el "
        "documento de requisitos del proyecto final, con diez historias de usuario y sus "
        "criterios de aceptación (García Coqueco, 2026). La tarea de la semana 5 pide "
        "construir la primera funcionalidad a partir de una historia de prioridad Must, "
        "escribir su contrato y sus pruebas antes del código, implementarla con un asistente "
        "de código, refactorizarla con las pruebas en verde y registrar las decisiones en una "
        "bitácora de uso de inteligencia artificial.",
        indent=True,
    )
    parrafo(
        doc,
        "Este informe describe el proceso y el resultado. Primero presenta la historia "
        "seleccionada y su contrato; después explica la estrategia de pruebas, la "
        "implementación, el refactor y la bitácora; por último, resume el uso responsable y "
        "las conclusiones. El código, las pruebas y el historial de commits están en el "
        "repositorio del proyecto, y la bitácora completa se conserva en el archivo "
        "bitacora_ia.md.",
        indent=True,
    )

    h1(doc, "Funcionalidad de la semana 5: HU-01")
    parrafo(
        doc,
        "De las cinco historias Must del documento de requisitos se eligió la HU-01 porque es "
        "la base del inventario y porque se puede resolver con una función principal y sus "
        "casos límite. Sin registrar las compras no se sabe qué materiales hay, y las "
        "historias de producción y venta dependen de esa existencia. La funcionalidad cabe en "
        "una sola operación: sumar una cantidad comprada a un material ya registrado y dejar "
        "el movimiento en el historial.",
        indent=True,
    )

    h2(doc, "Historia de usuario y criterio de aceptación")
    parrafo(
        doc,
        "La historia conserva el identificador y la necesidad de origen del documento de la "
        "semana 3. El criterio tiene un escenario normal y un escenario de error con datos "
        "concretos, tal como se exige en la tarea.",
        indent=True,
    )
    tabla_apa(
        doc,
        1,
        "Historia de usuario HU-01 y su criterio de aceptación",
        ["Elemento", "Contenido"],
        [
            (
                "Historia",
                "Como dueña, quiero registrar las compras de materiales para saber cuánto "
                "tengo de cada uno antes de hacer una tanda.",
            ),
            ("Prioridad", "Must"),
            ("Necesidad de origen", "N-01: saber qué materiales se están acabando."),
            (
                "Escenario 1 (normal)",
                "Dado que hay 800 g de «Cera de soja», cuando registro la compra de 2.000 g, "
                "entonces el inventario queda en 2.800 g y la compra aparece en el historial "
                "con la fecha de hoy.",
            ),
            (
                "Escenario 2 (error)",
                "Dado que hay 800 g de «Cera de soja», cuando intento registrar una compra de "
                "−500 g, entonces el sistema no la guarda, muestra «La cantidad debe ser mayor "
                "que cero» y el inventario sigue en 800 g.",
            ),
        ],
        anchos=[1.6, 4.9],
    )
    nota(doc, "Elaboración propia a partir del documento de requisitos de la semana 3 (García Coqueco, 2026).")

    h2(doc, "Contrato de la función")
    parrafo(
        doc,
        "El contrato se escribió en el README antes de las pruebas y antes del código. La "
        "firma declara los tipos, el valor de retorno y el parámetro opcional de fecha. La "
        "operación modifica la existencia del material y devuelve un registro inmutable de la "
        "compra, para que el historial sea verificable.",
        indent=True,
    )
    bloque_codigo(
        doc,
        "from datetime import date\n"
        "\n"
        "class Inventario:\n"
        "    def registrar_compra(\n"
        "        self,\n"
        "        codigo: str,\n"
        "        cantidad: float,\n"
        "        fecha: date | None = None,\n"
        "    ) -> Compra: ...",
    )
    tabla_apa(
        doc,
        2,
        "Parámetros del contrato de registrar_compra",
        ["Parámetro", "Tipo", "Descripción"],
        [
            (
                "codigo",
                "str",
                "Código del material ya registrado en el catálogo, por ejemplo «MAT-CERA».",
            ),
            (
                "cantidad",
                "float",
                "Cantidad comprada, mayor que cero, en la unidad del material: gramos, "
                "mililitros o unidades.",
            ),
            (
                "fecha",
                "date | None",
                "Fecha de la compra. Si es None, se usa date.today().",
            ),
        ],
        anchos=[1.0, 1.2, 4.3],
    )
    parrafo(
        doc,
        "La función devuelve un objeto Compra con codigo_material, cantidad y fecha. Además, "
        "la existencia del material se consulta con el método existencia(codigo) y el "
        "historial con historial(codigo). Se asume que el material existe antes de la compra, "
        "que la cantidad usa la misma unidad del material y que el sistema es de un solo "
        "usuario, funciona sin internet y guarda los datos en memoria en esta iteración.",
        indent=True,
    )
    parrafo(
        doc,
        "Los casos límite y errores definidos en el contrato son los siguientes: cantidad "
        "igual a cero se rechaza; cantidad negativa se rechaza con el mismo mensaje y sin "
        "modificar el inventario; cantidad igual a uno es válida; existencia inicial en cero "
        "es válida y queda igual a la cantidad comprada; un código no registrado se rechaza "
        "con un error de negocio; y una fecha no indicada se registra con la fecha del día.",
        indent=True,
    )

    h2(doc, "Ejemplos de entrada y salida")
    parrafo(
        doc,
        "La Tabla 3 reúne cinco ejemplos del contrato, con los mismos datos que usan las "
        "pruebas. Los tres primeros son casos válidos; los dos últimos muestran los errores "
        "del criterio de aceptación y del supuesto de catálogo previo.",
        indent=True,
    )
    tabla_apa(
        doc,
        3,
        "Ejemplos de entrada y salida de registrar_compra",
        ["N.º", "Operación", "Existencia inicial", "Resultado"],
        [
            ("1", "registrar_compra(\"MAT-CERA\", 2000)", "800 g", "Existencia 2.800 g y compra en el historial con la fecha de hoy."),
            ("2", "registrar_compra(\"MAT-FRASCO\", 24)", "10 unidades", "Existencia 34 unidades."),
            ("3", "registrar_compra(\"MAT-ESENCIA\", 500)", "0 ml", "Existencia 500 ml."),
            ("4", "registrar_compra(\"MAT-CERA\", 0)", "800 g", "ErrorInventario: «La cantidad debe ser mayor que cero»; sigue en 800 g y no queda registro."),
            ("5", "registrar_compra(\"MAT-AROMA\", 100)", "No existe", "ErrorInventario: «El material 'MAT-AROMA' no está registrado»."),
        ],
        anchos=[0.4, 2.0, 1.2, 2.9],
    )
    nota(doc, "Elaboración propia. Los datos son de ejemplo y coinciden con las pruebas automatizadas.")

    h1(doc, "Pruebas primero")
    parrafo(
        doc,
        "El trabajo siguió el ciclo de pruebas primero. Primero se escribió el contrato en el "
        "README; después se crearon las pruebas y se hizo un commit con el conjunto en rojo, "
        "antes de que existiera el módulo de inventario; luego se implementó la función hasta "
        "dejar todas las pruebas en verde; por último se refactorizó sin modificar las "
        "pruebas. El historial conserva los tres momentos con mensajes explícitos: pruebas en "
        "rojo, pruebas en verde y refactor.",
        indent=True,
    )

    h2(doc, "Casos cubiertos")
    parrafo(
        doc,
        "Se escribieron nueve pruebas con pytest (pytest, 2026): tres normales, tres de "
        "límite y tres de error. La Tabla 4 indica qué comprueba cada una. Los nombres de "
        "las pruebas describen el comportamiento esperado y no el detalle de la implementación.",
        indent=True,
    )
    tabla_apa(
        doc,
        4,
        "Pruebas automatizadas de la HU-01",
        ["Prueba", "Tipo", "Qué verifica"],
        [
            ("test_compra_de_cera_suma_al_inventario", "Normal", "800 g + 2.000 g = 2.800 g."),
            ("test_compra_de_frascos_suma_al_inventario", "Normal", "10 unidades + 24 = 34 unidades."),
            ("test_compra_queda_en_el_historial_con_la_fecha_de_hoy", "Normal", "Devuelve un objeto Compra con la fecha del día y aparece en el historial."),
            ("test_compra_de_una_sola_unidad_es_valida", "Límite", "La cantidad mínima positiva, 1, se acepta: 800 g + 1 g = 801 g."),
            ("test_compra_sobre_material_sin_existencias_es_valida", "Límite", "Una existencia inicial en 0 queda igual a la cantidad comprada."),
            ("test_compra_con_fecha_personalizada_se_guarda_con_esa_fecha", "Límite", "La fecha explícita se conserva en el registro."),
            ("test_compra_con_cantidad_cero_lanza_error_y_no_cambia_existencias", "Error", "Cantidad 0: mensaje del criterio, existencia intacta y sin historial."),
            ("test_compra_con_cantidad_negativa_lanza_error_y_no_cambia_existencias", "Error", "Cantidad −500: mensaje del criterio, existencia intacta y sin historial."),
            ("test_compra_de_material_no_registrado_lanza_error", "Error", "Código inexistente: error de negocio con el nombre del material."),
        ],
        anchos=[2.9, 0.8, 2.8],
    )
    nota(doc, "Elaboración propia. Las nueve pruebas se ejecutan con python -m pytest.")

    h2(doc, "Del rojo al verde")
    parrafo(
        doc,
        "Antes de la implementación, el commit de pruebas quedó en rojo: pytest no pudo "
        "importar el módulo jy_velas y reportó ModuleNotFoundError. Esa es la evidencia de que "
        "las pruebas se escribieron primero. Después de implementar la función, el mismo "
        "comando reportó nueve pruebas superadas, como se muestra a continuación.",
        indent=True,
    )
    bloque_codigo(doc, "$ python -m pytest\n.........\n9 passed in 0.03s")
    parrafo(
        doc,
        "En el historial de Git, el commit «test: pruebas de registrar compra de materiales "
        "(en rojo)» antecede al commit «feat: implementar registrar compra de materiales "
        "(pruebas en verde)». El Anexo C reproduce el historial completo.",
        indent=True,
    )

    h1(doc, "Implementación con el asistente")
    parrafo(
        doc,
        "La implementación usa solo la biblioteca estándar de Python (Python Software "
        "Foundation, 2026): dataclasses, datetime y tipos nativos. El módulo define Material, "
        "Compra, ErrorInventario e Inventario. "
        "Material guarda código, nombre, unidad, existencia y mínimo de aviso; Compra es un "
        "registro inmutable de un movimiento; ErrorInventario representa un error de negocio "
        "que la interfaz podrá mostrar sin exponer detalles técnicos. El catálogo se guarda en "
        "un diccionario indexado por código y el historial en una lista.",
        indent=True,
    )
    parrafo(
        doc,
        "El asistente de código del IDE (OpenCode, 2026) propuso la estructura de clases y la "
        "validación de la cantidad. La "
        "primera versión sumaba la cantidad a la existencia antes de validarla. Con una compra "
        "de −500 g el método lanzaba el mensaje correcto, pero la existencia quedaba en 300 g "
        "en vez de 800 g. La prueba "
        "test_compra_con_cantidad_negativa_lanza_error_y_no_cambia_existencias falló con "
        "«assert 300 == 800». Se corrigió el orden: primero se valida y solo después se "
        "modifica el inventario. Este es el error que atraparon las pruebas y que se describe "
        "en la bitácora.",
        indent=True,
    )

    h1(doc, "Refactorización")
    parrafo(
        doc,
        "Con las pruebas en verde se hizo un refactor. Se extrajeron dos constantes para los "
        "mensajes de error y se creó el método privado _buscar_material, que concentra la "
        "búsqueda en el catálogo y el error de material no registrado; también se agregó "
        "_validar_cantidad para aislar la regla de negocio. Antes, la búsqueda y el mensaje de "
        "cantidad estaban duplicados entre registrar_compra y existencia.",
        indent=True,
    )
    parrafo(
        doc,
        "El refactor no cambió el comportamiento ni el contrato. No se modificó ninguna "
        "prueba y python -m pytest volvió a reportar nueve pruebas superadas. El commit "
        "«refactor: constantes y busqueda de material sin duplicacion» explica qué cambió. La "
        "ventaja es que los mensajes se editan en un solo lugar y que la regla de búsqueda se "
        "puede reutilizar cuando se agreguen más operaciones del inventario.",
        indent=True,
    )

    h1(doc, "Bitácora de uso de IA")
    parrafo(
        doc,
        "La bitácora registra seis entradas, cada una con fecha, la sugerencia o el prompt, la "
        "decisión, la razón y la verificación. Hay dos sugerencias aceptadas, dos aceptadas "
        "con cambios y dos rechazadas. La Tabla 5 resume las entradas; el detalle completo "
        "está en bitacora_ia.md, en la raíz del repositorio.",
        indent=True,
    )
    tabla_apa(
        doc,
        5,
        "Resumen de la bitácora de uso de IA",
        ["N.º", "Sugerencia del asistente", "Decisión", "Verificación"],
        [
            ("1", "Usar dataclasses y un diccionario por código, sin dependencias externas.", "Aceptada", "9 pruebas en verde; búsqueda O(1)."),
            ("2", "Devolver solo la nueva existencia.", "Aceptada con cambios", "Se devuelve un objeto Compra para verificar el historial y la fecha."),
            ("3", "Guardar las compras en SQLite o con pandas.", "Rechazada", "El ADR-001 pide solo la biblioteca estándar; la persistencia es otra iteración."),
            ("4", "Escribir exactamente cinco pruebas.", "Aceptada con cambios", "Se amplió a nueve para cubrir fecha, existencia cero y material inexistente."),
            ("5", "Extraer constantes y un método de búsqueda.", "Aceptada", "Las pruebas siguieron en verde sin modificarlas."),
            ("6", "Usar decimal.Decimal para las cantidades.", "Rechazada", "Son magnitudes físicas, no dinero; float con pytest.approx es suficiente."),
        ],
        anchos=[0.4, 2.6, 1.4, 2.1],
    )
    nota(doc, "Elaboración propia a partir de bitacora_ia.md.")
    parrafo(
        doc,
        "El error que atraparon las pruebas se documentó en la sección «Errores que atraparon "
        "las pruebas»: la validación tardía dejaba el inventario modificado ante una cantidad "
        "negativa. La corrección fue mover la validación antes de la suma y volver a ejecutar "
        "el conjunto completo. La reflexión final de la bitácora explica que el asistente fue "
        "más útil en la parte mecánica y que las pruebas fueron las que garantizaron el "
        "comportamiento.",
        indent=True,
    )

    h1(doc, "Uso responsable y verificación")
    parrafo(
        doc,
        "El repositorio no contiene claves, contraseñas ni archivos .env. El archivo .gitignore "
        "excluye .env, entornos virtuales, cachés de Python y los documentos fuente de la "
        "asignación. Las pruebas no se modificaron para hacer pasar el código: el único cambio "
        "de comportamiento se hizo en la implementación y quedó descrito en la bitácora. Cada "
        "línea del código se puede explicar porque el contrato, las pruebas y el refactor están "
        "documentados, y porque el docente puede pedir en clase la explicación de cualquier "
        "parte.",
        indent=True,
    )
    tabla_apa(
        doc,
        6,
        "Autoevaluación con la rúbrica de la tarea",
        ["Criterio", "Puntos máximos", "Puntaje estimado"],
        [
            ("1. Contrato", "10", "10"),
            ("2. Pruebas", "25", "25"),
            ("3. Implementación", "20", "20"),
            ("4. Pruebas primero en el historial", "10", "10"),
            ("5. Refactorización", "10", "10"),
            ("6. Bitácora de IA", "15", "15"),
            ("7. Uso responsable", "10", "10"),
            ("Total", "100", "100"),
        ],
        anchos=[3.5, 1.5, 1.5],
    )
    nota(doc, "Elaboración propia con base en la rúbrica publicada en la tarea de la semana 5.")

    h1(doc, "Conclusiones")
    parrafo(
        doc,
        "La funcionalidad cumple el contrato de la HU-01: registra compras válidas, actualiza "
        "la existencia, deja el movimiento en el historial con su fecha y rechaza las "
        "cantidades no positivas y los materiales no registrados sin alterar el inventario. "
        "Las nueve pruebas pasan con un solo comando y el historial de Git muestra el contrato, "
        "las pruebas en rojo, la implementación en verde y el refactor.",
        indent=True,
    )
    parrafo(
        doc,
        "El resultado de aprendizaje se alcanzó porque el asistente permitió generar y "
        "refactorizar el código, pero la comprensión y la verificación quedaron en las pruebas "
        "y en las decisiones registradas. La principal lección es que las pruebas no solo "
        "comprueban el resultado: también obligan a pensar en el orden de las validaciones y "
        "en los casos límite. La siguiente funcionalidad será la HU-07, registrar una venta "
        "con su medio de pago, que reutilizará el catálogo y el historial de este módulo.",
        indent=True,
    )

    h1(doc, "Referencias")
    referencia(
        doc,
        "García Coqueco, J. S. (2026). Documento de requisitos del proyecto final "
        "[Documento de la semana 3]. Fundación Escuela Tecnológica de Neiva «Jesús Oviedo Pérez».",
    )
    referencia(
        doc,
        "OpenCode. (2026). OpenCode [Asistente de código para el IDE]. https://opencode.ai",
    )
    referencia(
        doc,
        "Python Software Foundation. (2026). Python (Versión 3.11) [Software de computador]. "
        "https://www.python.org",
    )
    referencia(
        doc,
        "pytest. (2026). pytest (Versión 9.2) [Software de computador]. https://pytest.org",
    )

    doc.add_page_break()
    parrafo(doc, "Anexo A", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    parrafo(
        doc,
        "Código fuente de la funcionalidad",
        bold=True,
        align=WD_ALIGN_PARAGRAPH.CENTER,
        keep_with_next=True,
    )
    bloque_codigo(doc, leer("jy_velas/inventario.py"))

    doc.add_page_break()
    parrafo(doc, "Anexo B", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    parrafo(
        doc,
        "Pruebas automatizadas",
        bold=True,
        align=WD_ALIGN_PARAGRAPH.CENTER,
        keep_with_next=True,
    )
    bloque_codigo(doc, leer("tests/test_registrar_compra.py"))

    doc.add_page_break()
    parrafo(doc, "Anexo C", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    parrafo(
        doc,
        "Historial de commits",
        bold=True,
        align=WD_ALIGN_PARAGRAPH.CENTER,
        keep_with_next=True,
    )
    bloque_codigo(doc, historial_commits())


def main() -> None:
    doc = Document()
    configurar_documento(doc)
    numerar_paginas(doc.sections[0])
    portada(doc)
    resumen(doc)
    cuerpo(doc)
    DOCS.mkdir(exist_ok=True)
    doc.save(SALIDA_DOCX)
    print(f"Informe generado: {SALIDA_DOCX}")


if __name__ == "__main__":
    main()
