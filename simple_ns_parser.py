from types import SimpleNamespace

def parse(d):
    x = SimpleNamespace()
    _ = [
        setattr(
            x,
            k,
            (
                parse(v)
                if isinstance(v, dict)
                else [parse(e) for e in v] if isinstance(v, list) else v
            ),
        )
        for k, v in d.items()
    ]
    return x
