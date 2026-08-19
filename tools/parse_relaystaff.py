# 【リレー要員】一覧 list03.pdf → relaystaff.json
# https://aquatics.or.jp/swim/jo_entry53/list03.pdf
# 列: 選手番号 / 加盟団体 / 氏名 / 所属名 / 登録団体 / 学年 / 性別 / 年齢
import pdfplumber, collections, json, re

BOUND = [("no",0,100),("pref",100,150),("name",150,255),("club",255,355),
         ("reg",355,415),("grade",415,478),("gender",478,520),("age",520,600)]
SEP = {"name"}          # 姓と名は空白で分けたまま持つ（表示を個人エントリーと揃える）

rows = []
with pdfplumber.open("list03.pdf") as pdf:
    for p in pdf.pages:
        lines = collections.defaultdict(list)
        for w in p.extract_words():
            lines[round(w["top"] / 3)].append(w)
        for k in sorted(lines):
            ln = sorted(lines[k], key=lambda w: w["x0"])
            if ln[0]["text"] in ("選手番号",) or ln[0]["text"].startswith("【"):
                continue
            rows.append([(round(w["x0"], 1), w["text"]) for w in ln])

out = []
for r in rows:
    cell = {k: [] for k, _, _ in BOUND}
    for x, t in r:
        for k, a, b in BOUND:
            if a <= x < b:
                cell[k].append(t)
    d = {k: (" ".join(v) if k in SEP else "".join(v)) for k, v in cell.items()}
    if not re.fullmatch(r"\d+", d["no"] or ""):
        continue
    d["pref"] = d["pref"].replace(" ", "")
    if not d["name"]:
        continue
    out.append(d)

json.dump(out, open("relaystaff.json", "w", encoding="utf-8"), ensure_ascii=False)
print("リレー要員", len(out), "名")
print(out[0]); print(out[-1])
