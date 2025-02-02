import nbformat
from nbconvert import HTMLExporter
import os

def convert_notebook_to_html(notebook_path, output_html_path):

    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = nbformat.read(f, as_version=4)

    # nbconvert's HTMLExporter to converts the notebook to html
    html_exporter = HTMLExporter()
    html_exporter.template_name = 'classic'  # this is a built in template, not sure if we want to use another
    (body, resources) = html_exporter.from_notebook_node(notebook)

    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(body)

    print(f"Notebook converted to HTML and saved to {output_html_path}")

if __name__ == "__main__":
    notebook_path = 'sankalp_singh_project1.ipynb'
    output_html_path = 'output_notebook.html'

    convert_notebook_to_html(notebook_path, output_html_path)