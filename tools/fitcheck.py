"""Estimate whether each Marp slide fits in 1280x720 with the baleen theme.

    npx @marp-team/marp-cli@4 slides.md --theme-set themes --html --template bare -o /tmp/bare.html
    python3 tools/fitcheck.py /tmp/bare.html .            # every slide, as a % of the space
    python3 tools/fitcheck.py /tmp/bare.html . --explain 12   # block by block, for one slide

Needs beautifulsoup4, lxml, Pillow and the Barlow TTFs (FIT_FONTS=dir if they
aren't in a usual font folder). FIT_THEME picks the size profile below.

deck.html is `marp --template bare --html` output. There's no browser here, so
this lays out the blocks itself: Barlow metrics from the installed fonts, the
theme's sizes, margins and paddings, greedy word wrap. It is an estimate
(roughly +/- 5 %), so it flags anything over 97 % of the space as tight.
"""
import os
import re
import sys

# theme profiles: the two this deck has used
PROFILES = dict(
    baleen=dict(pad=(64, 80, 72), size=26, lh=1.4, h1=54, pre=19, table=21, callout=23, gap=48,
                compact=dict(size=21, h1=44)),
    # baleen plus the deck-level style in talkhass/slides.md
    talkhass=dict(pad=(52, 72, 64), size=24, lh=1.4, h1=48, pre=16, table=19, callout=21, gap=44,
                  cpad=(12, 20), shot=400, callout_mt0=True, shot_h1=42, compact=dict(size=20, h1=42)),
    hass=dict(pad=(46, 64, 58), size=24, lh=1.45, h1=46, pre=15.5, table=19, callout=22, gap=40,
              compact=dict(size=21, h1=40, pre=13, table=17, callout=19)),
)
P = PROFILES[os.environ.get("FIT_THEME", "talkhass")]
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag
from PIL import Image, ImageFont

def _font_dir():
    for d in [os.environ.get("FIT_FONTS", ""), Path.home() / ".local/share/fonts",
              Path.home() / "Library/Fonts", "/Library/Fonts", "/usr/share/fonts/truetype/barlow"]:
        if d and (Path(d) / "Barlow-Regular.ttf").exists():
            return Path(d)
    sys.exit("fitcheck: can't find Barlow-Regular.ttf; set FIT_FONTS to the folder that has the Barlow TTFs")


FD = _font_dir()
_fonts = {}


def font(name, size):
    k = (name, round(size * 4))
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(str(FD / f"{name}.ttf"), max(1, round(size * 4)))
    return _fonts[k]


def width(text, name, size, track=0.0, upper=False):
    if name == "Barlow":
        name = "Barlow-Regular"
    if upper:
        text = text.upper()
    return font(name, size).getlength(text) / 4 + track * size * len(text)


def runs(el, fam, size, bold=False):
    """Flatten inline content into (word, width, size) tokens."""
    out = []
    for c in el.children:
        if isinstance(c, NavigableString):
            for w in re.split(r"(\s+)", str(c)):
                if not w:
                    continue
                if w.isspace():
                    out.append((" ", width(" ", fam, size), size))
                else:
                    out.append((w, width(w, fam + ("-SemiBold" if bold else "-Regular"), size)
                                if fam == "Barlow" else width(w, fam, size), size))
        elif isinstance(c, Tag):
            if c.name == "br":
                out.append(("\n", 0, size))
            elif c.name == "code":
                for w in re.split(r"(\s+)", c.get_text()):
                    if w:
                        out.append((w, len(w) * 0.6 * size * 0.82 + 8, size))
            elif c.name in ("strong", "b", "em"):
                out += runs(c, fam, size, True)
            elif "pill" in (c.get("class") or []):
                t = c.get_text()
                out.append((t, width(t, "BarlowSemiCondensed-SemiBold", 15, 0.08, True) + 26, size))
            else:
                out += runs(c, fam, size, bold)
    return out


def lines(tokens, avail):
    n, x = 1, 0.0
    for w, wd, _ in tokens:
        if w == "\n":
            n, x = n + 1, 0.0
            continue
        if w == " ":
            x += wd
            continue
        if x > 0 and x + wd > avail:
            n, x = n + 1, wd
        else:
            x += wd
    return n


