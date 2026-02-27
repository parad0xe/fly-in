"""

N = Vextex count

h: int = height
f: int = flow
u: int = capacity

s = start
t = target
v = vextex [!s & !t]

e = edge = (v, w)

residual_capacity = u(e) - f(e)

αf(v): int = f_in(v) - f_out(v) = excess

Initialization:
    h(s) = N

    h(t) = 0
    h(v) = 0

    e(s) = 0
    e(t) = 0
    e(v) = 0

Invariants:
    h(s) = abs(nb_drones)
    h(t) = 0
    ∀e(v, w); h(v) <= h(w) + 1

Subroutines:
    push(v):


Preflow:
    initial push

Main Loop:
    while excess(v) > 0:
        cv = max(h(v))


"""
