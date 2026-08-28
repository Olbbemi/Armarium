"""판정기 호출 공용 헬퍼.

판정기는 두 인자를 받는 것과 문맥까지 세 인자를 받는 것이 섞여 있다. 문맥이 필요한 판정기만
받게 하려는 것이라, 부르는 쪽이 시그니처를 보고 맞춰 넘긴다.
"""
import contextlib, inspect, signal

DEFAULT_TIMEOUT = 10


@contextlib.contextmanager
def time_limit(seconds):
    """판정기 하나에 제한 시간을 건다.

    끝나지 않는 판정기 하나가 검증 전체를 세우면, 무엇이 세웠는지도 안 남는다.
    SIGALRM 이 없는 플랫폼에서는 제한 없이 돈다 -- 그 사실은 부르는 쪽이 알린다.
    """
    if not seconds or not hasattr(signal, "SIGALRM"):
        yield
        return

    def handler(signum, frame):
        raise TimeoutError("판정기가 %s초 안에 끝나지 않았다" % seconds)

    old = signal.signal(signal.SIGALRM, handler)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


def has_timeout():
    return hasattr(signal, "SIGALRM")


def call_check(fn, *args, ctx=None, timeout=None):
    with time_limit(timeout):
        return _dispatch(fn, *args, ctx=ctx)


def _dispatch(fn, *args, ctx=None):
    try:
        arity = len(inspect.signature(fn).parameters)
    except (TypeError, ValueError):
        arity = len(args)
    if arity > len(args):
        return fn(*args, ctx)
    return fn(*args)
