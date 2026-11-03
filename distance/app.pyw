"""
Distance folder entry point - forwards directly to root master application.
"""
import sys
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
root_app = os.path.join(root_dir, "app.pyw")

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

if os.path.exists(root_app):
    with open(root_app, "rb") as f:
        exec(compile(f.read(), root_app, 'exec'))
