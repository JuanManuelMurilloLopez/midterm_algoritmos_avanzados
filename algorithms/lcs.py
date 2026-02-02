def longest_common_substring(s, t):
    n, m = len(s), len(t)
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    max_len = 0
    end_pos = 0

    for i in range(1, n + 1):
        for j in range(1, m + 1):

            if s[i - 1] == t[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1

                if dp[i][j] > max_len:
                    max_len = dp[i][j]
                    end_pos = i
            
            else:
                dp[i][j] = 0

    substring = s[end_pos - max_len : end_pos]

    explanation = {
        "algorithm": "Longest Common Substring",
        "substring": substring,
        "length": max_len,
        "dp_table": dp
    }

    return max_len, substring, explanation

def predict_from_pattern(pattern):
    if pattern.count("G") > pattern.count("P"):
        return "G"
    if pattern.count("P") > pattern.count("G"):
        return "P"
    else:
        return "E"
    
def advantage_score(lcs_length, window_size):
    if window_size == 0:
        return 0.0
    return lcs_length / window_size
