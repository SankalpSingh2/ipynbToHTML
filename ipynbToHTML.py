import nbformat
from nbconvert import HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor
import os

def convert_notebook_to_html(notebook_path, output_html_path):
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)

    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
    ep.preprocess(nb, {'metadata': {'path': os.path.dirname(notebook_path)}})

    html_exporter = HTMLExporter(template_name='classic')
    body, _ = html_exporter.from_notebook_node(nb)

    with open("failed_attempts/plotly_figure.html", "r", encoding="utf-8") as plotly_file:
        plotly_html = plotly_file.read()

    plotly_script = '<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>\n'
    final_html = body.replace("</body>", plotly_script + plotly_html + "\n</body>")

    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(final_html)

if __name__ == "__main__":
    convert_notebook_to_html(
        "simple_graph.ipynb",
        "failed_attempts/final_output.html"
    )
