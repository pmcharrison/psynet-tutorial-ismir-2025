# conf.py
project = "PsyNet @ ISMIR 2025"
author = "Me"
extensions = ["sphinx_design", "sphinx_copybutton"]
templates_path = ["_templates"]
exclude_patterns = []

html_theme = "pydata_sphinx_theme"
html_theme_options = {
    "logo": {"text": "PsyNet @ ISMIR 2025"},
    "use_edit_page_button": True,
    "show_toc_level": 2,
    "secondary_sidebar_items": ["page-toc", "edit-this-page"],
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/pmcharrison/psynet-tutorial-ismir-2025",
            "icon": "fa-brands fa-github",
        },
    ],
    "footer_start": [],
    "footer_center": [],
    "footer_end": []
}

html_context = {
    "github_user": "pmcharrison",
    "github_repo": "psynet-tutorial-ismir-2025",
    "github_version": "main",
    "doc_path": "docs",
}

html_sidebars = {
    "**": []
}

