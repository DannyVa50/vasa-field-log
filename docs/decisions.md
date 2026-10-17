# Decision log

Product and technical decisions, newest first. "Danny" means the owner's decision; the rest are engineering choices made within his requirements. Before reversing anything here, ask.

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
