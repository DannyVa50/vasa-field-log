# -*- coding: utf-8 -*-
"""Wrap the artifact body into a self-contained HTML file that runs with no
Claude runtime: every claude.use() call is guarded, storage falls back to
localStorage, and the download uses a plain blob link."""
import io, re, sys

src, dst = sys.argv[1], sys.argv[2]
body = io.open(src, encoding="utf-8").read()

# --- 1. guarded capability lookup -------------------------------------------
helper = '''
/* standalone build: no Claude runtime here, so every capability resolves null */
async function useCap(name){
  try{
    if(typeof claude !== "undefined" && claude && typeof claude.use === "function"){
      return await claude.use(name);
    }
  }catch(e){}
  return null;
}
'''
body = body.replace('"use strict";', '"use strict";\n' + helper, 1)
body = body.replace('await claude.use("db")', 'await useCap("db")')
body = body.replace('await claude.use("downloads")', 'await useCap("downloads")')

# --- 2. standalone banner ----------------------------------------------------
banner = '''<div style="max-width:1180px;margin:0 auto;padding:10px 16px 0">
<div class="note warn" style="font-size:12.5px">
<b>גרסה עצמאית לבדיקה.</b> הנתונים נשמרים במכשיר הזה בלבד ואינם מסתנכרנים —
מסלול החתימה במשרד לא יעבוד בקובץ הזה. לשמירת הטופס: שיתוף ← הדפסה ← שמירה כ-PDF.
</div></div>
'''
body = body.replace('<main>', banner + '<main>', 1)

# --- 3. full document wrapper (the artifact host normally supplies this) ------
head = '''<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="יומן שדה">
<meta name="color-scheme" content="light dark">
<style>
  html{color-scheme:light dark}
  body{margin:0;font:14px system-ui,sans-serif;background:#fafafa}
  img{max-width:100%}
  [hidden]{display:none!important}
</style>
'''
tail = '''
</body>
</html>
'''
# the <title> and <style> at the top of body belong in <head>
m = re.match(r'(\s*<title>.*?</title>\s*<link[^>]*>\s*<style>.*?</style>\s*)',
             body, re.S)
if not m:
    raise SystemExit("could not split head assets out of the body")
head_assets, rest = m.group(1), body[m.end():]

out = head + head_assets + "</head>\n<body>\n" + rest + tail
io.open(dst, "w", encoding="utf-8").write(out)

print("wrote:", dst)
print("bytes:", len(out.encode("utf-8")))
for probe in ['useCap("db")', 'useCap("downloads")', 'claude.use(']:
    print(("  found " if probe in out else "  ABSENT"), probe)
