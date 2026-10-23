import os
import runpy
os.environ.setdefault('RENDER_SCRIPT', 'render_dinero')
runpy.run_path('voz_edge.py', run_name='__main__')

