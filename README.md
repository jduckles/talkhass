# Home Assistant: a state engine for your house

A [Marp](https://marp.app/) talk template about Home Assistant as a state engine —
the states you can know about a house, how to infer the ones you cannot measure,
the three ways to run it, the project's history, and the hardware Nabu Casa builds.

## Files

| Path | Purpose |
| --- | --- |
| `slides.md` | The deck. Marp frontmatter + Markdown, one `---` per slide. |
| `themes/hass.css` | Custom Marp theme (`theme: hass`). Reskin the deck here. |
| `assets/state-loop.svg` | Diagram: devices → integrations → state machine → automations. |
| `assets/recorder.svg` | Diagram: event bus → recorder → SQLite → history. |
| `assets/timeline.svg` | Diagram: project history from 2013 to today. |
| `assets/architecture.svg` | Block model: core, extensions, database, web UI, mobile apps. |
| `assets/power-cycle.svg` | Chart: appliance power draw with start/finish thresholds. |
| `package.json` | Marp CLI scripts. |
| `.github/workflows/pages.yml` | CI: build the deck and publish it to the `html` branch. |

## Build

```bash
npm install
npm run preview   # live preview in a browser window
npm run build     # dist/slides.html + dist/assets/
npm run pdf       # dist/slides.pdf  (needs Chrome/Chromium)
npm run pptx      # dist/slides.pptx (static, one image per slide)
npm run png       # dist/slides.001.png, .002.png, ...
```

`dist/` is generated and gitignored. The HTML build copies `assets/` next to
the deck so the SVG diagrams resolve when the file is opened or served
directly. PDF and image exports run with `--allow-local-files` so the
diagrams are embedded.

Or without installing:

```bash
npx @marp-team/marp-cli --theme-set themes --preview slides.md
```

The preview script watches `slides.md` and `themes/hass.css`.

## Publish to GitHub Pages

`.github/workflows/pages.yml` builds the deck on every push to `main` and
force-pushes a single commit to the `html` branch. GitHub Pages serves that
branch. The workflow also adds `index.html` (a copy of `slides.html`) and
`.nojekyll` so the site root and all SVG assets work unchanged.

One-time setup:

1. Push this repo to GitHub, including `package-lock.json`.
2. Let the workflow run once (**Actions → Publish slides**), or run it manually
   with **Run workflow**. This creates the `html` branch.
3. **Settings → Pages → Build and deployment**:
   - Source: **Deploy from a branch**
   - Branch: **`html`**, folder **`/ (root)`**
   - Save.

Every later push to `main` rebuilds and redeploys. The deck is then at
`https://<owner>.github.io/<repo>/` (for this repo:
`https://jduckles.github.io/talkhass/`).

Notes:

- The workflow needs `contents: write`, which is declared in the file. If your
  organization restricts `GITHUB_TOKEN` permissions, enable write access under
  **Settings → Actions → General → Workflow permissions**.
- PDF and PPTX are not built in CI: they need a local Chrome/Chromium. Run
  `npm run pdf` or `npm run pptx` and commit/attach the output if you want
  downloadable slides.
- `force_orphan: true` keeps the `html` branch to one commit per deploy, so it
  never accumulates build history.

## Editing

- **Slide breaks** are `---` lines outside code fences.
- **Per-slide directives** go in HTML comments before the slide content:
  `<!-- _class: lead -->`, `<!-- _paginate: false -->`, `<!-- _footer: '' -->`.
- **Speaker notes** are HTML comments after the slide content. They do not render
  in the HTML/PDF/PPTX output but are available in Marp's presenter view.
- **Layouts** use plain HTML (`<div class="columns">`, `.callout`, `.pill`,
  `.big`, `.muted`, `.small`). HTML is enabled by default in Marp CLI.
- **Math** works via Marp's built-in KaTeX (`$…$`, `$$…$$`) if you add it.

## Images

The deck is 960×540 CSS px. With the theme's padding and a title, about **330 px
of height** is available for an image. Pasted screenshots are often 2500 px wide,
so never leave them unsized.

- **Bounded height (recommended for screenshots):** put
  `<!-- _class: screenshot -->` before the slide title. The theme caps every
  image on that slide at `max-height: 330px` and scales width proportionally.
- **Per-image sizing:** `![h:330](assets/shot.png)` for tall screenshots;
  `![w:860](assets/chart.png)` for wide charts whose height is naturally small.
- **Side by side, same scale:** give both images heights proportional to their
  source pixel heights, so the scale factor matches (text stays the same size).
  For example, 930 px and 1368 px sources at `h:245` and `h:360` both scale by
  about 0.263. Wrap them in `.image-pair` to center the pair.
- **Crop first.** A tight 1400 px crop of the cards you are discussing reads far
  better than the full browser window. The best fix is usually fewer pixels, not
  a smaller scale.
- **Full-bleed:** `![bg contain](assets/shot.png)` fits the whole image;
  `bg cover` crops it. Use `contain` for screenshots.
- **Source size:** export at roughly 1600–2000 px wide (2× the slide) and
  compress. Multi-megapixel PNGs bloat the repo and slow the Pages build without
  looking sharper on a projector.

## Theme

`themes/hass.css` imports Marp's `default` theme and overrides it. All colours
are custom properties declared on `section`:

```css
--ink: #10202b;        /* body text */
--muted: #5a6f7e;      /* secondary text */
--paper: #f6f9fb;      /* slide background */
--panel: #e9f1f6;      /* tables, section slides */
--accent: #03a9f4;     /* Home Assistant blue */
--accent-deep: #0277bd;
--warm: #e65100;       /* warnings */
```

Change those five values and the whole deck follows. Slide classes:

- `lead` — dark title/closing slides
- `section` — tinted chapter dividers
- helper classes in the theme: `.columns`, `.callout`, `.callout.warn`,
  `.callout.quiet`, `.pill`, `.big`, `.small`, `.tiny`, `.muted`, `.center`,
  `.quote`

## Notes on accuracy

Entity IDs, service names, and config keys use the current Home Assistant
syntax (`triggers` / `conditions` / `actions`, `action:` instead of `service:`).
The recorder schema shown (`states` joined to `states_meta`) is the modern
schema; very old databases stored `entity_id` directly on `states`.

The deck deliberately avoids version numbers and prices so it stays true for
longer. Add them locally if the talk needs them.
