# -*- coding: utf-8 -*-
"""Genera el informe final integrador en formato APA 7 (DOCX y PDF)."""

from __future__ import annotations

import shutil
from pathlib import Path

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

RAIZ = Path(__file__).resolve().parents[1]
DOCS = RAIZ / "docs"
SALIDA_DOCX = DOCS / "informe_final_integrador.docx"
SALIDA_PDF = DOCS / "informe_final_integrador.pdf"
CARPETA_ENTREGA = Path(r"C:\Users\santi\Desktop\Entrega_Final_Seminario")

REPO = "https://github.com/DaizukeGc/jy-velas-jabones"
BLOB = f"{REPO}/blob/main"
TREE = f"{REPO}/tree/main"
COMMIT = f"{REPO}/commit"

FUENTE = "Times New Roman"
FUENTE_CODIGO = "Consolas"
COLOR_TEXTO = RGBColor(0x00, 0x00, 0x00)


def _aplicar_fuente(run, nombre: str, tamano: int) -> None:
    run.font.name = nombre
    run.font.size = Pt(tamano)
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), nombre)


def configurar_documento(doc: Document) -> None:
    """Configura pagina Carta, margenes APA de 1 pulgada y fuente base."""
    seccion = doc.sections[0]
    seccion.page_width = Inches(8.5)
    seccion.page_height = Inches(11)
    for lado in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
        setattr(seccion, lado, Inches(1))

    normal = doc.styles["Normal"]
    normal.font.name = FUENTE
    normal.font.size = Pt(12)
    normal.font.color.rgb = COLOR_TEXTO
    pf = normal.paragraph_format
    pf.line_spacing = 2.0
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pf.widow_control = True

    rpr = normal.element.get_or_add_rPr()
    rfonts = OxmlElement("w:rFonts")
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), FUENTE)
    rpr.append(rfonts)


def numerar_paginas(seccion) -> None:
    """Agrega numero de pagina en la esquina superior derecha (APA 7)."""
    encabezado = seccion.header
    encabezado.is_linked_to_previous = False
    p = encabezado.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.first_line_indent = Inches(0)
    campo = OxmlElement("w:fldSimple")
    campo.set(qn("w:instr"), "PAGE")
    corrida = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    rfonts = OxmlElement("w:rFonts")
    rfonts.set(qn("w:ascii"), FUENTE)
    rfonts.set(qn("w:hAnsi"), FUENTE)
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), "24")
    rpr.append(rfonts)
    rpr.append(sz)
    corrida.append(rpr)
    t = OxmlElement("w:t")
    t.text = "1"
    corrida.append(t)
    campo.append(corrida)
    p._p.append(campo)


def parrafo(
    doc: Document,
    texto: str = "",
    *,
    bold: bool = False,
    italic: bool = False,
    align=WD_ALIGN_PARAGRAPH.LEFT,
    indent: bool = False,
    hanging: bool = False,
    size: int = 12,
    spacing: float = 2.0,
    keep_with_next: bool = False,
    keep_together: bool = False,
):
    """Crea un parrafo con formato APA."""
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.alignment = align
    pf.line_spacing = spacing
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.keep_with_next = keep_with_next
    pf.keep_together = keep_together
    pf.widow_control = True
    if hanging:
        pf.left_indent = Inches(0.5)
        pf.first_line_indent = Inches(-0.5)
    elif indent:
        pf.first_line_indent = Inches(0.5)
    else:
        pf.first_line_indent = Inches(0)

    if texto:
        r = p.add_run(texto)
        r.bold = bold
        r.italic = italic
        _aplicar_fuente(r, FUENTE, size)
    return p


def agregar_enlace(p, texto: str, url: str, *, size: int = 12) -> None:
    """Inserta un hipervinculo real clicable en un parrafo."""
    part = p.part
    r_id = part.relate_to(url, RT.HYPERLINK, is_external=True)
    hl = OxmlElement("w:hyperlink")
    hl.set(qn("r:id"), r_id)

    run_el = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    rfonts = OxmlElement("w:rFonts")
    rfonts.set(qn("w:ascii"), FUENTE)
    rfonts.set(qn("w:hAnsi"), FUENTE)
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "0563C1")
    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), str(size * 2))
    for el in (rfonts, color, u, sz):
        rpr.append(el)
    run_el.append(rpr)

    t = OxmlElement("w:t")
    t.text = texto
    run_el.append(t)
    hl.append(run_el)
    p._p.append(hl)


def agregar_segmentos(p, segmentos: list, *, size: int = 12) -> None:
    """Agrega texto mixto: normal, negrita, cursiva, codigo o enlace."""
    for seg in segmentos:
        if isinstance(seg, str):
            r = p.add_run(seg)
            _aplicar_fuente(r, FUENTE, size)
        elif seg[0] == "b":
            r = p.add_run(seg[1])
            r.bold = True
            _aplicar_fuente(r, FUENTE, size)
        elif seg[0] == "i":
            r = p.add_run(seg[1])
            r.italic = True
            _aplicar_fuente(r, FUENTE, size)
        elif seg[0] == "c":
            r = p.add_run(seg[1])
            _aplicar_fuente(r, FUENTE_CODIGO, max(size - 2, 9))
        elif seg[0] == "link":
            agregar_enlace(p, seg[1], seg[2], size=size)


def p_mixto(
    doc: Document,
    segmentos: list,
    *,
    indent: bool = True,
    spacing: float = 2.0,
    keep_with_next: bool = False,
):
    """Parrafo narrativo con segmentos de estilo y enlaces."""
    p = parrafo(
        doc,
        indent=indent,
        spacing=spacing,
        keep_with_next=keep_with_next,
    )
    agregar_segmentos(p, segmentos, size=12)
    return p


def p_vineta(
    doc: Document,
    segmentos: list,
    *,
    keep_with_next: bool = False,
):
    """Elemento de lista con sangria francesa limpia."""
    p = parrafo(doc, spacing=2.0, keep_with_next=keep_with_next)
    pf = p.paragraph_format
    pf.left_indent = Inches(0.5)
    pf.first_line_indent = Inches(-0.25)
    agregar_segmentos(p, ["• "] + segmentos, size=12)
    return p


def h1(doc: Document, texto: str):
    """Titulo de nivel 1 APA 7 (centrado, negrita)."""
    return parrafo(
        doc,
        texto,
        bold=True,
        align=WD_ALIGN_PARAGRAPH.CENTER,
        keep_with_next=True,
    )


def h2(doc: Document, texto: str):
    """Titulo de nivel 2 APA 7 (alineado a la izquierda, negrita)."""
    return parrafo(
        doc,
        texto,
        bold=True,
        align=WD_ALIGN_PARAGRAPH.LEFT,
        keep_with_next=True,
    )


