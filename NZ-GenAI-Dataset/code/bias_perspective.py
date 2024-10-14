import argparse
import time
from pathlib import Path

import dotenv
import pandas as pd
from googleapiclient import discovery

API_KEY = dotenv.dotenv_values()["PERSPECTIVE_API_KEY"]

ATTRIBUTES = [
    "TOXICITY",
    "SEVERE_TOXICITY",
    "IDENTITY_ATTACK",
    "INSULT",
    "PROFANITY",
    "THREAT",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--prompts", type=Path, required=True, help="Path to prompts CSV."
    )
    parser.add_argument(
        "--output_dir", type=Path, required=True, help="Path to output results."
    )
    args = parser.parse_args()

    client = discovery.build(
        "commentanalyzer",
        "v1alpha1",
        developerKey=API_KEY,
        discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",  # noqa
        static_discovery=False,
    )

    df = pd.read_csv(args.prompts, header=0)

    rate = 1.1

    results = []
    for idx, completion in enumerate(df["completion"]):
        print(f"Evaluating completion {idx}/{len(df)}")

        start_time = time.monotonic()
        analyze_request = {
            "comment": {"text": completion},
            "languages": ["en"],
            "requestedAttributes": {x: {} for x in ATTRIBUTES},
        }
        try:
            response = client.comments().analyze(body=analyze_request).execute()
        except Exception:
            time.sleep(5)
            rate += 0.1
            response = client.comments().analyze(body=analyze_request).execute()
        attribute_scores = response["attributeScores"]
        results.append(
            tuple(attribute_scores[key]["summaryScore"]["value"] for key in ATTRIBUTES)
        )

        # Rate limit ~1 req/s
        time_to_wait = max(start_time + rate - time.monotonic(), 0)
        time.sleep(time_to_wait)

    results_df = pd.DataFrame(
        results,
        columns=[f"perspective_{key.lower()}" for key in ATTRIBUTES],
    )
    df = pd.concat([df, results_df], axis=1)
    output_file = args.output_dir / f"{args.prompts.stem}.csv"
    df.to_csv(output_file, index=False)
    print(f"Wrote results CSV to {output_file}")


if __name__ == "__main__":
    main()
