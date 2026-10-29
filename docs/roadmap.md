# Roadmap and known limits

Status as of 17.10.2026. Items are roughly in priority order. None is committed to; Danny decides.

## Sync between devices

**Limit:** records live only on the device that created them. The office route doesn't work across devices: the secretary can't open the field team's record on another device to get the lab's signature. The two ways that work today are (a) the lab signs on the field iPad, or (b) the iPad is brought to the office.

**Direction:** a small backend that stores records per sampling day. The code already has the seams from the Claude-artifact version: `pushRemote`, `attachRemote`, `openDoc`, `remoteIdx`, and the "במאגר המשותף" tags in the records list. Points to decide:
- **Where the data lives.** The company uses Microsoft 365, so SharePoint/OneDrive via Microsoft Graph is a candidate. Supabase and Firebase are simpler to build on.
- **Sign-in:** who can see which records, for example whether samplers see only their own days.
- **Conflicts:** two devices editing the same day offline. Today it is last-writer-wins per record.

The change log must survive a merge.

## Storage capacity

`localStorage` is about 5 MB per origin on iOS. Signatures (PNG), the drawn sketch (PNG) and the sketch photo (JPEG, ≤1000 px) take most of the space. A heavy user could fill it after some dozens of days, and then the red "האחסון במכשיר מלא" pill appears.

**Direction:**
- Move records to **IndexedDB**, which has a much larger quota and is async, with a one-time migration from `localStorage`.
- Add a way to **archive / delete old records** once their PDFs have been sent. It has to respect the quality-record rules: probably export first, then delete.

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
- **Check on the iPad** whether the share title becomes the Mail subject. If not, consider putting the subject only in the body's first line.
- **Photos of borehole points** (planned in the prototype).
- **Automatic GPS coordinates** per borehole.
- **Split custody storage:** the split now has its own handover and lab receipt (17.10.2026). It still shares the "storage before handover" fields with the main custody. If splits are stored separately, they'd need their own storage block.
- **Sample-level `extra` and `qc` fields** exist in the data model but have no UI.
- **Searchable PDF text:** PDFs are images today. Real text would need font embedding in `pdfFromJpegs`. Low priority.
- **Other sampling types** (soil gas, groundwater) have their own forms and are not covered.
