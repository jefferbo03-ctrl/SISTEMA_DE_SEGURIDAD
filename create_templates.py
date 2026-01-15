#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear todos los templates HTML con la codificación correcta
"""
import os

# Crear carpeta templates si no existe
os.makedirs('templates', exist_ok=True)

# Template: base.html
base_html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Sistema de Alerta Temprana{% endblock %}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
            color: white;
            padding: 25px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .header h1 {
            font-size: 24px;
            font-weight: 600;
        }

        .user-info {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .user-info span {
            font-size: 14px;
        }

        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s;
        }

        .btn-primary {
            background: #5a67d8;
            color: white;
        }

        .btn-primary:hover {
            background: #4c51bf;
        }

        .btn-success {
            background: #48bb78;
            color: white;
        }

        .btn-success:hover {
            background: #38a169;
        }

        .btn-danger {
            background: #f56565;
            color: white;
        }

        .btn-danger:hover {
            background: #e53e3e;
        }

        .btn-secondary {
            background: #718096;
            color: white;
        }

        .btn-secondary:hover {
            background: #4a5568;
        }

        .nav {
            background: #f7fafc;
            padding: 15px 30px;
            border-bottom: 2px solid #e2e8f0;
            display: flex;
            gap: 15px;
        }

        .nav a {
            text-decoration: none;
            color: #4a5568;
            padding: 8px 15px;
            border-radius: 5px;
            transition: all 0.3s;
        }

        .nav a:hover, .nav a.active {
            background: #5a67d8;
            color: white;
        }

        .content {
            padding: 30px;
        }

        .flash-messages {
            margin-bottom: 20px;
        }

        .flash {
            padding: 15px 20px;
            border-radius: 5px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .flash.ok {
            background: #c6f6d5;
            color: #22543d;
            border-left: 4px solid #48bb78;
        }

        .flash.warn {
            background: #feebc8;
            color: #744210;
            border-left: 4px solid #ed8936;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        table thead {
            background: #edf2f7;
        }

        table th {
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #2d3748;
            border-bottom: 2px solid #cbd5e0;
        }

        table td {
            padding: 12px;
            border-bottom: 1px solid #e2e8f0;
        }

        table tr:hover {
            background: #f7fafc;
        }

        .badge {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            display: inline-block;
        }

        .badge-danger {
            background: #fed7d7;
            color: #c53030;
        }

        .badge-warning {
            background: #feebc8;
            color: #c05621;
        }

        .badge-success {
            background: #c6f6d5;
            color: #22543d;
        }

        .badge-info {
            background: #bee3f8;
            color: #2c5282;
        }

        .alert-icon {
            display: inline-block;
            width: 20px;
            height: 20px;
            line-height: 20px;
            text-align: center;
            background: #ed8936;
            color: white;
            border-radius: 50%;
            font-size: 12px;
            font-weight: bold;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #2d3748;
        }

        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #cbd5e0;
            border-radius: 5px;
            font-size: 14px;
        }

        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #5a67d8;
            box-shadow: 0 0 0 3px rgba(90, 103, 216, 0.1);
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }

        .stat-card h3 {
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 10px;
        }

        .stat-card .number {
            font-size: 32px;
            font-weight: bold;
        }

        .search-bar {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }

        .search-bar input {
            flex: 1;
            padding: 10px 15px;
            border: 1px solid #cbd5e0;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        {% raw %}{% if session.user_id %}{% endraw %}
        <div class="header">
            <h1>Sistema de Alerta Temprana</h1>
            <div class="user-info">
                <span>👤 {% raw %}{{ session.username }}{% endraw %} ({% raw %}{{ session.role }}{% endraw %})</span>
                <a href="{% raw %}{{ url_for('logout') }}{% endraw %}" class="btn btn-secondary">Cerrar Sesión</a>
            </div>
        </div>

        <div class="nav">
            <a href="{% raw %}{{ url_for('index') }}{% endraw %}" class="{% raw %}{{ 'active' if request.endpoint == 'index' else '' }}{% endraw %}">🏠 Inicio</a>
            {% raw %}{% if session.role in ['admin', 'superuser'] %}{% endraw %}
            <a href="{% raw %}{{ url_for('add') }}{% endraw %}" class="{% raw %}{{ 'active' if request.endpoint == 'add' else '' }}{% endraw %}">➕ Añadir Persona</a>
            <a href="{% raw %}{{ url_for('upload') }}{% endraw %}" class="{% raw %}{{ 'active' if request.endpoint == 'upload' else '' }}{% endraw %}">📤 Cargar Excel</a>
            <a href="{% raw %}{{ url_for('users') }}{% endraw %}" class="{% raw %}{{ 'active' if request.endpoint == 'users' else '' }}{% endraw %}">👥 Usuarios</a>
            <a href="{% raw %}{{ url_for('settings') }}{% endraw %}" class="{% raw %}{{ 'active' if request.endpoint == 'settings' else '' }}{% endraw %}">⚙️ Configuración</a>
            {% raw %}{% endif %}{% endraw %}
        </div>
        {% raw %}{% endif %}{% endraw %}

        <div class="content">
            {% raw %}{% if get_flashed_messages() %}{% endraw %}
            <div class="flash-messages">
                {% raw %}{% for message in get_flashed_messages(with_categories=true) %}{% endraw %}
                <div class="flash {% raw %}{{ message[0] }}{% endraw %}">
                    {% raw %}{% if message[0] == 'ok' %}{% endraw %}✓{% raw %}{% else %}{% endraw %}⚠{% raw %}{% endif %}{% endraw %}
                    {% raw %}{{ message[1] }}{% endraw %}
                </div>
                {% raw %}{% endfor %}{% endraw %}
            </div>
            {% raw %}{% endif %}{% endraw %}

            {% raw %}{% block content %}{% endblock %}{% endraw %}
        </div>
    </div>

    {% raw %}{% block scripts %}{% endblock %}{% endraw %}
</body>
</html>"""

