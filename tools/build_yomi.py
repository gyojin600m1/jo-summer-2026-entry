# KANJIDIC2 から「リレー要員(公式ヨミガナが無い617名)」の名前・所属に出る漢字だけの読み表を作る。
# 出力: yomi.json  {漢字: [読み(ひらがな) …長い順]}
import json, re, sys, xml.etree.ElementTree as ET

XML = sys.argv[1] if len(sys.argv) > 1 else "kanjidic2.xml"
data = json.load(open("data.json", encoding="utf-8"))

need = set()
for r in data["staff"]:
    need |= set(r[1]) | set(r[3])
need = {c for c in need if "一" <= c <= "鿿" or c == "々"}
# 異体字はKANJIDIC2に読みが無いことがあるので、標準字体の読みを借りる
ALIAS = {"髙":"高","﨑":"崎","濵":"濱","邉":"辺","邊":"辺","栁":"柳","桒":"桑","眞":"真","德":"徳",
         "靑":"青","澤":"沢","齋":"斎","齊":"斉","嶋":"島","塚":"塚","礼":"礼","逸":"逸","槙":"槙"}
need |= {v for k, v in ALIAS.items() if k in need}
print("必要な漢字", len(need))

def k2h(s):
    return "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in s)

VOICE = {"か":"が","き":"ぎ","く":"ぐ","け":"げ","こ":"ご","さ":"ざ","し":"じ","す":"ず","せ":"ぜ","そ":"ぞ",
         "た":"だ","ち":"ぢ","つ":"づ","て":"で","と":"ど","は":["ば","ぱ"],"ひ":["び","ぴ"],"ふ":["ぶ","ぷ"],
         "へ":["べ","ぺ"],"ほ":["ぼ","ぽ"]}

def variants(r):
    out = {r}
    head = r[0]
    if head in VOICE:
        v = VOICE[head]
        for x in ([v] if isinstance(v, str) else v):
            out.add(x + r[1:])
    if len(r) > 1 and r[-1] in "くきちつ":
        out.add(r[:-1] + "っ")
    if "ず" in r: out.add(r.replace("ず", "づ"))
    if "づ" in r: out.add(r.replace("づ", "ず"))
    if "じ" in r: out.add(r.replace("じ", "ぢ"))
    return out

yomi = {}
for _, el in ET.iterparse(XML, events=("end",)):
    if el.tag != "character":
        continue                      # 子要素をclearすると親のcharacterが空になるので触らない
    lit = el.findtext("literal")
    if lit not in need:
        el.clear(); continue
    rs = set()
    for rm in el.iter("reading"):
        t = rm.get("r_type")
        v = (rm.text or "").strip()
        if not v: continue
        if t == "ja_on":
            rs.add(k2h(v.replace("-", "").replace(".", "")))
        elif t == "ja_kun":
            v = v.replace("-", "")
            parts = v.split(".")
            rs.add("".join(parts)); rs.add(parts[0])
    for nr in el.iter("nanori"):
        if nr.text: rs.add(nr.text.strip())
    all_r = set()
    for r in rs:
        r = "".join(ch for ch in r if "ぁ" <= ch <= "ゖ")
        if r: all_r |= variants(r)
    if all_r:
        yomi[lit] = sorted(all_r, key=lambda x: (-len(x), x))
    el.clear()

for k, v in ALIAS.items():
    if k not in yomi and v in yomi:
        yomi[k] = yomi[v]
miss = sorted(need - set(yomi))
print("読みが取れた漢字", len(yomi), "／ 取れず", len(miss), "".join(miss[:40]))
json.dump(yomi, open("yomi.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
import os
print("yomi.json", os.path.getsize("yomi.json"), "bytes")
for c in "岡村莉桜":
    print(" ", c, yomi.get(c))
