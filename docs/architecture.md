# Architecture

The app is one HTML file (`index.html`) with two `<script>` blocks. The first holds the app (~1,500 lines of plain ES2020+, no modules, no dependencies). The second holds the blank form pages (`FORM_PAGES`, base64 PNGs written by `build/embed_forms.py`). `sw.js` and `manifest.webmanifest` make it an installable offline app.

Why it is built this way is explained in [decisions.md](decisions.md). In short: it had to run from a file inside Documents by Readdle on an iPad, with no server, no build tools on the user's side, and no reception in the field.

```
index.html
├─ <head>         meta/manifest/icons · Google Fonts link · CSS (one light, high-contrast theme)
├─ <body>         top bar (record name, state pills, tabs) · <main> with one <section> per tab
├─ <script> app   reference data → state → change log → records/persistence → views
│                 → PDF → Excel → file delivery → email → records list → shell → installed app → init
└─ <script>       FORM_PAGES = { "57": [page1, continuation], "33.1": [page1, continuation] }
sw.js             offline cache + update check
```

---

## State and data model

There is one global, `S`: the **open sampling day** (a "record"). The shape comes from `blankDay()`:

```js
{
  v: 1,                      // bumped each time a locked record is reopened
  id: "day-2026-10-17-1a2b3c4d",
  locked: false,
  updated: "",               // ISO timestamp of the last save; "" = pristine (never saved)
  head: {                    // day details, shared by both forms
    site, address, date /* YYYY-MM-DD */, client, clientRep, contact, billTo,
    weather: [], landuse, gwl, pid /* instrument serial */, pidOpen, rig, rigOther,
    s1, s2, approver, arrive, finish, tStart, tEnd,
    accredited: true, ready5556, cooled: true, subDrill, subSample, calLab, cal100,
    guideSurvey, guidePiles, planApproved, planShown,
    dayLetter: "A",
    lab, labOther, labSplit, labSplitOther,   // a name from LABS or "אחר" + the typed name; use labName(key)
    extraTests: ["","","","",""],
    notesLog, notesCoc, notesSplit
  },
  samples: [ blankSample() ... ],   // the field-log rows
  deviations: [ {what, why, who} ],
  storage:  { place, keeper, fromD, fromT, toD, toT, tempOk /* "תקין" | "לא תקין" | "" */ },
  handover:      { byName, byDate, byTime, labName, labDate, labTime },   // chain of custody → main lab
  handoverSplit: { byName, byDate, byTime, labName, labDate, labTime },   // split custody → secondary lab
  sigs:     { s1, s2, by, lab, bySplit, labSplit },    // PNG data URLs
  sketch: "",                       // PNG data URL (drawn on screen)
  sketchPhoto: "",                  // JPEG data URL (photo of a paper sketch, max 1000 px, q 0.6)
  changes: [ {t, who, label, from, to} ]
}
```

A sample (`blankSample()`):

```js
{ id /* uuid */, boring, depth, time, name, nameAuto: true, dayLetter,
  soil: [], color: [], odour, moist, pid, pid20, note,
  toCoc: false, tool, packs, stype: "חטף", tests: [], extra: [], cocNote, qc,
  toSplit: false, sp: { tool, packs, stype: "חטף", tests: [], extra: [], note },
  auto: ["stype", "sp.stype"] }   // keys whose current value was copied in, not typed (see change log)
```

`extra` and `qc` exist on samples but no UI uses them yet. The open analysis names are per day (`head.extraTests`), and a sample's `tests` array holds analysis **names**: both the fixed `TESTS` and the day's extra names.

**`normalize(d)`** upgrades any stored record to the current shape:
- It merges `d` over `blankDay()`, including the nested `head`, `storage`, `handover`, `handoverSplit` and `sigs`.
- It pads `extraTests` to 5 and maps old analysis names through `TEST_OLD`.
- It moves a free-text lab name that isn't in `LABS` (from versions before the lab list) to `"אחר"` + `labOther` / `labSplitOther`, so the printed name doesn't change.

Every record loaded from storage goes through it, so **new fields must have defaults in `blankDay()` / `blankSample()`**.

**Labs:** `LABS` is the pick list. `labPicker(key, label)` is a select plus a free-text input when "אחר" is chosen. It is used for the same field in both the custody tab and the handover tab. `labName("lab" | "labSplit")` returns the name to print or export.

