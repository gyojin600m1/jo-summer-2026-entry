import json, re, math, collections, unicodedata

ev = json.load(open("jo_raw.json"))
nit = json.load(open("nittei.json"))
p2n = json.load(open("page2no.json"))
staff = [d for d in json.load(open("relaystaff.json")) if d["name"]]

# ---- 半角カナ → ひらがな
HK = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜｦﾝｧｨｩｪｫｯｬｭｮ"
def kana_hira(s):
    if not s: return ""
    s = unicodedata.normalize("NFKC", s)          # 半角カナ→全角カナ(濁点結合)
    out = []
    for ch in s:
        o = ord(ch)
        if 0x30A1 <= o <= 0x30F6: out.append(chr(o - 0x60))
        elif ch in " 　・": pass
        else: out.append(ch)
    return "".join(out)

DAY = lambda no: 1 if no <= 68 else 2 if no <= 132 else 3 if no <= 182 else 4 if no <= 230 else 5
CLS = ["10歳以下", "11～12歳", "13～14歳", "15～16歳", "ＣＳ"]
STY = ["自由形", "背泳ぎ", "平泳ぎ", "バタフライ", "個人メドレー", "フリーリレー", "メドレーリレー"]

prefs, pidx = [], {}
def pref_i(p):
    p = p.replace(" ", "")
    if p not in pidx:
        pidx[p] = len(prefs); prefs.append(p)
    return pidx[p]

swim, sidx = [], {}
def sw_i(no, name, kana, pref, club, ckana, grade, age, g):
    if no not in sidx:
        sidx[no] = len(swim)
        swim.append([int(no), name, kana_hira(kana), pref_i(pref), club, kana_hira(ckana), grade, age, 0 if g == "男子" else 1])
    return sidx[no]

def t2s(t):
    t = t.strip()
    m = re.match(r"^(?:(\d+):)?(\d+)\.(\d+)$", t)
    if not m: return 9e9
    return int(m.group(1) or 0) * 60 + int(m.group(2)) + int(m.group(3)) / 100

events, relays = [], []
for e in ev:
    page = e["page"]; no = int(p2n.get(page, page))
    head = e["head"]
    g = 0 if head.startswith("男子") else 1
    m = re.match(r"^(男子|女子)\s+(\d+m)\s+(\S+)\s+予選\s+(\S+)$", head)
    dist, style, cls = m.group(2), m.group(3), m.group(4)
    info = nit.get(str(no), {})
    heats = info.get("heats")
    if heats is None:
        mm = re.search(r"（\s*(\d+)\s*\)", info.get("raw", "")); heats = int(mm.group(1)) if mm else None
    base = {"no": no, "day": DAY(no), "time": info.get("time"), "heats": heats,
            "g": g, "cls": CLS.index(cls), "dist": dist, "style": STY.index(style), "page": page}
    if e["header"][0] == "選手番号":
        rows = []
        for r in e["rows"]:
            sno, pref, name, kana, club, ckana, grade, age, et = r[:9]
            i = sw_i(sno, name, kana, pref, club, ckana, grade, age, head[:2])
            rows.append([i, et])
        rows.sort(key=lambda x: t2s(x[1]))
        base["rows"] = rows
        events.append(base)
    else:
        rows = []
        for r in e["rows"]:
            tno, pref, team, tkana, et, order, gaku = r[:7]
            mem = [x.strip().replace("　", " ") for x in order.split("・") if x.strip()]
            rows.append([int(tno), pref_i(pref), team, et, mem, gaku, kana_hira(tkana)])
        rows.sort(key=lambda x: t2s(x[3]))
        base["rows"] = rows
        relays.append(base)

# 同じ競技No.を複数の年齢区分で共有する種目(13〜16歳/CS)の合計を持たせる
tot = collections.Counter()
mix = collections.Counter()
for e in events:
    tot[e["no"]] += len(e["rows"]); mix[e["no"]] += 1
for e in events:
    e["tot"] = tot[e["no"]]; e["mix"] = mix[e["no"]]
for e in relays:
    e["tot"] = len(e["rows"]); e["mix"] = 1

events.sort(key=lambda x: (x["no"], x["cls"]))
relays.sort(key=lambda x: x["no"])

# リレー要員(個人エントリー無し)
indpn = {(swim[i][3], swim[i][1].replace(" ", "").replace("　", "")) for i in range(len(swim))}
staff_out = []
for d in staff:
    key = (pref_i(d["pref"]), d["name"].replace(" ", "").replace("　", ""))
    if key in indpn: continue
    staff_out.append([int(d["no"]), d["name"], pref_i(d["pref"]), d["club"], d["grade"], d["age"], 0 if d["gender"] == "男子" else 1])

# 県別集計
kens = collections.defaultdict(lambda: {"people": 0, "men": 0, "women": 0, "ind": 0, "rel": 0})
for i, s in enumerate(swim):
    k = kens[s[3]]; k["people"] += 1; k["men" if s[8] == 0 else "women"] += 1
for s in staff_out:
    k = kens[s[2]]; k["people"] += 1; k["men" if s[6] == 0 else "women"] += 1
for e in events:
    for i, t in e["rows"]: kens[swim[i][3]]["ind"] += 1
for e in relays:
    for r in e["rows"]: kens[r[1]]["rel"] += 1

def clubkey(c):
    return unicodedata.normalize("NFKC", c.split("／")[0]).replace(" ", "").replace("・", "")
clubs = collections.Counter()
for s in swim: clubs[clubkey(s[4])] += 1
for s in staff_out: clubs[clubkey(s[3])] += 1
for s in swim: s.append(clubkey(s[4]))
for s in staff_out: s.append(clubkey(s[3]))

data = {
    "meet": {
        "name": "第49回 全国JOCジュニアオリンピックカップ夏季水泳競技大会",
        "short": "夏季JO(東京)",
        "venue": "東京アクアティクスセンター(東京都江東区)",
        "dates": "2026年8月22日(土)〜26日(水)　※8月21日(金)は公式練習日",
        "created": "2026/07/31 最終エントリーのデータ",
    },
    "stats": {"people": len(swim) + len(staff_out), "ind_people": len(swim), "relay_only": len(staff_out),
              "men": sum(1 for s in swim if s[8] == 0) + sum(1 for s in staff_out if s[6] == 0),
              "women": sum(1 for s in swim if s[8] == 1) + sum(1 for s in staff_out if s[6] == 1),
              "clubs": len(clubs), "kens": len(prefs),
              "ind": sum(len(e["rows"]) for e in events), "relay": sum(len(e["rows"]) for e in relays),
              "events": len(events) + len(relays)},
    "prefs": prefs, "cls": CLS, "sty": STY,
    "swim": swim, "staff": staff_out, "events": events, "relays": relays,
    "kens": {str(k): v for k, v in kens.items()},
}
json.dump(data, open("data.json", "w"), ensure_ascii=False, separators=(",", ":"))
import os
print("data.json", os.path.getsize("data.json"), "bytes")
print(data["stats"])
