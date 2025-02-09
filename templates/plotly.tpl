{% extends 'classic.tpl' %}

{% block header %}
{{ super() }}
{{ plotly_header | safe }}
{% endblock header %}
{% block body %}
{{ super() }}