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
  kind: "soil",              // "soil" | "gas" — chosen when the record is created (newDocDialog); old records normalize to "soil"
  id: "day-2026-10-17-1a2b3c4d",
  locked: false,
  updated: "",               // ISO timestamp of the last save; "" = pristine (never saved)
  head: {                    // day details, shared by both forms
    site, address, date /* YYYY-MM-DD */, client, clientRep, contact, billTo,
    weather: [], landuse, gwl, pid /* instrument serial */, pidOpen, rig, rigOther,
    s1, s2, approver, arrive, finish, tStart, tEnd,
    accredited: true, ready5556, cooled: true, subDrill, subSample, calLab, cal100,
    guideSurvey, guidePiles, planDeclared, planShown,   // planApproved: edition-21 key, kept in old records, not shown or printed
    dayLetter: "A",
    lab, labOther, labSplit, labSplitOther,   // a name from LABS or "אחר" + the typed name; use labName(key)
    extraTests: ["","","","",""],
    notesLog, notesCoc, notesSplit
  },
  samples: [ blankSample() ... ],   // the field-log rows
  cocExtra: [ blankExtra() ... ],   // rows that exist only in the chain of custody (free rows and duplicates)
  splitExtra: [ blankExtra() ... ], // the same for the split custody
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
  soil: [], color: [], odour: "לא", moist, pid, pid20, note,
  toCoc: false, tool: "צנצנת", packs: "1", stype: "חטף", tests: [], extra: [], cocNote, qc,
  toSplit: false, sp: { tool: "צנצנת", packs: "1", stype: "חטף", tests: [], extra: [], note },
  auto: ["odour", "tool", "packs", "stype", "sp.tool", "sp.packs", "sp.stype"] }
  // auto: keys whose current value was copied in or is a default, not typed (see change log)
```

A custody-only row (`blankExtra()`):

```js
{ id /* uuid */, dup: false /* true = duplicate (חזרה) */, after: "" /* id of the row a duplicate sits under */,
  name, depth, time, pid, dayLetter, tool: "צנצנת", packs: "1", stype: "חטף", tests: [], note,
  auto: ["tool", "packs", "stype"] }
