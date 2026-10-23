#!/usr/bin/env python3
# DINERO render con voz gratis (edge-tts) generada aqui, escena por escena.
# Si el job ya trae audio_b64 se comporta igual que render_dinero.py.
import asyncio
import base64
import json
import os
import sys

import render as R
import render_dinero as D

VOZ = 'es-MX-JorgeNeural'
RATE = '+6%'
GAP = 0.18


async def _tts(texto, voz, rate, path):
    import edge_tts
    await edge_tts.Communicate(texto, voz, rate=rate).save(path)


def generar(job, work):
    voz = job.get('voz_edge') or VOZ
    os.makedirs(work, exist_ok=True)
    partes, durs = [], []
    for i, s in enumerate(job['escenas']):
        p = '%s/e%02d.mp3' % (work, i)
        ok = False
        for intento in range(3):
            try:
                asyncio.run(_tts(' '.join(str(s['texto']).split()), voz, RATE, p))
                if os.path.getsize(p) > 1000:
                    ok = True
                    break
            except Exception as e:
                print('edge-tts fallo escena %d intento %d: %s' % (i + 1, intento + 1, e), file=sys.stderr)
        if not ok:
            raise SystemExit('DINERO: edge-tts no pudo generar la voz de la escena %d' % (i + 1))
        w = '%s/e%02d.wav' % (work, i)
        R.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', p, '-af', 'apad=pad_dur=%.2f,aresample=44100' % GAP, '-ac', '1', w])
        partes.append(w)
        durs.append(R.duration(w))
    lst = work + '/voz_list.txt'
    with open(lst, 'w') as f:
        for w in partes:
            f.write('file ' + os.path.basename(w) + chr(10))
    mp3 = work + '/voz_edge.mp3'
    R.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c:a', 'libmp3lame', '-q:a', '2', mp3])
    return mp3, durs


def main():
    job_path, out_path = sys.argv[1], sys.argv[2]
    with open(job_path, encoding='utf-8') as f:
        job = json.load(f)
    if job.get('audio_b64') or not job.get('escenas'):
        return D.main()
    mp3, durs = generar(job, 'work_voz')
    textos = [s.get('texto', '') for s in job['escenas']]
    mapa = {}
    for t, d in zip(textos, durs):
        mapa[t] = d
    mapa[textos[-1]] = mapa[textos[-1]] + R.TAIL
    R.peso = lambda texto: mapa.get(texto, 3.0)
    with open(mp3, 'rb') as f:
        job['audio_b64'] = base64.b64encode(f.read()).decode()
    job['velocidad'] = 1.0
    with open('job_edge.json', 'w', encoding='utf-8') as f:
        json.dump(job, f)
    sys.argv = [sys.argv[0], 'job_edge.json', out_path]
    D.main()


if __name__ == '__main__':
    main()
