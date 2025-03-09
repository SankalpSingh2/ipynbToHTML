import nbformat
from nbconvert import HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor
import os
import base64
from traitlets.config import Config
import shutil
import re
from pathlib import Path


def convert_notebook_to_html(notebook_path, output_html_path, execute=True):
    """
    Convert a Jupyter notebook to HTML, supporting various visualization libraries.

    Parameters:
    -----------
    notebook_path : str
        Path to the input Jupyter notebook
    output_html_path : str
        Path where the HTML file will be saved
    execute : bool, default=True
        Whether to execute the notebook cells before converting
    """
    # Read the notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)

    # Create output directory for resources
    output_dir = os.path.dirname(output_html_path)
    resources_dir = os.path.join(output_dir, 'resources')
    os.makedirs(resources_dir, exist_ok=True)

    # Execute the notebook if requested
    if execute:
        print(f"Executing notebook: {notebook_path}")
        try:
            ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
            ep.preprocess(nb, {'metadata': {'path': os.path.dirname(notebook_path)}})
        except Exception as e:
            print(f"Warning: Error executing notebook: {e}")

    # Configure the HTML exporter
    c = Config()

    # Enable extracting figures and other output
    c.HTMLExporter.preprocessors = [
        'nbconvert.preprocessors.ExtractOutputPreprocessor',
    ]

    # Set up the HTML exporter with custom configuration
    html_exporter = HTMLExporter(config=c)
    html_exporter.exclude_input_prompt = True
    html_exporter.exclude_output_prompt = True

    # Convert the notebook to HTML
    (body, resources) = html_exporter.from_notebook_node(nb)

    # Process resources (like images)
    if resources.get('outputs'):
        for filename, data in resources.get('outputs', {}).items():
            output_file = os.path.join(resources_dir, filename)
            with open(output_file, 'wb') as f:
                f.write(data)

        # Update image paths in HTML
        for filename in resources.get('outputs', {}):
            body = body.replace(f'attachment:{filename}', f'resources/{filename}')

    # Add additional scripts for enhanced visualization support
    additional_scripts = """
    <!-- Additional support for interactive visualizations -->
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>

    <!-- Support for bokeh visualizations -->
    <link href="https://cdn.bokeh.org/bokeh/release/bokeh-3.4.0.min.css" rel="stylesheet">
    <link href="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-3.4.0.min.css" rel="stylesheet">
    <link href="https://cdn.bokeh.org/bokeh/release/bokeh-tables-3.4.0.min.css" rel="stylesheet">
    <script src="https://cdn.bokeh.org/bokeh/release/bokeh-3.4.0.min.js"></script>
    <script src="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-3.4.0.min.js"></script>
    <script src="https://cdn.bokeh.org/bokeh/release/bokeh-tables-3.4.0.min.js"></script>

    <!-- Support for matplotlib widgets -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.6/require.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <script>
        // Configure RequireJS for matplotlib widgets
        require.config({
            paths: {
                jupyter: "https://cdnjs.cloudflare.com/ajax/libs/jupyter-js-widgets/3.5.1/extension",
                @jupyter-widgets/base: "https://unpkg.com/@jupyter-widgets/base@^2.0.0/dist/index",
                @jupyter-widgets/controls: "https://unpkg.com/@jupyter-widgets/controls@^1.5.0/dist/index"
            }
        });
    </script>

    <!-- Support for pandas tables styling -->
    <style>
    .dataframe {
        border-collapse: collapse;
        width: 100%;
        margin: 20px 0;
    }
    .dataframe th, .dataframe td {
        padding: 8px;
        text-align: left;
        border: 1px solid #ddd;
    }
    .dataframe th {
        background-color: #f2f2f2;
        font-weight: bold;
    }
    .dataframe tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    </style>
    """

    # Insert additional scripts before the closing </head> tag
    body = body.replace('</head>', f'{additional_scripts}\n</head>')

    # Support for plotly visualizations - ensure all plotly outputs are properly handled
    plotly_pattern = r'<div id="([a-f0-9-]+)".*?></div>\s*<script.*?Plotly.newPlot\('
    if re.search(plotly_pattern, body):
        # Add specific plotly initialization code if plotly outputs are detected
        plotly_init = """
        <script>
        // Ensure Plotly is properly initialized
        window.addEventListener('load', function() {
            // Find all divs that look like Plotly containers and re-render if needed
            const plotlyDivs = document.querySelectorAll('div[id^="plotly-"]');
            plotlyDivs.forEach(div => {
                if (div.data && div.layout) {
                    Plotly.newPlot(div.id, div.data, div.layout);
                }
            });
        });
        </script>
        """
        body = body.replace('</body>', f'{plotly_init}\n</body>')

    # Support for Matplotlib widgets
    if 'matplotlib.widgets' in body:
        # Add specific initialization for matplotlib widgets
        mpl_widget_init = """
        <script>
        // Initialize Matplotlib widget support
        window.addEventListener('load', function() {
            // Find all widget containers and activate
            document.querySelectorAll('.jupyter-widgets').forEach(function(el) {
                // This helps reactivate widgets that might not have initialized properly
                if (window.require && window.require.defined('@jupyter-widgets/controls')) {
                    window.require(['@jupyter-widgets/controls'], function(widgets) {
                        // Trigger any pending widget updates
                        if (widgets && widgets.WidgetManager) {
                            console.log('Attempting to reactivate widgets...');
                        }
                    });
                }
            });
        });
        </script>
        """
        body = body.replace('</body>', f'{mpl_widget_init}\n</body>')

    # Ensure Bokeh autoload scripts are properly processed
    bokeh_pattern = r'<script\s+src="data:application/javascript;charset=utf-8;base64,([^"]+)"></script>'
    matches = re.findall(bokeh_pattern, body)

    for match in matches:
        try:
            decoded_script = base64.b64decode(match).decode('utf-8')
            # Replace CDN references to ensure latest versions
            decoded_script = decoded_script.replace(
                'https://cdn.bokeh.org/bokeh/release/bokeh-',
                'https://cdn.bokeh.org/bokeh/release/bokeh-3.4.0.'
            )
            encoded_script = base64.b64encode(decoded_script.encode('utf-8')).decode('utf-8')
            body = body.replace(match, encoded_script)
        except Exception as e:
            print(f"Warning: Error processing Bokeh script: {e}")

    # Write the HTML file
    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(body)

    print(f"Notebook converted to HTML: {output_html_path}")
    return output_html_path


