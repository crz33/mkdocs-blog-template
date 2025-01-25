import csv

# create category map / url : (slug, display-name)
categories = {}
with open("hooks-category.csv") as f:
    csv_reader = csv.reader(f)
    for record in csv_reader:
        categories[f"blog/category/{record[0]}/"] = record


def on_pre_page(page, config, files):
    """
    change category title
    """
    if page.url in categories:
        page.title = categories[page.url][1]
    return page


def on_page_markdown(markdown, page, config, files):
    """
    change category page title
    """
    if page.url in categories:
        markdown = markdown.replace(
            f"# {categories[page.url][0]}",
            f"# {categories[page.url][1]}",
        )
    return markdown
