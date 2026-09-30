from pathlib import Path
import re

import pypandoc

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.table import (
    WD_CELL_VERTICAL_ALIGNMENT,
    WD_TABLE_ALIGNMENT,
)
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE

from docx.oxml import OxmlElement
from docx.oxml.ns import qn


BASE_DIR = Path(__file__).parent

DEFAULT_REFERENCE_DOC = (
    BASE_DIR
    / "templates"
    / "default_report.docx"
)


# =====================================================
# General helpers
# =====================================================

def extract_document_title(markdown_text):
    """
    Extract the first Markdown heading and use it
    as the DOCX document title.
    """

    for line in markdown_text.splitlines():

        match = re.match(
            r"^\s*#{1,6}\s+(.+?)\s*$",
            line,
        )

        if match:
            return match.group(1).strip()

    return "Research Report"


def _style_name(paragraph):
    """
    Return the Word style name for a paragraph.
    """

    if paragraph.style:
        return paragraph.style.name

    return ""


def _is_heading(paragraph):
    """
    Determine whether a paragraph is a heading.
    """

    name = _style_name(
        paragraph
    )

    return (
        name == "Title"
        or name.startswith(
            "Heading"
        )
    )


def _numbered_heading_depth(text):
    """
    Infer semantic heading depth from numbering.

    Examples:

    4. Detailed Candidate Analysis
        -> depth 1

    4.1 Nixxy, Inc.
        -> depth 2

    4.1.1 Ownership
        -> depth 3
    """

    text = text.strip()

    # Top-level section:
    # 1. Executive Summary
    if re.match(
        r"^\d+\.\s+\S",
        text,
    ):
        return 1

    # Nested section:
    # 4.1 ...
    # 4.1.1 ...
    match = re.match(
        r"^(\d+(?:\.\d+)+)\s+\S",
        text,
    )

    if not match:
        return None

    return len(
        match.group(1).split(".")
    )


def normalize_heading_hierarchy(doc):
    """
    Normalize heading hierarchy after Pandoc conversion.

    Rules:

    First heading
        -> Title

    1. Executive Summary
        -> Heading 1

    4.1 Nixxy
        -> Heading 2

    4.1.1 Ownership
        -> Heading 3

    Unnumbered headings inside a numbered subsection
    cannot appear larger than their parent.

    This makes report hierarchy independent of occasional
    Markdown heading-level inconsistencies produced by
    the research agent.
    """

    first_heading_seen = False

    current_numeric_depth = 0


    for paragraph in doc.paragraphs:

        text = (
            paragraph.text
            .strip()
        )

        if not text:
            continue

        if not _is_heading(
            paragraph
        ):
            continue


        # ---------------------------------------------
        # Report title
        # ---------------------------------------------

        if not first_heading_seen:

            paragraph.style = (
                "Title"
            )

            first_heading_seen = True

            continue


        # ---------------------------------------------
        # Appendix
        # ---------------------------------------------

        if re.match(
            r"^Appendix\b",
            text,
            flags=re.IGNORECASE,
        ):

            paragraph.style = (
                "Heading 1"
            )

            current_numeric_depth = 1

            continue


        # ---------------------------------------------
        # Numbered headings
        # ---------------------------------------------

        depth = (
            _numbered_heading_depth(
                text
            )
        )


        if depth is not None:

            current_numeric_depth = (
                depth
            )


            if depth == 1:

                paragraph.style = (
                    "Heading 1"
                )


            elif depth == 2:

                paragraph.style = (
                    "Heading 2"
                )


            else:

                paragraph.style = (
                    "Heading 3"
                )


            continue


        # ---------------------------------------------
        # Unnumbered headings
        # ---------------------------------------------

        style_name = (
            _style_name(
                paragraph
            )
        )


        # Example:
        #
        # 4.1 Nixxy
        #     Company Overview
        #
        # Company Overview should never appear
        # larger than 4.1.
        if current_numeric_depth >= 2:

            if style_name in {
                "Heading 1",
                "Heading 2",
            }:

                paragraph.style = (
                    "Heading 3"
                )


        # Example:
        #
        # 6. Candidate Prioritization
        #     Priority 1 — Nixxy
        #
        # A non-numbered Heading 1 beneath a numbered
        # section should become Heading 2.
        elif current_numeric_depth == 1:

            if style_name == "Heading 1":

                paragraph.style = (
                    "Heading 2"
                )


