import re
import pathlib
import functools
from mkdocs.utils.meta import YAML_RE
import yaml
from yaml import SafeLoader

""" HTML of cardlink """
# https://xwrite.jp/man_editor_blogcard/
BLOG_CARD_COVER = (
    "<div class='crz33-cardlink'>"
    "  <a href='{url}'></a>"
    "  <div class='label'>{tag}</div>"
    "  <div class='body has_cover'>"
    "    <div class='thumbnail'>"
    "      <img loading='lazy' src='{img_src}'/>"
    "    </div>"
    "    <div class='header'>"
    "      <h1>{title}</h1>"
    "      <time>{time}</time>"
    "      <span class='categories'>{categories}</span>"
    "    </div>"
    "  </div>"
    "</div>"
)

BLOG_CARD = (
    "<div class='crz33-cardlink'>"
    "  <a href='{url}'></a>"
    "  <div class='label'>{tag}</div>"
    "  <div class='body'>"
    "    <div class='header'>"
    "      <h1>{title}</h1>"
    "      <time>{time}</time>"
    "      <span class='categories'>{categories}</span>"
    "    </div>"
    "  </div>"
    "</div>"
)


def on_page_markdown(markdown, page, config: dict, files):

    # config
    myconf = None
    if config.get("extra") and config["extra"].get("crz33"):
        myconf = config["extra"]["crz33"]

    # ends if no card link is defined
    if myconf is None or not myconf.get("cardlink"):
        return markdown

    # create key:fullpath, value:url for all documents
    path2url = {}
    for f in files.documentation_pages():
        path2url[f.abs_src_path] = f.dest_uri.replace("/index.html", "/")

    # replace [#](./sample-01.md) to blogcard
    markdown = re.sub(
        r"\[#\]\((.*\.md)\)",
        functools.partial(
            create_cardlink,
            abs_src_path=pathlib.Path(page.file.abs_src_path),
            path2url=path2url,
            myconf=myconf,
        ),
        markdown,
    )
    return markdown


def create_cardlink(
    match,
    abs_src_path: pathlib.Path,
    path2url: dict,
    myconf: dict,
):
    # Create target path and URL relative to the page
    target_path = abs_src_path.parent.joinpath(match[1])
    target_url = f"/{path2url[str(target_path.resolve())]}"

    # Read target markdown
    with open(target_path, "r", encoding="UTF-8") as f:
        markdown = f.read()

    # Read meta(frontmatter)
    meta_match = YAML_RE.match(markdown)
    meta_info: dict = yaml.load(meta_match.group(1), SafeLoader) or {}

    # cover
    html_block = BLOG_CARD_COVER
    if meta_info.get("cover", False):
        html_block = BLOG_CARD_COVER
    else:
        html_block = BLOG_CARD

    return html_block.format(
        url=target_url,
        title=meta_info["title"],
        img_src=myconf["cover_path"].format(slug=meta_info["slug"]),
        desc=meta_info.get("description") or "",
        tag=myconf["cardlink"]["tag"],
        time=meta_info.get("date"),
        categories=", ".join(meta_info.get("categories") or ""),
    )
