# Gym diary progress plots

Run from the command line (Python 3.10+):

```bash
conda create -n gym -c conda-forge python=3.12 matplotlib
conda activate gym
python plot_progress.py
```

Outputs go to `figures/`: `weight_progress.png`, a shareable `weight_progress.pdf`, and `daily_summary.csv` containing the plotted statistics. Rerunning replaces these generated outputs.

Append new sessions to `gym_diary.csv` using the same columns and exercise IDs, then rerun the last command. Dates must use YYYY-MM-DD. See `gym_diary_csv_notes.md` for column definitions. New exercise IDs receive their own panels automatically.

Optional paths:

```bash
python plot_progress.py --input gym_diary.csv --output-dir figures
```

Each point is mean recorded weight across performed sets of one exercise on one date. Bars show sample standard deviation (n−1 denominator), omitted for a single set. Set weights are treated as descriptive replicates, even when deliberately increasing within a session; these bars are not confidence intervals. `n` is the number of sets with known weight. Skipped sets and ambiguous weights are excluded. Unknown completed reps are not imputed or used to weight averages.

Color is the mean available difficulty rating (easy=1, moderate=2, hard=3); these are ordinal ratings, not a calibrated effort scale. A set with separate arm ratings contributes their mean, so it counts once. Missing difficulty is ignored; an entirely unrated day is gray. `n_sets_with_difficulty` in the summary shows coverage. For assisted pull-ups, the plotted weight is assistance: a decrease means less help. Other weights retain the original equipment conventions; equipment changes and changes in reps or form should be considered with your PT.

## Recorded rep shortfalls and failure

Diamond markers identify days with at least one set below its target reps or an explicit failure note. The `!2` annotation means two affected sets, not two missing reps. Side-specific shortfalls count a set once. Circles mean no shortfall was recorded; missing reps never imply completion. Inferred completed counts from the diary are included.

Failure flags include all performed sets, including the ambiguous 17 October pull-up set whose weight is unknown. Weight means, SD, and color still use only sets with known weights. The summary adds `n_sets_performed`, `n_sets_with_rep_counts`, `n_sets_below_target`, and `n_sets_with_shortfall_or_failure` so coverage and exclusions are visible.

For future explicit failure entries, you may add an optional `failure_reported` column to the input CSV (1=yes, 0=no, NA=unknown). Otherwise the script recognizes the words “failed”, “failure”, or “falhei” in notes. Use that structured column for new data if wording becomes more varied. A numeric rep shortfall is flagged independently of this field; stopping below target does not always mean muscular failure.
