"""M10 -- 픽스처 필수. 판정기가 죽었는지 알 길이 없는 규칙을 찾는다."""


def check(rules_dir, rules):
    out = []
    for r in rules:
        if r["fixtures"] or r["meta"].get("fixtures"):
            continue
        out.append({"file": str(r["path"]), "line": 1,
                    "snippet": r["path"].name,
                    "section": "(fixture)",
                    "message": "픽스처가 없어 판정기가 죽어도 드러나지 않는다"})
    return out
