# SEIKO のスタートリスト（組・レーン）を読む
# https://swim.seiko.co.jp/2026/S70601/start/{日}S{競技No}.pdf
# 個人: 水路@73 / 加盟@93 / 登録No@141 / 氏名@190 / ヨミガナ@275 / 所属名@347 / 学年@468 / ﾀｲﾑ@505
# リレー: 水路@73 / 登録No.@117 / チーム名@141 / 加盟@226 / 泳者の登録No@275 …
import pdfplumber, glob, os, re, json, collections, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else "sl"
out = {}
for path in sorted(glob.glob(os.path.join(SRC, "*.pdf"))):
    no = int(os.path.basename(path)[3:6])
    rows = []
    relay = False
    with pdfplumber.open(path) as pdf:
        first = pdf.pages[0].extract_text() or ""
        if "まだ作成されていません" in first:
            continue
        relay = "リレー" in first.split("\n")[3] if len(first.split("\n")) > 3 else False
        for page in pdf.pages:
            line = collections.defaultdict(list)
            for w in page.extract_words():
                line[round(w["top"], 1)].append(w)
            heat = None
            for k in sorted(line):
                ws = sorted(line[k], key=lambda w: w["x0"])
                head = ws[0]
                m = re.fullmatch(r"(\d+)組", head["text"])
                if m and head["x0"] < 60:
                    heat = int(m.group(1)); continue
                if heat is None:
                    continue
                if not (68 <= head["x0"] < 86 and re.fullmatch(r"\d", head["text"])):
                    continue
                lane = int(head["text"])
                lo, hi = (108, 140) if relay else (138, 188)
                ent = [w["text"] for w in ws if lo <= w["x0"] < hi and re.fullmatch(r"\d+", w["text"])]
                if not ent:
                    continue                      # 空きレーン
                rows.append({"heat": heat, "lane": lane, "no": int(ent[0])})
    out[no] = {"relay": relay, "rows": rows}

json.dump(out, open("startlist.json", "w"), ensure_ascii=False, separators=(",", ":"))
print("スタートリストのある競技No:", len(out))
print("のべ人数/チーム:", sum(len(v["rows"]) for v in out.values()))
print("個人:", sum(len(v["rows"]) for v in out.values() if not v["relay"]),
      "／ リレー:", sum(len(v["rows"]) for v in out.values() if v["relay"]))
