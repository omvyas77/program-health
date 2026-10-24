# The scenario arithmetic, kept free of Streamlit so tests can import it. project() is the same
# recurrence as forecast/undergrad.py, which this app can't import on Community Cloud;
# tests/test_app.py pins the two together.


def project(h0, f, t, c, years):
    values, h = [], float(h0)
    for _ in range(years):
        h = f + t + c * h
        values.append(h)
    return values


def grow(start, rate, years):
    return [start * (1 + rate) ** i for i in range(1, years + 1)]


def change_line(label, last_fall, yours, base, changes):
    if not changes:
        return f"Your scenario matches the base: {base:,.0f} {label} in Fall {last_fall}."
    difference = round(yours) - round(base)
    direction = "more" if difference > 0 else "fewer"
    gap = f"{abs(difference):,} {direction} than" if difference else "the same as"
    return (
        f"Your scenario has {yours:,.0f} {label} in Fall {last_fall}, {gap} the base of "
        f"{base:,.0f}. Changed from base: {'; '.join(changes)}."
    )
