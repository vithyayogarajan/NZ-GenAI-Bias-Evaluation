
## Bias Evaluation

Pre-trained models obtained from the open-sourced [Hugging Face platform](https://huggingface.co/evaluate-measurement). 

Toxicity is measured using a pre-trained model and [Perspective API](https://www.perspectiveapi.com/). It is defined as either toxic or non-toxic, where the toxic if the score is $>=$ 0.5. 

Sentiment analysis is performed using [VADER](https://github.com/cjhutto/vaderSentiment), a lexicon and rule-based sentiment analysis tool, where positive, negative, and neutral scores are reported. 

Regard scores are extended from sentiment scores, which measures the language polarity towards and social perceptions of a demographic. 

HONEST is a lexicon-based metric designed to compare across multiple demographics by measuring the number of hurtful completions based on a pre-compiled list of words.  

The holistic evaluation of language models (HELM) bias scores are obtained using the open-sourced code. The [HELM bias score](https://github.com/stanford-crfm/HELM/tree/main) is calculated by computing the target words' and demographic groups' mean stereotypical association bias using pre-defined word lists.

Llama-safeguard is a fine-tuned guardrail model developed on the Llama2-7b architecture. Llama-safeguard uses eight categories to determine if a string of text is safe or unsafe:
    O1: Violence and Hate 
    O2: Criminal Planning 
    O3: Sexual Content 
    O4: Guns and Illegal Weapons 
    O5: Regulated or Controlled Substances 
    O6: Self-Harm; O7: Financial Information related to Amazon 
    O8: Talk about Cancer (i.e. should not provide medical advice). 
