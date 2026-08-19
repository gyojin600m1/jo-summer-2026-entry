import re, html, json, os, glob, unicodedata, collections

DIR = "jolist"

def read(p):
    return open(p, encoding="cp932", errors="replace").read()

def cells(tr):
    return [html.unescape(re.sub("<[^>]+>", "", x)).replace("　", " ").strip()
            for x in re.findall(r"(?is)<td[^>]*>(.*?)</td>", tr)]

def norm(s):
    return re.sub(r"\s+", "", s)

events = []
for path in sorted(glob.glob(os.path.join(DIR, "*.html"))):
    pid = os.path.basename(path)[:3]
    t = read(path)
    m = re.search(r"種目：.*?<td[^>]*>(.*?)</td>", t, re.S)
    head = html.unescape(re.sub("<[^>]+>", "", m.group(1))).strip()
    head = re.sub(r"\s+", " ", head)
    body = t[t.find("エントリー情報ココカラ"):]
    trs = re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", body)
    rows = []
    header = None
    for tr in trs:
        c = cells(tr)
        if not c or len(c) < 5:
            continue
        if c[0] in ("選手番号", "チーム番号"):
            header = c
            continue
        rows.append(c)
    events.append({"page": pid, "head": head, "header": header, "rows": rows})

print("ページ数", len(events))
ind = [e for e in events if e["header"] and e["header"][0] == "選手番号"]
rel = [e for e in events if e["header"] and e["header"][0] == "チーム番号"]
print("個人ページ", len(ind), "／ リレーページ", len(rel))
print("個人のべエントリー", sum(len(e["rows"]) for e in ind))
print("リレーのべエントリー", sum(len(e["rows"]) for e in rel))
bad = [e["page"] for e in events if not e["header"]]
print("ヘッダ取れず", bad)
json.dump(events, open("jo_raw.json", "w"), ensure_ascii=False)
for e in events[:3] + events[-3:]:
    print(e["page"], "|", e["head"], "|", len(e["rows"]), "件")
