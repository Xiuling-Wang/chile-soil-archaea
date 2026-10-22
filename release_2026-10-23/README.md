# Submitted-figure layout entry — 23 October 2026

The submitted paper has **Figures 1–4 and S1–S6**. This directory makes the
final author-layout workflow explicit without rerunning statistical models.

```sh
python -m pip install PyMuPDF
python release_2026-10-23/render_layouts.py
python release_2026-10-23/render_s6.py
```

Outputs are written only to `release_2026-10-23/output/`. Neither command
changes an input PDF, the paper or the existing R analysis files.

`render_layouts.py` is the portable adaptation of the established vector
recomposition recipe. It assembles nine figures from frozen pre-layout PDFs
using measured clip/translation coordinates. It is a layout-reproduction
entry, not a raw-read or statistical pipeline, and does not certify that every
recomposed panel is pixel-identical to the author's final artwork.

`render_s6.py` separately implements the author's final choice for Fig. S6:
horizontal site/pool headings with light-grey strips. The earlier generic
recipe's S6 branch is deliberately excluded because it described a superseded
rotated-header layout. The body of the supplied parent PDF is preserved as
vector artwork; no bubble value or taxon label is recomputed.

`inputs/S6_site_pool_values.csv` supplies the 42-ASV × four-site × two-pool
display values. This is a functional/taxonomic context display, not a direct
demonstration of methanogenesis or activity. Sample-level analysis and
inference remain in the root analysis snapshot.

`INPUT_SHA256.json` fingerprints the supplied inputs;
`SUBMITTED_FIGURE_SHA256.json` fingerprints the untouched submitted originals
for provenance. PDF byte hashes can differ with metadata or renderer versions.
The current submitted files remain the authority for final appearance.

This addition does not include manuscripts, private correspondence, personal
filesystem paths, isolate materials or raw sequence data. No new licence is
assigned. The prior code and data history is preserved.
