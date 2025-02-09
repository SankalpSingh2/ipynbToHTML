import nbformat
from nbconvert import HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor
from traitlets.config import Config
import os


def convert_notebook_with_plotly(notebook_path, output_html_path):
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)

    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
    ep.preprocess(nb, {'metadata': {'path': os.path.dirname(notebook_path)}})

    c = Config()
    c.TemplateExporter.extra_template_basedirs = ['templates']
    c.TemplateExporter.template_name = 'plotly_template'

    html_exporter = HTMLExporter(config=c)
    html_exporter.exclude_input = False
    html_exporter.exclude_output_prompt = True

    (body, resources) = html_exporter.from_notebook_node(nb)

    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(body)


if __name__ == "__main__":
    convert_notebook_with_plotly(
        "notebook_3.ipynb",
        "full_notebook_output.html"
    )