def batch_convert_notebooks(notebook_dir, output_dir=None, pattern="*.ipynb"):
    """
    Convert all notebooks in a directory matching the given pattern.

    Parameters:
    -----------
    notebook_dir : str
        Directory containing notebooks
    output_dir : str, optional
        Directory where HTML files will be saved (defaults to notebook_dir/html)
    pattern : str, default="*.ipynb"
        Pattern to match notebook files
    """
    if output_dir is None:
        output_dir = os.path.join(notebook_dir, 'html')

    os.makedirs(output_dir, exist_ok=True)

    notebook_paths = list(Path(notebook_dir).glob(pattern))

    if not notebook_paths:
        print(f"No notebooks found matching pattern '{pattern}' in {notebook_dir}")
        return

    print(f"Found {len(notebook_paths)} notebooks to convert")

    for notebook_path in notebook_paths:
        output_html_path = os.path.join(output_dir, f"{notebook_path.stem}.html")
        try:
            convert_notebook_to_html(str(notebook_path), output_html_path)
            print(f"Converted: {notebook_path.name} -> {output_html_path}")
        except Exception as e:
            print(f"Error converting {notebook_path.name}: {e}")

    print(f"Conversion complete. HTML files saved to {output_dir}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Convert Jupyter notebooks to HTML with visualization support')
    parser.add_argument('input', help='Input notebook file or directory')
    parser.add_argument('--output', '-o', help='Output HTML file or directory')
    parser.add_argument('--no-execute', action='store_true', help='Do not execute the notebook cells')
    parser.add_argument('--pattern', default='*.ipynb', help='Pattern for batch conversion (default: *.ipynb)')

    args = parser.parse_args()

    input_path = os.path.abspath(args.input)

    if os.path.isdir(input_path):
        # Batch convert notebooks in directory
        output_dir = args.output if args.output else os.path.join(input_path, 'html')
        batch_convert_notebooks(input_path, output_dir, args.pattern)
    else:
        # Convert single notebook
        if args.output:
            output_path = args.output
        else:
            output_dir = os.path.dirname(input_path)
            output_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(input_path))[0]}.html")

        convert_notebook_to_html(input_path, output_path, not args.no_execute)