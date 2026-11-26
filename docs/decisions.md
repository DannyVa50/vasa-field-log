# Decision log

Product and technical decisions, newest first. "Danny" means the owner's decision; the rest are engineering choices made within his requirements. Before reversing anything here, ask.

## 26.11.2026 — Full review: fixes

An independent code review of 23–26.11 changes plus end-to-end runs (upgrade from the 23.11 version, reload, real GPS dialog, locked record, installation export → import) found and fixed:
- **"-27" printed as "27-"** on form 59 (right-to-left canvas): the canister pressure cells are drawn left-to-right. Positive values print byte-identical to before.
- **A photo missing on this iPad blocked the whole email** (e.g. a record opened from the shared database, which carries the photo list but not the images): missing photos are skipped and the sampler is told which.
- **Photos of a renamed borehole or a deleted well were invisible but still emailed**: they are shown at the end of their card ("לא ביומן" / "באר שנמחקה") with "הסר".
- **A touch while scrolling filled a date field with today without saving it**: undone if the field did not get focus.
- **IndexedDB upgrade blocked by another open tab of the old version**: connections close on `versionchange`.
- **A photo finished processing after the record was locked**: discarded.
- Not changed (product decisions, noted): any record except the open one can be deleted, also one open in another tab; the image stamp keeps the site name at capture time while file names follow the current site name.

## 26.11.2026 — Change-log rules from the answers; the question is turned off

- **The "האם לתעד שינוי?" question is off** (Danny): `ASK_LOG = false`. The answers already collected stay on the devices and can still be exported.
- **Answers analysed** (7 records from Oran, 11–25.11.2026, soil and gas): 56 logged changes, 53 "כן", 3 "לא". Every field category answered "כן" stays logged: well and blank sampling fields, canister number and volume, times, names, site and address, accreditation, certificate pages, sampler and lab signatures, soil borehole / depth / moisture / packs.
- **New rule 6** (from the answers): re-signing or clearing the **handover signature** (`sig.by`, `sig.bySplit`) **before that lab's representative has signed** is not logged. Both "לא" answers were this case (the same record, a minute apart, before the lab signed). Once the lab has signed, every signature change is logged as before.
- **Not changed:** unticking a sample for custody (`toCoc`) stays logged — one "לא" and one "כן", no clear rule.

## 26.11.2026 — Field requests: calendar, canister vacuum, GPS, tube defaults

- **Calendar opens on today** (Danny: on the iPad every date picker opened in August). An empty date field gets today's date the moment it is touched (touchstart / mousedown / focus), before the picker opens; closing the picker without a change keeps today, as the iPad already does with time fields. A first entry, so not logged. Not reproducible on a desktop: iPad check needed.
- **Canister pressure is shown negative** (Danny: it is a vacuum; the sampler types the number without a minus). Canister start / end, split and blanks: a positive number typed is stored and shown as negative ("28" → "-28"), so the screen, forms 59 and the Excel show "-28" (`txt` option `neg`). The 26–30 / 3–5 checks compare the value without its sign. Values saved before 26.11.2026 stay as they were. The leak test (shut-in) is unchanged (Danny).
- **GPS keeps the more accurate point** (Danny): a new reading replaces a GPS point only when its accuracy is smaller; otherwise the old point stays and a message says so. A typed point has no accuracy and is replaced.
- **Tube defaults** (Danny: "the faded grey should be the default"): installation tube type "טפלון", tube diameter "1/4 אינץ׳"; sampling-only tube "טפלון 1/4 אינץ׳". In `auto`, like the soil defaults. Records saved before keep their values. The other grey hints are units or examples (in/hg, ppm, °C, SG-1, ק1) and stay hints.

## 24.11.2026 — Soil gas: one photo per well

