#!/usr/bin/env python3
"""Plot daily set-weight means, sample SD, and recorded difficulty."""
import argparse
import csv
from collections import defaultdict
from datetime import date
from pathlib import Path
from statistics import mean, stdev
import os
import re

os.environ.setdefault('MPLCONFIGDIR', '/tmp/gym-matplotlib')
os.environ.setdefault('XDG_CACHE_HOME', '/tmp/gym-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import Normalize, LinearSegmentedColormap
from matplotlib.lines import Line2D

BASE = Path(__file__).resolve().parent


def number(value):
    return None if value in (None, '', 'NA') else float(value)


def summarize(path):
    groups = defaultdict(list)
    with path.open(newline='', encoding='utf-8') as stream:
        for row in csv.DictReader(stream):
            if number(row['performed']) != 1:
                continue
            date.fromisoformat(row['date'])
            groups[(row['exercise'], row['date'], row['weight_type'])].append(row)
    result = []
    for (exercise, day, kind), sets in sorted(groups.items()):
        weighted_sets = [s for s in sets if number(s['weight_kg']) is not None]
        weights = [number(s['weight_kg']) for s in weighted_sets]
        if not weights:
            continue
        shortfalls = 0
        affected = 0
        known_counts = 0
        for entry in sets:
            counts = [number(entry.get(k)) for k in ('reps_completed', 'reps_left', 'reps_right')]
            counts = [v for v in counts if v is not None]
            target = number(entry.get('target_reps'))
            known_counts += bool(counts)
            short = target is not None and any(v < target for v in counts)
            shortfalls += short
            # Optional explicit field takes precedence over searching legacy notes.
            explicit = number(entry.get('failure_reported'))
            failure = explicit == 1 if explicit is not None else bool(
                re.search(r'\b(failed|failure|falhei)\b', entry.get('notes', ''), re.I))
            affected += bool(short or failure)
        ratings = []
        for s in weighted_sets:
            rating = number(s['difficulty'])
            if rating is None:
                sides = [number(s[k]) for k in ('difficulty_left', 'difficulty_right')]
                sides = [v for v in sides if v is not None]
                rating = mean(sides) if sides else None
            if rating is not None:
                if not 1 <= rating <= 3:
                    raise ValueError(f'Difficulty outside 1–3: {exercise}, {day}')
                ratings.append(rating)
        result.append(dict(exercise=exercise, date=day, weight_type=kind,
                           n_sets=len(weights), mean_weight_kg=mean(weights),
                           sd_weight_kg=stdev(weights) if len(weights)>1 else None,
                           mean_difficulty=mean(ratings) if ratings else None,
                           n_sets_with_difficulty=len(ratings),
                           n_sets_performed=len(sets), n_sets_with_rep_counts=known_counts,
                           n_sets_below_target=shortfalls,
                           n_sets_with_shortfall_or_failure=affected))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=BASE/'gym_diary.csv')
    parser.add_argument('--output-dir', type=Path, default=BASE/'figures')
    args = parser.parse_args()
    rows = summarize(args.input)
    if not rows:
        parser.error('No performed sets with recorded weights found.')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (args.output_dir/'daily_summary.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows({k: 'NA' if v is None else v for k,v in r.items()} for r in rows)
    exercises = sorted({r['exercise'] for r in rows})
    cols = min(3, len(exercises))
    fig, axes = plt.subplots((len(exercises)+cols-1)//cols, cols,
                             figsize=(14, 8.5), squeeze=False)
    cmap = LinearSegmentedColormap.from_list('effort', ['#16827c', '#e6ad36', '#b33b55'])
    norm = Normalize(1, 3)
    plt.rcParams['pdf.fonttype'] = 42
    for ax, exercise in zip(axes.flat, exercises):
        series = [r for r in rows if r['exercise']==exercise]
        kinds = {r['weight_type'] for r in series}
        if len(kinds)!=1:
            raise ValueError(f'Mixed weight types for {exercise}; use separate exercise IDs.')
        days = [date.fromisoformat(r['date']) for r in series]
        weights = [r['mean_weight_kg'] for r in series]
        ax.plot(days, weights, color='#a1a9b2', linewidth=1.4, zorder=1)
        for day, r in zip(days, series):
            color = '#929aa5' if r['mean_difficulty'] is None else cmap(norm(r['mean_difficulty']))
            if r['sd_weight_kg'] is not None:
                ax.errorbar(day, r['mean_weight_kg'], yerr=r['sd_weight_kg'],
                            fmt='none', ecolor='#647282', capsize=4, linewidth=1.4, zorder=2)
            affected = r['n_sets_with_shortfall_or_failure']
            ax.scatter(day, r['mean_weight_kg'], color=color,
                       marker='D' if affected else 'o',
                       edgecolor='#263442' if affected else 'white',
                       linewidth=1, s=85, zorder=3)
            label = f"n={r['n_sets']}" + (f"\n!{affected}" if affected else '')
            ax.annotate(label, (mdates.date2num(day), r['mean_weight_kg']),
                        xytext=(0, 12), textcoords='offset points', ha='center', fontsize=8,
                        color='#525e6b')
        assistance = kinds == {'assistance'}
        ax.set_title(exercise.replace('_', ' ').title() + (' ↓' if assistance else ''),
                     fontsize=12, fontweight='bold', loc='left')
        ax.set_ylabel('Assistance (kg) · lower is harder' if assistance else 'Recorded load (kg)')
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=3, maxticks=5))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b\n%Y'))
        ax.grid(axis='y', alpha=.18)
        ax.spines[['top','right']].set_visible(False)
        ax.margins(x=.12, y=.30)
        ax.tick_params(labelsize=9)
    for ax in list(axes.flat)[len(exercises):]:
        ax.set_visible(False)
    fig.suptitle('Gym diary · weight over time', fontsize=21, fontweight='bold', x=.06, ha='left')
    fig.text(.06, .925, 'Points: daily mean   |   Bars: ±1 sample SD   |   n: weighted sets   |   !: sets with rep shortfall / failure', fontsize=11)
    fig.subplots_adjust(left=.07, right=.94, bottom=.17, top=.84, wspace=.36, hspace=.48)
    cax = fig.add_axes([.27, .105, .36, .018])
    bar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax, orientation='horizontal')
    bar.set_ticks([1,2,3], labels=['Easy (1)', 'Moderate (2)', 'Hard (3)'])
    bar.set_label('Mean recorded difficulty (ordinal ratings)', fontsize=9)
    fig.legend(handles=[Line2D([],[],marker='o',linestyle='',color='#929aa5', label='Difficulty unrecorded'),
                        Line2D([],[],marker='D',linestyle='',color='#263442', markerfacecolor='white',
                               label='Rep shortfall / failure recorded')],
               loc='lower right', bbox_to_anchor=(.95,.065), frameon=False, fontsize=9)
    fig.text(.06, .018, 'Weight statistics exclude skipped sets and unknown weights; failure flags include performed sets with unknown weight.\n'
             'Circles mean no shortfall recorded, not confirmed completion. SD shows set variation. '
             'Lower pull-up assistance is harder.',
             fontsize=8, color='#525e6b')
    for extension in ('png', 'pdf'):
        fig.savefig(args.output_dir/f'weight_progress.{extension}', dpi=200, facecolor='white')
    plt.close(fig)
    print(f'Saved PNG, PDF and daily_summary.csv in {args.output_dir.resolve()}')


if __name__ == '__main__':
    main()
