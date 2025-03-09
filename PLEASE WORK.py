import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import HTMLExporter
from traitlets.config import Config
import sys
from IPython.core.display import display, HTML


def convert_notebook_to_html(notebook_path, output_html="output.html"):
    """Executes a Jupyter Notebook and converts it into a standalone interactive HTML file with Bokeh interactivity."""

    # Load the notebook
    with open(notebook_path, "r", encoding="utf-8") as f:
        notebook = nbformat.read(f, as_version=4)

    # Configure the ExecutePreprocessor to run all cells
    execute_preprocessor = ExecutePreprocessor(timeout=600, kernel_name="python3")

    try:
        execute_preprocessor.preprocess(notebook, {'metadata': {'path': '.'}})
    except Exception as e:
        print(f"⚠️ Warning: Some cells may have failed to execute. Error: {e}")

    # Configure HTML exporter
    c = Config()
    c.HTMLExporter.embed_images = True  # Ensure images and plots are embedded
    html_exporter = HTMLExporter(config=c)
    html_exporter.exclude_input = False  # Show code cells in the output

    # Convert notebook to HTML
    (body, resources) = html_exporter.from_notebook_node(notebook)

    # Save the interactive HTML file
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(body)

    print(f"✅ Successfully converted '{notebook_path}' to '{output_html}' with Bokeh interactivity!")

    return output_html


def display_html_inside_notebook(output_html):
    """Displays the generated interactive HTML inside the Jupyter Notebook."""
    html_code = f'<iframe src="{output_html}" width="100%" height="600px"></iframe>'
    display(HTML(html_code))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_notebook.py your_notebook.ipynb [output.html]")
        sys.exit(1)

    notebook_path = sys.argv[1]
    output_html = sys.argv[2] if len(sys.argv) > 2 else "output.html"

    output_html = convert_notebook_to_html(notebook_path, output_html)

    # If running inside Jupyter, display the iframe
    try:
        get_ipython()  # Check if inside Jupyter Notebook
        display_html_inside_notebook(output_html)
    except NameError:
        print(f"✅ Notebook converted successfully: Open {output_html} in a browser.")
