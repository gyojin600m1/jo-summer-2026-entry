# part1(head+CSS) + part2(body) + part3(JS) を結合し、__DATA__ に data.json を埋め込む。
# yomi.json があれば data.yomi として同梱する（リレー要員のひらがな検索用）。
import json, os

data = json.load(open("data.json", encoding="utf-8"))
if os.path.exists("yomi.json"):
    data["yomi"] = json.load(open("yomi.json", encoding="utf-8"))
blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

html = (open("part1.html", encoding="utf-8").read()
        + open("part2.html", encoding="utf-8").read()
        + open("part3.html", encoding="utf-8").read().replace("__DATA__", blob))

for out in ["/Users/fukudashunki/jo-summer-2026-entry/index.html",
            "/private/tmp/claude-501/-Users-fukudashunki/94335342-8d12-4643-95fb-b5ab6d3c1907/scratchpad/preview.html"]:
    try:
        open(out, "w", encoding="utf-8").write(html)
    except Exception as e:
        print("skip", out, e)
print("index.html", len(html.encode()), "bytes / yomi", len(data.get("yomi", {})), "字")
