def mean_absolute_percentage_error(y_true, y_pred):
    if not y_true:
        return 0.0

    total = 0.0
    count = 0
    for true, pred in zip(y_true, y_pred):
        if true == 0:
            continue
        total += abs((true - pred) / true)
        count += 1

    return (total / count) if count else float("inf")


def r2_score(y_true, y_pred):
    if not y_true:
        return 0.0

    mean_true = sum(y_true) / len(y_true)
    ss_res = sum((true - pred) ** 2 for true, pred in zip(y_true, y_pred))
    ss_tot = sum((true - mean_true) ** 2 for true in y_true)
    return 1.0 - ss_res / ss_tot if ss_tot else 0.0


def evaluate_model(y_true, y_pred):
    results = {
        "mape": mean_absolute_percentage_error(y_true, y_pred),
        "r2": r2_score(y_true, y_pred),
    }
    print(f"Evaluation metrics: {results}")
    return results
