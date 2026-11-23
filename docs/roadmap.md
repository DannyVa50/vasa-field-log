# Roadmap and known limits

Status as of 17.10.2026. Items are roughly in priority order. None is committed to; Danny decides.

## Active soil gas — remaining stages (started 16.11.2026)

Stage 1 (record type, shared details, installation and sampling headers, gas handover) is built on branch `soil-gas-stage1`. Remaining, in order — see [decisions](decisions.md#16112026--active-soil-gas-forms-591-and-59-stage-1):

- **Stage 2 — installation (form 59.1): built 16.11.2026, not yet tested on an iPad** (Outlook attachment → Files → "ייבוא התקנה" picker can only be tested there). Scope was: wells table (times, PID in the borehole, permeability ≤7.5 inHg at 100 ml/min, sand / granular bentonite / wet bentonite ticks, probe depth, soil profile, notes; the cement column prints empty), checks, PDF on the official form (measure coordinates), installation data file in the email + "ייבוא התקנה" on another iPad (locked, integrity code, duplicate warning, logged).
- **Stage 3 — sampling (form 59): built 16.11.2026.** Scope was: wells carried over from installation (or typed in manual mode), canister, vacuum, purge, IPA, times, canister pressure, TO-15, notes; checks (≥8 h equilibrium and purge minutes from appendix C — full mode only; shut-in 7.5–15 inHg with change ≤0.5; canister start 26–30 / end 3–5 inHg; purge flow 150±10); QC (from 10 samples: duplicate, equipment blank, air blank); split custody to a secondary lab; PDF.
- **Stage 4 — delivery: built 16.11.2026** (email and the 72-hour check in stage 3; client Excel). Scope was: handover within 72 h, email text, file names, client Excel for gas.
- **Stage 5 — pilot:** browser test, one real survey alongside paper, user guide (Hebrew), email to samplers.

## Sync between devices

**Limit:** records live only on the device that created them. The office route doesn't work across devices: the secretary can't open the field team's record on another device to get the lab's signature. The two ways that work today are (a) the lab signs on the field iPad, or (b) the iPad is brought to the office.

**Direction:** a small backend that stores records per sampling day. The code already has the seams from the Claude-artifact version: `pushRemote`, `attachRemote`, `openDoc`, `remoteIdx`, and the "במאגר המשותף" tags in the records list. Points to decide:
- **Where the data lives.** The company uses Microsoft 365, so SharePoint/OneDrive via Microsoft Graph is a candidate. Supabase and Firebase are simpler to build on.
- **Sign-in:** who can see which records, for example whether samplers see only their own days.
- **Conflicts:** two devices editing the same day offline. Today it is last-writer-wins per record.

The change log must survive a merge.

## Storage capacity

Certificate pages moved to IndexedDB on 23.11.2026 after a device filled up; the rest is still in `localStorage`, and records can be deleted after 45 days (23.11.2026). `localStorage` is about 5 MB per origin on iOS. Signatures (PNG), the drawn sketch (PNG) and the sketch photo (JPEG, ≤1000 px) take most of the space. A heavy user could fill it after some dozens of days, and then the red "האחסון במכשיר מלא" pill appears.

**Direction:**
- Move records to **IndexedDB**, which has a much larger quota and is async, with a one-time migration from `localStorage`.
- Deleting old records: built 23.11.2026 (see [decisions](decisions.md)). Records are not exported first; only their change log is kept on the device.

## Backup import

"ייצוא נתונים" exports a record as JSON, but nothing imports it. An import is needed to:
- restore a record after a device is lost or reset
- move records from the old Readdle copy, or from Safari, into the installed app
- move a record to another device by hand, as a stop-gap before sync

The import must keep the change log and add a "יובא" (imported) entry.

## Change-log rules from the learning period

Since 22.10.2026 the app asks "האם לתעד שינוי?" before every logged change (`ASK_LOG`). First round (Oren, 67 answers) analysed on 29.10.2026 → rules in `isChange` (see [decisions](decisions.md)). Next step: when the other samplers' CSVs arrive, check their "לא" answers against the current rules, propose any further change to Danny, then set `ASK_LOG = false`.

## Change-log traceability — deferred items (ask Danny at the next update)

From the 29.10.2026 review against ISRAC's requirement (see [decisions](decisions.md)). Danny asked to be asked again at the next update:
- record the actual editor ("מי מבצע את השינוי?") for changes to an earlier day's record or after a lab signature, instead of always sampler 1
- keep the previous image of a replaced or cleared signature / sketch / sketch photo, and log strokes added to an existing sketch
- a separate "תיעוד שינויים" PDF (office only, or as the last page of the field log)

## Smaller items

- **Default email recipient:** the share sheet can't pre-fill one. Possible workaround: copy an address to the clipboard, or add a `mailto:` "To" in the fallback path only.
- **Check on the iPad** whether Apple Mail takes the share title as the subject (Outlook doesn't — it uses the body's first line, which now holds the subject; resolved 09.11.2026).
- **Photos of borehole points** (planned in the prototype).
- **Automatic GPS coordinates** per borehole.
- **Split custody storage:** the split now has its own handover and lab receipt (17.10.2026). It still shares the "storage before handover" fields with the main custody. If splits are stored separately, they'd need their own storage block.
- **Sample-level `extra` and `qc` fields** exist in the data model but have no UI.
- **Searchable PDF text:** PDFs are images today. Real text would need font embedding in `pdfFromJpegs`. Low priority.
- **Other sampling types** (soil gas, groundwater) have their own forms and are not covered.
