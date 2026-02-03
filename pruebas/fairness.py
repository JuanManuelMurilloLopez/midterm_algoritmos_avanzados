import pandas as pd

def rhythm_gap_fairness(df, threshold):
    df = df.copy()

    if not {"rhythm_home", "rhythm_away", "correct"}.issubset(df.columns):
        raise ValueError(
            f"DataFrame does not contain required columns. Found: {df.columns}"
        )

    df["rhythm_diff"] = abs(df["rhythm_home"] - df["rhythm_away"])

    favored = df[df["rhythm_diff"] >= threshold]
    balanced = df[df["rhythm_diff"] < threshold]

    acc_favored = favored["correct"].mean() if len(favored) else 0
    acc_balanced = balanced["correct"].mean() if len(balanced) else 0

    return {
        "accuracy_favored": round(acc_favored, 3),
        "accuracy_balanced": round(acc_balanced, 3),
        "fairness_gap": round(abs(acc_favored - acc_balanced), 3),
        "samples_favored": len(favored),
        "samples_balanced": len(balanced),
    }