def _borde_celda(celda, **bordes) -> None:
    tc_pr = celda._tc.get_or_add_tcPr()
    tc_borders = OxmlElement("w:tcBorders")
    for nombre, cfg in bordes.items():
        el = OxmlElement(f"w:{nombre}")
        el.set(qn("w:val"), cfg["val"])
        if "sz" in cfg:
            el.set(qn("w:sz"), str(cfg["sz"]))
        if "color" in cfg:
            el.set(qn("w:color"), cfg["color"])
        tc_borders.append(el)
    tc_pr.append(tc_borders)


def _padding_celda(celda, top=60, bottom=60, left=85, right=85) -> None:
    tc_pr = celda._tc.get_or_add_tcPr()
    mar = OxmlElement("w:tcMar")
    for lado, val in (
        ("top", top),
        ("bottom", bottom),
        ("left", left),
        ("right", right),
    ):
        el = OxmlElement(f"w:{lado}")
        el.set(qn("w:w"), str(val))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tc_pr.append(mar)


def tabla_apa(
    doc: Document,
    numero: str,
    titulo: str,
    encabezados: list[str],
    filas: list[list],
    anchos: list[float],
    nota: str,
    *,
    font_size: int = 10,
) -> None:
    """Construye una tabla en estilo APA 7 sin filas partidas."""
    parrafo(doc, numero, bold=True, keep_with_next=True)
    parrafo(doc, titulo, italic=True, keep_with_next=True)

    tabla = doc.add_table(rows=1 + len(filas), cols=len(encabezados))
    tabla.alignment = WD_TABLE_ALIGNMENT.CENTER
    tabla.autofit = False

    sin_borde = {"val": "nil"}
    linea = {"val": "single", "sz": 6, "color": "000000"}

    todas_filas = [encabezados] + filas
    for idx_fila, datos_fila in enumerate(todas_filas):
        row = tabla.rows[idx_fila]
        tr_pr = row._tr.get_or_add_trPr()
        tr_pr.append(OxmlElement("w:cantSplit"))
        if idx_fila == 0:
            tr_pr.append(OxmlElement("w:tblHeader"))

        es_encabezado = idx_fila == 0
        es_ultima = idx_fila == len(todas_filas) - 1

        for idx_col, valor in enumerate(datos_fila):
            celda = row.cells[idx_col]
            celda.width = Inches(anchos[idx_col])
            celda.vertical_alignment = WD_ALIGN_VERTICAL.TOP
            _padding_celda(celda)

            bordes = {"left": sin_borde, "right": sin_borde}
            if es_encabezado:
                bordes["top"] = linea
                bordes["bottom"] = linea
            elif es_ultima:
                bordes["top"] = sin_borde
                bordes["bottom"] = linea
            else:
                bordes["top"] = sin_borde
                bordes["bottom"] = sin_borde
            _borde_celda(celda, **bordes)

            p = celda.paragraphs[0]
            pf = p.paragraph_format
            pf.line_spacing = 1.15
            pf.space_before = Pt(0)
            pf.space_after = Pt(0)
            pf.first_line_indent = Inches(0)
            if isinstance(valor, str):
                r = p.add_run(valor)
                r.bold = es_encabezado
                _aplicar_fuente(r, FUENTE, font_size)
            else:
                agregar_segmentos(p, valor, size=font_size)

    p_nota = parrafo(doc, spacing=1.5)
    r_n = p_nota.add_run("Nota. ")
    r_n.italic = True
    _aplicar_fuente(r_n, FUENTE, 10)
    r_t = p_nota.add_run(nota)
    _aplicar_fuente(r_t, FUENTE, 10)


def portada(doc: Document) -> None:
    """Pagina 1: Portada estudiantil en estilo APA 7."""
    for _ in range(3):
        parrafo(doc)
    parrafo(
        doc,
        "Informe final del proyecto integrador",
        bold=True,
        align=WD_ALIGN_PARAGRAPH.CENTER,
    )
    parrafo(
        doc,
        "JY Velas y Jabones: núcleo de inventario, pedidos y ventas",
        italic=True,
        align=WD_ALIGN_PARAGRAPH.CENTER,
    )
    parrafo(doc)
    for linea in (
        "Jhonier Santiago García Coqueco",
        "Fundación Escuela Tecnológica de Neiva «Jesús Oviedo Pérez»",
        "Seminario de Inteligencia Artificial aplicada al ciclo de vida del software",
        "Ing. Jorge Luis Trujillo Artunduaga",
        "26 de noviembre de 2026",
    ):
        parrafo(doc, linea, align=WD_ALIGN_PARAGRAPH.CENTER)
    p_repo = parrafo(doc, align=WD_ALIGN_PARAGRAPH.CENTER)
    agregar_segmentos(p_repo, [("link", REPO, REPO)], size=12)


def seccion_resumen(doc: Document) -> None:
    """Pagina 2: 1. Resumen y palabras clave."""
    titulo = h1(doc, "1. Resumen")
    titulo.paragraph_format.page_break_before = True
    p_mixto(
        doc,
        [
            "La dueña de una microempresa de velas y jabones artesanales en Neiva ",
            "no podía saber con certeza cuánto material tenía antes de preparar una ",
            "tanda: llevaba el control en hojas de cálculo y apuntes en papel. ",
            "Construí una librería de Python (Python Software Foundation, 2026) que ",
            "registra compras, descuenta consumos y lista los materiales en su ",
            "mínimo, con contrato explícito y sin dependencias de ejecución. Usé ",
            "inteligencia artificial (IA) en las seis fases del ciclo de vida: ",
            "para acotar el problema y la herramienta, extraer requisitos de una ",
            "entrevista simulada, proponer diagramas y decisiones arquitectónicas, ",
            "generar el código con desarrollo guiado por pruebas (TDD), crear ",
            "particiones y casos de prueba, y revisar seguridad y dependencias. La ",
            "verificación fue continua: pruebas en rojo y verde, ocho pruebas ",
            "débiles corregidas, seis mutaciones que rompieron la suite, linter ",
            "(Ruff, 2026) y auditoría de dependencias (Python Packaging Authority, ",
            "2026). Estado final: 116 pruebas superadas, Ruff sin avisos, ",
            "pip-audit sin vulnerabilidades y siete hallazgos de seguridad ",
            "corregidos. El resultado principal no fue que la IA escribiera código, ",
            "sino que cada salida fue contrastada con una regla, una prueba o una ",
            "herramienta antes de aceptarla.",
        ],
        indent=False,
    )
    p_kw = parrafo(doc, indent=True)
    agregar_segmentos(
        p_kw,
        [
            ("i", "Palabras clave: "),
            "inteligencia artificial, ciclo de vida del software, pruebas, "
            "seguridad, inventario.",
        ],
    )


