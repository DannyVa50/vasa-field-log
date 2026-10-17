# Domain — what the app is for

## The company

**Vasa Ecology Ltd.** (וזה אקולוגיה בע״מ, www.vasa-eco.co.il) is an Israeli environmental field-services company. It does environmental drilling and soil, soil-gas and groundwater sampling, mostly for environmental consultants. These consultants submit soil surveys to the Ministry of Environmental Protection (המשרד להגנת הסביבה).

Sampling is accredited under **ISO/IEC 17025:2017, accreditation no. 294**, issued by ISRAC, the Israel Laboratory Accreditation Authority (הרשות הלאומית להסמכת מעבדות). Because of that, the field log and the chain of custody are **controlled quality records**:

- They are printed on the company's controlled forms, each with an edition number.
- Every change to a recorded value must stay traceable: the original value, who changed it, and when.
- A record that has been handed to the lab is closed.

This app covers **soil sampling** only: forms 57 and 33.1. Soil-gas and groundwater sampling have their own forms and are not in the app.

## Who uses it

| Role | Hebrew | What they do in the app |
|---|---|---|
| Sampler 1 (lead) | דוגם 1 | Fills the day on the iPad in the field and signs. Every logged change is attributed to sampler 1 (the app has no logins) |
| Sampler 2 | דוגם 2 | Second team member. Signs |
| Report approver | מאשר הדו״ח | Named on form 33.1 |
| Office (secretary) | המשרד / הפקידה | Sometimes hands the samples to the lab courier at the office: fills in the handover and lab-receipt fields and gets the lab signature. That requires the record to be on the office device, see [roadmap](roadmap.md#sync-between-devices) |
| Lab representative | נציג המעבדה | Signs receipt of the samples, on the iPad in the field or at the office. Their signature lets the record be locked |
| Client / consultant | לקוח / יועץ | Receives the PDFs and the Excel file, usually by email |

Planned operation: two drilling rigs plus a vacuum truck and 2–3 samplers, in 5–6 teams. Several teams can sample on the same date, so every sampling day is its own record with a unique id.

## A sampling day, start to finish

1. **Open the day** (tab "יום דיגום"). Fill in:
   - site, address, date, day letter (A on the first day at a site, B on the second, …)
   - client, client's representative, contact, who to bill
   - samplers, PID instrument, drilling rig
   - arrival time, start temperature, weather, land use, groundwater level
   - the check-marks: accredited job, readiness, calibrations, cooled storage, subcontractors, which guidelines the sampling followed
   - Samplers sign.
2. **Field log** (tab "יומן שדה", form 57). One row per sample:
   - borehole no., depth, sample name (auto: `borehole-depth`), time
   - soil type, colour (up to two), odour, moisture, PID, PID 20%, notes
   - A new row inherits the borehole, soil and colour from the row above, and the time is set to now.
   - Tick **משמורת** to send the sample to the lab, and **פיצול** to also send a split to a secondary lab.
3. **Chain of custody** (tabs "שרשרת משמורת" and "משמורת פיצול", form 33.1).
   - Ticked samples arrive with name, depth, time and PID already filled.
   - Per sample: sampling tool (jar / liner), number of containers, type (grab is the default, or composite), and which analyses (7 fixed columns plus up to 5 user-named ones).
   - Lab and notes. The lab is picked from the list (בקטוכם, אלכם, אמינולאב, מכון הנפט) or "אחר" with a typed name. The split goes to a **different lab** than the main custody.
4. **Sketch**: required for stockpile and verification sampling (work instruction 30001 §7c). Draw it on screen or photograph a paper sketch.
5. **End of day**: finish time, end temperature, field-log notes.
6. **Deviations, storage, handover** (tab "מסירה וקבצים"):
   - Deviations from the sampling plan: what changed, why it was needed, who approved.
   - Overnight storage, with the 4±2 °C check.
   - Handed over by (name, date, time, signature).
   - Received at the lab: lab (from the list), representative, date, time and signature.
   - When there are split samples: a **separate handover and lab receipt for the split**, signed by the secondary lab's representative.
   - **Lock**: possible only after every lab that received samples has signed. Reopening a locked record requires a reason, which is logged.
7. **Files**: PDF field log, PDF chain of custody, PDF split custody, client Excel. Or **שליחה במייל**: pick the files and an email opens with them attached.

## The two forms

The PDFs are the official forms themselves. The blank pages of the Word forms in `forms/` are the background, and the values are drawn into the cells.

### Form 57 — field log (יומן שדה), edition 10, A4 portrait

- **Header**: site, address, date, readiness ✓, drilling rig, arrival/finish times, start/end temperature, samplers and signatures, client, client rep, PID instrument, PID in open air, weather, calibration ✓ (lab, daily 100 ppm), cooled storage ✓.
- **Table**, 30 rows per page: borehole, sample no., depth, time, soil type (lithology), colour, odour, moisture, PID, PID 20%, notes.
- **Notes** line(s) at the bottom. Overflow continues on the last page.
- **Sketch**: an extra page of form 57, with the table area blanked out. It is counted in "page X of Y".

### Form 33.1 — chain of custody for soil sampling (שרשרת משמורת לדיגום קרקע), edition 21, A4 landscape

- **Header**: site, date, lab, bill to, address, weather, land use, groundwater level, PID instrument, sampler 1 + signature, approver, client, contact.
- **Yes/no** questions (circled): drilling by a subcontractor, sampling by a subcontractor, deviations none/some.
- **Check-boxes**: which guidelines were followed, whether the plan was approved and shown to the lab.
- **Table**: 10 rows on page 1 and 20 on each continuation page. Columns: sample id, depth, time, tool code (1 = liner/sleeve, 2 = jar), containers, type code (ח = grab, מ = composite), 7 fixed analyses (TPH D+O, ICP metals, PFAS, CR6+, PH, SVOC, VOC), 5 open analysis columns, PID, notes.
- **Storage before handover**, then **handover** and **lab receipt** with signatures.
- **"*** סוף דו"ח ***"** (end of report) must end every chain of custody, on its last page.
- The **ISRAC accreditation logo** is printed only when the job is accredited.
- The **split custody** is the same form, with the split samples, the secondary lab, and the split's own handover and lab receipt.

## Rules from work instruction 30001 that the app enforces or prompts

| Rule | Where | What the app does |
|---|---|---|
| Sample name = borehole + depth | log | Auto-filled (`autoName`), and can be overridden |
| PID ≥ 20 ppm | §3.3 | Row highlighted, plus a note suggesting VOC analysis and samples 1 m above and below to delimit the contamination (`PID_HOT`) |
| Not accredited → drop the ISRAC logo | §7b | Logo blanked on form 33.1. A warning is shown on the day tab |
| Sketch for stockpiles / verification sampling | §7c | Sketch card, printed as a page of form 57 |
| Deviations and additions | §8 | What / why / who approved. Printed in the 33.1 notes line |
| Storage temperature 4±2 °C | — | "Not OK" shows a warning that an exceptions form is required |
| QC: duplicates and splits | — | Non-blocking note on the custody tab. For n samples in custody: duplicates = 0 if n = 0, 1 if n < 10, otherwise ⌈n/20⌉; splits = 0 if n ≤ 9, otherwise ⌈n × 10%⌉. Splits are counted from the split column. Duplicates are **not** marked in the app, so the note asks the sampler to check them. Duplicates and splits are not sent for VOC or TPH GRO |

## Glossary — Hebrew ↔ code

| Hebrew | English | Code |
|---|---|---|
| יום דיגום / רשומה | sampling day / record | `S`, `blankDay()`, `id` = `day-<date>-<8 hex>` |
| אתר | site | `head.site` |
| אות היום | day letter (A, B, …) | `head.dayLetter`, `DAYS` |
| דוגם 1 / דוגם 2 | sampler 1 / 2 | `head.s1`, `head.s2`, `SAMPLERS` |
| מאשר הדו״ח | report approver | `head.approver` |
| עבודה בהסמכה | accredited job | `head.accredited` |
| יומן שדה | field log (form 57) | `viewLog`, `renderLog`, `F57`, kind `"log"` |
| שרשרת משמורת | chain of custody (form 33.1) | `custodyView("coc")`, `renderCoc(false)`, `F33`, kind `"coc"` |
| משמורת פיצול | split custody | `custodyView("split")`, `renderCoc(true)`, kind `"split"`, sample field `sp` |
| מס׳ קידוח | borehole no. | `sample.boring` |
| עומק | depth (m) | `sample.depth` |
| שם / זיהוי דגימה | sample name / id | `sample.name`, `nameAuto` |
| סוג קרקע / ליתולוגיה | soil type / lithology | `sample.soil`, `SOIL` |
| צבע · ריח · לחות | colour · odour · moisture | `color`, `odour`, `moist` |
| PID · PID 20% | photo-ionisation reading, and the 20% re-reading | `pid`, `pid20`, `head.pid` = instrument serial |
| כלי דיגום: ליינר (שרוול) / צנצנת | sampling tool: liner (sleeve) / jar | `tool`, `TOOL`, `TOOL_CODE` |
| אריזות | containers | `packs` |
| חטף / מורכב | grab / composite | `stype`, `STYPE_CODE` |
| בדיקות / אנליזות | analyses | `tests`, `TESTS`, `head.extraTests` |
| חזרה / פיצול | duplicate / split | `qcNeeded()` |
| חריגות ותוספות | deviations and additions | `S.deviations` |
| אחסון לפני מסירה | storage before handover | `S.storage` |
| מעבדה / מעבדה משנית | lab / secondary (split) lab | `head.lab`, `head.labSplit` (+ `…Other`), `LABS`, `labName()` |
| מסירה / קבלה במעבדה | handover / lab receipt | `S.handover`, `sigs.by`, `sigs.lab` |
| מסירה / קבלה — פיצול | split handover / receipt | `S.handoverSplit`, `sigs.bySplit`, `sigs.labSplit`, `HAND.split` |
| שרטוט | sketch | `S.sketch` (drawn), `S.sketchPhoto` (photo) |
| תיעוד שינויים | change log | `S.changes`, `logChange` |
| נעילה | lock | `S.locked` |
| Excel ללקוח | client Excel | `buildXlsx`, kind `"xlsx"` |
| שליחה במייל | send by email | `mailDialog` |
