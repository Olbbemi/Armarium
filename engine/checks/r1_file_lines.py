"""R1 -- 파일 줄 수 상한. 빼는 것 없이 원문 줄을 센다."""
LIMIT = 200


def check(path, text):
    n = len(text.splitlines())
    if n <= LIMIT:
        return []
    return [{"line": n, "snippet": "%d lines" % n,
             "section": "(file)",
             "message": "파일이 %d줄로 상한 %d 을 넘는다" % (n, LIMIT)}]