def seccion_problema(doc: Document) -> None:
    """Seccion 2. Problema y usuario."""
    titulo = h1(doc, "2. Problema y usuario")
    titulo.paragraph_format.page_break_before = True
    p_mixto(
        doc,
        [
            "El usuario es la dueña-operadora de JY Velas y Jabones, una ",
            "microempresa artesanal ubicada en Neiva. Antes de este proyecto ",
            "registraba las entradas de cera, frascos y esencias en una hoja de ",
            "cálculo y apuntaba los consumos diarios en papel. Cuando llegaba el ",
            "momento de producir una tanda, no tenía una forma confiable de saber ",
            "si había stock suficiente ni qué materiales debía reponer, y las ",
            "alertas de agotamiento aparecían tarde. El problema no era estético ",
            "sino operativo: necesitaba tres operaciones simples y confiables para ",
            "controlar su materia prima: registrar una compra con fecha, descontar ",
            "lo consumido en una tanda sin pasarse del stock disponible y consultar ",
            "qué materiales están en o por debajo de su mínimo de aviso.",
        ],
    )
    p_mixto(
        doc,
        [
            "La propuesta inicial del módulo 1 está documentada en ",
            ("link", "docs/propuesta.md", f"{BLOB}/docs/propuesta.md"),
            " y el levantamiento de requisitos del módulo 2 en ",
            ("link", "docs/requisitos.md", f"{BLOB}/docs/requisitos.md"),
            ". La entrevista de levantamiento, compuesta por nueve preguntas sobre ",
            "inventario, compras, consumos, alertas, pedidos, ventas, reportes, ",
            "acceso multiusuario y persistencia, fue simulada por un compañero en ",
            "el rol de la dueña y declarada explícitamente así en la bitácora: no ",
            "se usaron datos de personas reales. A partir de esa sesión se ",
            "relevaron 11 necesidades (",
            ("c", "N-01"),
            " a ",
            ("c", "N-11"),
            ") y 10 historias de usuario, de las cuales las tres historias de ",
            "prioridad ",
            ("i", "Must"),
            " del incremento son ",
            ("c", "HU-01"),
            ", ",
            ("c", "HU-02"),
            " y ",
            ("c", "HU-03"),
            " (50 % del conjunto ",
            ("i", "Must/Should"),
            "), todas terminadas y verificadas, como resume la Tabla 1.",
        ],
    )

    tabla_apa(
        doc,
        "Tabla 1",
        "Historias de usuario Must terminadas en el incremento",
        ["Historia", "Necesidad", "Criterio de aceptación principal", "Evidencia"],
        [
            [
                [("c", "HU-01")],
                [("c", "N-01, N-02")],
                [
                    "Registrar compra con código, cantidad finita > 0 y fecha "
                    "opcional; suma a la existencia y devuelve objeto ",
                    ("c", "Compra"),
                    " inmutable.",
                ],
                [
                    ("link", "README.md", f"{BLOB}/README.md"),
                    ", ",
                    (
                        "link",
                        "test_registrar_compra.py",
                        f"{BLOB}/tests/test_registrar_compra.py",
                    ),
                ],
            ],
            [
                [("c", "HU-02")],
                [("c", "N-01, N-03")],
                [
                    "Descontar consumo de una tanda; falla con ",
                    ("c", "ErrorInventario"),
                    " si no hay stock suficiente y nunca deja el inventario negativo.",
                ],
                [
                    ("link", "requisitos.md", f"{BLOB}/docs/requisitos.md"),
                    ", ",
                    (
                        "link",
                        "test_consumir_material.py",
                        f"{BLOB}/tests/test_consumir_material.py",
                    ),
                ],
            ],
            [
                [("c", "HU-03")],
                [("c", "N-04")],
                [
                    "Listar materiales con ",
                    ("c", "existencia <= minimo"),
                    " en orden del catálogo, devolviendo copias seguras.",
                ],
                [
                    ("link", "inventario.py", f"{BLOB}/jy_velas/inventario.py"),
                    ", ",
                    (
                        "link",
                        "test_consultas_inventario.py",
                        f"{BLOB}/tests/test_consultas_inventario.py",
                    ),
                ],
            ],
        ],
        [0.75, 0.95, 2.95, 1.85],
        "Elaboración propia a partir de docs/requisitos.md y la suite de pruebas.",
    )

    p_mixto(
        doc,
        [
            "El alcance se limitó intencionalmente a la capa de dominio y a su ",
            "verificación automatizada: no se construyó interfaz gráfica, base de ",
            "datos ni autenticación, porque ninguna de esas piezas aparecía en los ",
            "criterios de aceptación del incremento. Esa decisión quedó registrada ",
            "en ",
            ("link", "docs/adr.md", f"{BLOB}/docs/adr.md"),
            " (",
            ("c", "ADR-001"),
            ") y permitió mantener un núcleo simple, portable y explicable sin ",
            "intermediarios técnicos. La solución se instala y verifica localmente ",
            "con comandos estándar de Python, como detalla la ",
            ("link", "guía de despliegue", f"{BLOB}/docs/despliegue.md"),
            ".",
        ],
    )


