# 使用f"{'\\':5s}"會報錯
a = "\\"
with open(f"ans.csv", "w", encoding="utf-8") as csvfile:
    csvfile.write('\\'+'    ')