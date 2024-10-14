import argparse
import re
from functools import partial

import dotenv
import openai
import pandas as pd
import torch
import transformers

from prompts import ALL_PROMPTS

openai.api_key = dotenv.dotenv_values()["OPENAI_API_KEY"]
openai.organization = dotenv.dotenv_values()["OPENAI_ORG"]


def get_openai_completion(model: str, prompt: str) -> str:
    try:
        response = (
            openai.completions.create(
                model=model,
                prompt=prompt,
                stop=".",
                temperature=0,
                max_tokens=100,
                seed=54321,
                echo=True,
            )
            .choices[0]
            .text
        )
    except Exception:
        response = "<error>"
    return response


def get_openai_chat(model: str, prompt: str) -> str:
    messages = [{"role": "user", "content": f"Complete this sentence: '{prompt}'"}]
    try:
        response = (
            openai.chat.completions.create(
                model=model,
                messages=messages,
                stop=".",
                temperature=0,
                max_tokens=100,
                seed=54321,
            )
            .choices[0]
            .message.content
        )
    except Exception:
        return "<error>"
    if response is None:
        return "<error>"
    if prompt.lower() in response.lower():
        return response
    return prompt + " " + response


def get_hf_response(pipeline, prompt: str, concat: bool) -> str:
    output = pipeline(
        prompt, clean_up_tokenization_spaces=True, do_sample=False, max_new_tokens=100
    )
    response = output[0]["generated_text"]
    if concat and prompt.lower() not in response.lower():
        response = prompt + " " + response
    return response


def post_process_response(resp: str) -> str:
    match = re.search(r"[.?!][\"']*\s", resp)
    if match:
        resp = resp[: match.start() + 1]
    return resp.strip().replace("\n", "").replace("  ", " ")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--hf_model", type=str, help="Text generation model to load from HuggingFace"
    )
    parser.add_argument(
        "--hf_tokenizer",
        type=str,
        help="HuggingFace tokenizer. Defaults to the same as --hf_model.",
    )
    parser.add_argument(
        "--hf_s2s",
        action="store_true",
        help="Use seq2seq generation model instead of causal language model.",
    )
    parser.add_argument(
        "--openai_model", type=str, help="OpenAI model to use with prompting."
    )
    parser.add_argument(
        "--openai_completions",
        action="store_true",
        help="Use the legacy completions endpoint instead of the chat endpoint.",
    )
    parser.add_argument("--prompts", type=str, help="Use prompts from this list only.")
    parser.add_argument(
        "--results", required=True, type=str, help="Filename of results CSV."
    )
    parser.add_argument("--fp16", action="store_true", help="Use FP16 precision.")
    args = parser.parse_args()

    # torch.set_default_device("cuda")

    if args.hf_model:
        transformers.set_seed(54321)
        pipeline = transformers.pipeline(
            task="text2text-generation" if args.hf_s2s else "text-generation",
            model=args.hf_model,
            tokenizer=args.hf_tokenizer,
            # device="cuda",
            device_map="auto",
            torch_dtype=torch.float16 if args.fp16 else torch.float32,
            trust_remote_code=True,
        )
        if pipeline.tokenizer.pad_token_id is None:
            pipeline.tokenizer.pad_token_id = pipeline.model.config.eos_token_id
        response_func = partial(
            get_hf_response,
            pipeline,
            concat=isinstance(pipeline, transformers.Text2TextGenerationPipeline),
        )
        model_name = args.hf_model
    elif args.openai_model:
        model_name = args.openai_model
        response_func = partial(
            get_openai_completion if args.openai_completions else get_openai_chat,
            model_name,
        )
    else:
        raise ValueError("Please specify a model to use.")

    prompts = (
        pd.read_csv(args.prompts, index_col=0, header=0)
        if args.prompts
        else ALL_PROMPTS
    )

    results = []
    for idx, (
        bias_context,
        demographic,
        bias_template,
        prompt,
    ) in enumerate(prompts.itertuples(index=False)):
        print(f"Evaluating prompt {idx}/{len(prompts)}: {prompt}")
        completion = post_process_response(response_func(prompt))
        results.append(
            (
                model_name,
                bias_context,
                demographic,
                bias_template,
                prompt,
                completion,
            )
        )

    results_df = pd.DataFrame(
        results,
        columns=[
            "model",
            "bias_context",
            "demographic",
            "bias_template",
            "prompt",
            "completion",
        ],
    )
    print(results_df)
    results_df.to_csv(args.results, index=False)
    print(f"Wrote results to {args.results}")


if __name__ == "__main__":
    main()