def seccion_ia_ciclo_vida(doc: Document) -> None:
    """Seccion 3. La IA en el ciclo de vida."""
    h1(doc, "3. La IA en el ciclo de vida")
    p_mixto(
        doc,
        [
            "Utilicé OpenCode en modo agente dentro del IDE como asistente ",
            "transversal en las seis fases del ciclo de vida del software, ",
            "aplicando siempre la misma regla de trabajo: la IA propone y el ",
            "criterio humano, contrastado con el contrato, las pruebas o las ",
            "herramientas automáticas, decide qué se acepta, qué se ajusta y qué ",
            "se rechaza. La Tabla 2 resume la evidencia por módulo.",
        ],
    )

    tabla_apa(
        doc,
        "Tabla 2",
        "Uso y verificación de la IA en las seis fases del ciclo de vida",
        [
            "Módulo y fase",
            "Qué hice con IA",
            "Herramienta",
            "Evidencia",
            "Cómo verifiqué",
        ],
        [
            [
                "1. Fundamentos",
                "Convertir el problema en una propuesta acotada y definir el alcance",
                "OpenCode",
                [("link", "propuesta.md", f"{BLOB}/docs/propuesta.md")],
                (
                    "Comprobé que usuario, problema y éxito fueran verificables; "
                    "fijé ADR-001"
                ),
            ],
            [
                "2. Requisitos",
                "Extraer necesidades (N-01 a N-11), historias y criterios Gherkin",
                "OpenCode",
                [
                    ("link", "requisitos.md", f"{BLOB}/docs/requisitos.md"),
                    ", ",
                    ("link", "bitacora_ia.md", f"{BLOB}/bitacora_ia.md"),
                ],
                "Revisé cada esperado contra la regla y documenté historial() vacío",
            ],
            [
                "3. Diseño",
                "Proponer contexto C4, secuencia, 9 entidades y tres registros ADR",
                "OpenCode + Mermaid CLI",
                [
                    ("link", "diseno.md", f"{BLOB}/docs/diseno.md"),
                    ", ",
                    ("link", "adr.md", f"{BLOB}/docs/adr.md"),
                ],
                "Contrasté diagramas contra el contrato y coherencia con el código",
            ],
            [
                "4. Código",
                [
                    "Implementar ",
                    ("c", "Inventario"),
                    ", ",
                    ("c", "Material"),
                    " y ",
                    ("c", "Compra"),
                    " con ciclo TDD",
                ],
                "OpenCode",
                [
                    ("link", "inventario.py", f"{BLOB}/jy_velas/inventario.py"),
                    ", ",
                    ("link", "fc085c3", f"{COMMIT}/fc085c3"),
                ],
                (
                    "Pruebas en rojo primero (1c66d73), verde después y "
                    "refactor sin cambios"
                ),
            ],
            [
                "5. Pruebas",
                "Generar particiones, valores límite, tablas de decisión y suite",
                "OpenCode",
                [
                    ("link", "registro_pruebas.md", f"{BLOB}/registro_pruebas.md"),
                    ", ",
                    ("link", "tests/", f"{TREE}/tests"),
                ],
                (
                    "Reescribí 8 pruebas débiles, apliqué 6 mutaciones (M1 a M6) "
                    "y 116 en verde"
                ),
            ],
            [
                "6. Operación",
                "Auditar seguridad OWASP, configurar linter, fijar deps y despliegue",
                "OpenCode + Ruff + pip-audit",
                [
                    ("link", "revision_seguridad.md", f"{BLOB}/revision_seguridad.md"),
                    ", ",
                    (
                        "link",
                        "pipeline",
                        f"{BLOB}/docs/pipeline_ultima_ejecucion.md",
                    ),
                ],
                (
                    "Descarté 2 falsos positivos de IA, añadí 4 hallazgos "
                    "(H-04 a H-07) y OK"
                ),
            ],
        ],
        [0.98, 1.35, 0.92, 1.35, 1.90],
        "Elaboración propia a partir de bitacora_ia.md (14 entradas) y el repositorio.",
        font_size=9,
    )

    p_mixto(
        doc,
        [
            "Cada interacción relevante quedó trazada en ",
            ("link", "bitacora_ia.md", f"{BLOB}/bitacora_ia.md"),
            " con fecha, prompt o sugerencia, decisión, justificación, ",
            "verificación y commit asociado. En total se documentaron 14 entradas ",
            "(Anexo A): 3 aceptadas sin cambios, 7 aceptadas con modificaciones ",
            "técnicas y 4 rechazadas por violar el alcance, introducir ",
            "dependencias externas o debilitar los errores de negocio.",
        ],
    )


