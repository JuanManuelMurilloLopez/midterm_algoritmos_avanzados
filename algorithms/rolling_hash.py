# Comparación de subcadenas largas
def rolling_hash(s, base=257, mod=10**9 + 1):
    h = 0
    hashes = []

    for c in s:
        h = (h * base + ord(c)) % mod
        hashes.append(h)

    explanation = {
        "algorithm": "Rolling Hash",
        "base": base,
        "mod": mod,
        "hashes": hashes
    }

    return hashes, explanation