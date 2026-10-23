import json
import os
import sys

from motion6 import *
from motion6 import frame, phrases_de, PLANTILLAS, PALETA, build_sfx, SR, W, H, FPS


def _director():
    # el director arma solo las escenas que llegan con texto o con guion
    try:
        p = sys.argv[1]
        if not (p.endswith('.json') and os.path.exists(p)):
            return
        job = json.load(open(p, encoding='utf-8'))
        import director
        job['escenas'] = director.autocompletar(job.get('escenas'), job.get('guion'), job.get('opciones'))
        json.dump(job, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    except Exception as e:
        print('director fallo', e, file=sys.stderr)


_director()