- **One photo per well** (Danny), in the installation tab (sampling-only and imported records: in the sampling tab). Stamped with the site, the well name and the date; file "<site> <well> <ddmmyy>.jpg"; attached with the other photos. Same rules as borehole photos (re-shoot not logged, removal logged).
  - Engineering: the photo is keyed to the well id, not its name, so renaming a well keeps the photo (the name already burned into the image stays as it was). Photos stay on the iPad that took them: an imported installation arrives without them.

## 24.11.2026 — Field photos: site and borehole

- **Site photos** (Danny): at the end of the day tab (soil) and the survey-details tab (soil gas), as many as wanted. Stamped with the site name and the date.
- **Borehole photos** (Danny): one per borehole in the soil field log ("אחד לכל קידוח"). Stamped with the site name, the borehole number and the date. Danny asked for "שם דגימה" on the photo; with one photo per borehole the borehole number is what identifies it.
- **Size 100–300 KB** (Danny): scaled to at most 1600 px on the long side, JPEG quality stepped down from 0.82 until ≤ 300 KB (smaller scale if needed), and up to 0.95 while < 100 KB. Measured on real 5–39 MB camera photos: 171–172 KB at 1600 px.
- **File name** (Danny): "<site> <ddmmyy>.jpg"; borehole "<site> קידוח <n> <ddmmyy>.jpg"; same name again → " (2)", " (3)".
- **Attached to the email as image files** (Danny): one option "צילומים — JPG", ticked, in soil and in both gas days.
- Engineering choices:
  - The date on the photo and in the file name is the day the photo was taken (in soil normally the record date).
  - A site name is required before taking a photo, because it is burned into the image.
  - Images live in IndexedDB store `photo` (database version 3); the record holds only `photos: [{id, kind: "site"|"bore", b, d, t}]`. Photos are not sent to the shared database. Deleting a record deletes its photos.
  - Adding a photo is a first entry and a borehole re-shoot replaces the photo; neither is logged (re-shoot: Danny). Removing a photo is logged and confirms through the in-app dialog.
  - A borehole photo stays with the record if the borehole is renamed in the log (it is still emailed, under the old number).

## 24.11.2026 — Soil coordinates: once per borehole, Excel only

- **Once per borehole** (Danny): in the Excel field-log sheet the coordinates are printed only on the first row of each borehole; the borehole's other rows leave the coordinate cells empty. Before, every row repeated them.
- **Still Excel only** (Danny, reconfirmed): not on form 57 or any other form.

## 24.11.2026 — Samplers delete records at any time

- **Delete any record at any time** (Danny), replacing the 45-day limit of 23.11 for the "מחיקה" button in the records tab. Still one by one, never the open record, only records stored on this device, with the same confirmation ("make sure the documents are in the client folder in the cloud", cannot be undone) and the change log kept in IndexedDB `gone`.
  - Engineering: the 80% storage prompt still offers only records older than 45 days (`canOffer`); that was not part of the request.

## 24.11.2026 — Soil defaults: odour, sampling tool, packs, storage temperature

- **Defaults** (Danny): field log odour "לא" (Danny wrote "אין"; the list is "לא / כן / חזק" and was not changed); chain of custody and split custody: sampling tool "צנצנת", packs "1"; storage temperature 4±2°C "תקין".
  - Engineering: defaults are in `auto`, like `stype`, so changing one the first time is not logged; after that every change is. They apply to new samples and new added custody rows; existing records keep their values. A duplicate still copies the source row's tool and packs.
  - The storage temperature is one field for both custody forms, so "תקין" now prints on form 33.1 and on the split form even when the storage section is otherwise empty.

## 23.11.2026 — Soil gas: purge rate, purge volumes per well, 1.4 L canister

- **Purge rate 100–200 ml/min** (Danny), replacing 150±10 of 16.11; no other message about the rate. WI 40002 clause 9.8.4.3 still says 150±10.
  - Engineering: the purge-time check followed the 150 column of appendix C and would have raised a false error at other rates, so it now uses the 100 / 150 / 200 tables (read from the document; 150 unchanged), inversely scaled between them, and scaled by the number of volumes chosen.