**Handover per lab:** the chain of custody and the split custody go to different labs, so each has its own handover, lab receipt and signatures. `HAND.coc` / `HAND.split` map each to its data:
- the handover object: `S.handover` / `S.handoverSplit`
- signature keys: `by`, `lab` / `bySplit`, `labSplit`
- the head lab key
- change-log key prefixes: `ho.` / `hs.`
- the label prefix (`"פיצול — "`)

The main custody keeps its pre-split labels and keys, so its change log continues unbroken. `handCards(kind)` renders the two cards. The split cards appear only when there are split samples.

Derived values: `cocRows()` (samples with `toCoc`), `splitRows()` (samples with `toSplit`), `allTests()` (fixed + named extras), and `qcNeeded()` (see [domain.md](domain.md)).

## Rendering

`render()` rebuilds the tab bar, the **active tab's whole section**, and the top bar after every `save()`. The views (`viewDay`, `viewLog`, `custodyView(kind)`, `viewHand`, `viewHist`, `viewDocs`) return fresh DOM built with `el(tag, attrs, ...children)`. Inputs commit on `change` (blur or select), not on `input`, so a rebuild never interrupts typing.

Form helpers: `field(label, node, hint)`, `txt(val, on, {type, ph})`, `area`, `sel(val, list, on)`, `multi` (multi-select chips), `toggle` (one boolean chip). All pass `disabled: RO()`, where `RO()` is `S.locked`.

Signatures (`pad`) and the sketch are `<canvas>` elements drawn with pointer events. On pointer-up they're stored as PNG data URLs. They're drawn in the screen's text colour and recoloured to black (`inked`) when printed.

## Change log (ISO 17025)

The app keeps a change log because the records are accredited quality records. The rules:

- **Only a change to an existing value is logged.** Typing into an empty field is not a change. Neither is focusing a field without changing it: iPad time and date fields fill themselves on focus, so a touch alone must not be logged.
- **A change is logged once it settles.** `logChange(label, from, to, key)` keeps a pending entry per key and restarts a 3-second timer (`COMMIT_MS`). Repeated edits keep the **original** `from`. `commitChange` writes `{t, who: head.s1, label, from, to}` to `S.changes`, unless `from` was empty or `from === to`.
- **Copied values are not changes.** When a new log row inherits the borehole, time, soil or colour, those keys go into `sample.auto`. The first edit of such a key removes it from `auto` without logging.
- **Pending changes are flushed** (`flushChanges`) before switching records and on `pagehide`, so a change lands in the right record.
- Checkboxes, signatures ("signed" / "cleared"), the sketch, adding and deleting rows, locking and reopening are all logged.
- The log cannot be edited or deleted from the UI. `viewHist` shows it, newest first.

Setters that log: `setHead(k, v, label)`, `setSub(obj, k, v, label, key)`, `setSample(sm, k, v, label)`, `setSplit(sm, k, v, label)`, and `setColor`. Use them for any new field.

**Lock** (its own card, "נעילת הרשומה"): "נעל וסגור" is enabled only when every lab that received samples has signed and its representative is named. That means the main lab always, and the split lab too when there are split samples (`labSigned`, `pendingLabs`). A locked record is read-only. "פתח לעריכה" asks for a reason, bumps `S.v`, logs the reopening, and unlocks.

## Records and storage

Each sampling day is a separate record. `localStorage` keys:

| Key | Content |
|---|---|
| `vasa-doc:<id>` | The full record (JSON) |
| `vasa-index` | Array of `meta()` summaries `{id, title, date, client, n, locked, updated}` for the records list |
| `vasa-current` | Id of the record that was open last |
| `vasa-day` | Legacy single-record key from the first prototype. Migrated by `migrateOld()` on first run, then removed |
| `vasa-install-hint` | `"off"` once the iPad install hint has been dismissed |

