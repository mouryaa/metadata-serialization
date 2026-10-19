# OntoURL & LLMs for Ontologies — Strategy Memo

Oct 13, 2026 · @Mourya

## Executive summary

LLMs are ready to read, explain and query formal ontologies, but not to author them unsupervised. OntoURL, a new 36,159-item benchmark built from 43 expert ontologies including FIBO, measures this across 15 tasks and 20 open models.

1. **Reading and inference work.** The best open models score 85 to 95% on recognizing definitions, class membership and inferred hierarchy, ahead of a small closed-book human baseline.
2. **Building precise structure does not.** Property-relation and constraint triples top out at 12.0 and 35.2 F1 zero-shot (27.6 and 41.9 with examples), where humans score about 50.
3. **General models beat specialists.** Finance, medical, legal and biology fine-tunes lost to same-size general models, even in their own domains.
4. **Mid-size is enough.** 24 to 32B models land within a few points of 70B models on most tasks, which matters for self-hosting.
5. **Prompting must fit the task.** Examples help structured output; chain-of-thought helps formal logic checks and hurts triple generation.

The practical design is an LLM working beside a reasoner and a curator: the model drafts and explains, the reasoner verifies, the human decides. Before committing, rerun the open benchmark pipeline on our own ontologies and on the frontier models OntoURL did not test.

## The paper in brief

