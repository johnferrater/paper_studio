from apps.sources.models import Source


def _authors(source):
    return source.authors.strip() or "Unknown author"


def format_apa(source):
    author = _authors(source)
    year = source.year or "n.d."
    text = f"{author} ({year}). {source.title.strip()}."
    if source.source_type in (Source.SourceType.BOOK, Source.SourceType.REPORT):
        if source.publisher:
            text += f" {source.publisher}."
    elif source.source_type == Source.SourceType.WEBSITE:
        if source.url:
            text += f" {source.url}"
    elif source.publisher:
        text += f" {source.publisher}."
    if source.doi:
        text += f" https://doi.org/{source.doi}"
    return " ".join(text.split())


def format_mla(source):
    author = _authors(source).rstrip(".")
    text = f'{author}. "{source.title.strip()}."'
    if source.publisher:
        text += f" {source.publisher},"
    text += f" {source.year}." if source.year else " n.d."
    if source.url:
        text += f" {source.url}."
    return " ".join(text.split())


def format_citation(source, style):
    if style == "MLA":
        return format_mla(source)
    return format_apa(source)