# Template: add_edit_user.html
add_edit_user_html = """{% raw %}{% extends "base.html" %}

{% block content %}{% endraw %}
<h2 style="margin-bottom: 20px; color: #2d3748;">
    {% raw %}{% if user %}{% endraw %}Editar Usuario{% raw %}{% else %}{% endraw %}Añadir Nuevo Usuario{% raw %}{% endif %}{% endraw %}
</h2>

<div style="max-width: 600px; margin: 0 auto;">
    <form method="POST" style="background: #f7fafc; padding: 30px; border-radius: 10px;">
        <div class="form-group">
            <label for="username">Nombre de Usuario *</label>
            <input type="text" id="username" name="username" value="{% raw %}{% if user %}{{ user.username }}{% endif %}{% endraw %}" required>
        </div>

        <div class="form-group">
            <label for="email">Email</label>
            <input type="email" id="email" name="email" value="{% raw %}{% if user %}{{ user.email }}{% endif %}{% endraw %}">
        </div>

        <div class="form-group">
            <label for="password">Contraseña {% raw %}{% if user %}{% endraw %}(dejar en blanco para no cambiar){% raw %}{% else %}{% endraw %}*{% raw %}{% endif %}{% endraw %}</label>
            <input type="password" id="password" name="password" {% raw %}{% if not user %}{% endraw %}required{% raw %}{% endif %}{% endraw %}>
        </div>

        <div class="form-group">
            <label for="role">Rol *</label>
            <select id="role" name="role" required>
                <option value="user" {% raw %}{% if user and user.role == 'user' %}{% endraw %}selected{% raw %}{% endif %}{% endraw %}>Usuario</option>
                <option value="admin" {% raw %}{% if user and user.role == 'admin' %}{% endraw %}selected{% raw %}{% endif %}{% endraw %}>Admin</option>
                <option value="superuser" {% raw %}{% if user and user.role == 'superuser' %}{% endraw %}selected{% raw %}{% endif %}{% endraw %}>Super Usuario</option>
            </select>
        </div>

        <div style="margin-top: 30px; display: flex; gap: 10px; justify-content: flex-end;">
            <a href="{% raw %}{{ url_for('users') }}{% endraw %}" class="btn btn-secondary">Cancelar</a>
            <button type="submit" class="btn btn-success">
                {% raw %}{% if user %}{% endraw %}💾 Guardar Cambios{% raw %}{% else %}{% endraw %}✅ Crear Usuario{% raw %}{% endif %}{% endraw %}
            </button>
        </div>
    </form>

    <div style="margin-top: 20px; padding: 15px; background: #bee3f8; border-left: 4px solid #3182ce; border-radius: 5px;">
        <p style="color: #2c5282; font-size: 14px;">
            <strong>Nota:</strong> Los campos marcados con (*) son obligatorios.
        </p>
    </div>
</div>
{% raw %}{% endblock %}{% endraw %}"""

templates = {
    'base.html': base_html,
    'add_edit_user.html': add_edit_user_html
}

print("🔧 Creando archivos template...\n")

for filename, content in templates.items():
    filepath = os.path.join('templates', filename)
    # Remover {% raw %} y {% endraw %} antes de escribir
    content = content.replace('{% raw %}', '').replace('{% endraw %}', '')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Creado: {filepath}")

print("\n✅ Templates creados correctamente!")
print("\nAhora ejecuta: python app.py")