- **Purge volumes per well, 3 or 5** (Danny). The sampling-day value is the default for all wells. Form 59 has one cell for it and stays as is: when wells differ the cell prints "3 / 5" and each row's value goes in its notes; the Excel custody sheet gets a column. One value for all wells prints exactly as before. A warning appears only for fewer volumes than the depth requires (3 to 1.5 m, 5 deeper — WI 9.8.4.2, MoEP guidelines).
- **Canister volume 1.4 L** added (Danny), for wells, splits and blanks.

## 23.11.2026 — Screen jumping while typing, and device storage full (field report)

- **Cause of the jump:** every field commit rebuilt the whole section synchronously during blur, replacing the field just tapped; the 3-second change-log commit did the same to a field being typed in, and the uncommitted text was lost. The canister certificate thumbnails, which have no height until decoded, moved everything below them on each rebuild.
- **Fix:** while a field has focus, or the render came from a field, the rebuild is deferred and done *around* the focused field (`patchAround`): it and its ancestors stay, everything else is replaced, and the scroll is compensated. Applies to soil and gas. Forms, Excel and email were compared byte for byte with the deployed version: identical.
- **Storage full:** a photographed certificate page is about 0.5 million characters (the 18.11 estimate of 130 KB per page was measured on a synthetic image and was wrong), against about 5 MB for all of `localStorage`. The report did not come with access to the iPad, so this is the probable cause, not a confirmed one. Certificate pages moved to IndexedDB, with a verified one-time migration.
- **No silent loss:** with storage full, leaving the record, starting a new one, or refreshing for a new version used to discard unsaved changes while saying the record was saved. Now the app stays in the record and says so.
- **Deleting records from the iPad** (Danny): the field documents are kept in the client folder in the cloud; the iPad copy is for answering clients in the field. A sampler can delete records one by one, a month and a half (45 days) after the work. At 80% of the storage the app asks to delete old records down to about 50%.
  - Engineering choices: age counts from the later of the record date and the last edit, so a mistyped date (Kfar Hess, 18.08) does not make a fresh record deletable; the open record and records younger than 45 days are never offered, also in the 80% prompt; unlocked records are offered and marked. The prompt lists the records (oldest first, each can be unticked), appears on opening, on switching records and when a save fails, and after "לא עכשיו" not again until the next day.
  - **The change log survives**: in soil it is only in the Excel, which is not ticked by default, so it may not be in the client folder. `deleteDoc` stores it in IndexedDB and reads it back first; if that fails nothing is deleted. Exported from the records tab.
  - Closing the app no longer counts as an edit (`persistNow`), so reading an old record does not make it new.
- **Excel ticked by default in the soil email** (Danny): the change log is only in the Excel, so it reaches the client folder.
- **ITM parameters corrected.** The app used an outdated WGS84/Israel 1993 parameter set taken from `templates/itm.py`; the published set for EPSG:2039 (epsg.io: 23.772,17.49,17.859,-0.3132,-1.85274,1.67299,-5.4262) differs by 1.2–1.3 m in the Tel Aviv–Hadera area, up to 2.6 m in Eilat. Points measured 19–23.11.2026 carry that difference.

## 19.11.2026 — Coordinates (GPS)