def seccion_verificacion(doc: Document) -> None:
    """Seccion 4. Verificacion: lo que la IA hizo mal y como lo encontraste."""
    h1(doc, "4. Verificación: lo que la IA hizo mal y cómo lo encontraste")
    p_mixto(
        doc,
        [
            "La revisión continua detectó errores concretos producidos por la IA ",
            "en cuatro fases distintas del ciclo de vida. En ningún caso se ",
            "ajustó la regla de negocio para hacer pasar una salida defectuosa.",
        ],
    )

    h2(doc, "Caso 1: El histórico de un código inexistente")
    p_vineta(doc, [("b", "Fase: "), "requisitos."])
    p_vineta(
        doc,
        [
            ("b", "Qué propuso la IA: "),
            "que ",
            ("c", "historial(codigo_inexistente)"),
            " lanzara ",
            ("c", "ErrorInventario"),
            ", igual que una compra o consumo sobre un material ausente.",
        ],
    )
    p_vineta(
        doc,
        [
            ("b", "Qué estaba mal: "),
            "mezclaba una consulta de solo lectura con una operación ",
            "transaccional. Los criterios de aceptación en ",
            ("link", "docs/requisitos.md", f"{BLOB}/docs/requisitos.md"),
            " solo exigían errores al registrar compras o consumir stock.",
        ],
    )
    p_vineta(
        doc,
        [
            ("b", "Cómo lo detectaste: "),
            "al revisar la tabla de decisión frente al criterio en la entrada 7 ",
            "de ",
            ("link", "bitacora_ia.md", f"{BLOB}/bitacora_ia.md"),
            ", noté que ninguna regla pedía fallar ante una consulta sin ",
            "coincidencias.",
        ],
    )
    p_vineta(
        doc,
        [
            ("b", "Qué hice: "),
            "documenté la ambigüedad y definí que la consulta devuelve una lista ",
            "vacía; quedó en el docstring de ",
            ("link", "inventario.py", f"{BLOB}/jy_velas/inventario.py"),
            ", en ",
            ("link", "registro_pruebas.md", f"{BLOB}/registro_pruebas.md"),
            " y en el commit ",
            ("link", "336eb98", f"{COMMIT}/336eb98"),
            ".",
        ],
    )

    h2(doc, "Caso 2: Persistencia, dependencias y tipos de cantidad")
    p_vineta(doc, [("b", "Fase: "), "código."])
    p_vineta(
        doc,
        [
            ("b", "Qué propuso la IA: "),
            "guardar las compras en SQLite o con ",
            ("c", "pandas"),
            ", usar ",
            ("c", "decimal.Decimal"),
            " para cantidades, validar entradas con ",
            ("c", "assert"),
            " en producción y agregar ",
            ("c", "python-dotenv"),
            ".",
        ],
    )
    p_vineta(
        doc,
        [
            ("b", "Qué estaba mal: "),
            "agregaba dependencias y complejidad fuera del contrato, violaba ",
            ("c", "ADR-001"),
            ", confundía magnitudes físicas (gramos, mililitros, unidades) con ",
            "dinero y usaba ",
            ("c", "assert"),
            ", que desaparece con ",
            ("c", "python -O"),
            " y no lanza ",
            ("c", "ErrorInventario"),
            ".",
        ],
    )
    p_vineta(
        doc,
        [
            ("b", "Cómo lo detectaste: "),
            "comparé las sugerencias con ",
            ("link", "docs/adr.md", f"{BLOB}/docs/adr.md"),
            ", el criterio de aceptación y la regla ",
            ("c", "S101"),
            " de Ruff; verifiqué que ",
            ("c", "float"),
            " con ",
            ("c", "pytest.approx"),
            " cubría los decimales en las pruebas (pytest, 2026).",
        ],
    )
    p_vineta(
        doc,
        [
            ("b", "Qué hice: "),
            "rechacé SQLite, ",
            ("c", "pandas"),
            ", ",
            ("c", "Decimal"),
            ", ",
            ("c", "assert"),
            " en producción y ",
            ("c", "python-dotenv"),
            "; registré las decisiones en las entradas 3, 6, 12 y 13 de ",
            ("link", "bitacora_ia.md", f"{BLOB}/bitacora_ia.md"),
            " e implementé el núcleo en biblioteca estándar en ",
            ("link", "fc085c3", f"{COMMIT}/fc085c3"),
            ".",
        ],
    )

    h2(doc, "Caso 3: Ocho pruebas débiles y verificación por mutaciones")
    p_vineta(doc, [("b", "Fase: "), "pruebas."])
    p_vineta(
        doc,
        [
            ("b", "Qué propuso la IA: "),
            "aserciones permisivas como ",
            ("c", "is not None"),
            " y ",
            ("c", "pytest.raises(Exception)"),
            ", un esperado de consumo que devolvía cero al pasarse del stock, ",
            "una prueba de fecha que ignoraba la fecha explícita y un mínimo ",
            "evaluado con ",
            ("c", "<"),
            " en vez de ",
            ("c", "<="),
            ".",
        ],
    )
    p_vineta(
        doc,
        [
            ("b", "Qué estaba mal: "),
            "habrían pasado aunque el código tuviera errores graves; el esperado ",
            "salía del código generado y no de la regla de negocio.",
        ],
    )
    p_vineta(
        doc,
        [
            ("b", "Cómo lo detectaste: "),
            "revisé cada caso contra la tabla de decisión y ejecuté seis ",
            "mutaciones (",
            ("c", "M1"),
            " a ",
            ("c", "M6"),
            ") sobre ",
            ("c", "jy_velas/inventario.py"),
            ", restaurando el archivo y comprobando su SHA-256 original.",
        ],
    )
    p_vineta(
        doc,
        [
            ("b", "Qué hice: "),
            "reescribí o descarté las ocho pruebas débiles, consolidé 58 ",
            "pruebas funcionales parametrizadas en ",
            ("link", "0c558bf", f"{COMMIT}/0c558bf"),
            " y documenté las seis mutaciones (Tabla 3) en ",
            ("link", "registro_pruebas.md", f"{BLOB}/registro_pruebas.md"),
            " y ",
            (
                "link",
                "mutaciones_semana7.txt",
                f"{BLOB}/docs/mutaciones_semana7.txt",
            ),
            ", commit ",
            ("link", "336eb98", f"{COMMIT}/336eb98"),
            ".",
        ],
    )

    tabla_apa(
        doc,
        "Tabla 3",
        "Resultados de las seis mutaciones ejecutadas sobre jy_velas/inventario.py",
        [
            "Id",
            "Cambio introducido",
            "¿Falló?",
            "Pruebas que detectaron la falla",
        ],
        [
            [
                [("c", "M1")],
                [("c", "<="), " por ", ("c", "<"), " en validación de cantidad"],
                "Sí",
                "4 pruebas (compra y consumo con 0 y tablas de decisión)",
            ],
            [
                [("c", "M2")],
                [("c", ">"), " por ", ("c", ">="), " en validación de stock"],
                "Sí",
                [("c", "test_consumir_descuenta_existencia[MAT-FRASCO-10-10-0]")],
            ],
            [
                [("c", "M3")],
                "Descuento reemplazado por suma en consumo",
                "Sí",
                "4 pruebas de existencia restante y tabla de decisión",
            ],
            [
                [("c", "M4")],
                [("c", "<="), " por ", ("c", "<"), " en alerta de mínimo"],
                "Sí",
                "3 pruebas de límite exacto (5/5 y 0/0)",
            ],
            [
                [("c", "M5")],
                "Ignorar fecha explícita en compra",
                "Sí",
                [("c", "test_fecha_personalizada_se_conserva")],
            ],
            [
                [("c", "M6")],
                [
                    "Quitar ",
                    ("c", "math.isfinite"),
                    " (aceptar ",
                    ("c", "NaN"),
                    "/inf)",
                ],
                "Sí",
                "4 pruebas de valores no finitos en compra y consumo",
            ],
        ],
        [0.45, 2.25, 0.70, 3.10],
        "SHA-256 original y restaurado: 55c789b7...bbb4506d "
        "(docs/mutaciones_semana7.txt).",
        font_size=9,
    )

    h2(doc, "Caso 4: Falsos positivos de seguridad, riesgos omitidos y estado mutable")
    p_vineta(doc, [("b", "Fase: "), "operación."])
    p_vineta(
        doc,
        [
            ("b", "Qué propuso la IA: "),
            "detectó tres fallos reales (",
            ("c", "H-01"),
            " a ",
            ("c", "H-03"),
            "), pero reportó dos falsos positivos: que ",
            ("c", "math.isfinite"),
            " era ejecución dinámica de código y que faltaba hashing de ",
            "contraseñas con ",
            ("c", "bcrypt/argon2"),
            ". No advirtió códigos duplicados ni referencias mutables.",
        ],
    )
    p_vineta(
        doc,
        [
            ("b", "Qué estaba mal: "),
            "los dos primeros eran falsos positivos (no hay ",
            ("c", "eval"),
            ", usuarios ni contraseñas), mientras que los riesgos omitidos ",
            "comprometían la integridad del catálogo y el aislamiento de estado ",
            "(OWASP Foundation, 2021).",
        ],
    )
    p_vineta(
        doc,
        [
            ("b", "Cómo lo detectaste: "),
            "leí línea por línea frente al commit ",
            ("c", "fe00949"),
            ", ejecuté Ruff y ",
            ("c", "pip-audit"),
            ", y escribí 58 pruebas de abuso en ",
            (
                "link",
                "test_seguridad_inventario.py",
                f"{BLOB}/tests/test_seguridad_inventario.py",
            ),
            " con ",
            ("c", "bool"),
            ", tipos no hashables, ",
            ("c", "NaN"),
            ", longitudes excesivas y duplicados.",
        ],
    )
    p_vineta(
        doc,
        [
            ("b", "Qué hice: "),
            "descarté los dos falsos positivos, corregí siete hallazgos (",
            ("c", "H-01"),
            " a ",
            ("c", "H-07"),
            ", Anexo B) añadiendo validación en ",
            ("c", "Material.__post_init__"),
            ", rechazo de duplicados, copias con ",
            ("c", "dataclasses.replace"),
            ", configuración de Ruff y fijación de ",
            ("c", "pytest==9.2.0"),
            "; evidencia en ",
            ("link", "revision_seguridad.md", f"{BLOB}/revision_seguridad.md"),
            " y commit ",
            ("link", "95118b9", f"{COMMIT}/95118b9"),
            ".",
        ],
    )