def text_h(el, avail, size, lh, fam="Barlow"):
    toks = runs(el, fam, size)
    if not any(w.strip() for w, _, _ in toks):
        return 0
    return lines(toks, avail) * size * lh


def img_size(img, base, avail, ctx):
    src = img.get("src", "")
    style = img.get("style", "")
    p = base / src
    nat = (800, 450)
    try:
        if src.endswith(".svg"):
            vb = re.search(r'viewBox="([\d.\s-]+)"', p.read_text()[:3000])
            a = [float(v) for v in vb.group(1).split()]
            nat = (a[2], a[3])
        else:
            nat = Image.open(p).size
    except Exception:
        pass
    w = re.search(r"width:\s*([\d.]+)px", style)
    h = re.search(r"height:\s*([\d.]+)px", style)
    if w:
        W = float(w.group(1)); H = W * nat[1] / nat[0]
    elif h:
        H = float(h.group(1)); W = H * nat[0] / nat[1]
    else:
        W, H = nat
    if W > avail:
        H *= avail / W; W = avail
    mh = P.get("shot", 470)
    if ctx.get("screenshot") and H > mh:
        W *= mh / H; H = mh
    return W, H


class Ctx(dict):
    pass


def block(el, avail, size, ctx, base):
    """Return (margin_top, height, margin_bottom, max_width) for a block element."""
    cls = el.get("class") or []
    n = el.name
    if n in ("h1", "h2", "h3"):
        if n == "h1":
            s = ctx.get("h1", P["h1"]); f = "BarlowCondensed-Bold"
            if ctx.get("screenshot") and P.get("shot_h1"):
                s = P["shot_h1"]
        elif n == "h2":
            s = 30; f = "Barlow-Regular"
        else:
            s = 18; f = "BarlowSemiCondensed-SemiBold"
        t = el.get_text().upper() if n == "h3" else el.get_text()
        tr = 0.08 if n == "h3" else 0
        ln = lines([(w, width(w, f, s, tr), s) if w != " " else (" ", width(" ", f, s), s)
                    for w in re.split(r"(\s+)", t) if w], avail)
        return 0, ln * s * 1.08, 0.35 * s, avail
    if n == "p":
        imgs = el.find_all("img")
        if imgs and not el.get_text().strip():
            ws, hs = zip(*(img_size(i, base, avail, ctx) for i in imgs))
            return size, max(hs), size, sum(ws)
        return size, text_h(el, avail, size, P["lh"]), size, avail
    if n in ("ul", "ol"):
        s = size * (1.5 if ctx.get("big") else 1)
        ind = 1.1 * s
        h = 0
        for li in el.find_all("li", recursive=False):
            inner = 0
            sub = [c for c in li.children if isinstance(c, Tag) and c.name in ("ul", "ol", "p")]
            tmp = BeautifulSoup("<span></span>", "lxml").span
            for c in list(li.children):
                if not (isinstance(c, Tag) and c.name in ("ul", "ol")):
                    tmp.append(c.__copy__() if isinstance(c, Tag) else NavigableString(str(c)))
            inner += text_h(tmp, avail - ind, s, P["lh"])
            for c in sub:
                if c.name in ("ul", "ol"):
                    mt, hh, mb, _ = block(c, avail - ind, s, ctx, base)
                    inner += mt + hh + mb
            h += inner + 0.18 * s * 2
        return 0.2 * s, h, 0.2 * s, avail
    if n == "pre":
        s = ctx.get("pre", P["pre"])
        code = el.get_text().rstrip("\n").split("\n")
        wmax = max(len(l) for l in code) * 0.6 * s + 40
        return s, len(code) * s * 1.45 + 32 + 3, s, wmax
    if n == "blockquote":
        s = 34
        h = sum(text_h(p, avail - 28, s, 1.3) for p in el.find_all("p")) + s * 0.0
        return 0.4 * s, h + (len(el.find_all("p")) - 1) * s, 0.4 * s, avail
    if n == "table":
        s = ctx.get("table", P["table"])
        rows = el.find_all("tr")
        ncol = max(len(r.find_all(["td", "th"])) for r in rows)
        # auto layout: share the width by each column's longest content
        need = [0.0] * ncol
        for r in rows:
            for i, c in enumerate(r.find_all(["td", "th"])):
                need[i] = max(need[i], sum(wd for _, wd, _ in runs(c, "Barlow", s)) + 16)
        tot = sum(need)
        colw = need if tot <= avail else [max(60, avail * x / tot) for x in need]
        h = 0
        for r in rows:
            cells = r.find_all(["td", "th"])
            if cells and cells[0].name == "th":
                h += 15 * 1.4 + 12 + 1.5
            else:
                h += max((text_h(c, colw[i] - 14, s, P["lh"]) or s * 1.4)
                         for i, c in enumerate(cells)) + 2 * ctx.get("tdpad", 8) + 1
        return 0.4 * s, h, 0.4 * s, min(tot, avail)
    if n == "div":
        if "columns" in cls:
            kids = [c for c in el.children if isinstance(c, Tag)]
            gap = P["gap"]
            fr = [3, 2] if "wide-left" in cls else [1, 1]
            hs = []
            for i, k in enumerate(kids[:2]):
                cw = (avail - gap) * fr[i] / sum(fr)
                hs.append(flow(k, cw, size, ctx, base, independent=True))
            return 0.3 * size, max(hs or [0]), 0, avail
        if "stats" in cls and avail < 700 and P is PROFILES.get("talkhass"):
            kids = el.find_all("div", class_="stat")
            cw = (avail - 32) / 2
            hs = [60 + 6 + text_h(k.find("small"), min(cw, 14 * 19), 19, 1.4) for k in kids]
            rows = [max(hs[i:i + 2]) for i in range(0, len(hs), 2)]
            ws = [max(width(k.find("span").get_text(), "BarlowCondensed-Bold", 60) for k in kids)]
            return 0.6 * size, sum(rows) + 20 * (len(rows) - 1), 0.6 * size, 2 * ws[0] + 32
        if "stats" in cls:
            kids = el.find_all("div", class_="stat")
            ws, hs = [], []
            for k in kids:
                sp, sm = k.find("span"), k.find("small")
                w1 = width(sp.get_text(), "BarlowCondensed-Bold", 84)
                w2 = min(width(sm.get_text(), "Barlow-Regular", 19), 14 * 19)
                ws.append(max(w1, w2))
                hs.append(84 + 6 + text_h(sm, max(w1, w2), 19, 1.4))
            return 0.6 * size, max(hs), 0.6 * size, sum(ws) + 56 * (len(ws) - 1)
        if "callout" in cls:
            s = ctx.get("callout", P["callout"])
            cv, ch = P.get("cpad", (16, 22))
            inner = flow(el, avail - 2 * ch - 3, s, ctx, base, independent=not P.get("callout_mt0"), last_mb0=True)
            return 0.6 * s, inner + 2 * cv + 3, 0.6 * s, avail
        if "image-pair" in cls:
            imgs = el.find_all("img")
            sz = [img_size(i, base, avail, ctx) for i in imgs]
            return 0.6 * size, max(h for _, h in sz), 0, sum(w for w, _ in sz) + 44 * (len(sz) - 1)
        if "big" in cls:
            c2 = Ctx(ctx); c2["big"] = True
            return 0, flow(el, avail, size, c2, base), 0, avail
        return 0, flow(el, avail, size, ctx, base), 0, avail
    if n == "img":
        w, h = img_size(el, base, avail, ctx)
        return 0, h, 0, w
    if n in ("header", "footer"):
        return 0, 0, 0, 0
    return 0, text_h(el, avail, size, P["lh"]), 0, avail