```

**Custody rows.** `custodyRows(isSplit)` is the one list of form 33.1 rows, in print order, used by the custody tabs, the PDF, the Excel file, the email counts and the tab counts:
- the field-log samples ticked for custody (`cocRows()` / `splitRows()`), then the free rows (`after: ""`)
- each duplicate is inserted under its `after` row, after any earlier duplicates of the same row
- a duplicate whose row left the custody (unticked or deleted in the log) goes to the end, so no record is dropped silently

Each item is `{id, src, x, bag, name, depth, time, pid, dayLetter, note, dup}`. `src` is the sample (or null), `x` the extra row (or null). `bag` is where tool, packs, type and tests live: the sample, `sample.sp` for the split, or the extra row. `setRow(r, k, v, label, isSplit)` routes an edit to `setSample` / `setSplit` / `setExtra`. In the main custody a sample's note is `cocNote`. `hasSplit()` replaces "are there split samples" checks, so a split custody with only free rows still gets its handover cards, PDF and Excel sheet.

**Duplicates:** `duplicateRow(r, isSplit)` copies everything except `tests`, appends " חזרה" to the name, and lists the copied keys in `auto` (same rule as a new log row: the first edit of a copied value is not a change). The long press is `longPress(tr, fn)`: 3 s (`LONG_MS`), ignored on inputs/selects/buttons, cancelled by pointerup/cancel/leave or by moving more than 12 px. `askDuplicate` and `deleteRow` confirm through `askYes(title, text, yes, onYes, danger)`, an in-app dialog. **Don't use the browser's `confirm()`**: some hosts block it and it returns false at once, so the action silently does nothing. That's how the first version of the ✕ failed in testing. Rows with `dup: true` get no long press.

`extra` and `qc` exist on samples but no UI uses them yet. The open analysis names are per day (`head.extraTests`), and a sample's `tests` array holds analysis **names**: both the fixed `TESTS` and the day's extra names.

**`normalize(d)`** upgrades any stored record to the current shape:
- It merges `d` over `blankDay()`, including the nested `head`, `storage`, `handover`, `handoverSplit` and `sigs`.
- It pads `extraTests` to 5 and maps old analysis names through `TEST_OLD`.
- It fills `cocExtra` / `splitExtra` (empty in records from before 21.10.2026) and merges each row over `blankExtra()`.
- `storage` defaults to `tempOk: "תקין", auto: ["tempOk"]`; `setSub` honours `auto` the same way `setSample` does. A stored record whose `storage` has no `auto` (from before 24.11.2026) gets `auto: []` and, if it never had `tempOk`, `tempOk: ""`, so old records print and log exactly as before.
- `rowHasData` ignores `tool` / `packs` while they are still the untouched defaults (`ROW_DEFAULT`), so deleting an otherwise empty added row stays unlogged.
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

Derived values: `cocRows()` (samples with `toCoc`), `splitRows()` (samples with `toSplit`), `custodyRows(isSplit)` and `hasSplit()` (above), `allTests()` (fixed + named extras), and `qcNeeded()` (see [domain.md](domain.md)). `qcNeeded()` counts custody rows without the duplicates as `n`, and reports `haveDup`, `haveSpl` and `badDup` (duplicates marked for VOC or TPH GRO).

### Soil-gas records (`kind: "gas"`)

A gas record is one active soil-gas survey: installation (form 59.1) and sampling (form 59), usually on different days. `S.gas` (from `blankGas(mode)`; present, blank, on every record, and filled in by `normalize()`):

```js
gas: {
  mode: "full",            // "full" — installation is recorded here; "manual" — sampling only, installation details typed from form 59
  inst: { date, s1, weather: [], method, methodOther, boreDia, tubeType, tubeDia, probe,
          pid, lamp, pidOpen, calLab, cal100 },                    // form 59.1 header, installation day
  samp: { date, s1, weather: [], instDate /* manual mode */, tube /* manual mode */, purgeVols,
          canSupplier, canSupplierOther, canDate, pid, lamp, calLab, cal100, deviation /* "אין" | "יש" */ },
  wells: [ blankWell() ... ],   // one row per well: installation fields (form 59.1) and sampling fields (form 59)
  blanks: [ blankBlank() ... ], // EB (material blank, also counts as air blank) / AB (air blank) canisters
  imported: null           // {from, by, exportedAt, at, file} when the installation came from another iPad's data file
}
```

A well (`blankWell`): `{id, name, tStart, tEnd, pidHole, perm, sand, bentGran, bentWet, depth, profile, note, auto: []}` — the form-59.1 columns minus cement (dropped, Danny 16.11.2026; the column prints empty). `WELL_LABEL` names the fields for the log and for re-import diffs. `setWell(w, k, v, part)` logs under `gas.well.<part>.<id>.<k>`; `addWell` names the new well from the previous one (`nextWellName`: SG-3 → SG-4) and pre-fills the start time, both in `auto` (a first edit is not a change). `dropLastWell` logs only if the row had data. Checks (`wellInstIssues`): permeability > 7.5 inHg, probe depth < 1 m, end before start, and (once the end time is in) not all fill layers ticked. The bore-diameter field shows the appendix-A fill volume (`FILL_CC`).

**Installation data file (cross-iPad).** `instFileBlob()` writes `{type:"vasa-gas-install", v, exportedAt, from: record id, by: installer, head: INST_HEAD_LABEL keys, inst, wells: install fields only, sig, changes, code}`; `code` is SHA-256 (`crypto.subtle`) of the JSON of everything else, so a hand-edited or damaged file is refused. It is not protection against someone recomputing the code. It goes out as a mail attachment (`instData`) or via "קובץ נתוני התקנה". `importInstall()` (records tab, "ייבוא התקנה") picks a file, `readInstFile` checks type and code, then `importInstallFile`:
- the source record is on this device → offer to open it;
- already imported (`gas.imported.from` matches) → `dupDialog`: open it, or, if the file is newer and the record isn't locked, `updateFromInstall`, which overwrites the installation part and logs every changed field (`עדכון מקובץ התקנה — …`, by the installer), wells added/removed, the installer's own log entries since, and one summary entry; sampling fields of existing wells are untouched;
- otherwise a new gas record is built from the file (its change log carried over, plus a "ייבוא התקנה מקובץ" entry) and opened on the sampling tab.

In an imported record the installation part is read-only: `instRO(build)` sets `roInst` while building those cards, and `RO()` is `S.locked || roInst`; the installer's signature shows as an image, not a pad. Shared details (`S.head`) stay editable.

```js
```

- Shared with soil, in `S.head`: site, address, client, contact, billTo, approver, accredited, planDeclared, planShown, and the lab keys. `head.date` / `head.dayLetter` are blank in a gas record. Use `recDate(d)` for the record's date (sampling date, else installation date) — `meta()` and `docTitle()` do.
- Signatures: `sigs.gi` (installation sampler) and `sigs.gs` (sampling sampler); handover signatures are the soil ones (`by`, `lab`).
- In full mode the sampling header shows the installation date and "tubing type and diameter" read-only from `inst` (`fixedField`); in manual mode they are typed (`samp.instDate`, `samp.tube`).
- Gas field setters go through `setSub` with keys `gas.inst.<k>` / `gas.samp.<k>` (`gsub(part, k, label)`).
- Tabs: `TABS` entries have an optional `when()`. Soil: יום דיגום, יומן שדה, שרשרת משמורת, משמורת פיצול. Gas: פרטי הסקר (`viewGasHead`), התקנה (`viewInst`, hidden in manual mode), דיגום (`viewSamp`). `render()` falls back to the details tab if the active tab doesn't exist in the open record's type.
- Handover for gas: a "חריגות אין/יש" card and a no-cooling / 72-hour note replace the soil deviations list and storage card. File generation for gas is not built yet (stages 2–4).

### Sampling (form 59)

Well sampling fields (`SAMP_LABEL`): `can, vol, vacFrom, vacTo` (shut-in), `flow, purgeMin, pidAfter, ipa, sStart, sEnd, canFrom, canTo, to15` (default true), `sNote`, `dup` (lab duplicate from the same canister), `split` + `spCan, spVol, spCanFrom, spCanTo` (second canister on a T-splitter, to the secondary lab). These are not in the installation data file, and `updateFromInstall` never touches them. `viewSamp` shows a card per well (`wellSampCard`) and per blank (`blankCard`); in manual mode the card also has probe number and depth, and wells are added there.

Checks (`wellSampIssues`, Danny's rules 16.11.2026): shut-in start 7.5–15 inHg and drop ≤ 0.5; flow 100–200 (Danny 23.11.2026); purge volumes per well (`purgeVols`, default from the day — `wellVols`, printed by `purgeVolsForm`) not fewer than the depth requires; purge minutes from appendix C by rate (`PURGE_T`, full mode); canister start 26–30, end 3–5 (also for the split canister and blanks); end before start; IPA not ticked on a sampled well; split ticked without a canister. Full mode only: ≥ 8 h from installation end to sampling start (`eqHours`), and purge minutes ≥ `purgeNeeded(depth, boreDia)` from appendix C at 150 ml/min (`PURGE_150`; deeper row, 1.5 m minimum row, 1.75" → 2"). The header's purge-volume count is compared with `purgeVolsNeeded()` (5 if any well is deeper than 1.5 m, else 3).

QC (`gasQc`, guidelines): only from 10 sampled wells (wells with a canister number); then duplicate and split `ceil(n/20)` each, and at least one blank on the day. Handover: `gasDeadline` shows "deliver by" = last sampling end + 72 h, and warns per lab if the lab received it later.

### Form 59 PDF

`F59` (edition 11, measured from `forms/form-59.pdf`): one template page, 10 rows; more rows repeat the page, "סוף דו"ח" only on the last. `gasCustodyRows(isSplit)`: main = all wells then blanks (a duplicate well notes "חזרה"); split = wells ticked for split with the split canister. Header from `samp` and `head`; installation date and tubing from the installation (or the typed values in manual mode: `gasInstDate`, `gasTube`). The QC boxes are ticked from the data (main form only); deviations ring "אין"/"יש"; the "per the Ministry's guidelines" box is always ticked; the plan boxes follow `planDeclared` / `planShown`. Handover from `HAND.coc` / `HAND.split`. `buildPdf("gcoc" | "gsplit")`.

### Form 59.1 PDF

`F591` (edition 6, measured from `forms/form-59.1.pdf`): one template page, 10 well rows. More wells → the same page again with the full header, "דף X מתוך Y", and the small row number in the margin (`mark`) rewritten (20, 30…). The ISRAC logo is whited out when the job is not accredited. Notes (`inst.notes`) flow into the lines under the table on the last page. `renderInst()`; `buildPdf("inst")`. `put(…, {ltr:true})` draws a left-to-right value (the PID lamp, "11.7 eV") so its words don't swap; `sel()` prefixes such option labels with an LRM for the same reason on screen.

### Gas email

`mailKinds()` returns `GAS_MAIL_KINDS` in a gas record: form 59.1 PDF, the installation data file (not in sampling-only or imported records), form 59 and the split form 59. `gasMailText`: with a form 59 attached it is the sampling email — subject "מסמכי שדה מיום דיגום גז קרקע <date> <site>", sample counts and the handover lines (`handoverLines`, which uses `gasCustodyRows` in a gas record); otherwise the installation email — "מסמכי שדה מיום התקנה גז קרקע <date> <site>" (Danny, 16.11.2026). The subject is also the body's first line. File names: `fileDate(kind)` — installation files by the installation date, the rest by `recDate`.

## Rendering

`render()` rebuilds the tab bar, the **active tab's whole section**, and the top bar after every `save()`. The views (`viewDay`, `viewLog`, `custodyView(kind)`, `viewHand`, `viewHist`, `viewDocs`) return fresh DOM built with `el(tag, attrs, ...children)`. Inputs commit on `change` (blur or select), not on `input`, and the handlers of `txt` / `area` / `sel` run inside `fromField`, so the rebuild they cause is deferred.

**The focused field is never rebuilt.** `render()` calls `draw()` at once unless the view is unchanged (`viewKey`, same `S`) and either a field has focus or the call came from a field; then `renderSoon()` draws after the focus change has settled and no pointer is down. `draw()` then uses `patchAround(old, new, focus)`: the focused element and its ancestors stay in the DOM, every other node is replaced by the new one, and the scroll is compensated. If the structure around the field changed it falls back to a full rebuild after committing the field. A kept field keeps its **old handler**, so handlers must read `S` when they run, not values captured when drawn. Repeating cards and rows carry `data-id` so a field is never matched to another well or sample. A click on any button first commits the open field (`commitField`), because on iPad a button does not take focus.

Form helpers: `field(label, node, hint)`, `txt(val, on, {type, ph})`, `area`, `sel(val, list, on)`, `multi` (multi-select chips), `toggle` (one boolean chip). All pass `disabled: RO()`, where `RO()` is `S.locked`.

**Time and date inputs commit on blur, not on `change`.** The iPad's wheel picker fires `change` on every spin, and a save there rebuilds the section and replaces the input under the open picker, so the picker jumps. `txt` marks the value dirty while the input has focus and calls `on` on blur. `render()` also returns early while a `main input[type=time|date]` has focus, and re-runs once on its blur. Any re-render can hit this, e.g. a change-log commit firing 3 s after an earlier edit. Keep both guards if you touch `txt` or `render`.

Signatures (`pad`) and the sketch are `<canvas>` elements drawn with pointer events. On pointer-up they're stored as PNG data URLs. They're drawn in the screen's text colour and recoloured to black (`inked`) when printed.

**Images need a fixed height** in anything above the fields: they decode after the rebuild and would push the content down.

### Canister certificate and coordinates

`S.canCert` (JPEG data URLs, up to `CERT_MAX`) is held in memory; on the device it is stored in IndexedDB (`vasa-files` / `cert`, key = record id), and `persistLocal` writes the record without it once `certMoved` has the id. `S.certN` is the page count, so opening a record knows to load (`loadCert`). Writes are verified by reading back before the pages leave the record. All access is serialised through `certDo`. Without IndexedDB the pages stay in the record. `moveOldCerts` migrates records written before 23.11.2026.

**Field photos** (24.11.2026): `S.photos = [{id, kind: "site"|"bore", b, d, t}]`; the JPEG bytes are in IndexedDB `vasa-files` / `photo` (version 3) keyed by photo id, as `{type, buf: ArrayBuffer}`. `makePhoto` scales, stamps (`stampPhoto`) and compresses to 100–300 KB; `photoNames()` builds the file names; `photoFiles()` feeds the `photos` mail option (`mailFile` may return several files). `sitePhotosCard()` ends the soil day tab and the gas survey tab; `borePhotosCard()` follows the coordinates card in the field log. `deleteDoc` removes a record's photos.

`S.coords` (soil, keyed by borehole) and `gx/gy/gacc/gt/gsrc/gday` on each gas well hold ITM coordinates; see [decisions](decisions.md#19112026--coordinates-gps).

## Change log (ISO 17025)

The app keeps a change log because the records are accredited quality records. The rules:

- **Only a change to an existing value is logged.** Typing into an empty field is not a change. Neither is focusing a field without changing it: iPad time and date fields fill themselves on focus, so a touch alone must not be logged.
- **A change is logged once it settles.** `logChange(label, from, to, key)` keeps a pending entry per key and restarts a 3-second timer (`COMMIT_MS`). Repeated edits keep the **original** `from`, stored raw (array, boolean) so the rules can check its type. `commitChange` writes `{t, who: actor(key), label, from, to}` to `S.changes` (values flattened to strings) only if `isChange(from, to, key)`.
- **`isChange` holds the rules** (Danny, 29.10.2026, from the first round of "האם לתעד שינוי?" answers):
  1. A **first tick** of a checkbox is not a change (`from === false`): "not ticked" is a default, not a value the sampler entered. **Unticking** is logged.
  2. A correction of an existing value is logged; a first entry into an empty field is not.
  3. **Analyses** (keys ending `.tests`): adding is not a change; removing an analysis that was already chosen is logged.
  4. **Deleting an empty custody row** (`rowHasData` false: no name, depth, PID, tool, packs, note or analyses) is not logged — `deleteRow` skips `logChange`.
  5. Signatures, handover fields and the sketch are always logged (they go through the normal "existing value changed" path). **Once any lab has signed** (`labSignedAny()`), rules 1 and 3 no longer apply: every tick and every added analysis is logged.
- **Copied values and defaults are not changes.** When a new log row inherits the borehole, time, soil or colour, those keys go into `sample.auto`; so do the defaults (odour, tool, packs, type) and `storage.tempOk`. The first edit of such a key removes it from `auto` without logging.
- **Pending changes are flushed** (`flushChanges`) before switching records and on `pagehide`, so a change lands in the right record.
- Unticking, signatures ("signed" / "cleared"), the sketch, deleting rows with data, locking and reopening are all logged.
- `actor(key)`: in a soil record, `head.s1`. In a gas record, keys `gas.inst.*` and `sig.gi` → the installation sampler; anything else → the sampling sampler, or the installation sampler until one is chosen. Lock / reopen entries use `actor()`.
- The log cannot be edited or deleted from the UI. `viewHist` shows it, newest first.

**Learning period — "האם לתעד שינוי?" (`ASK_LOG`, from 22.10.2026).** When `logChange` sees a change that will be logged (`isChange(origin, to, key)`) and the key has no question pending yet, `askLog` queues an in-app question. Questions show one at a time (`askQueue`, `nextAsk`), and the dialog can't be dismissed without an answer. Rules:
- **The answer never decides whether the change is logged.** `commitChange` logs exactly as before and adds `ask` ("כן" / "לא" / "" if not answered yet) and `k` (the change key, e.g. `head.calLab` or `<sample id>.tests`).
- If the 3-second commit happens before the answer, `q.entry` points at the logged entry, and the answer is written into it and saved.
- `shown()` shows booleans as "מסומן" / "לא מסומן" in the dialog only. The log still stores `true` / `false`.
- `askAnswers()` collects every answered change from all records on the device. `exportAnswers()` delivers them as a UTF-8 CSV with a BOM through `offerFile`.
- `viewHist` shows "לתעד: …" per entry and a card with the export button.

First round analysed 29.10.2026 (one sampler, 67 answers) → the `isChange` rules above. The question stays on until the other samplers' answers arrive; then check them against the rules and set `ASK_LOG = false`. Keep `ask` / `k` on old entries.

Setters that log: `setHead(k, v, label)`, `setSub(obj, k, v, label, key)`, `setSample(sm, k, v, label)`, `setSplit(sm, k, v, label)`, and `setColor`. Use them for any new field.

**Lock** (its own card, "נעילת הרשומה"): "נעל וסגור" is enabled only when every lab that received samples has signed and its representative is named. That means the main lab always, and the split lab too when there are split samples (`labSigned`, `pendingLabs`). A locked record is read-only. "פתח לעריכה" asks for a reason, bumps `S.v`, logs the reopening, and unlocks.

## Records and storage

Each sampling day is a separate record. `localStorage` keys:

| Key | Content |
|---|---|
| `vasa-doc:<id>` | The full record (JSON) |
| `vasa-index` | Array of `meta()` summaries `{id, kind, title, date, client, n, locked, updated}` for the records list (`n` = samples, or wells in a gas record) |
| `vasa-current` | Id of the record that was open last |
| `vasa-day` | Legacy single-record key from the first prototype. Migrated by `migrateOld()` on first run, then removed |
| `vasa-install-hint` | `"off"` once the iPad install hint has been dismissed |

- `save()` stamps `updated`, then `persistLocal()` writes the record and index synchronously, then re-renders. A remote push is debounced by 700 ms.
- If `localStorage` throws (quota), `storageFull` shows a red pill: "the last change was not saved". iOS gives about **5 MB per origin**, and signatures and sketch images are the bulk (certificate pages are in IndexedDB). While `storageFull`, `switchTo` refuses to leave an unsaved record and returns false — callers must check it.
- Deletion and storage: `deleteDoc` (`canDelete`: any record on this device except the open one), `checkStorage` / `cleanupPlan` (80% → 50%, offers only `canOffer`: older than 45 days), `storeState`. The quota is not exposed by the browser: 5 MB is assumed, counted as the browser does (two bytes per character once a value has a non-Latin character), corrected downwards when a save fails (`vasa-cap`) and to 10 MB when more than 5 MB fits. The change log of deleted records is in IndexedDB `vasa-files` / `gone`. See [roadmap](roadmap.md#storage-capacity).
- **"שמירה ורשומה חדשה"** saves the open record and opens `newDocDialog`: soil, gas full (installation and sampling), or gas sampling-only. A pristine soil record (`updated === ""`) is never stored. A new gas record is stored at once (still pristine) so a restart reopens it as gas; `switchTo` drops a pristine stored record (`dropLocal`) when leaving it.
- The record title is built by `docTitle()`: `site · date · day letter · sampler 1`, or for gas `site · גז קרקע · date · sampler`.
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
- Sheets: day details (key/value), field log, chain of custody, split custody (only when there are split samples), and **"תיעוד שינויים"** (always last).
- **Change-log sheet** (Danny, 29.10.2026, in answer to ISRAC's traceability requirement): `S.changes` oldest first — time (`toLocaleString("he-IL")`, as in the answers CSV), who, change, old value, new value. Booleans go through `shown()` ("מסומן" / "לא מסומן"), empty values show "ריק". The internal `ask` and `k` are left out. With no changes the sheet has one row, "לא נרשמו שינויים". This is the only copy of the log that leaves the iPad.
- The details sheet lists the lab, the handover and the lab receipt for each custody. The split ones are prefixed "פיצול — ".
- **Analysis totals:** each custody sheet ends, after a blank row, with a "סה״כ אנליזות" row. It holds the count of each analysis under its column, and the total plus the number of samples in the notes column. The row sits **outside** the autofilter range (`filterRows`), so sorting or filtering doesn't move it. The style is 6 (`XS.total`).
- **Analysis summary per lab** at the end of the details sheet: for each custody that has rows (`custodyRows(false)`, then `custodyRows(true)`), a header row (lab type + `labName`), one row per analysis in `allTests()` with its count, then "סה״כ אנליזות" and "מספר דגימות" as numbers. A parallel `kinds` array gives each details row its style (`sec` label, `an` cell, `tot` total).
- All sheets are `rightToLeft`. Table sheets have a frozen header row and an autofilter.
- `xnum()` stores numeric strings as numbers.
- Style 5 (`XS.num`) gives numbers **general** alignment, because in an RTL sheet `horizontal="right"` puts numbers on the left (verified in Excel).
- Tool and type are written as words (שרוול / צנצנת, חטף / מורכב), not form codes.


**Gas records** use `gasWorkbookSheets()` (`buildXlsx` picks by record type): "פרטי הסקר" (shared details, an installation section in full mode — noting an imported installation —, a sampling section, sample/QC counts, handover per lab, notes), "התקנה" (form 59.1 columns, full mode only), "שרשרת משמורת" and, with a split, "משמורת פיצול" (form 59 columns, from `gasCustodyRows`), and the change log (`changesSheet()`, shared with soil). File name "נתוני דיגום גז קרקע <site> <date>" (`gxlsx`).
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
   - Body: greeting; site, address, date, client, samplers and sample counts; the handover status of each custody that has rows (`handoverLines()`: signed by the lab when both `sigs[by]` and `sigs[lab]` exist, else "not yet received, a lab-signed copy will follow"); the list of attached files; signed with sampler 1, the company name and the website.
3. **"פתיחת המייל"**:
   - If `navigator.canShare({files})` is true, `navigator.share({files, title: subject, text: body})` opens the OS share sheet. The user picks Mail or Outlook, which opens a new email with the attachments and body.
   - Otherwise (no file sharing, e.g. desktop Firefox, or Chromium in some contexts) there's a fallback: a download link per file, plus a `mailto:` link with the subject and body, and the user attaches the files by hand.

Limits of the share sheet:
- The recipient cannot be pre-filled.
- **Subject** (Danny, 09.11.2026): "מסמכי שדה מיום דיגום <date> <site>". **Outlook on iOS ignores the share `title`** and takes the first line of `text` as the subject (Rami's email of 08.11.2026 arrived as "שלום,"). So the body's first line *is* the subject, followed by a blank line and "שלום,". Keep it that way if you change the body.

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
