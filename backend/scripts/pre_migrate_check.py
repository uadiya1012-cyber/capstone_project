#!/usr/bin/env python3
"""
Pre-migration check script
- Parses config/settings.py to extract INSTALLED_APPS
- Verifies local apps exist as packages
- Parses config/urls.py for include() modules and checks they exist
- Scans each app's views.py for render(template_name) calls and checks template files exist under templates/
Run from the backend directory.
"""
import ast
from pathlib import Path
import re
import sys

BASE = Path(__file__).resolve().parent
PROJECT = BASE.parent  # backend folder
CONFIG = PROJECT / 'config'
TEMPLATES_DIR = PROJECT / 'templates'

errors = []
notes = []

# Helper to parse a list assigned to a name in a module
def extract_list_from_file(file_path, variable_name):
    if not file_path.exists():
        return None
    src = file_path.read_text(encoding='utf-8')
    try:
        tree = ast.parse(src)
    except Exception as e:
        errors.append(f"Failed to parse {file_path}: {e}")
        return None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if getattr(target, 'id', None) == variable_name:
                    # node.value should be a List
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        items = []
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                items.append(elt.value)
                        return items
    return None

# 1) INSTALLED_APPS
settings_py = CONFIG / 'settings.py'
installed = extract_list_from_file(settings_py, 'INSTALLED_APPS')
if installed is None:
    errors.append('Could not find INSTALLED_APPS in config/settings.py')
else:
    notes.append(f'Found {len(installed)} entries in INSTALLED_APPS')
    # Check local app directories
    for app in installed:
        # Skip django builtins or dotted paths
        if app.startswith('django.') or '.' in app:
            continue
        app_path = PROJECT / app
        if not app_path.exists() or not (app_path / '__init__.py').exists():
            # Likely a third-party app installed in the environment (e.g. rest_framework)
            notes.append(f"App '{app}' is not a local package in the project (expected at {app_path}). If this is a third-party app make sure it's installed in your environment.")

# 2) includes in config/urls.py
urls_py = CONFIG / 'urls.py'
if not urls_py.exists():
    errors.append('config/urls.py not found')
else:
    src = urls_py.read_text(encoding='utf-8')
    includes = re.findall(r"include\(['\"]([^'\"]+)['\"]\)", src)
    notes.append(f'Found {len(includes)} include() entries in config/urls.py')
    for mod in includes:
        # check if module refers to 'app.urls' or direct module
        parts = mod.split('.')
        if parts[0] in ('django', 'rest_framework'):
            continue
        # check the first part is a local package
        pkg = PROJECT / parts[0]
        if not pkg.exists() or not (pkg / '__init__.py').exists():
            errors.append(f"Included module '{mod}' refers to missing package {pkg}")
        # if ends with urls, check urls.py exists inside app
        if parts[-1] == 'urls':
            urls_path = PROJECT / parts[0] / 'urls.py'
            if not urls_path.exists():
                errors.append(f"Included URLs module '{mod}' - expected file {urls_path} not found")

# 3) scan views for template paths used in render() using AST (avoid matching dict keys)
for app_dir in PROJECT.iterdir():
    if not app_dir.is_dir():
        continue
    if (app_dir / '__init__.py').exists():
        views_py = app_dir / 'views.py'
        if views_py.exists():
            src = views_py.read_text(encoding='utf-8')
            try:
                tree = ast.parse(src)
            except Exception as e:
                errors.append(f"Failed to parse {views_py}: {e}")
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    # function name can be 'render' or something.render
                    func = node.func
                    func_name = None
                    if isinstance(func, ast.Name):
                        func_name = func.id
                    elif isinstance(func, ast.Attribute):
                        func_name = func.attr
                    if func_name != 'render':
                        continue
                    # render(request, 'template.html', ...)
                    if len(node.args) >= 2:
                        tpl_arg = node.args[1]
                        if isinstance(tpl_arg, ast.Constant) and isinstance(tpl_arg.value, str):
                            tpl = tpl_arg.value
                            candidates = []
                            if tpl.startswith(app_dir.name + '/'):
                                candidates.append(TEMPLATES_DIR / tpl)
                            else:
                                candidates.append(TEMPLATES_DIR / app_dir.name / tpl)
                                candidates.append(TEMPLATES_DIR / tpl)
                            found = False
                            for c in candidates:
                                if c.exists():
                                    found = True
                                    break
                            if not found:
                                errors.append(f"Template '{tpl}' referenced in {views_py} not found. Checked: {', '.join(str(x) for x in candidates)}")

# Summarize
print('\nPre-migration check report')
print('Project dir:', PROJECT)
print('Templates dir:', TEMPLATES_DIR)
print('')
if notes:
    print('Notes:')
    for n in notes:
        print(' -', n)
    print('')
if errors:
    print('Errors (please fix before running makemigrations/migrate):')
    for e in errors:
        print(' -', e)
    sys.exit(2)
else:
    print('No issues found. You can proceed with makemigrations and migrate.')
    sys.exit(0)