def flow(el, avail, size, ctx, base, independent=False, last_mb0=False, flex=False):
    kids = [c for c in el.children if isinstance(c, Tag) and c.name not in ("header", "footer")]
    h, prev_mb, first = 0.0, 0.0, True
    for i, k in enumerate(kids):
        mt, hh, mb, wmax = block(k, avail, size, ctx, base)
        if last_mb0 and i == len(kids) - 1:
            mb = 0
        if wmax > avail + 2:
            ctx.setdefault("wide", []).append(f"{k.name}.{'.'.join(k.get('class') or [])} {wmax:.0f}px > {avail:.0f}px")
        if flex:
            h += mt + hh + mb
        else:
            if first:
                h += mt if independent else 0
            else:
                h += max(prev_mb, mt)
            h += hh
            prev_mb = mb
        first = False
    if not flex and independent:
        h += prev_mb
    return h


def check(html_path, base):
    soup = BeautifulSoup(Path(html_path).read_text(), "lxml")
    out = []
    secs = [x for x in soup.find_all("section")
            if x.get("data-marpit-advanced-background") not in ("background", "pseudo")]
    for i, sec in enumerate(secs, 1):
        cls = sec.get("class") or []
        title = (sec.find(["h1", "h2"]) or sec).get_text().strip().split("\n")[0][:60]
        if {"figure", "lead", "section"} & set(cls):
            out.append((i, "-", 0, " ".join(cls), title, ""))
            continue
        ctx = Ctx()
        size = P["size"]
        if "compact" in cls:
            c = dict(P["compact"]); size = c.pop("size"); ctx.update(c)
        if "screenshot" in cls:
            ctx["screenshot"] = True
        if "small-code" in cls:
            ctx["pre"] = 13
        if "small-table" in cls:
            ctx["table"] = 16; ctx["tdpad"] = 4
        st = sec.get("style", "")
        for key in ("pre", "table", "callout", "h1"):
            m = re.search(rf"--fit-{key}:\s*([\d.]+)", st)
            if m:
                ctx[key] = float(m.group(1))
        m = re.search(r"--fit-size:\s*([\d.]+)", st)
        if m:
            size = float(m.group(1))
        t, lr, b = P["pad"]; avail_w, avail_h = 1280 - 2 * lr, 720 - t - b
        h = flow(sec, avail_w, size, ctx, base, flex=True)
        pct = h / avail_h * 100
        out.append((i, f"{pct:.0f}%", pct, " ".join(cls), title, "; ".join(ctx.get("wide", []))))
    return out