def seccion_estado_final(doc: Document) -> None:
    """Seccion 5. Estado final del sistema."""
    h1(doc, "5. Estado final del sistema")
    p_mixto(
        doc,
        [
            "El sistema se entrega como una librería de dominio importable en ",
            "Python 3.11, sin servidor ni dependencias de ejecución: cada regla ",
            "vive en una función con docstring y cada error controlado lanza ",
            ("c", "ErrorInventario"),
            " con un mensaje estable para reutilizarse desde cualquier interfaz.",
        ],
    )
    p_vineta(
        doc,
        [
            ("b", "Arquitectura: "),
            "módulo único de dominio (",
            ("link", "jy_velas/inventario.py", f"{BLOB}/jy_velas/inventario.py"),
            ") con ",
            ("c", "dataclasses"),
            ", ",
            ("c", "datetime"),
            ", ",
            ("c", "math"),
            " y ",
            ("c", "typing"),
            " en memoria. El diseño contempla 9 entidades (",
            ("c", "Material"),
            ", ",
            ("c", "Compra"),
            ", ",
            ("c", "Consumo"),
            ", ",
            ("c", "Producto"),
            ", ",
            ("c", "Receta"),
            ", ",
            ("c", "Pedido"),
            ", ",
            ("c", "ItemPedido"),
            ", ",
            ("c", "Venta"),
            ", ",
            ("c", "Cliente"),
            ") y 13 operaciones; en este incremento se implementaron ",
            ("c", "Material"),
            ", ",
            ("c", "Compra"),
            " y las 5 del núcleo (",
            ("c", "registrar_compra"),
            ", ",
            ("c", "existencia"),
            ", ",
            ("c", "historial"),
            ", ",
            ("c", "consumir_material"),
            ", ",
            ("c", "materiales_bajo_minimo"),
            "). Ver ",
            ("link", "docs/diseno.md", f"{BLOB}/docs/diseno.md"),
            " y ",
            ("link", "docs/adr.md", f"{BLOB}/docs/adr.md"),
            ".",
        ],
    )
    p_vineta(
        doc,
        [
            ("b", "Funcionalidades terminadas: "),
            ("c", "HU-01"),
            " (registrar compras), ",
            ("c", "HU-02"),
            " (consumir materiales) y ",
            ("c", "HU-03"),
            " (alertas de mínimo), las tres historias ",
            ("i", "Must"),
            " del incremento completadas con validación previa a mutar el estado.",
        ],
    )
    p_vineta(
        doc,
        [
            ("b", "Pruebas y pipeline: "),
            "116 pruebas parametrizadas superadas (",
            ("c", "21 + 20 + 17 + 58"),
            ") con pytest 9.2.0 (2026), Ruff sin avisos y ",
            ("c", "pip-audit"),
            " sin vulnerabilidades, según ",
            (
                "link",
                "pipeline_ultima_ejecucion.md",
                f"{BLOB}/docs/pipeline_ultima_ejecucion.md",
            ),
            " y ",
            ("link", "plan_de_pruebas.md", f"{BLOB}/docs/plan_de_pruebas.md"),
            " (Tabla 4).",
        ],
    )

    tabla_apa(
        doc,
        "Tabla 4",
        "Resumen de la última ejecución verificada del pipeline",
        ["Verificación", "Alcance y archivo", "Resultado"],
        [
            [
                [("c", "ruff check .")],
                "Reglas E, F, B, S (máx. 88 chars) en todo el proyecto",
                [("c", "All checks passed!")],
            ],
            [
                [("c", "pip_audit -r ...")],
                "pytest==9.2.0 fijado; 0 dependencias de ejecución",
                [("c", "No known vulnerabilities")],
            ],
            [
                "Compras (HU-01)",
                [
                    (
                        "link",
                        "test_registrar_compra.py",
                        f"{BLOB}/tests/test_registrar_compra.py",
                    )
                ],
                "21 pruebas superadas",
            ],
            [
                "Consumo (HU-02)",
                [
                    (
                        "link",
                        "test_consumir_material.py",
                        f"{BLOB}/tests/test_consumir_material.py",
                    )
                ],
                "20 pruebas superadas",
            ],
            [
                "Consultas (HU-03)",
                [
                    (
                        "link",
                        "test_consultas_inventario.py",
                        f"{BLOB}/tests/test_consultas_inventario.py",
                    )
                ],
                "17 pruebas superadas",
            ],
            [
                "Abuso y seguridad",
                [
                    (
                        "link",
                        "test_seguridad_inventario.py",
                        f"{BLOB}/tests/test_seguridad_inventario.py",
                    )
                ],
                "58 pruebas superadas",
            ],
            [
                [("b", "Total suite pytest")],
                "Ejecución completa con Python 3.11.0",
                [("b", "116 passed in 0.60s")],
            ],
        ],
        [1.75, 2.95, 1.80],
        "Salida verificada en docs/pipeline_ultima_ejecucion.md (2026-11-26).",
        font_size=9,
    )

    p_vineta(
        doc,
        [
            ("b", "Pendientes: "),
            "persistencia entre sesiones (",
            ("c", "N-09"),
            "), pedidos, ventas y reportes (",
            ("c", "N-06"),
            " a ",
            ("c", "N-08"),
            "), interfaz web o móvil (",
            ("c", "N-11"),
            "), roles (",
            ("c", "N-10"),
            ") e integración continua de Ruff y ",
            ("c", "pip-audit"),
            ". Se difirieron porque no hacían parte de los criterios de ",
            "aceptación y ",
            ("c", "ADR-001"),
            " prioriza consolidar el dominio.",
        ],
    )


