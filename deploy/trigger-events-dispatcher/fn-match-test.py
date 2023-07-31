import fnmatch
import re
import time


def get_triggers():
    tt = {}
    tt["*"] = {}
    tt["arpa.*"] = {}
    tt["wallbox.chargers"] = {}
    for i in range(10000):
        tt[f"{i}.*"] = {}
        tt[f"{i}-sub.*"] = {}
        tt[f"{i}-text.*"] = {}
    return tt


triggers = get_triggers()


class Trigger:

    def __init__(self, path):

        self._regex = re.compile(fnmatch.translate(path))

    def match(self, group):

        return self._regex.match(group)

    def execute(self):
        pass

def trigger_func():
    pass

triggers_obj = []
triggers_match = {}
triggers_tpl = []

for t in triggers:

    triggers_obj.append(Trigger(t))
    triggers_match[t] = {
        "regex": re.compile(fnmatch.translate(t))
    }
    triggers_tpl.append(
        (
            re.compile(fnmatch.translate(t)),
            []
        )
    )


def timeit(fn, group):
    st = time.time()
    fn(group)
    return time.time()-st


def check_with_obj(group):
    for t in triggers_obj:
        if t.match(group) is not None:
            t.execute()
    return None


def check_with_dict(group):
    for t in triggers_match:
        if triggers_match[t]["regex"].match(group) is not None:
            trigger_func()
    return None


def check_with_tuple(group):
    for t in triggers_tpl:
        r, tt = t
        if r.match(group):
            trigger_func()

print(f"WITH OBJECTS: {timeit(check_with_obj, 'arpa.sync')}")
print(f"WITH MATCH: {timeit(check_with_dict, 'arpa.sync')}")
print(f"WITH TUPLES: {timeit(check_with_tuple, 'arpa.sync')}")