# =====================================================
# DOCX XML helpers
# =====================================================

def set_cell_shading(
    cell,
    fill,
):
    """
    Set table cell background color.
    """

    tc_pr = (
        cell
        ._tc
        .get_or_add_tcPr()
    )


    # Remove existing shading
    # so our value always wins.
    for node in tc_pr.findall(
        qn("w:shd")
    ):

        tc_pr.remove(
            node
        )


    shd = OxmlElement(
        "w:shd"
    )


    shd.set(
        qn("w:val"),
        "clear",
    )


    shd.set(
        qn("w:color"),
        "auto",
    )


    shd.set(
        qn("w:fill"),
        fill,
    )


    tc_pr.append(
        shd
    )


def set_cell_margins(
    cell,
    top=120,
    start=120,
    bottom=120,
    end=120,
):
    """
    Set internal table-cell padding.

    Values are in twips.
    """

    tc_pr = (
        cell
        ._tc
        .get_or_add_tcPr()
    )


    tc_mar = (
        tc_pr
        .first_child_found_in(
            "w:tcMar"
        )
    )


    if tc_mar is None:

        tc_mar = OxmlElement(
            "w:tcMar"
        )

        tc_pr.append(
            tc_mar
        )


    for margin, value in (

        ("top", top),

        ("start", start),

        ("bottom", bottom),

        ("end", end),

    ):

        node = tc_mar.find(
            qn(
                f"w:{margin}"
            )
        )


        if node is None:

            node = OxmlElement(
                f"w:{margin}"
            )

            tc_mar.append(
                node
            )


        node.set(
            qn("w:w"),
            str(value),
        )


        node.set(
            qn("w:type"),
            "dxa",
        )


def set_table_borders(
    table,
):
    """
    Apply light gray table borders.
    """

    tbl_pr = (
        table
        ._tbl
        .tblPr
    )


    borders = (
        tbl_pr
        .first_child_found_in(
            "w:tblBorders"
        )
    )


    if borders is None:

        borders = OxmlElement(
            "w:tblBorders"
        )

        tbl_pr.append(
            borders
        )


    for border_name in (

        "top",

        "left",

        "bottom",

        "right",

        "insideH",

        "insideV",

    ):

        border = borders.find(
            qn(
                f"w:{border_name}"
            )
        )


        if border is None:

            border = OxmlElement(
                f"w:{border_name}"
            )

            borders.append(
                border
            )


        border.set(
            qn("w:val"),
            "single",
        )


        border.set(
            qn("w:sz"),
            "4",
        )


        border.set(
            qn("w:space"),
            "0",
        )


        border.set(
            qn("w:color"),
            "D1D5DB",
        )


def set_repeat_table_header(
    row,
):
    """
    Repeat table header when a table spans pages.
    """

    tr_pr = (
        row
        ._tr
        .get_or_add_trPr()
    )


    # Avoid duplicate header settings.
    for node in tr_pr.findall(
        qn("w:tblHeader")
    ):

        tr_pr.remove(
            node
        )


    tbl_header = OxmlElement(
        "w:tblHeader"
    )


    tbl_header.set(
        qn("w:val"),
        "true",
    )


    tr_pr.append(
        tbl_header
    )


def center_table(
    table,
):
    """
    Center the table itself on the page.

    Cell text remains left-aligned.

    Both python-docx and explicit OOXML are used
    for better Word / LibreOffice compatibility.
    """

    table.alignment = (
        WD_TABLE_ALIGNMENT.CENTER
    )


    tbl_pr = (
        table
        ._tbl
        .tblPr
    )


    jc = (
        tbl_pr
        .first_child_found_in(
            "w:jc"
        )
    )


    if jc is None:

        jc = OxmlElement(
            "w:jc"
        )

        tbl_pr.append(
            jc
        )


    jc.set(
        qn("w:val"),
        "center",
    )