[OntoURL](https://doi.org/10.1016/j.websem.2026.100886) (Zhang, Lai, Meng, Bos; University of Groningen and Leiden; *Journal of Web Semantics* 91, published online 12 Sep 2026) is the first single benchmark that scores LLMs on all three things people want from them around ontologies: reading them, reasoning over them, and helping build them.

**The URL taxonomy.** The authors split ontology capability into three levels, modeled on Bloom's taxonomy. "URL" has nothing to do with web addresses.

| Level | Question it answers | Tasks |
| --- | --- | --- |
| Understanding | Can the model recognize facts the ontology states outright? | U1 class definitions, U2 class relations, U3 property domain/range, U4 instance types, U5 instance descriptions |
| Reasoning | Can it derive facts the ontology implies but does not state? | R1 inferred class relations, R2 property constraints and chains, R3 inferred instance types, R4 SWRL-style rules, R5 Description Logic satisfiability |
| Learning | Can it produce new ontology content? (ontology engineering, not model training) | L1 term extraction, L2 definition writing, L3 hierarchy triples, L4 property-relation triples, L5 domain/range constraint triples |

**Scale.** 36,159 items from 43 expert-built open ontologies across 8 domains. Business & Finance is the largest share (29.8%), drawn from FIBO, its Financial Instruments module, BPMN, the Occupation Ontology, the W3C-style Organization Ontology and the Public Contracts Ontology. Health & Medicine (17.6%) and Arts/Media (13.4%) follow.

**How the answer key is built.** Gold answers come from the ontology files or from a formal reasoner (HermiT), never from an LLM. Reasoning items that the reasoner cannot validate in time are dropped, not guessed. DeepSeek is used only to smooth the wording of 1,262 term-extraction passages, and any rewrite that drops an ontology label is rejected.

**Quality checks.** Wrong answer options are chosen to be plausible (siblings, near-ancestors), not random. Three experts reviewed a 20% sample of every task each. On the shared 5% overlap, 97.8% of items passed for syntax and 95.4% for semantic correctness, with Fleiss' kappa of 0.85 to 0.89.

**Who was tested.** 20 open-weight models: 14 general-purpose (Qwen2.5 7B/32B/72B, Qwen3 8B/32B, Gemma-4 E4B/26B, Phi-4, Llama 3.3 70B, Aya-Expanse 8B/32B, InternLM3-8B, Mistral-Small-24B, GLM-4-32B), two ontology-fine-tuned models (OLLM-wiki and OLLM-arxiv), and four domain specialists (Finance-Chat, Medicine-Chat, BioMistral, SaulLM). No closed frontier models (GPT, Claude, Gemini) were evaluated.

## Key findings

Open LLMs already read and reason over ontologies well, scoring 78 to 95% on nine of the ten closed-form tasks. They cannot yet be trusted to author property relations or constraints, where the best scores are 12.0 and 35.2 F1.

&#91;embedded content: OntoURL Table 4 (zero-shot, best general-purpose model) and Table 5 (human mean of 3 participants, computed here)\]

The human baseline uses 40 sampled items per task under closed-book rules, so treat it as context rather than a head-to-head. L2 also favors models, because BERTScore rewards wording close to the reference definition.

1. **Recognition is strong, except for property semantics.** Best scores exceed 85% on U1, U2, U4 and U5, but only 65.9% on U3 (property domain and range). The authors suspect domain/range facts are rare in ordinary text, though they do not test this.
2. **Constrained reasoning is not harder than recognition.** Qwen2.5-32B reaches 92.6% on R1 and 95.0% on R2. Formal Description Logic (R5) separates models most: zero-shot scores run from 53.0% (Qwen2.5-7B) to 88.2% (Llama 3.3 70B).
3. **Quality drops along the construction pipeline.** Term extraction peaks at 91.5, hierarchy triples at 56.8, constraint triples at 35.2 and property-relation triples at 12.0. In the case study, strong models emit well-formed but invented relations that are not in the source ontology.
4. **Size helps, but task leaders come from 32B to 72B.** Qwen2.5-72B leads seven tasks and Qwen2.5-32B leads four. Mistral-Small-24B and Phi-4 (14B) land within about five points on most closed-form tasks.
5. **Domain specialists lose to generalists, even in their home domain.** On the finance tasks, Finance-Chat-7B averages 0.01% on understanding and 10.45% on reasoning, versus 82.74% and 81.97% for Qwen3-32B. On biology reasoning, Qwen3-8B scores 81.0% and BioMistral 9.8%. Models fine-tuned on taxonomies (OLLM) stay below 50% on most understanding and reasoning tasks.
6. **Mid-depth concepts are hardest.** Accuracy is 82 to 94% at the ontology root but falls to 73.5 to 79.5% at depths 2 to 3, then recovers deeper down. Common labels with close sibling distractors seem to cause this.
7. **Few-shot examples help construction; chain-of-thought mostly does not.** Four examples lift Qwen2.5-72B's L3 to L5 average from 33.9 to 41.7, and Llama 3.3 70B's L4 from 11.3 to 27.6 with two. Chain-of-thought adds 6.5 to 25.2 points on R5 but costs 2.3 to 4.0 points on structured construction, and 5.8 points on Qwen3-32B's understanding average.

## Model-selection guide

Pick by task, not by leaderboard. A 24 to 32B open model with the right prompt covers most ontology reading and reasoning work. Construction tasks need a human owner whatever model you pick. Every score below is from OntoURL (Tables 4, F.26 and F.27); closed frontier models were not tested and should be benchmarked before you assume they do better.

| Ontology job | OntoURL tasks | Best observed score | Smallest model near the top | Prompting | Who owns the output |
| --- | --- | --- | --- | --- | --- |
| Look up a class, definition or instance type | U1, U2, U4, U5 | 85.6 to 90.4% zero-shot (Qwen2.5-72B) | Mistral-Small-24B (84.2 to 88.1%); 7 to 8B models reach 75 to 84% | Zero-shot. Few-shot adds little and can hurt. | LLM, with spot checks |
| Look up a property's domain or range | U3 | 66.4% (Gemma-4-26B, 4-shot) | None reliable | Don't use an LLM. Query the ontology directly (e.g., SPARQL). | System of record |
| Infer superclasses and property constraints | R1, R2 | 92.9% and 95.2% (Qwen2.5-72B, 4-shot) | Qwen2.5-32B (92.6% and 95.0% zero-shot) | Zero-shot is enough. | Reasoner for truth, LLM to explain it |
| Infer an instance's class; apply rules | R3, R4 | 79.4% and 85.4% (4-shot) | Qwen2.5-32B or Mistral-Small-24B | Few-shot gives 1 to 6 points. | Reasoner for truth, LLM to explain it |
| Judge Description Logic satisfiability | R5 | 95.4% (Gemma-4-26B with chain-of-thought) | Gemma-4-26B; small models swing 53 to 87% | Chain-of-thought (+6.5 to +25.2 points). | A DL reasoner does this exactly; use the LLM only for explanations |
| Pull candidate terms from text | L1 | 95.1 F1 (Qwen2.5-32B, 4-shot) | Phi-4 (93.9 F1, 4-shot) | 4-shot | LLM drafts, curator approves |
| Draft class definitions | L2 | 84 to 89 BERTScore (most models) | Any 7B+ model | Zero- or few-shot | Curator edits; the metric doesn't measure correctness |
| Propose a class hierarchy | L3 | 60.4 F1 (Qwen2.5-72B, 4-shot) | Qwen2.5-32B (60.3 F1, 2-shot) | 2 to 4 shots; avoid chain-of-thought | Curator decides; LLM proposes |
| Propose property relations | L4 | 27.6 F1 (Llama 3.3 70B, 2-shot) | Mistral-Small-24B (26.2 F1, 4-shot) | Few-shot more than doubles F1 | Human-led; LLM only suggests |
| Propose domain/range constraints | L5 | 41.9 F1 (Qwen2.5-72B, 4-shot) | Qwen3-32B (39.9 F1, 4-shot) | 4-shot | Human-led; validate with a reasoner or SHACL |

Three prompting rules hold across the results.

1. **Use examples for structured output.** Few-shot is the one technique that reliably lifts triple generation (L3 to L5). It works mainly by showing the output format.
2. **Use chain-of-thought only for yes/no logic.** It helps Description Logic checks and hurts tasks that need exact triples.
3. **Pilot every prompt on every model.** The same chain-of-thought prompt dropped Aya-Expanse-32B from 82.8% to 18.8% on U1, and the OLLM models fell to chance on multiple choice and to zero on term extraction with few-shot prompts. Parse failures, not knowledge gaps, drove much of this.

On model choice, prefer a strong general-purpose model over a domain-tuned one. OntoURL found no case where a finance, medical, legal or biology specialist beat a same-size generalist on ontology work, even in its own domain.

## Research landscape

The wider literature agrees with OntoURL: LLMs recall and apply familiar ontology structure well, but their "reasoning" leans on word meaning, and precise axiom-level construction is not yet automatable. OntoURL's contribution is putting all three capability levels on one scorecard over the same 43 ontologies.

| Theme | Work | What it found | What it adds to OntoURL |
| --- | --- | --- | --- |
| Stored knowledge | [Wu et al., ACL 2023](https://aclanthology.org/2023.acl-long.173/) (outstanding paper) | Pretrained models memorize some entity types, hierarchies and domain/range constraints, and can reason with them, but imperfectly. | An early sign of the U3 domain/range weakness. |
| Stored knowledge | [Bombieri et al., ACM TIST](https://arxiv.org/abs/2401.14931v2) | Only a small share of concept ID–label pairs (Gene Ontology, Uberon, ICD-10, Wikidata) is memorized correctly. Accuracy tracks how often a concept appears on the web. | Never trust a model to recall identifiers or IRIs. Retrieve them from the ontology. |
| Stored knowledge | [Sun et al., VLDB 2024](https://arxiv.org/html/2406.11131v2) (TaxoGlimpse) | Across 18 models and 10 taxonomies, accuracy is good on common taxonomies, drops on specialized ones, and generally falls from root to leaf. | OntoURL instead sees a mid-depth dip and recovery, so depth effects depend on the ontology and the task. |
| Reasoning | [He et al., ACL Findings 2023](https://arxiv.org/abs/2302.06761v3) (OntoLAMA) | Language models hold less subsumption knowledge than general inference knowledge, but improve sharply given a few examples. | Earlier evidence that few-shot examples matter for ontology inference. |
| Reasoning | [Wang et al., EMNLP Findings 2024](https://arxiv.org/abs/2406.17532v2) (DL-Lite) | Models handle Description Logic syntax and concept/role semantics, but fail on transitivity of negative inclusions and on large instance sets. | Explains why R5 spreads models so widely and why scale of the ABox matters. |
| Reasoning | [Jiang et al., KDD 2025](https://arxiv.org/html/2503.00912v1) (HiBench) | Basic hierarchy reasoning is solid; complex or implicit hierarchies are not. In-context examples help; plain chain-of-thought helps little. | Same prompting pattern as OntoURL, on generic hierarchies. |
| Reasoning | [Tang et al., 2023](https://arxiv.org/abs/2305.14825v2) | Models reason well when content matches common sense, and struggle when meaning is stripped out or contradicts it. | OntoURL uses readable labels. Opaque IDs or counter-intuitive internal terms would likely score lower. |
| Construction | [Babaei Giglou et al., ISWC 2023](https://arxiv.org/abs/2307.16648v2) (LLMs4OL) and the [2024 challenge](https://themoonlight.io/review/llms4ol-2024-overview-the-1st-large-language-models-for-ontology-learning-challenge) | Zero-shot tests of nine model families on term typing, taxonomy discovery and non-taxonomic relations; now an annual ISWC challenge. | The main venue for tracking progress on L1 to L4-style tasks. |
| Construction | [Lo et al., NeurIPS 2024](https://neurips.cc/virtual/2024/poster/94942) (OLLM) | Fine-tuning a model to emit whole taxonomy subgraphs beats piecing together subtasks on Wikipedia. | In OntoURL, these same models fail most other tasks: narrow fine-tuning does not generalize. |
| Construction | [Lippolis et al., ESWC 2025](https://arxiv.org/abs/2503.05388v1) | With the Ontogenia prompt, o1-preview drafts OWL ontologies from user stories and competency questions well enough for engineers, beating novice modelers. Quality still varies run to run. | The strongest positive construction result, and on a closed reasoning model OntoURL did not test. |
| Construction | [Bakker et al., 2025](https://arxiv.org/abs/2512.05594v1) (OntoAxiom) | 12 models on 2,771 axioms from 9 ontologies. Not good enough to automate; subclass scores range from 0.642 (FOAF) to 0.218 (music). Useful as candidate generators. | Independently confirms the L4/L5 bottleneck. |
| Evaluation method | [Paulheim, ISWC 2025 workshop](https://ceur-ws.org/Vol-4041/paper2.pdf) | Public ontologies are likely in training data; proposes evaluating on generated, unseen test ontologies. | OntoURL's main validity risk; test on your own private ontologies. |
| Evaluation method | [Saeedizade et al.](https://semantic-web-journal.net/node/4055) (CoLLM) | Three tests (repeatability, model-update impact, model replacement) applied to 59 experiments from 5 studies. | A ready protocol for re-checking results when a model version changes. |
| Evaluation method | [Alharbi et al., ISWC 2024](https://ceur-ws.org/Vol-3953/369.pdf) | Sets out what a competency-question benchmark should contain. | Competency questions are a gap OntoURL leaves open. |
| Surveys | [Garijo et al., 2024](https://ceur-ws.org/Vol-3953/364.pdf); [Li, Garijo, Poveda-Villalón](https://semantic-web-journal.net/node/4039) | LLMs act mainly as auxiliary engineers, domain experts and evaluators. Task definitions, datasets and metrics are not standardized. | Why a unified benchmark like OntoURL is useful. |
| Debate | [Neuhaus, Applied Ontology 2023](https://doi.org/10.3233/AO-230072); [Neuhaus and Hastings, FOIS 2024](https://utwente.nl/en/eemcs/fois2024/resources/papers/hastings-the-illusionary-goal-of-automating-ontology-development.pdf) | Ontologies stay relevant. Full automation misreads ontology building, which is consensus-making, not translation. | Supports OntoURL's human-in-the-loop conclusion on principle, not only on scores. |

The rest of OntoURL's 114 references fall into four groups: classical ontology learning from text (Hearst patterns, Maedche and Staab, surveys by Biemann and Asim), classical DL reasoners (FaCT++, ELK, HermiT, Arachne), ontology matching (OAEI-style alignment systems), and the source ontologies themselves (FIBO, Gene Ontology, NCIt, CIDOC CRM and others).

One caution on versions: the [2025 arXiv preprint](https://alphaxiv.org/benchmarks/leiden-university/ontourl) reported 57,303 questions from 40 ontologies, with learning-task F1 often below 5%. The journal version rebuilt the benchmark (36,159 items, 43 ontologies). Cite only the journal numbers.

## Critical assessment

OntoURL is a careful benchmark, but its numbers are a floor for today's best systems and an imperfect guide to private enterprise ontologies. Seven limits matter most.

1. **No frontier or reasoning models.** All 20 models are open-weight and 4 to 72B. Lippolis et al. got usable OWL drafts from o1-preview, so construction scores (L3 to L5) likely understate what current closed reasoning models can do.
2. **Public ontologies invite memorization.** FIBO, the Gene Ontology and NCIt are all on the open web. The authors admit OntoURL measures ontology-oriented behavior, not unseen knowledge. Scores on a private, internally coded ontology could be noticeably lower.
3. **Readable labels flatter the models.** Items use human-readable names. Tang et al. show models reason worse when meaning is removed, and enterprise models often use codes, abbreviations or internal jargon.
4. **Strict metrics undercount valid answers and overcount fluent ones.** Triple-F1 needs an exact match, so a correct but differently phrased triple scores zero; other studies found many "false positives" were valid alternatives or gaps in the reference ontology ([Toro et al., DRAGON-AI](https://arxiv.org/pdf/2312.10904)). BERTScore on L2 rewards similar wording, not correct definitions.
5. **The human baseline is thin.** Three participants answered 40 items per task, without access to the ontology. Real curators work with the ontology open, so the human-vs-model gap on recognition overstates the advantage in practice.
6. **Small and uneven samples.** L4 has only 264 items and L5 613. Business & Finance is 29.8% of items, Human & Society 2.6%. Each model was run once at temperature 0 with no confidence intervals, so gaps of 1 to 2 points between top models are noise.
7. **No tool-assisted setting.** Retrieval, SPARQL access, reasoner-in-the-loop and fine-tuning were not tested. These are how a production system would actually be built.

One housekeeping point: the paper cites the dataset at `XiaoZhang98/OntoURL` under CC BY 4.0, while an earlier `XiaoZhang98/OntoBench` dataset (Apache 2.0) is also on Hugging Face. Confirm you have the journal release before running anything.

## Recommendations

Treat the LLM as a fast reader and drafter sitting next to the ontology and a reasoner, never as the ontology itself. Six steps follow from the evidence.

**Adopt now**

1. **Use LLMs to read and explain ontologies.** Definition lookup, class membership, hierarchy questions and term extraction all score 85 to 95%. Ground each answer in the ontology through retrieval or SPARQL, so the model never recalls IDs or domain/range facts from memory.
2. **Keep a formal reasoner for anything that must be correct.** Inference, consistency and satisfiability checks belong to a reasoner (HermiT, ELK). The LLM translates the result into plain language.
3. **Run construction as "LLM proposes, curator decides."** Use 2 to 4 worked examples per prompt, avoid chain-of-thought for triple output, and pass every proposed axiom through a reasoner and SHACL shape checks before a human reviews it.

**Test next**

4. **Build a private OntoURL.** The construction pipeline is open source (MIT). Point it at one or two internal ontologies to get leakage-free test items in your own vocabulary.
5. **Benchmark the models you would actually use.** Include at least one closed frontier reasoning model and one 24 to 32B self-hostable model. Add CoLLM-style repeatability and model-update checks so a version change can't silently move results.
6. **Skip domain-specialist fine-tunes for this work.** No finance, medical, legal or biology model beat a general model of the same size here. Spend effort on retrieval and validation instead.

**Track**: the annual LLMs4OL challenge at ISWC, OntoAxiom results, and any OntoURL rerun that includes frontier models.

## Technical appendix

Everything needed to rerun or extend OntoURL is public. The settings below come from the paper's Appendix E.

| Item | Setting |
| --- | --- |
| Inference | vLLM on 4× NVIDIA H100 80 GB, CUDA 12.8, model chat templates |
| Decoding | Temperature 0.0, top-p 1.0, seed 0, single run per model |
| Output limits | 128 tokens (multiple choice, true/false), 512 (L1, L2), 1,024 (L3 to L5); chain-of-thought runs get 1,024 / 768 / 2,048 |
| Prompt variants | Zero-shot, 2-shot, 4-shot (examples from a held-out pool), zero-shot chain-of-thought |
| Scoring | Accuracy (U1 to R5); Entity-F1 (L1); BERTScore F1 with roberta-large, no baseline rescaling (L2); Triple-F1 after literal and regex parsing (L3 to L5) |
| Parse failures | Unparseable answers count as wrong or as empty sets; failure counts are logged separately |
| Reproducibility | Hugging Face snapshot hashes listed per model; early result files did not record exact model commits |

**Resources**

- Paper: [doi.org/10.1016/j.websem.2026.100886](https://doi.org/10.1016/j.websem.2026.100886) (open access, CC BY)
- Construction pipeline: [github.com/LastDance500/Bench\_Construct](https://github.com/LastDance500/Bench_Construct) (MIT)
- Evaluation code: [github.com/LastDance500/OntoURL](https://github.com/LastDance500/OntoURL) (MIT)
- Dataset: [huggingface.co/datasets/XiaoZhang98/OntoURL](https://huggingface.co/datasets/XiaoZhang98/OntoURL) (CC BY 4.0 where source licenses permit)
- Related datasets: [OntoLAMA](https://zenodo.org/records/7700458), [TaxoGlimpse](https://vldb.org/pvldb/vol17/p2919-sun.pdf), [HiBench](https://arxiv.org/abs/2503.00912), [OLLM](https://neurips.cc/virtual/2024/poster/94942)

## Sources

- [Zhang et al., OntoURL, Journal of Web Semantics 91 (2026)](https://doi.org/10.1016/j.websem.2026.100886)
- [OntoURL arXiv preprint summary (2025)](https://alphaxiv.org/benchmarks/leiden-university/ontourl)
- [Wu et al., ACL 2023](https://aclanthology.org/2023.acl-long.173/)
- [Bombieri et al., Do LLMs Dream of Ontologies?](https://arxiv.org/abs/2401.14931v2)
- [Sun et al., VLDB 2024](https://arxiv.org/html/2406.11131v2)
- [He et al., OntoLAMA](https://arxiv.org/abs/2302.06761v3)
- [Wang et al., DL-Lite](https://arxiv.org/abs/2406.17532v2)
- [Jiang et al., HiBench](https://arxiv.org/html/2503.00912v1)
- [Tang et al., semantic vs symbolic reasoners](https://arxiv.org/abs/2305.14825v2)
- [Babaei Giglou et al., LLMs4OL](https://arxiv.org/abs/2307.16648v2)
- [Lo et al., OLLM](https://neurips.cc/virtual/2024/poster/94942)
- [Lippolis et al., Ontology generation](https://arxiv.org/abs/2503.05388v1)
- [Bakker et al., OntoAxiom](https://arxiv.org/abs/2512.05594v1)
- [Paulheim, leakage-free evaluation](https://ceur-ws.org/Vol-4041/paper2.pdf)
- [Saeedizade et al., CoLLM](https://semantic-web-journal.net/node/4055)
- [Alharbi et al., CQ benchmark desiderata](https://ceur-ws.org/Vol-3953/369.pdf)
- [Garijo et al., landscape](https://ceur-ws.org/Vol-3953/364.pdf)
- [Li, Garijo, Poveda-Villalón, systematic review](https://semantic-web-journal.net/node/4039)
- [Neuhaus, Applied Ontology](https://doi.org/10.3233/AO-230072)
- [Neuhaus and Hastings, FOIS 2024](https://utwente.nl/en/eemcs/fois2024/resources/papers/hastings-the-illusionary-goal-of-automating-ontology-development.pdf)
- [Toro et al., DRAGON-AI](https://arxiv.org/pdf/2312.10904)
- [OntoBench dataset on Hugging Face](https://huggingface.co/datasets/XiaoZhang98/OntoBench/blob/main/data/1_2_class2class.csv)