- `save()` stamps `updated`, then `persistLocal()` writes the record and index synchronously, then re-renders. A remote push is debounced by 700 ms.
- If `localStorage` throws (quota), `storageFull` shows a red pill: "the last change was not saved". iOS gives about **5 MB per origin**, and signatures and sketch images are the bulk. See [roadmap](roadmap.md#storage-capacity).
- **"שמירה ורשומה חדשה"** saves the open record and opens a blank one. A pristine record (`updated === ""`) is never stored.
- The record title is built by `docTitle()`: `site · date · day letter · sampler 1`.
- An installed iOS web app has **its own storage**, separate from Safari's. Removing the icon deletes the records. `navigator.storage.persist()` is requested on startup.

### Optional remote store (legacy)

The app began as a Claude artifact, where `claude.use("db")` provided a shared database. `useCap(name)` returns that capability or `null`, and outside Claude it is always `null`. With it, records sync to `days/<id>`, `days/<id>/sig/signatures`, `days/<id>/log/changes` (last 800), `days/<id>/shot/sketch` and `index/<id>`. `attachRemote()` subscribes to the open day, and the pill shows "מסונכרן". This is how the office handover route was meant to work. In the hosted PWA the code path is dormant. A real sync backend is on the [roadmap](roadmap.md#sync-between-devices), and it should plug in at `pushRemote` / `attachRemote` / `openDoc`.

## PDF generation

`window.print()` does nothing inside in-app web views such as Readdle, so PDFs are drawn on `<canvas>` and packed into a PDF in the app (`buildPdf(kind)`):

1. **`formPage(F, idx)`** draws the blank form page (`FORM_PAGES[F.key][0 | 1]`: first page or continuation page, 200 DPI PNG) on a canvas. It then scales the context so **1 unit = 1 PDF point**, with the origin at the top-left, x to the right and y down.
2. Values are drawn into boxes `[x0, x1, y0, y1]` (PDF points) from the coordinate tables **`F57`** and **`F33`**:
   - `head` — header cells
   - `cols` and `rows` — table columns and the table's top/bottom on page 1 vs continuation pages
   - `per` — rows per page
   - `next` — continuation-page header
   - `notes` — note lines: `first` / `only` / `last`
   - `total` / `pageNo` — page numbering
   - `marks` — the small row numbers in the margin
   - F33 also has `testEdges`, `yesNo`, `dev`, `boxes`, `store`, `hand`, `isrc`, `endMark`
3. Drawing primitives:
   - `put(g, text, box, {size, bold, align, min})` writes right-aligned RTL text. It shrinks the font down to `min` before wrapping to two lines, and clips to the box.
   - `tick` draws a ✓ and `ring` circles yes/no.
   - `sign` draws a signature scaled into the box, recoloured to black.
   - `whiteout` blanks an area, used for the ISRAC logo, "end of report" on middle pages, page digits and the sketch area.
4. Pagination:
   - `pageCount` comes from the row counts (`per`). A single page whose notes don't fit gets a continuation page.
   - `flowNotes` flows note words into the first page's note lines, then the last page's.
   - `pageMarks` writes "page X of Y" and renumbers the margin row numbers.
5. `renderLog()` covers form 57, with the sketch as an extra counted page (`sketchPage`). `renderCoc(isSplit)` covers form 33.1, including the "*** סוף דו"ח ***" placement rules and the ISRAC logo. For the split copy, it prints the secondary lab, the split handover and the split signatures (`HAND.split`). Inside the page-1 block, `H` is the header-box table (`F.head`), so the handover mapping is named `HK`. Don't reuse `H` there.
6. `canvasJpeg` (q 0.9) → `pdfFromJpegs(pages)`: a minimal hand-written PDF 1.4 with one full-page JPEG image per page. **The text is not searchable or selectable.** This is a known, accepted trade-off.

Printed codes follow the form's legend: tool 1 = liner/sleeve, 2 = jar (`TOOL_CODE`); type ח = grab, מ = composite (`STYPE_CODE`). The PDF font is `Arial, "Arial Hebrew"`, which is present on iPad and Windows.

**New form edition:** see [operations.md](operations.md#a-new-edition-of-form-57-or-331).

## Excel generation

`buildXlsx()` → `workbookBlob(workbookSheets())` writes an `.xlsx` without libraries:

- Office Open XML parts with inline strings, packed by `zipBlob()` (zip "stored" method, CRC-32 in `crc32`).
- Sheets: day details (key/value), field log, chain of custody, and split custody (only when there are split samples).
- The details sheet lists the lab, the handover and the lab receipt for each custody. The split ones are prefixed "פיצול — ".
- **Analysis totals:** each custody sheet ends, after a blank row, with a "סה״כ אנליזות" row. It holds the count of each analysis under its column, and the total plus the number of samples in the notes column. The row sits **outside** the autofilter range (`filterRows`), so sorting or filtering doesn't move it. The style is 6 (`XS.total`).
- All sheets are `rightToLeft`. Table sheets have a frozen header row and an autofilter.
- `xnum()` stores numeric strings as numbers.
- Style 5 (`XS.num`) gives numbers **general** alignment, because in an RTL sheet `horizontal="right"` puts numbers on the left (verified in Excel).
- Tool and type are written as words (שרוול / צנצנת, חטף / מורכב), not form codes.

## File delivery

`offerFile(blob, filename)` opens a dialog with every way to get the file, because none of them works everywhere:

- **share** (`navigator.share({files})`) when `canShare` allows it
- **save** via the Claude `downloads` capability (artifact only)
- **download** (`<a download>`)
- **open** in a new tab

Sharing must be triggered directly by a tap (iOS user-activation rule). That's why it is a button in the dialog and not run right after the file is generated.

File names come from `fileName(kind)`: `<kind name> <site> DDMMYY` + extension, e.g. `יומן שדה מגרש 12 171026.pdf`. `showName()` adds an invisible LRM before the date, **for display only**, so that RTL text doesn't show `pdf.171026`.

## Email

`mailDialog()` ("שליחה במייל" in the files card):

1. **Choose**: chips for the field log, chain of custody, split custody (shown only when there are split samples) and the client Excel.
   - Defaults: the field log on; custody on when it has samples; split on when shown; Excel off.
2. **"הכנת המייל"** builds the chosen files with `mailFile(kind)`, which uses `buildPdf` / `buildXlsx`. It also builds the subject and body with `mailText(names)`.
   - Subject: `מסמכי יום דיגום — <site> — dd.mm.yyyy`.
   - Body: greeting; site, address, date, client, samplers and sample counts; the list of attached files; signed with sampler 1, the company name and the website.
3. **"פתיחת המייל"**:
   - If `navigator.canShare({files})` is true, `navigator.share({files, title: subject, text: body})` opens the OS share sheet. The user picks Mail or Outlook, which opens a new email with the attachments and body.
   - Otherwise (no file sharing, e.g. desktop Firefox, or Chromium in some contexts) there's a fallback: a download link per file, plus a `mailto:` link with the subject and body, and the user attaches the files by hand.

Limits of the share sheet:
- The recipient cannot be pre-filled.
- Whether iOS copies `title` into Mail's subject line is not documented. That's why the body repeats the site and date in its first line.

The **iPad behaviour must be verified on a device** (see [operations.md](operations.md#what-to-check-on-the-ipad-after-a-change-to-files-or-email)).

## Installed app (PWA) and offline

- `manifest.webmanifest`: `standalone`, `lang: he`, `dir: rtl`, scope `./`, icons from `icons/`.
- The iOS meta tags in the head: `apple-mobile-web-app-capable`, `apple-touch-icon` and the status-bar style.
- **`sw.js`**:
  - On install it caches the shell (`./`, manifest, icons) in `vasa-shell-v<N>` and activates immediately (`skipWaiting` + `clients.claim`). Old caches are deleted on activate.
  - **The page** is served cache-first (`./` and `index.html` share one entry), so the app opens instantly with or without reception.
  - **Update check**: the page posts `{type: "check-update"}` after registering and every time it becomes visible, because an installed iPad app is usually resumed rather than reloaded. The worker fetches `./` with `cache: "no-cache"` and compares it with the cached text. If they differ, it stores the new copy and replies `{type: "update-ready"}`. The page then shows the pill **"גרסה חדשה מוכנה — רענון"**. Tapping it saves pending changes (`persistNow`) and reloads into the new version. The app never reloads on its own, so a sampler mid-entry is not interrupted.
  - Manifest and icons: stale-while-revalidate.
  - **Google Fonts** (`fonts.googleapis.com`, `fonts.gstatic.com`): cache-first into `vasa-fonts-v<N>`, filled on the first visit with reception. The CSS response is opaque (no `crossorigin`), which is still cacheable.
- `setupApp()`:
  - registers the worker (http/https only; under `file://` the app runs without it)
  - requests persistent storage
  - wires the update pill
  - on desktop Chrome/Edge, shows an "התקנה כאפליקציה" pill from `beforeinstallprompt`
  - `installHint()` shows a dismissible note in iPad/iPhone Safari (HTTPS, not yet installed) explaining Add to Home Screen. It warns that records entered in Safari do not carry over into the installed app.
