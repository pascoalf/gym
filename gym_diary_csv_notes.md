# Gym diary CSV reference

`gym_diary.csv` contains 95 rows across six sessions. Each row is one recorded set, including one explicitly skipped set. Exercise and set order follow the original diary; repeated set labels were renumbered sequentially.

## Columns

| Column | Meaning |
|---|---|
| date | ISO date (YYYY-MM-DD). Year 2026 assumed from final entry; 21 November corrected to 21 October by the author. |
| exercise | Consistent exercise identifier. Cable exercise names are combined as confirmed by the author. |
| exercise_order | Position of the exercise within that session. |
| set_number | Set within the exercise, starting at 1. |
| target_reps | Planned repetitions per set, not a claim of completion. |
| weight_kg | Recorded load in kg. NA for skipped sets or ambiguous changing loads. |
| weight_type | assistance for assisted pull-ups; external_load otherwise. Lower pull-up assistance means greater difficulty. |
| performed | 1 = recorded as performed; 0 = explicitly skipped. |
| reps_completed | Completed repetitions where a single count is available; NA when missing or only side-specific. |
| reps_left, reps_right | Completed repetitions for separately documented arms. Do not add these to reps_completed. |
| difficulty | Ordinal rating: 1 = easy, 2 = moderate, 3 = hard. NA if absent or recorded separately by side. |
| difficulty_left, difficulty_right | Same rating scale for separately documented arms. |
| reps_inferred | 1 if a populated repetition count was inferred; 0 otherwise, including when repetition counts are missing. |
| target_reps_inferred | 1 if the target was inferred from other sessions (19 October cable extensions). |
| notes | Context, uncertainty, and corrections. NA when there is no note. |

## Missing data and interpretation

- NA is a missing or uncertain value, never zero. Unreported actual reps remain NA even if no failure was mentioned. This limits volume calculations until more information is available.
- Failing on rep 4 is interpreted as 3 completed reps; failing on rep 3 as 2. Failing the last of 12 reps is interpreted as 11 completed. These counts are flagged as inferred.
- Right-arm curl counts on 10 October remain NA because the wording is ambiguous. The original wording is described in notes.
- The ambiguous second pull-up set on 17 October has NA for both load and completed reps; its possible 7-to-14 kg assistance change is preserved in notes.
- Three curl sets on 17 October are retained despite the heading specifying two.
- Side-specific ratings include a few contextual interpretations, identified in notes. Unilateral versus bilateral execution is otherwise unspecified; later entries are not assumed to document each arm separately.
- Loads are recorded as written, including 26.5 kg on 21 October. Curl loads are likely per dumbbell, but the notes do not establish equipment or load conventions consistently enough to calculate combined loads. Machine loads are machine settings; cross-exercise comparisons need care.
- Original notes remain in `gym_diary.txt`; the readable version is `gym_diary_clean.md`. No plots or derived performance estimates are included.
