# Decision log

Product and technical decisions, newest first. "Danny" means the owner's decision; the rest are engineering choices made within his requirements. Before reversing anything here, ask.

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