- **Requirement:** MoEP soil-survey guidelines (21.04.2016, v1) section 3.1.5: GPS marking "up to 2.5 m" accuracy. The soil-gas guidelines (v2, 2021) only ask for coordinates in the results table.
- **Per-device switch, off by default** (Danny): a browser cannot tell a cellular iPad (GPS) from a Wi-Fi-only one (network location). The switch lives in localStorage (`vasa-gps`), not in the record. Off = no measure button at all; the coordinates card still shows when a record already has coordinates.
- **Measurement:** `watchPosition` with high accuracy for up to 30 s; the reading with the best reported accuracy is kept. Converted to ITM (EPSG:2039) in the app — Helmert + TM; parameters corrected 23.11.2026, see above. Stored as whole metres, plus accuracy, time and source (GPS / manual). Warning above 2.5 m.
- **Where:** soil — one point per borehole (`coords`, keyed by borehole number). Gas — per well (`gx/gy/gacc/gt/gsrc/gday`), on both the installation and sampling days (Danny); measured at installation → shown on sampling, no re-measure. Coordinates travel in the installation data file; in an imported record those measured at installation are locked; a point measured on sampling day is not overwritten by a later installation file without coordinates.
- **Output** (Danny): Excel only. Soil — the field-log sheet. Gas — by the day the point was measured (`gday`): installation → the installation sheet; sampling day (including sampling-only records) → the main custody sheet (not the split sheet). Columns are headed "רשת ישראל החדשה (ITM)" and are added to a sheet only when it has coordinates, so existing files are unchanged. Never on the forms (no field for it; forms are fixed).
- **Change log** (Danny): GPS measurements are not logged at all; a manual edit of an existing value is.
- Pilot: one Bad Elf Flex Mini Standard ordered 19.11.2026 to test against known points.

## 18.11.2026 — Soil gas after the first field use

Reviewed the first two real surveys (Kfar Hess, Tal Shahar). Danny approved only these changes:

- **TO-15 warning** (Danny): a well with a canister number but TO-15 unticked shows a warning, like IPA. At Kfar Hess TO-15 was unticked by mistake on the first well.
- **Canister cleaning certificate** (Danny): the certificate from the lab is filed with the survey. The sampling tab has a card to photograph each page; the app turns the photo into a grayscale "scan" (black point at the 1st percentile, white point at the 90th). The pages become a separate PDF (A4 width, height by aspect) offered in the email. Pages are kept out of the day document (`canCert`, remote doc `days/{id}/shot/cert`), like the sketch photo; up to 6 pages of ~1600 px. Adding a page is a first entry (not logged); removing one is logged.
- **Record order:** Rami saw the Kfar Hess record at the bottom of the list. The list was already sorted by date, newest first. The record sat at the bottom because its sampling date had been set to 18.08 by mistake. No change was made.
- **Files per day** (Danny): at the end of the installation day only form 59.1 and the installation data file can be sent. At the end of the sampling day: form 59.1, custody form 59 (and the split form when there is one), Excel, and the cleaning certificate when there is one, all ticked by default. The sampling day starts when a sampling date is entered; an imported record and a sampling-only record are always on the sampling day. The email subject follows the day, which also fixes the Tal Shahar email (installation sent with an empty form 59, so it went out as a sampling email with no date).
- Not approved for now: date-sanity warnings and a missing-signature reminder.

## 16.11.2026 — Active soil gas (forms 59.1 and 59), stage 1

Danny asked to extend the app to active soil-gas surveys: well installation (form 59.1, edition 6) and sampling (form 59, edition 11). Sources: the two forms, WI 40002 (edition 14) with appendices A/B/C, and the Ministry's active soil-gas guidelines (version 2, 04.07.2021). Decisions:

