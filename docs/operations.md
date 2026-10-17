# Operations

## Hosting

- **GitHub Pages** serves the repo `DannyVa50/vasa-field-log` (public), branch `main`, folder `/` (root).
- URL: **https://dannyva50.github.io/vasa-field-log/**
- `.nojekyll` makes Pages serve the files as they are, with no Jekyll processing.
- The site is static. **No field data ever goes to the server.** Records stay in each device's browser storage. The only things served are the app files.
- The repo being public means the app code, the blank forms and the dropdown lists (sampler names, PID serial numbers) are publicly readable. Danny accepted this on 17.10.2026 ([decisions.md](decisions.md)). Never commit field data or exports (`exports/` is git-ignored).

Pages settings can be checked with:
```bash
gh api repos/DannyVa50/vasa-field-log/pages
```

## Deploying a change

1. Make the change on a branch and test it locally (see [CLAUDE.md § Testing](../CLAUDE.md#testing)).
2. Merge into `main` and push. Pages publishes in about a minute. Watch it with `gh run list --repo DannyVa50/vasa-field-log` (the "pages build and deployment" workflow).
3. Installed devices pick up the update by themselves. The next time the app is opened or brought to the foreground with reception, the service worker downloads the new `index.html` and the pill **"גרסה חדשה מוכנה — רענון"** appears. One tap reloads into the new version. A device that never taps keeps the old version until the app is fully closed and reopened.

**When to bump the cache version.** `SHELL` / `FONTS` in `sw.js` need a bump only when `sw.js` itself changes in a way that needs a fresh cache, for example a new file in `ASSETS` or a different cache layout. Any byte change to `sw.js` makes browsers install the new worker. Changes to `index.html`, the manifest or the icons need **no** bump: the page is checked by content, and the others are revalidated in the background.

**Data compatibility.** A new version must open every record saved by older versions. Defaults go in `blankDay()` / `blankSample()`, and upgrades go in `normalize()`.

## Installing on devices

The user-facing steps are in Hebrew in [user-guide.md](user-guide.md). The technical side:

- **iPad / iPhone**: Safari → Share → "הוספה למסך הבית" (Add to Home Screen). It runs standalone, with its own storage, separate from Safari's. It must be opened once with reception so the service worker can cache everything. Other iOS browsers can also add to the home screen on recent iOS versions, but Safari is the tested path.
- **Windows / Mac**: Chrome or Edge → the install icon in the address bar, or the in-app "התקנה כאפליקציה" pill.
- **Another device later**: same steps, any time. Nothing is tied to the first device. The new device starts with **no records**, because records don't move between devices (see [roadmap](roadmap.md#sync-between-devices)).
- `docs/install-qr.png` is a QR code of the app URL, for sending over WhatsApp or printing. To regenerate it:
  ```bash
  python -c "import qrcode; qrcode.make('https://dannyva50.github.io/vasa-field-log/', box_size=10, border=3).save('docs/install-qr.png')"
  ```
- **Old method (prototype):** copying `index.html` to the iPad and opening it in Documents by Readdle still works (`file://`), but with no offline cache, no updates and separate storage. Records made there do **not** appear in the installed app. Moving them needs an import feature that doesn't exist yet ([roadmap](roadmap.md#backup-import)).

## Backups

The only copy of a record is on the device that made it, plus whatever PDFs, Excel files or emails were sent from it.

- "ייצוא נתונים" (change-log tab) exports the open record as JSON, with the full change log and signatures. There is **no import yet** ([roadmap](roadmap.md#backup-import)).
- The real safeguard today is the workflow: **send the PDFs by email at the end of each day.**
- Deleting the home-screen icon, or "Clear History and Website Data" in Safari settings for this site, deletes the records on that device.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| The app shows an old version | It is cached. Bring the app to the foreground with reception and wait for the pill, then tap it. Last resort: fully close the app (swipe it away) and reopen it |
| Red pill "האחסון במכשיר מלא" | `localStorage` is full (~5 MB on iOS). The last change was not saved. Send the old days' PDFs, then remove old records (no UI for this yet, see [roadmap](roadmap.md#storage-capacity)) |
| "פתיחת המייל" shows download links instead of the share sheet | The browser can't share files (desktop Firefox, some desktop setups). Download the files and attach them to the email that opens. On an iPad this should not happen. If it does, check the iOS version |
| The email has no subject on the iPad | iOS may not pass the share title to Mail. The site and date are in the body's first line. Type a subject |
| Fonts look different offline | The app was never opened with reception after installing, so Google Fonts weren't cached. Open it once online |
| The install hint doesn't show on iPad | It shows only in Safari, over HTTPS, when the app isn't installed and the hint hasn't been dismissed (`localStorage["vasa-install-hint"]`) |

## A new edition of form 57 or 33.1

1. Replace `forms/form-57.docx` or `forms/form-33.1.docx`.
2. Export it to PDF **from Word** (Save As → PDF) under the same name in `forms/`.
3. Run `python build/embed_forms.py`. It needs `pymupdf` and `Pillow`. It re-renders the pages at 200 DPI into `FORM_PAGES` in `index.html`.
4. If any cell moved, update the boxes in `F57` / `F33` in `index.html`. Measure them in PDF points from the new export, e.g. with PyMuPDF: `page.get_text("dict")` or `page.get_drawings()` for the cell lines.
5. Check page 1 and a continuation page of each form, with long values, and with a non-accredited job (ISRAC logo hidden). Update the edition numbers in README.md and [domain.md](domain.md).

## What to check on the iPad after a change to files or email

None of these can be tested on a desktop:
1. Install from Safari (or open the installed app), turn on Airplane Mode, and confirm the app opens and records are there.
2. Generate each PDF and the Excel file → share / save to Files works.
3. "שליחה במייל" → "הכנת המייל" → "פתיחת המייל" → choose Mail. Check the attachments, the body, and whether the subject was filled.
4. Signatures and the sketch draw correctly with a finger and with an Apple Pencil.
5. Close the app fully, reopen it, and check the records are still there.