# =====================================================
# Hyperlink styling
# =====================================================

def configure_hyperlink_style(
    doc,
):
    """
    Make hyperlinks professional but identifiable.
    """

    styles = (
        doc.styles
    )


    try:

        hyperlink = (
            styles[
                "Hyperlink"
            ]
        )


    except KeyError:

        hyperlink = (
            styles.add_style(
                "Hyperlink",
                WD_STYLE_TYPE.CHARACTER,
            )
        )


    hyperlink.font.name = (
        "Arial"
    )


    hyperlink.font.size = (
        Pt(10.5)
    )


    hyperlink.font.color.rgb = (
        RGBColor(
            55,
            65,
            81,
        )
    )


    hyperlink.font.underline = (
        True
    )


# =====================================================
# Paragraph formatting
# =====================================================

def format_paragraphs(
    doc,
):
    """
    Improve pagination behavior.
    """

    for paragraph in doc.paragraphs:

        style_name = (
            _style_name(
                paragraph
            )
        )


        # Body paragraphs
        if style_name == "Normal":

            paragraph.paragraph_format.widow_control = (
                True
            )


            if len(
                paragraph.text
            ) < 120:

                paragraph.paragraph_format.keep_together = (
                    True
                )


        # Titles and headings
        if (

            style_name == "Title"

            or style_name.startswith(
                "Heading"
            )

        ):

            paragraph.paragraph_format.keep_with_next = (
                True
            )


# =====================================================
# Table formatting helpers
# =====================================================

def is_wide_table(
    table,
):
    """
    Tables with 5+ columns receive slightly
    smaller typography.
    """

    return (

        bool(
            table.rows
        )

        and

        len(
            table.rows[0].cells
        ) >= 5

    )


def average_first_column_length(
    table,
):
    """
    Detect short ID-style first columns.
    """

    values = []


    for row in table.rows[1:]:

        if not row.cells:
            continue


        value = (
            row.cells[0]
            .text
            .strip()
        )


        if value:

            values.append(
                len(value)
            )


    if not values:

        return None


    return (
        sum(values)
        / len(values)
    )


def optimize_first_column(
    table,
):
    """
    Narrow short identifier columns such as:

    F-001
    R-001
    S-001
    """

    if not table.rows:

        return


    if len(
        table.rows[0].cells
    ) < 2:

        return


    avg_length = (
        average_first_column_length(
            table
        )
    )


    if (

        avg_length is None

        or avg_length > 12

    ):

        return


    target_width = (
        Inches(
            0.9
        )
    )


    try:

        table.columns[0].width = (
            target_width
        )


    except Exception:

        pass


    for row in table.rows:

        row.cells[0].width = (
            target_width
        )


# =====================================================
# Table formatting
# =====================================================

def format_tables(
    doc,
):
    """
    Apply professional formatting to every table.
    """

    for table in doc.tables:


        # ---------------------------------------------
        # Center table on page
        # ---------------------------------------------

        center_table(
            table
        )


        # ---------------------------------------------
        # Borders
        # ---------------------------------------------

        set_table_borders(
            table
        )


        wide = (
            is_wide_table(
                table
            )
        )


        # Let Word calculate remaining widths.
        table.autofit = True


        # ---------------------------------------------
        # Body cells
        # ---------------------------------------------

        for row in table.rows:

            for cell in row.cells:


                cell.vertical_alignment = (
                    WD_CELL_VERTICAL_ALIGNMENT.CENTER
                )


                set_cell_margins(
                    cell
                )


                for paragraph in cell.paragraphs:


                    paragraph.alignment = (
                        WD_ALIGN_PARAGRAPH.LEFT
                    )


                    paragraph.paragraph_format.space_before = (
                        Pt(0)
                    )


                    paragraph.paragraph_format.space_after = (
                        Pt(2)
                    )


                    paragraph.paragraph_format.line_spacing = (
                        1.0
                    )


                    for run in paragraph.runs:


                        run.font.name = (
                            "Arial"
                        )


                        run.font.size = (

                            Pt(8.5)

                            if wide

                            else Pt(9)

                        )


        # ---------------------------------------------
        # Header row
        # ---------------------------------------------

        if table.rows:


            header_row = (
                table.rows[0]
            )


            set_repeat_table_header(
                header_row
            )


            for cell in header_row.cells:


                set_cell_shading(
                    cell,
                    "E9EDF2",
                )


                for paragraph in cell.paragraphs:


                    paragraph.paragraph_format.space_after = (
                        Pt(2)
                    )


                    for run in paragraph.runs:


                        run.bold = (
                            True
                        )


                        run.font.name = (
                            "Arial"
                        )


                        run.font.size = (

                            Pt(8.5)

                            if wide

                            else Pt(9)

                        )


        # ---------------------------------------------
        # Short ID first-column optimization
        # ---------------------------------------------

        optimize_first_column(
            table
        )


