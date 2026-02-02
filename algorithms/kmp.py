# Algoritmo para detectar patrones repetidos en el historial de un equipo
def kmp_prefix_function(s):
    pi = [0] * len(s)
    j = 0

    for i in range(1, len(s)):
        while j >0 and s[i] != s[j]:
            j = pi[j - 1]
        if s[i] == s[j]:
            j += 1
        pi[i] = j

    explanation = {
        "algorithm": "KMP Prefix Function",
        "prefix_table": pi,
        "meaning": "pi[i] = length of longest proper prefiz that ius also suffix"
    }

    return pi, explanation

def kmp_contains(text, pattern):
    if not pattern:
        return False, None

    combined = pattern + "#" + text
    pi, explanation = kmp_prefix_function(combined)

    found = any(v == len(pattern) for v in pi)
    return found, explanation