def explain(html_path, base, n):
    """Print each top-level block's share of slide n."""
    soup = BeautifulSoup(Path(html_path).read_text(), "lxml")
    secs = [x for x in soup.find_all("section")
            if x.get("data-marpit-advanced-background") not in ("background", "pseudo")]
    sec = secs[n - 1]
    cls = sec.get("class") or []
    ctx = Ctx(); size = P["size"]
    if "compact" in cls:
        c = dict(P["compact"]); size = c.pop("size"); ctx.update(c)
    if "small-code" in cls: ctx["pre"] = 13
    if "small-table" in cls: ctx["table"] = 16; ctx["tdpad"] = 4
    t, lr, b = P["pad"]
    for k in sec.children:
        if isinstance(k, Tag) and k.name not in ("header", "footer"):
            mt, hh, mb, w = block(k, 1280 - 2 * lr, size, ctx, base)
            print(f"  {k.name}.{'.'.join(k.get('class') or [])}: {mt:.0f}+{hh:.0f}+{mb:.0f}")


if __name__ == "__main__":
    html = sys.argv[1]
    base = Path(sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("-") else Path(html).parent)
    if "--explain" in sys.argv:
        explain(html, base, int(sys.argv[sys.argv.index("--explain") + 1]))
        sys.exit()
    bad = 0
    for i, p, pct, cls, title, wide in check(html, base):
        flag = "OVER" if pct > 100 or wide else ("tight" if pct > 97 else "")
        bad += flag == "OVER"
        print(f"{i:3d} {p:>5} {flag:5} {cls[:22]:22} {title}" + (f"  [wide: {wide}]" if wide else ""))
    print(f"\n{bad} slide(s) over (an estimate from font metrics, not a browser render)")
    sys.exit(1 if bad else 0)