- **Same app, a record type** chosen when a record is created: soil, or soil gas (Danny approved extending the app rather than a separate one).
- **One record per gas survey** covering installation and sampling, even on different days (Danny).
- **Installation and sampling are sometimes on different iPads / by different samplers** (Danny). Planned: the installation email carries a third data file, and the second iPad imports it ("ייבוא התקנה": save to Files, pick in the app). The imported installation part is locked, carries an integrity code, a duplicate import is warned, and the import is logged. Not built yet (stage 2).
- **Sampling without import must also work** (Danny): a "דיגום בלבד" record where the sampler fills only what form 59 holds — site details, the single installation date in the header, probe number and depth per row. In this mode there is **no equilibrium-wait check and no purge-time check** (the sampler's responsibility, Danny).
- **Forms 59 and 59.1 are used exactly as given, with no new editions and no added fields** (Danny, emphatic). The app collects only what the forms hold. Gaps against the guidelines (installing/sampling lab names, pressures at three times, total purge volume, per-well installation date, GPS device type) are not collected.
- **Scope:** permanent wells only at first (Danny). **Split** to a secondary lab when needed (Danny).
- **Rules where the sources disagree** (Danny): shut-in test 7.5–15 inHg (WI 9.8.3.2 and the guidelines; appendix B says 7.5–20); purge flow 150±10 ml/min (WI 9.8.4.3; WI 8.2.3 and appendix B allow wider), so purge minutes come from the 150 ml/min table of appendix C; the cement layer (top 15 cm) is dropped from the app (removed from the WI in 2021; still in appendix B and on form 59.1, where its column prints empty); rain: wait 5 days after ≥12 mm in 24 h (guidelines and WI 10.13.6; WI 9.3.2 says 7), shown as a reminder only.
- Engineering choices for appendix C lookups: a depth between rows uses the next deeper row; 1–1.5 m uses the 1.5 m row; 1.75" (in appendix A but not C) uses the 2" column. All err towards a longer purge.
- Stage 2 engineering choices (16.11.2026): the installation data file is JSON with a SHA-256 integrity code; a newer file for an already-imported installation updates that record field by field, logged, rather than creating a second record; drilling methods "דחיקה ישירה – גיאופרוב" / "מקדח ידני" / other, and the canister supplier from the labs list (approved by Danny 16.11.2026).
- **Email subjects (Danny, 16.11.2026):** "מסמכי שדה מיום התקנה גז קרקע <date> <site>", as in soil; the sampling email follows the same pattern, "מסמכי שדה מיום דיגום גז קרקע <date> <site>".
- Stage 3 engineering choices: a card per well rather than a table (form 59 has 16 columns); duplicate = a tick on the well (lab duplicate from the same canister, guidelines), split = a second canister on the same well; QC counted on wells with a canister number; the form-59 box "per the Ministry's active soil-gas guidelines" is always ticked; ranges in on-screen hints are written in words ("בין 26 ל-30") because "26–30" reverses in right-to-left text.
- **Change-log "who" in a gas record** is the sampler of the day the change belongs to: installation fields and the installation signature → the installation sampler; everything else → the sampling sampler, or the installation sampler until one is chosen.

## 09.11.2026 — Email subject

- **Subject: "מסמכי שדה מיום דיגום <date> <site>"** (Danny), e.g. "מסמכי שדה מיום דיגום 08.11.2026 ארטיק נס ציונה".
- Rami's email of 08.11.2026, sent through Outlook on the iPad, arrived with the subject "שלום," — the body's first line. Outlook ignores the share-sheet `title`. Engineering choice: the subject is now also the body's first line, so it's right in Outlook and in any app that does use `title`.

## 29.10.2026 — Change log in the client Excel (ISRAC traceability)

- ISRAC (Natasha Ben Avraham, 04.08.2026) asked that changes to technical records made on a tablet be traceable, even before the record is closed, as with paper records. A review against ISO/IEC 17025 §7.5.2 found the app meets the core requirement (original value, new value, time, what changed, from the first moment, not deletable in the app) with gaps: (1) the log lived only on the iPad, (2) "who" is always sampler 1, not the actual editor, (3) for signatures / sketch / photo only "exists / signed / cleared" is kept, not the previous image, and strokes added to an existing sketch aren't logged.
- **Danny's decision for now: gap 1 only.** The client Excel gets a "תיעוד שינויים" sheet with the full log, so it leaves the iPad with every daily email.
- **Gaps 2 and 3, and a separate change-log PDF, are deferred.** Danny asked to be asked again about them at the next update.

## 29.10.2026 — Change-log rules from the learning period, VOC-in-liner warning

- **New change-log rules** (Danny approved, after the first round of "האם לתעד שינוי?" answers: one sampler, 67 answers). Half the questions came from simply ticking a sample for the custody: the old rule "a first entry is not a change" never applied to checkboxes, because an unticked box is `false`, not empty. The sampler answered "לא" to every first tick once he got used to the question, "כן" to every untick and every correction of a measured value. Rules:
  1. A first tick is not logged; unticking is. This includes the morning checklist (Danny: the tick itself is the record).
  2. Correcting an existing value is logged (unchanged).
  3. Adding an analysis is not logged; removing one is.
  4. Deleting an empty custody row is not logged; a row with data is.
  5. Signatures, handover fields and the sketch are always logged, whatever a sampler answers. Once a lab has signed, rules 1 and 3 stop applying: every tick and added analysis after the signature is logged.
- The question stays on (`ASK_LOG = true`) until the other samplers' answers come in; they're checked against these rules before it's turned off.
- **Warning: VOC or TPH GRO with a liner** (Danny). VOC must be sampled into a jar + vials, never a liner (ISRAC finding, 22.10.2026); Danny extended it to TPH GRO, which is volatile too. A custody row with VOC or TPH GRO and tool "ליינר" is highlighted, and a red note at the top of the custody tab names the rows. It warns, it doesn't block.

## 29.10.2026 — Form 33.1, edition 22

- **From 29.10.2026 the app prints the chain of custody on edition 22** (Danny), valid from 15.10.2026. `forms/form-33.1.*` were replaced and `F33` was re-measured from the new PDF. Everything below the logos moved up (about 11.5 pt on page 1, 26.5 pt on page 2), the "אתר / מעבדה / תאריך" line on page 2 moved, and the ISRAC logo is larger (its blank-out box grew). Old records print on edition 22 too.
- **The Ministry-approval check-boxes changed** (Danny): "הסקר בוצע לפי תוכנית דיגום מאושרת על ידי המשרד להגנת הסביבה, על פי הצהרת יועץ" (new key `planDeclared`) and "…, התוכנית הוצגה למעבדה" (`planShown`, same key, new wording). Engineering choice: the edition-21 "תוכנית דיגום מאושרת" (`planApproved`) is **not** migrated into the consultant-declaration box, because it never said how the approval was attested. It stays in old records and is no longer shown or printed.
- **TPH GRO became a fixed column** (the form's change): 8 fixed analyses and 4 open columns. `normalize()` removes a fixed name from the open columns and compacts the rest, so records that typed "TPH GRO" into an open column keep their ticks, now under the fixed column. More than 4 open names are kept in the data, but only 4 fit on the form.

## 22.10.2026 — Analysis summary per lab in the Excel

- **The Excel's day-details sheet ends with an analysis summary per lab** (Danny): one block for the primary lab and, when there are splits, one for the secondary lab. Each block has the lab's name, the count of every analysis type (zeros included, so "how many PH" is answered too), the total, and the number of samples. Free rows and duplicates count, like the custody sheets.
- Engineering: the total and the sample count are separate number cells. A text such as "28 אנליזות ב-10 דגימות" starts with a digit, and Excel then shows it in the wrong direction in an RTL sheet.
- The same bug was in the custody sheets' total text, which now starts with a Hebrew word ("סה״כ 28 אנליזות ב-10 דגימות"). Verified in Excel.

## 22.10.2026 — Orange, handover status in the email

- **"כתום" (orange) added to the field-log colours** (Danny).
- **Learning period for the change log: "האם לתעד שינוי?"** (Danny). Before every change the app logs, the sampler is asked whether it should be logged. The goal is to learn from the answers which changes really need logging, and then update the rules. Danny's choices:
  - **The change is logged whatever the answer.** The answer is stored next to it (`ask`, plus the field key `k`). ISO 17025 traceability is never weakened during the learning period.
  - **Ask only about what is logged today**: a changed existing value, a tick/untick, a signature, a deleted row. First entries are not asked about (that would mean a question on almost every field).
  - **Collecting:** a "שליחת תשובות התיעוד" button in the change-log tab exports every answer on the device as one CSV (with a BOM for Excel), which the sampler emails to Danny.
  - **Danny turns it off** in a later version (`ASK_LOG = false`). Samplers can't turn it off.
- **The email body states the handover status of each chain of custody** (Danny). Handed over = the sampler signed the handover **and** the lab representative signed the receipt. Danny's wording:
  - handed over: "שרשרת משמורת חתומה ע״י מעבדה ראשית <lab> - הדגימות התקבלו במעבדה ב-<date>." / split: "שרשרת משמורת פיצול חתומה ע״י מעבדה משנית <lab> - הדגימות התקבלו במעבדה ב-<date>."
  - not yet: "הדגימות עדיין לא התקבלו במעבדה <lab>, ומסמך חתום ע״י המעבדה האנליטית יועבר בהמשך." / split: "דגימות הפיצול עדיין לא התקבלו במעבדה המשנית <lab>, …"
  - The lab name has no brackets. The split custody gets its own line when it has rows. The line is written whatever files are attached, because the client needs to know where the samples are.

## 21.10.2026 — Custody-only rows, duplicates, stable time picker

- **Free rows in the chain of custody and the split custody** (Danny): an "הוסף שורה" button, like the field log's, adds a row that exists only in the custody form. The sampler fills everything in it, including the sample id, depth, time and PID. It doesn't appear in the field log.
- **Duplicates (חזרה) by long press** (Danny): holding a custody row for 3 seconds opens "האם לבצע חזרה?". On confirm, a new row opens right under it with "חזרה" after the sample id. Everything is copied **except the analyses**, which the sampler picks for the duplicate. Engineering choices:
  - The row fills with colour during the press, so the sampler knows to keep holding.
  - A press on an input, select or button doesn't count. Moving the finger more than 12 px (scrolling) cancels.
  - A duplicate can't itself be duplicated. Locked records ignore the press.
  - Duplicates and free rows can be deleted (✕), after an in-app confirmation (not `confirm()`, which some hosts block). The deletion is logged.
- **The QC note now counts the duplicates** instead of asking the sampler to check them by hand. It warns when a duplicate is marked for VOC or TPH GRO (duplicates aren't sent for those).
- **Time and date fields save when the picker closes** (bug from the field). On the iPad, the time wheel fired `change` on every spin. Every save rebuilt the screen, which replaced the input under the open picker, so the picker jumped. `render()` is also deferred while a time/date input has focus, because a change-log commit 3 s after an earlier edit also re-renders.

## 17.10.2026 — Labs, split handover, analysis totals

- **Lab pick list** (Danny): בקטוכם, אלכם, אמינולאב, מכון הנפט, or "אחר" with a typed name. It applies to both the main lab and the secondary (split) lab. It is shown in the handover tab and in the custody tabs, and both are the same field. Records with a free-text lab from before the list open as "אחר" with that name, so the printed name doesn't change.
- **The split custody gets its own handover and lab receipt** (Danny): splits go to a different lab, whose representative signs separately. The split's PDF prints the split handover and signatures. The main custody keeps its fields and change-log labels unchanged.
- **Locking requires every lab that received samples to have signed**: the main lab, plus the split lab when there are splits. The lock moved to its own card, "נעילת הרשומה", after the receipts. This was an engineering choice that follows from the separate receipts. Reopening with a reason still works if the split lab signs after locking.
- **Excel: analysis totals per type** (Danny): a "סה״כ אנליזות" row under each custody sheet, kept out of the filter range.

## 17.10.2026 — From prototype to field app

- **Installable PWA hosted on GitHub Pages; the repo is made public** (Danny). Before this, the app was copied via an external SSD to the iPad and opened in Documents by Readdle every time. The considered alternatives were:
  - GitHub Pages with a paid plan, to keep the repo private
  - Cloudflare Pages / Netlify, which need a new account
  - a native app, which needs a Mac, an Apple developer account and App Store/TestFlight distribution

  Public Pages was the simplest: free, no new account, auto-deploy on push. The repo history was checked first: it holds no field data, emails, phone numbers or keys.
- **Offline: cache-first page plus an explicit update check** on load and whenever the app returns to the foreground, with a user-tapped "new version" pill. The app never reloads by itself, so a sampler mid-entry is never interrupted. Updates compare content, so deploys need no version bump.
- **Email through the OS share sheet** (`navigator.share` with files). A web page cannot attach files to an email by itself. The share sheet → Mail/Outlook gives a new email with the attachments and body. The flow takes two taps: "prepare" builds the files, and "open the email" shares, because iOS requires the share to come straight from a tap. Fallback where file sharing is unsupported: download the files plus a `mailto:` link with the subject and body.
- **The user chooses which files to attach each time** (Danny). The options are the field log, chain of custody, split custody (when relevant) and the client Excel. Defaults: the PDFs that have content on, Excel off.
- **"Send by email" is the primary (filled) button** in the files card. Excel became an outline button like the PDFs, so that only one button stands out.
- **Language** (Danny): everything the end user sees is Hebrew. Engineering and AI documentation is English. Folder and file names are English.
- **Records stay per device for now.** Sync between devices (the office handover route) is deferred ([roadmap](roadmap.md)).

## 14.10.2026 — File names and Excel

- **File names** (Danny): `<יומן שדה | שרשרת משמורת | שרשרת משמורת פיצול | נתוני דיגום> <site> DDMMYY`. The date is the sampling date, with no separators.
- **Excel numbers use general alignment.** In an RTL sheet, `horizontal="right"` puts text on the right but numbers on the **left**. Verified in real Excel.

## 13.10.2026 — Print on the official forms

- **The PDFs are the official forms 57 and 33.1 themselves.** The Word export is the background, and the values are drawn into the cells. The header, logos, declarations, legend and footer are identical to the original.
- Danny's rules:
  - Print only the pages the samples need. Add a continuation page when rows or notes overflow, and update "page X of Y" and the margin row numbers.
  - **"*** סוף דו"ח ***" must always end every chain of custody**: on the last page, including when there is only one page.
  - **The sketch is a counted page of form 57**, with the form's header and footer.
  - **When the job is not accredited, only the ISRAC logo is removed.**
  - The day letter and the custody/split ticks are not printed.
- Tool and sample type are printed as the form's legend codes (1 / 2, ח / מ).
- **Client Excel**: one file per sampling day, for consultants who reuse the data in their own reports.

## 23.09.2026 — Separate records; PDFs generated in-app

- **Every sampling day is a separate record** with a unique id, so several teams on the same date don't overwrite each other. The prototype's single record migrates automatically.
- **PDFs are drawn on canvas in the app**, not via `window.print()`. In-app web views such as Readdle ignore `print()`, so the PDF buttons silently did nothing. The cost: the PDF is an image, and its text is not searchable.
- **The file dialog offers several delivery routes** (share, download, open), because none works in every host app.
- First and second rounds of field review were applied: field-log columns, inheritance of borehole/soil/colour on new rows, a compact log table that fits an iPad in landscape, and one high-contrast light theme with no dark mode (readable in direct sun).

## 14.09.2026 — Prototype

- **Two forms are two views of one sampling-day record.** Site, date, samplers, PID and client are entered once. A sample ticked in the field log appears in the custody form with its depth, time and PID already filled.
- **A single HTML file with no dependencies and no build step**, so it can run from a file on an iPad with no server and no reception.
- **The change log follows ISO 17025**: only changes to existing values, after they settle, with the original value. Locked after the lab signs. Reopening needs a reason.
- Built first as a Claude artifact with a shared database (`claude.use("db")`) for the office route. `build/make_standalone.py` produced a standalone copy, and is now legacy.