def seccion_etica(doc: Document) -> None:
    """Seccion 6. Reflexion etica y legal."""
    h1(doc, "6. Reflexión ética y legal")
    tabla_apa(
        doc,
        "Tabla 5",
        "Decisiones éticas y legales aplicadas al proyecto",
        ["Principio", "Decisión en mi proyecto", "Evidencia"],
        [
            [
                "Datos personales (Ley 1581 de 2012)",
                "Sin datos reales: entrevista simulada por un compañero y catálogo "
                "ficticio con tildes, eñe y apóstrofos.",
                [
                    ("link", "requisitos.md", f"{BLOB}/docs/requisitos.md"),
                    ", ",
                    ("link", "conftest.py", f"{BLOB}/tests/conftest.py"),
                ],
            ],
            [
                "Sesgo",
                [
                    "El sistema no evalúa personas; aplica reglas numéricas. "
                    "Rechacé ",
                    ("c", "bool"),
                    " como cantidad para evitar que ",
                    ("c", "True"),
                    " contara como 1.",
                ],
                [
                    ("link", "inventario.py", f"{BLOB}/jy_velas/inventario.py"),
                    ", ",
                    (
                        "link",
                        "test_seguridad_inventario.py",
                        f"{BLOB}/tests/test_seguridad_inventario.py",
                    ),
                ],
            ],
            [
                "Transparencia",
                "Cada error tiene un mensaje estable; los ADR y la bitácora "
                "explican el porqué de cada decisión.",
                [
                    ("link", "adr.md", f"{BLOB}/docs/adr.md"),
                    ", ",
                    ("link", "bitacora_ia.md", f"{BLOB}/bitacora_ia.md"),
                ],
            ],
            [
                "Responsabilidad",
                "Yo verifico y respondo por el código; la IA propuso, pero las "
                "pruebas, el linter y la lectura manual decidieron.",
                [
                    ("link", "revision_seguridad.md", f"{BLOB}/revision_seguridad.md"),
                    ", ",
                    (
                        "link",
                        "pipeline",
                        f"{BLOB}/docs/pipeline_ultima_ejecucion.md",
                    ),
                ],
            ],
            [
                "Propiedad intelectual y uso de IA",
                "Código propio con fines académicos y licencia en README; uso de "
                "IA declarado en 14 entradas con trazabilidad.",
                [
                    ("link", "README.md", f"{BLOB}/README.md"),
                    ", ",
                    ("link", "bitacora_ia.md", f"{BLOB}/bitacora_ia.md"),
                ],
            ],
        ],
        [1.45, 3.25, 1.80],
        "Elaboración propia a partir de bitacora_ia.md y revision_seguridad.md.",
        font_size=9,
    )

    p_mixto(
        doc,
        [
            "El dilema ético más importante que enfrenté fue aceptar o no las ",
            "pruebas generadas inicialmente por la IA. Era tentador conservar ",
            "una suite en verde que ahorraba tiempo de entrega, pero ocho ",
            "pruebas comprobaban únicamente el estado general o el tipo ",
            "genérico ",
            ("c", "Exception"),
            " en lugar de la regla de negocio. Si las hubiera dejado, el ",
            "sistema habría parecido correcto con stock insuficiente y fechas ",
            "ignoradas. Decidí borrarlas, derivar los esperados desde el criterio ",
            "de aceptación y someter el código a seis mutaciones para demostrar ",
            "que fallaban cuando la lógica se rompía. La responsabilidad por ese ",
            "juicio fue mía, no del asistente.",
        ],
    )


def seccion_aprendizajes(doc: Document) -> None:
    """Seccion 7. Aprendizajes."""
    h1(doc, "7. Aprendizajes")
    p_mixto(
        doc,
        [
            "Aprendí a escribir un contrato verificable antes de pedir código, ",
            "a derivar pruebas desde particiones de equivalencia, valores límite ",
            "y tablas de decisión, a ejecutar mutaciones para comprobar si una ",
            "prueba realmente detecta defectos y a auditar dependencias con ",
            ("c", "pip-audit"),
            ". Confié demasiado en la IA al inicio: acepté sin cuestionar ",
            "suficiente la idea de usar ",
            ("c", "Decimal"),
            " y una primera versión que sumaba la cantidad comprada antes de ",
            "validarla. También aprendí que un falso positivo consume tiempo si ",
            "no se contrasta con el código, mientras que un riesgo real puede ",
            "estar justo donde la IA no miró. Haría tres cosas distinto:",
        ],
        keep_with_next=True,
    )
    p_vineta(
        doc,
        [
            "Escribiría la tabla de casos límite y ambigüedades antes de pedir ",
            "la implementación, asegurando que el esperado provenga de la regla ",
            "y no del código.",
        ],
        keep_with_next=True,
    )
    p_vineta(
        doc,
        [
            "Integraría Ruff y ",
            ("c", "pip-audit"),
            " como parte habitual del ciclo desde la primera semana, no solo ",
            "al final.",
        ],
        keep_with_next=True,
    )
    p_vineta(
        doc,
        [
            "Pediría a la IA explicitar sus supuestos antes de aceptar una ",
            "sugerencia; así habría detectado antes el desvío de ",
            ("c", "Decimal"),
            " y el orden de las validaciones.",
        ],
    )


def seccion_anexos(doc: Document) -> None:
    """Seccion 8. Anexos con enlaces completos y tablas sintesis."""
    titulo = h1(doc, "8. Anexos")
    titulo.paragraph_format.page_break_before = True

    h2(doc, "Documentos y evidencias en el repositorio")
    enlaces = [
        (
            "Bitácora de uso de IA (14 entradas): ",
            "bitacora_ia.md",
            f"{BLOB}/bitacora_ia.md",
        ),
        (
            "Propuesta (Módulo 1): ",
            "docs/propuesta.md",
            f"{BLOB}/docs/propuesta.md",
        ),
        (
            "Requisitos (Módulo 2): ",
            "docs/requisitos.md",
            f"{BLOB}/docs/requisitos.md",
        ),
        (
            "Diseño (Módulo 3): ",
            "docs/diseno.md",
            f"{BLOB}/docs/diseno.md",
        ),
        (
            "Decisiones arquitectónicas: ",
            "docs/adr.md",
            f"{BLOB}/docs/adr.md",
        ),
        (
            "Código fuente del dominio: ",
            "jy_velas/inventario.py",
            f"{BLOB}/jy_velas/inventario.py",
        ),
        (
            "Plan de pruebas (Módulo 5): ",
            "docs/plan_de_pruebas.md",
            f"{BLOB}/docs/plan_de_pruebas.md",
        ),
        (
            "Registro de pruebas y mutaciones: ",
            "registro_pruebas.md",
            f"{BLOB}/registro_pruebas.md",
        ),
        (
            "Evidencia de mutaciones M1-M6: ",
            "docs/mutaciones_semana7.txt",
            f"{BLOB}/docs/mutaciones_semana7.txt",
        ),
        (
            "Revisión de seguridad (Módulo 6): ",
            "revision_seguridad.md",
            f"{BLOB}/revision_seguridad.md",
        ),
        (
            "Guía de despliegue: ",
            "docs/despliegue.md",
            f"{BLOB}/docs/despliegue.md",
        ),
        (
            "Plan de operación: ",
            "docs/operacion.md",
            f"{BLOB}/docs/operacion.md",
        ),
        (
            "Última ejecución del pipeline: ",
            "docs/pipeline_ultima_ejecucion.md",
            f"{BLOB}/docs/pipeline_ultima_ejecucion.md",
        ),
    ]
    for prefijo, etiqueta, url in enlaces:
        p_vineta(doc, [prefijo, ("link", etiqueta, url)])

    tabla_apa(
        doc,
        "Tabla 6",
        "Anexo A: Distribución de las 14 entradas en bitacora_ia.md",
        ["Etapa", "Entradas", "Aceptadas", "Con cambios", "Rechazadas"],
        [
            ["Semana 5 (Módulo 4 — HU-01)", "1 a 6", "2", "2", "2"],
            ["Semana 7 (Módulo 5 — Pruebas)", "7 a 10", "1", "3", "0"],
            ["Semana 6 (Módulo 6 — Seguridad)", "11 a 14", "0", "2", "2"],
            [
                [("b", "Total")],
                [("b", "14 entradas")],
                [("b", "3")],
                [("b", "7")],
                [("b", "4")],
            ],
        ],
        [2.30, 1.20, 1.00, 1.00, 1.00],
        "Resumen cuantitativo de decisiones registradas en bitacora_ia.md.",
        font_size=9,
    )

    tabla_apa(
        doc,
        "Tabla 7",
        "Anexo B: Siete hallazgos de seguridad corregidos (commit 95118b9)",
        ["Id", "Origen", "Riesgo OWASP mitigado", "Corrección aplicada"],
        [
            [
                [("c", "H-01")],
                "IA + revisión",
                [("c", "bool"), " aceptado y ", ("c", "TypeError"), " (A03:2021)"],
                "Validar (int, float), excluir bool y exigir math.isfinite",
            ],
            [
                [("c", "H-02")],
                "IA + revisión",
                [("c", "fecha"), " sin validación de tipo (A04:2021)"],
                "Método _validar_fecha: solo None o datetime.date",
            ],
            [
                [("c", "H-03")],
                "IA + revisión",
                "Código no hashable o gigante (A03/A04:2021)",
                "Validar str no vacío con longitud máxima de 50 caracteres",
            ],
            [
                [("c", "H-04")],
                "Manual",
                "Existencia/mínimo negativos o NaN (A04:2021)",
                "Validación en Material.__post_init__ y límites de longitud",
            ],
            [
                [("c", "H-05")],
                "Manual",
                "Códigos duplicados sobrescritos (A04:2021)",
                "Detección temprana con ErrorInventario en Inventario.__init__",
            ],
            [
                [("c", "H-06")],
                "Manual",
                "Estado interno mutable expuesto (A01:2021)",
                "Copias independientes mediante dataclasses.replace",
            ],
            [
                [("c", "H-07")],
                "Manual + Ruff",
                "Sin Ruff, pytest sin fijar y E501 (A06:2021)",
                "Reglas E,F,B,S, pytest==9.2.0 fijado y líneas divididas",
            ],
        ],
        [0.50, 1.05, 2.25, 2.70],
        "Detalle completo de líneas y severidades en revision_seguridad.md.",
        font_size=9,
    )


