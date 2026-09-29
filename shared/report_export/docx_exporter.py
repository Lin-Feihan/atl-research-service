from pathlib import Path

import pypandoc


def markdown_to_docx(
    markdown_text,
    output_path,
    reference_doc=None,
):
    """
    Convert Markdown to DOCX using Pandoc.

    This shared renderer is used by all research agents.
    """

    output_path = Path(output_path)

    extra_args = [
        "--standalone",
    ]

    if reference_doc:
        extra_args.append(
            f"--reference-doc={reference_doc}"
        )

    try:
        pypandoc.convert_text(
            markdown_text,
            to="docx",
            format="gfm",
            outputfile=str(output_path),
            extra_args=extra_args,
        )
    except Exception as exc:
        raise RuntimeError(
            f"DOCX conversion failed: {exc}"
        ) from exc

    if not output_path.exists():
        raise RuntimeError(
            "Pandoc completed without creating "
            "the DOCX file."
        )

    return output_path
