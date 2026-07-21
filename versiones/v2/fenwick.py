class FenwickTree:
    def __init__(self, pesos):
        self.n = len(pesos)
        self.tree = [0] * (self.n + 1)

        for i, peso in enumerate(pesos):
            self.add(i, peso)

    def add(self, indice, delta):
        i = indice + 1
        while i <= self.n:
            self.tree[i] += delta
            i += i & -i

    def prefix_sum(self, indice):
        s = 0
        i = indice + 1
        while i > 0:
            s += self.tree[i]
            i -= i & -i
        return s

    @property
    def total(self):
        return self.prefix_sum(self.n - 1)

    def find(self, k):
        """
        Devuelve el índice cuya unidad acumulada contiene a k.
        k empieza en 1.
        """
        idx = 0
        bit = 1 << (self.n.bit_length() - 1)

        while bit:
            nxt = idx + bit
            if nxt <= self.n and self.tree[nxt] < k:
                idx = nxt
                k -= self.tree[nxt]
            bit >>= 1

        return idx