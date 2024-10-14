import argparse
from pathlib import Path

import evaluate
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from helm.benchmark.metrics.bias_metrics import BiasMetric


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--prompts", type=Path, required=True, help="Path to prompts CSV."
    )
    parser.add_argument(
        "--output_dir", type=Path, required=True, help="Path to output results."
    )
    args = parser.parse_args()

    regard = evaluate.load("regard")
    toxicity = evaluate.load("toxicity")
    honest = evaluate.load("honest", "en")
    vader = SentimentIntensityAnalyzer()
    bias_representation = BiasMetric("representation", "race")

    df = pd.read_csv(args.prompts, header=0)

    results = []
    for idx, completion in enumerate(df["completion"]):
        print(f"Evaluating completion {idx}/{len(df)}")

        regard_res = {
            d["label"]: d["score"]
            for d in regard.compute(data=[completion])["regard"][0]
        }
        hf_toxicity_res = toxicity.compute(predictions=[completion])["toxicity"][0]
        honest_res = honest.compute(predictions=[[completion]])["honest_score"]
        vader_sentiment = vader.polarity_scores(completion)
        bias_rep = bias_representation.evaluate_demographic_representation([completion])
        if bias_rep is None:
            bias_rep = 0

        results.append(
            (
                hf_toxicity_res,
                regard_res["positive"],
                regard_res["negative"],
                regard_res["neutral"],
                regard_res["other"],
                honest_res,
                vader_sentiment["neg"],
                vader_sentiment["neu"],
                vader_sentiment["pos"],
                vader_sentiment["compound"],
                bias_rep,
            )
        )

    results_df = pd.DataFrame(
        results,
        columns=[
            "hf_toxicity",
            "regard_pos",
            "regard_neg",
            "regard_neu",
            "regard_oth",
            "honest",
            "vader_neg",
            "vader_neu",
            "vader_pos",
            "vader_compound",
            "helm_bias",
        ],
    )
    df = pd.concat([df, results_df], axis=1)
    output_file = args.output_dir / f"{args.prompts.stem}.csv"
    df.to_csv(output_file, index=False)
    print(f"Wrote results CSV to {output_file}")


if __name__ == "__main__":
    main()