# =====================================================
# Document metadata
# =====================================================

def format_document_metadata(
    doc,
    document_title,
):
    """
    Set clean DOCX metadata.
    """

    properties = (
        doc.core_properties
    )


    properties.title = (
        document_title
    )


    properties.subject = (
        "Research Report"
    )


    properties.author = (
        "Agentic Trading Lab"
    )


    properties.keywords = (
        "research, due diligence, "
        "deep research, agent"
    )


    properties.comments = (
        "Generated through the "
        "Agentic Trading Lab research workflow."
    )


# =====================================================
# Output validation
# =====================================================

def validate_output(
    doc,
):
    """
    Detect common Markdown residue.

    This only prints warnings.
    It does not block report generation.
    """

    markdown_link_pattern = (
        re.compile(
            r"\[[^\]]+\]\([^)]+\)"
        )
    )


    heading_pattern = (
        re.compile(
            r"^\s*#{1,6}\s+"
        )
    )


    warnings = []


    for paragraph in doc.paragraphs:


        text = (
            paragraph.text
            .strip()
        )


        if not text:

            continue


        if (

            markdown_link_pattern.search(
                text
            )

            or heading_pattern.search(
                text
            )

            or text == "---"

        ):

            warnings.append(
                text
            )


    if warnings:


        print(
            "Warning: possible Markdown "
            "residue detected:"
        )


        for warning in warnings[:10]:

            print(
                f"  - {warning[:120]}"
            )


# =====================================================
# Main Markdown -> DOCX exporter
# =====================================================

def markdown_to_docx(
    markdown_text,
    output_path,
    reference_doc=None,
):
    """
    Shared Markdown -> DOCX renderer used
    by all research agents.
    """

    output_path = (
        Path(
            output_path
        )
    )


    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    # ---------------------------------------------
    # Reference template
    # ---------------------------------------------

    if reference_doc is None:

        reference_doc = (
            DEFAULT_REFERENCE_DOC
        )


    reference_doc = (
        Path(
            reference_doc
        )
    )


    extra_args = [
        "--standalone",
    ]


    if reference_doc.exists():

        extra_args.append(
            f"--reference-doc={reference_doc}"
        )


    # ---------------------------------------------
    # Step 1:
    # Markdown -> DOCX
    # ---------------------------------------------

    try:


        pypandoc.convert_text(
            markdown_text,
            to="docx",
            format="gfm",
            outputfile=str(
                output_path
            ),
            extra_args=extra_args,
        )


    except Exception as exc:


        raise RuntimeError(

            "Pandoc DOCX conversion failed: "
            f"{exc}"

        ) from exc


    if not output_path.exists():


        raise RuntimeError(
            "DOCX file was not created."
        )


    # ---------------------------------------------
    # Step 2:
    # DOCX post-processing
    # ---------------------------------------------

    doc = Document(
        output_path
    )


    document_title = (
        extract_document_title(
            markdown_text
        )
    )


    # Fix heading levels first.
    normalize_heading_hierarchy(
        doc
    )


    configure_hyperlink_style(
        doc
    )


    format_document_metadata(
        doc,
        document_title,
    )


    format_paragraphs(
        doc
    )


    format_tables(
        doc
    )


    validate_output(
        doc
    )


    # ---------------------------------------------
    # Step 3:
    # Save
    # ---------------------------------------------

    doc.save(
        output_path
    )


    return output_path
