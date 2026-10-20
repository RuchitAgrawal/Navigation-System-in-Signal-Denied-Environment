#!/usr/bin/env python
# scripts/run_scale_analysis.py -- CLI for scale drift analysis
import argparse, sys
from pathlib import Path
sys.path.insert(0, '.')
from experiments.runner import run_experiment, load_yaml
from experiments.scale_analysis import run_scale_analysis
from src.datasets.icl_nuim import load_icl_nuim_from_config
\n\ndef parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('-e', '--experiment', required=True)
    p.add_argument('-d', '--dataset', required=True)
    p.add_argument('-o', '--output', default='results')
    return p.parse_args()
\n\ndef main():
    args = parse_args()
    summary = run_experiment(args.experiment, args.dataset, args.output)
    print('Scale analysis: run separately after loading trajectory')
    print(f'  Experiment: {summary[\
