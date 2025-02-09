{% extends 'classic/index.html.j2' %}

{% block header %}
{{ super() }}

<!-- Plotly.js -->
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>

<!-- Custom Styling -->
<style>
    .jp-Notebook {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    .plotly-graph-div {
        margin: 20px 0;
        border: 1px solid #eee;
        border-radius: 5px;
    }
    .code_cell {
        background: #f8f9fa;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
</style>
{% endblock header %}