#!/usr/bin/env python3
"""
Phase 0 embedding script (staging). Usage:
  python phase0_embed.py --input-dir <session_folder> --outdir <out_dir> [--batch-size 6] [--to-qdrant]

Notes:
- Designed for offline, zero-telemetry embedding using sentence-transformers.
- Does not run automatically in this session; it's a prepared tool for Copilot / operator.
"""

import os
import sys
import json
import argparse
from pathlib import Path

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None


def check_memory_threshold(target_mb=1200):
    """Return True if available memory (MemAvailable) > target_mb"""
    try:
        with open('/proc/meminfo') as f:
            info = f.read()
        for line in info.splitlines():
            if line.startswith('MemAvailable:'):
                parts = line.split()
                kb = int(parts[1])
                mb = kb // 1024
                return mb > target_mb
    except Exception:
        return True  # assume ok if cannot read
    return False


def load_files(input_dir):
    p = Path(input_dir)
    files = sorted([str(x) for x in p.glob('*.md')])
    docs = []
    for f in files:
        text = Path(f).read_text(encoding='utf-8')
        docs.append({'path': f, 'text': text})
    return docs


def embed_batch(model, docs):
    texts = [d['text'] for d in docs]
    vectors = model.encode(texts, show_progress_bar=False)
    for i, d in enumerate(docs):
        d['vector'] = vectors[i].tolist()
    return docs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', required=True)
    parser.add_argument('--outdir', required=True)
    parser.add_argument('--batch-size', type=int, default=6)
    parser.add_argument('--model-name', default='sentence-transformers/multilingual-mpnet-base-v2')
    parser.add_argument('--to-qdrant', action='store_true')
    args = parser.parse_args()

    if not check_memory_threshold(target_mb=1200):
        print('ERROR: Available memory below safe threshold for embedding batches. Increase swap/zRAM or reduce batch size.')
        sys.exit(1)

    docs = load_files(args.input_dir)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if SentenceTransformer is None:
        print('WARNING: sentence-transformers not installed. The script is staged and ready to run when the environment is prepared.')
        # Write a manifest and exit
        manifest = {'files': [d['path'] for d in docs], 'count': len(docs)}
        outdir.joinpath('phase0_embed_manifest.json').write_text(json.dumps(manifest, indent=2))
        print('Wrote manifest to', outdir.joinpath('phase0_embed_manifest.json'))
        return

    model = SentenceTransformer(args.model_name)

    batches = [docs[i:i+args.batch_size] for i in range(0, len(docs), args.batch_size)]
    all_vectors = []
    for idx, batch in enumerate(batches, start=1):
        print(f'Embedding batch {idx}/{len(batches)} (size {len(batch)})')
        batch_with_vectors = embed_batch(model, batch)
        # Save batch vectors to disk as JSONL (staging)
        out_file = outdir.joinpath(f'batch_{idx}_vectors.jsonl')
        with open(out_file, 'w', encoding='utf-8') as fh:
            for d in batch_with_vectors:
                record = {'path': d['path'], 'vector': d['vector']}
                fh.write(json.dumps(record) + '\n')
        all_vectors.append(str(out_file))

    # Write summary
    summary = {'batches': len(batches), 'files': len(docs), 'batches_files': all_vectors}
    outdir.joinpath('phase0_embed_summary.json').write_text(json.dumps(summary, indent=2))
    print('Embedding staged. Summary written to', outdir.joinpath('phase0_embed_summary.json'))


if __name__ == '__main__':
    main()