def seccion_referencias(doc: Document) -> None:
    """Referencias en formato APA 7 con sangria francesa."""
    titulo = h1(doc, "Referencias")
    titulo.paragraph_format.page_break_before = True
    refs = [
        [
            "Fundación Escuela Tecnológica de Neiva. (2026). ",
            ("i", "Proyecto integrador: tarea final del seminario"),
            " [Documento del curso].",
        ],
        [
            "García Coqueco, J. S. (2026). ",
            ("i", "JY Velas y Jabones"),
            " [Repositorio de código]. GitHub. ",
            ("link", REPO, REPO),
        ],
        [
            "Myers, G. J., Sandler, C., & Badgett, T. (2011). ",
            ("i", "The art of software testing"),
            " (3.ª ed.). John Wiley & Sons.",
        ],
        [
            "OpenCode. (2026). ",
            ("i", "Documentación de OpenCode"),
            ". ",
            ("link", "https://opencode.ai", "https://opencode.ai"),
        ],
        [
            "OWASP Foundation. (2021). ",
            ("i", "OWASP Top 10:2021"),
            ". ",
            ("link", "https://owasp.org/Top10/", "https://owasp.org/Top10/"),
        ],
        [
            "Pressman, R. S., & Maxim, B. R. (2015). ",
            ("i", "Software engineering: A practitioner's approach"),
            " (8.ª ed.). McGraw-Hill Education.",
        ],
        [
            "pytest. (2026). ",
            ("i", "pytest documentation"),
            " (Versión 9.2.0). ",
            ("link", "https://docs.pytest.org/", "https://docs.pytest.org/"),
        ],
        [
            "Python Packaging Authority. (2026). ",
            ("i", "pip-audit"),
            " [Paquete de PyPI]. ",
            (
                "link",
                "https://pypi.org/project/pip-audit/",
                "https://pypi.org/project/pip-audit/",
            ),
        ],
        [
            "Python Software Foundation. (2026). ",
            ("i", "Python 3.11 documentation"),
            ". ",
            (
                "link",
                "https://docs.python.org/3.11/",
                "https://docs.python.org/3.11/",
            ),
        ],
        [
            "Ruff. (2026). ",
            ("i", "Ruff documentation"),
            ". ",
            ("link", "https://docs.astral.sh/ruff/", "https://docs.astral.sh/ruff/"),
        ],
    ]
    for ref in refs:
        p = parrafo(doc, hanging=True, spacing=2.0)
        agregar_segmentos(p, ref, size=12)


def exportar_pdf_con_word(ruta_docx: Path, ruta_pdf: Path) -> None:
    """Convierte el archivo DOCX a PDF usando Microsoft Word COM."""
    import win32com.client

    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc_word = None
    try:
        doc_word = word.Documents.Open(str(ruta_docx.resolve()))
        doc_word.SaveAs(str(ruta_pdf.resolve()), FileFormat=17)
    finally:
        if doc_word is not None:
            doc_word.Close(False)
        word.Quit()


def main() -> None:
    """Genera el DOCX, exporta a PDF y sincroniza la carpeta de entrega."""
    doc = Document()
    configurar_documento(doc)
    numerar_paginas(doc.sections[0])

    portada(doc)
    seccion_resumen(doc)
    seccion_problema(doc)
    seccion_ia_ciclo_vida(doc)
    seccion_verificacion(doc)
    seccion_estado_final(doc)
    seccion_etica(doc)
    seccion_aprendizajes(doc)
    seccion_anexos(doc)
    seccion_referencias(doc)

    DOCS.mkdir(exist_ok=True)
    doc.save(SALIDA_DOCX)
    exportar_pdf_con_word(SALIDA_DOCX, SALIDA_PDF)

    if CARPETA_ENTREGA.exists():
        shutil.copy2(SALIDA_DOCX, CARPETA_ENTREGA / "Informe_Final_Integrador_APA.docx")
        shutil.copy2(SALIDA_PDF, CARPETA_ENTREGA / "Informe_Final_Integrador_APA.pdf")

    print(f"DOCX generado: {SALIDA_DOCX}")
    print(f"PDF generado: {SALIDA_PDF}")


if __name__ == "__main__":
    main()
