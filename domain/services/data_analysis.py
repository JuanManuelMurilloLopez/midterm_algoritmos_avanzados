import csv

def print_analysis(df):        
    print("=== HEAD ===")
    print(df.head())


    print("\n=== ACCURACY ===")
    print(df["correct"].mean())

    print("\nPredicciones por clase:")
    print(df["predicted_winner"].value_counts())



def generate_csv(results_rows):
    with open("results_inference.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=results_rows[0].keys()
        )
        writer.writeheader()
        writer.writerows(results_rows)
