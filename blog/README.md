# Notebooks as Blog

This folder contains tools to convert Jupyter notebooks into static, scrollable HTML pages you can serve as a blog.

How it works

- Place any `.ipynb` files into `blog/notebooks/`.
- Run the converter to produce HTML files into `blog/site/` and an index page.

Quick start (macOS / zsh):

```bash
# from repo root
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install nbformat nbconvert
python3 profile-site/blog/convert_notebooks.py
# open the output site in your browser
python3 -m http.server 8001 --directory profile-site/blog/site
# open http://localhost:8001
```

If you prefer, you can convert a single notebook manually with:

```bash
jupyter nbconvert --to html profile-site/blog/notebooks/my_note.ipynb --output-dir=profile-site/blog/site
```

If you want, I can add a GitHub Action to auto-convert notebooks on push.
