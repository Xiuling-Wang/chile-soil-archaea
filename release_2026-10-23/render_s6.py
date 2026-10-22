#!/usr/bin/env python3
"""Fig. S6 column headers: replace the rotated "AZ  iDNA" labels with a horizontal two-level header.

Author, 2026-09-07: the rotated headers are ugly and there is plenty of horizontal room; the site colours are
already in the Sites legend, so the text above may be redundant; and in the companion bacterial project a DNA
pool is sometimes marked with a light grey background and the sites separated by rules.

House precedent — the bacterial paper's own bubble matrix (STOTEN mmc1, image7) uses exactly this figure type
and gives it a two-level HORIZONTAL header: the site code (bold, grey, larger) centred over the site's pair of
columns, and iDNA / eDNA (smaller) centred under it over each column. Its diversity figure (image8) is where
the light grey facet strips appear. Both candidates below follow that precedent:

  C1  plain horizontal two-level header + thin rules between sites          (= image7)
  C2  the same two rows drawn as light grey facet strips                    (= image7 + image8's strips)

Nothing but the header is touched: the panel, bubbles, row labels, legends and caption are stamped across as
vector, unchanged, and only moved up by the height the rotated labels no longer need. The site codes are kept
in both candidates because a column in which no ASV was detected carries no bubble, so it cannot be identified
from the colour legend alone.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path

import pymupdf as f

R = Path(__file__).resolve().parent
SRC = R / 'inputs/FigS6_rotated_header.pdf'
OUT = R / 'output'

# geometry measured from the figure itself
PANEL = f.Rect(141.0, 54.49, 528.04, 375.59)
COL0, COLW, NCOL = 169.3, 47.2, 8                  # centre of column 1, column pitch, column count
SITES = ["AZ", "SG", "LC", "NA"]
POOLS = ["iDNA", "eDNA"]
TRIM = 25.0                                         # height the rotated labels no longer need

ROWLAB = {"text": "ASV ID and taxon", "x": 72.35, "font": "hebo", "size": 8.0, "col": (0.149, 0.149, 0.149)}
SITE_STYLE = {"font": "hebo", "size": 8.4, "col": (0.149, 0.149, 0.149)}
POOL_STYLE = {"font": "helv", "size": 7.6, "col": (0.302, 0.302, 0.302)}
RULE = (0.78, 0.78, 0.78)
STRIP = (0.898, 0.898, 0.898)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def centre(i: int) -> float:
    return COL0 + COLW * i


def build(strips: bool, dest: Path) -> dict:
    src = f.open(SRC)
    sp = src[0]
    rot = [s_["text"].strip() for b in sp.get_text("dict")["blocks"] for l in b.get("lines", [])
           for s_ in l["spans"] if s_["text"].strip() and tuple(round(v) for v in l["dir"]) == (0, -1)]
    assert len(rot) == 8, f"expected the 8 rotated column headers in the parent figure, found {rot}"
    h2 = sp.rect.height - TRIM
    doc = f.open()
    p = doc.new_page(width=sp.rect.width, height=h2)

    # everything from the panel down, moved up by TRIM; vector, untouched
    body = f.Rect(0, PANEL.y0, sp.rect.width, sp.rect.height)
    p.show_pdf_page(body + f.Rect(0, -TRIM, 0, -TRIM), src, 0, clip=body)

    top = PANEL.y0 - TRIM                            # new panel top
    pool_base = top - 4.5
    site_base = pool_base - 11.5

    if strips:
        for s in range(4):                           # one strip per site, spanning its two columns
            x0 = centre(2 * s) - COLW / 2
            x1 = centre(2 * s + 1) + COLW / 2
            p.draw_rect(f.Rect(x0 + .6, site_base - 7.4, x1 - .6, site_base + 2.6),
                        color=None, fill=STRIP)
        for i in range(NCOL):                        # one strip per column
            p.draw_rect(f.Rect(centre(i) - COLW / 2 + .6, pool_base - 6.6, centre(i) + COLW / 2 - .6,
                               pool_base + 2.2), color=None, fill=STRIP)
    else:
        for s in range(1, 4):                        # thin rules between the sites
            x = centre(2 * s) - COLW / 2
            p.draw_line(f.Point(x, top), f.Point(x, PANEL.y1 - TRIM), color=RULE, width=0.4)

    def put(text, cx, style, baseline):
        w = f.get_text_length(text, fontname=style["font"], fontsize=style["size"])
        p.insert_text(f.Point(cx - w / 2, baseline), text, fontname=style["font"],
                      fontsize=style["size"], color=style["col"])
        return w

    for s, code in enumerate(SITES):
        put(code, (centre(2 * s) + centre(2 * s + 1)) / 2, SITE_STYLE, site_base)
    for i in range(NCOL):
        put(POOLS[i % 2], centre(i), POOL_STYLE, pool_base)
    p.insert_text(f.Point(ROWLAB["x"], pool_base), ROWLAB["text"], fontname=ROWLAB["font"],
                  fontsize=ROWLAB["size"], color=ROWLAB["col"])

    doc.save(dest, garbage=4, deflate=True)
    doc.close(); src.close()

    chk = f.open(dest)
    pg = chk[0]
    rot = {tuple(round(v, 2) for v in l["dir"]) for b in pg.get_text("dict")["blocks"]
           for l in b.get("lines", []) for s_ in l["spans"] if s_["text"].strip()}
    strings = sorted({s_["text"].strip() for b in pg.get_text("dict")["blocks"]
                      for l in b.get("lines", []) for s_ in l["spans"] if s_["text"].strip()})
    rep = {"file": str(dest.relative_to(R)), "sha256": sha(dest),
           "page_pt": [round(pg.rect.width, 2), round(pg.rect.height, 2)],
           "text_directions": sorted(str(x) for x in rot),
           "header_strings": [x for x in strings if x in SITES + POOLS + [ROWLAB["text"]]],
           "dropped": [x for x in ("Sites × DNA pools",) ],
           "still_present": {k: k in " | ".join(strings) for k in ("ASV_19670", "Methanomassiliicoccales",
                                                       "Mean relative abundance (%)", "Sites", "Fig. S6 |")},
           "style": "grey facet strips" if strips else "plain text + site rules"}
    chk.close()
    assert rep["text_directions"] == ["(1.0, 0.0)"], rep["text_directions"]   # nothing rotated any more
    assert all(rep["still_present"].values()), rep["still_present"]
    return rep


def main() -> None:
    OUT.mkdir(parents=True,exist_ok=True)
    for n,h in json.loads((R/'INPUT_SHA256.json').read_text()).items():
        assert sha(R/n)==h,n
    report=build(True,OUT/'FigS6.pdf')
    (OUT/'FigS6_receipt.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))


if __name__ == "__main__":
    main()
