#Algoritmo para medir la similitud local en las rachas recientes de los equipos
def z_function(s):
    n = len(s)
    z = [0] * n
    l, r = 0, 0

    for i in range(1, n):
        if i <= r:
            z[i] = min(r - i + 1, z[i - l])
            while i + z[i] < n and s[z[i]] == s[i + z[i]]:
                z[i] += 1
            if i + z[i] - 1 > r:
                l, r =  i, i + z[i] - 1

    explanation = {
        "algorithm": "Z-function",
        "z_array": z,
        "meaning": "z[i] = length of substring starting at i matching prefix"
    }

    return z, explanation