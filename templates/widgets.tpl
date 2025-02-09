{%- extends 'lab.tpl' -%}

{%- block header -%}
{{ super() }}

<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.4/require.min.js"></script>
<script src="https://unpkg.com/@jupyter-widgets/html-manager@^0.20.0/dist/embed-amd.js"></script>

{%- endblock header -%}