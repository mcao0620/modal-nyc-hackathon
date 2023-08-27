# Workflow Results
## Response
# Task Ticket: Refactor Scoring and Plotting Code

## Description
The task is to refactor the scoring and plotting code in the existing codebase. The code snippets provided include abstract base classes, methods for parsing responses from a language model, generating prompts, and executing operations. The goal is to improve the efficiency and readability of the code, as well as enhance the visualization of the results.

## Subtasks

### 1. Refactor the scoring code to calculate scores for different methods based on the results obtained. (Priority: 9)
- Update the `get_final_scores` function to calculate scores for different methods based on the results obtained.
- Iterate over the `results_complete` dictionary and extract the necessary information to calculate scores.
- Store the scores in a dictionary with the method names as keys.

```python
def get_final_scores(results_complete):
    scores = {}
    for method in results_complete.keys():
        scores[method] = []
        for result in results_complete[method]:
            # Calculate score based on result data
            # ...
            scores[method].append(
                [result["key"], score, solved, prompt_tokens, completion_tokens, cost]
            )
        scores[method] = sorted(scores[method], key=lambda x: x[0])
    return scores
```

### 2. Implement a function to parse the responses from the language model for aggregation and improvement prompts. (Priority: 7)
- Implement the `parse_aggregation_answer` method in the `Parser` class to parse the response from the language model for an aggregation prompt.
- Implement the `parse_improve_answer` method in the `Parser` class to parse the response from the language model for an improvement prompt.
- These methods should take the necessary inputs and return the new thought states after parsing the response.

```python
class Parser:
    def parse_aggregation_answer(states, texts):
        # Parse response for aggregation prompt
        # ...
        return new_states
    
    def parse_improve_answer(state, texts):
        # Parse response for improvement prompt
        # ...
        return new_state
```

### 3. Modify the existing code to generate prompts for the language model based on the provided thought states. (Priority: 6)
- Implement the `generate_prompt` method in the `Prompter` class to generate a prompt for the language model.
- Implement the `validation_prompt` method in the `Prompter` class to generate a validation prompt for the language model.
- Implement the `score_prompt` method in the `Prompter` class to generate a score prompt for the language model.
- These methods should take the necessary inputs and return the generated prompts as strings.

```python
class Prompter:
    def generate_prompt(num_branches, **kwargs):
        # Generate prompt for language model
        # ...
        return prompt
    
    def validation_prompt(**kwargs):
        # Generate validation prompt for language model
        # ...
        return prompt
    
    def score_prompt(state_dicts, **kwargs):
        # Generate score prompt for language model
        # ...
        return prompt
```

### 4. Update the plotting code to display the results in boxplots. (Priority: 8)
- Refactor the `plot_results` function to display the results in boxplots.
- Modify the function to take the necessary parameters for plotting, such as the method order, length, upper limits for the y-axis and cost, and display options.
- Generate the boxplots accordingly.

```python
def plot_results(directory, plotting_data, **kwargs):
    # Display results in boxplots
    # ...
```

### 5. Ensure that the refactored code is compatible with the existing codebase and follows the specified interfaces and abstract classes. (Priority: 10)
- Review the existing codebase and ensure that the refactored code integrates seamlessly.
- Verify that the refactored code follows the specified interfaces and abstract classes.
- Test the refactored code to ensure it produces the expected results.

## Note
The provided code snippets may not be complete or directly related to the issue. Please refer to the existing codebase for complete context and ensure that the refactored code integrates seamlessly with the existing code.
## Relevant Chunks
['def get_final_scores(results_complete):\n    scores = {}\n    for method in results_complete.keys():\n        scores[method] = []\n        for result in results_complete[method]:\n            score = 100\n            solved = False\n            cost = 1\n            prompt_tokens = 0\n            completion_tokens = 0\n            for op in result["data"]:\n                if "operation" in op and op["operation"] == "ground_truth_evaluator":\n                    try:\n                        score = min(op["scores"])\n                        solved = any(op["problem_solved"])\n                    except:\n                        continue\n                if "cost" in op:\n                    cost = op["cost"]\n                    prompt_tokens = op["prompt_tokens"]\n                    completion_tokens = op["completion_tokens"]\n            scores[method].append(\n                [result["key"], score, solved, prompt_tokens, completion_tokens, cost]\n            )\n        scores[method] = sorted(scores[method], key=lambda x: x[0])\n    return scores', 'def get_final_scores_doc_merge(results_complete):\n    scores = {}\n    for method in results_complete.keys():\n        scores[method] = []\n        for result in results_complete[method]:\n            score = 0\n            solved = False\n            cost = 1\n            prompt_tokens = 0\n            completion_tokens = 0\n            for op in reversed(result["data"]):\n                if "cost" in op:\n                    cost = op["cost"]\n                    prompt_tokens = op["prompt_tokens"]\n                    completion_tokens = op["completion_tokens"]\n                if "operation" in op and op["operation"] == "score":\n                    try:\n                        score = max(op["scores"])\n                        break\n                    except:\n                        continue\n            scores[method].append(\n                [result["key"], score, solved, prompt_tokens, completion_tokens, cost]\n            )\n        scores[method] = sorted(scores[method], key=lambda x: x[0])\n    return scores\n\n\ndef get_plotting_data(base_directory, score_method):\n    results_complete = get_complete_results(base_directory)\n    scores = score_method(results_complete)\n    results_plotting = {\n        method: {\n            "scores": [x[1] for x in scores[method]],\n            "solved": sum([1 for x in scores[method] if x[2]]),\n            "costs": [x[5] for x in scores[method]],\n        }\n        for method in scores.keys()\n    }\n    return results_plotting', 'plot_results(\n    "sorting",\n    get_plotting_data("sorting_gpt35_128", get_final_scores),\n    length=128,\n    y_upper=128,\n    cost_upper=17,\n    display_solved=False,\n    display_left_ylabel=True,\n    display_right_ylabel=True,\n)\n\nplot_results(\n    "keyword_counting",\n    get_plotting_data("keyword_counting_gpt35", get_final_scores),\n    methods_order=["io", "cot", "tot", "tot2", "gsp4", "gsp8", "gspx"],\n    methods_labels=["IO", "CoT", "ToT", "ToT2", "GoT4", "GoT8", "GoTx"],\n    y_upper=35,\n    cost_upper=9,\n    display_solved=True,\n    annotation_offset=-0.3,\n    display_left_ylabel=True,\n    display_right_ylabel=True,\n)\n\nplot_results(\n    "document_merging",\n    get_plotting_data("document_merging_gpt35_16k", get_final_scores_doc_merge),\n    methods_order=["io", "cot", "tot", "gsp", "gsp2"],\n    methods_labels=["IO", "CoT", "ToT", "GoT", "GoT2"],\n    y_upper=10,\n    cost_upper=15,\n    display_solved=False,\n    display_left_ylabel=True,\n    display_right_ylabel=True,\n)']
## Helpful Chunks
[]
