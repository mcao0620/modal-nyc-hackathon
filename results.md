# Workflow Results
## Response
# Task Ticket: Develop Web Crawler for OpenAI Response and Input Token Costs

## Issue Description
The task is to develop a web crawler that retrieves response and input token costs from the OpenAI website using the model ID.

## Subtasks

### 1. Implement Web Crawler
**Priority: 10**

- Develop a web crawler that can retrieve response and input token costs from the OpenAI website using the model ID.
- Ensure the web crawler is efficient, reliable, and handles any potential errors or exceptions gracefully.
- Test the web crawler with different model IDs and verify that it retrieves the response and input token costs accurately.
- Provide appropriate error handling and logging mechanisms to facilitate troubleshooting and debugging.

### 2. Implement `get_final_scores` Function
**Priority: 8**

- Implement the `get_final_scores` function to process the retrieved data and return the scores, solved status, prompt tokens, completion tokens, and cost for each method.
- Ensure the function handles different scenarios and provides accurate results.
- Write unit tests to verify the correctness of the implemented functionality.

### 3. Implement `add_operation` Method
**Priority: 7**

- Implement the `add_operation` method to add operations to the graph, considering their predecessors and successors.
- Adjust the roots and leaves based on the added operation's position within the graph.
- Ensure the method follows the specified coding standards and best practices.
- Write unit tests to verify the correctness of the implemented functionality.

### 4. Implement `plot_results` Function
**Priority: 6**

- Implement the `plot_results` function to plot the results for different methods and save the plot as a PDF file.
- Ensure the function handles different scenarios and provides accurate plots.
- Write unit tests to verify the correctness of the implemented functionality.

### 5. Implement `GraphOfOperations` Class
**Priority: 5**

- Implement the `GraphOfOperations` class to represent the graph of operations and provide methods for initializing the graph, appending operations, and generating prompts.
- Ensure the class follows the specified coding standards and best practices.
- Write unit tests to verify the correctness of the implemented functionality.

### 6. Implement `Prompter` Class
**Priority: 4**

- Implement the `Prompter` class as a concrete implementation of the abstract base class, providing methods for generating prompts.
- Ensure the class follows the specified coding standards and best practices.
- Write unit tests to verify the correctness of the implemented functionality.

### 7. Code Documentation and Comments
**Priority: 3**

- Document the code and provide clear comments to enhance readability and maintainability.
- Ensure the code follows the specified coding standards and best practices.

### 8. Code Review and Feedback
**Priority: 2**

- Perform code reviews and address any feedback or suggestions for improvement.
- Collaborate with the product manager and other stakeholders to clarify requirements and gather any additional information or specifications as needed.

### 9. Scalability and Performance Optimization
**Priority: 1**

- Ensure that the implementation is scalable and can handle a large volume of data efficiently.
- Optimize the code for performance and consider any potential security vulnerabilities.

### 10. Deployment and Monitoring
**Priority: 1**

- Deploy the web crawler to a production environment and monitor its performance and stability.
- Provide necessary documentation and support for the deployed solution.

### 11. Continuous Improvement
**Priority: 1**

- Continuously improve the web crawler based on user feedback and evolving requirements.

## Relevant Code Snippets
```python
plot_results(
    "sorting",
    get_plotting_data("sorting_gpt35_128", get_final_scores),
    length=128,
    y_upper=128,
    cost_upper=17,
    display_solved=False,
    display_left_ylabel=True,
    display_right_ylabel=True,
)

plot_results(
    "keyword_counting",
    get_plotting_data("keyword_counting_gpt35", get_final_scores),
    methods_order=["io", "cot", "tot", "tot2", "gsp4", "gsp8", "gspx"],
    methods_labels=["IO", "CoT", "ToT", "ToT2", "GoT4", "GoT8", "GoTx"],
    y_upper=35,
    cost_upper=9,
    display_solved=True,
    annotation_offset=-0.3,
    display_left_ylabel=True,
    display_right_ylabel=True,
)

plot_results(
    "document_merging",
    get_plotting_data("document_merging_gpt35_16k", get_final_scores_doc_merge),
    methods_order=["io", "cot", "tot", "gsp", "gsp2"],
    methods_labels=["IO", "CoT", "ToT", "GoT", "GoT2"],
    y_upper=10,
    cost_upper=15,
    display_solved=False,
    display_left_ylabel=True,
    display_right_ylabel=True,
)

def get_final_scores_doc_merge(results_complete):
    scores = {}
    for method in results_complete.keys():
        scores[method] = []
        for result in results_complete[method]:
            score = 0
            solved = False
            cost = 1
            prompt_tokens = 0
            completion_tokens = 0
            for op in reversed(result["data"]):
                if "cost" in op:
                    cost = op["cost"]
                    prompt_tokens = op["prompt_tokens"]
                    completion_tokens = op["completion_tokens"]
                if "operation" in op and op["operation"] == "score":
                    try:
                        score = max(op["scores"])
                        break
                    except:
                        continue
            scores[method].append(
                [result["key"], score, solved, prompt_tokens, completion_tokens, cost]
            )
        scores[method] = sorted(scores[method], key=lambda x: x[0])
    return scores


def get_plotting_data(base_directory, score_method):
    results_complete = get_complete_results(base_directory)
    scores = score_method(results_complete)
    results_plotting = {
        method: {
            "scores": [x[1] for x in scores[method]],
            "solved": sum([1 for x in scores[method] if x[2]]),
            "costs": [x[5] for x in scores[method]],
        }
        for method in scores.keys()
    }
    return results_plotting

def get_final_scores(results_complete):
    scores = {}
    for method in results_complete.keys():
        scores[method] = []
        for result in results_complete[method]:
            score = 100
            solved = False
            cost = 1
            prompt_tokens = 0
            completion_tokens = 0
            for op in result["data"]:
                if "operation" in op and op["operation"] == "ground_truth_evaluator":
                    try:
                        score = min(op["scores"])
                        solved = any(op["problem_solved"])
                    except:
                        continue
                if "cost" in op:
                    cost = op["cost"]
                    prompt_tokens = op["prompt_tokens"]
                    completion_tokens = op["completion_tokens"]
            scores[method].append(
                [result["key"], score, solved, prompt_tokens, completion_tokens, cost]
            )
        scores[method] = sorted(scores[method], key=lambda x: x[0])
    return scores
```

Please let me know if you need any further information or clarification.
## Relevant Chunks
['plot_results(\n    "sorting",\n    get_plotting_data("sorting_gpt35_128", get_final_scores),\n    length=128,\n    y_upper=128,\n    cost_upper=17,\n    display_solved=False,\n    display_left_ylabel=True,\n    display_right_ylabel=True,\n)\n\nplot_results(\n    "keyword_counting",\n    get_plotting_data("keyword_counting_gpt35", get_final_scores),\n    methods_order=["io", "cot", "tot", "tot2", "gsp4", "gsp8", "gspx"],\n    methods_labels=["IO", "CoT", "ToT", "ToT2", "GoT4", "GoT8", "GoTx"],\n    y_upper=35,\n    cost_upper=9,\n    display_solved=True,\n    annotation_offset=-0.3,\n    display_left_ylabel=True,\n    display_right_ylabel=True,\n)\n\nplot_results(\n    "document_merging",\n    get_plotting_data("document_merging_gpt35_16k", get_final_scores_doc_merge),\n    methods_order=["io", "cot", "tot", "gsp", "gsp2"],\n    methods_labels=["IO", "CoT", "ToT", "GoT", "GoT2"],\n    y_upper=10,\n    cost_upper=15,\n    display_solved=False,\n    display_left_ylabel=True,\n    display_right_ylabel=True,\n)', 'def get_final_scores_doc_merge(results_complete):\n    scores = {}\n    for method in results_complete.keys():\n        scores[method] = []\n        for result in results_complete[method]:\n            score = 0\n            solved = False\n            cost = 1\n            prompt_tokens = 0\n            completion_tokens = 0\n            for op in reversed(result["data"]):\n                if "cost" in op:\n                    cost = op["cost"]\n                    prompt_tokens = op["prompt_tokens"]\n                    completion_tokens = op["completion_tokens"]\n                if "operation" in op and op["operation"] == "score":\n                    try:\n                        score = max(op["scores"])\n                        break\n                    except:\n                        continue\n            scores[method].append(\n                [result["key"], score, solved, prompt_tokens, completion_tokens, cost]\n            )\n        scores[method] = sorted(scores[method], key=lambda x: x[0])\n    return scores\n\n\ndef get_plotting_data(base_directory, score_method):\n    results_complete = get_complete_results(base_directory)\n    scores = score_method(results_complete)\n    results_plotting = {\n        method: {\n            "scores": [x[1] for x in scores[method]],\n            "solved": sum([1 for x in scores[method] if x[2]]),\n            "costs": [x[5] for x in scores[method]],\n        }\n        for method in scores.keys()\n    }\n    return results_plotting', 'def get_final_scores(results_complete):\n    scores = {}\n    for method in results_complete.keys():\n        scores[method] = []\n        for result in results_complete[method]:\n            score = 100\n            solved = False\n            cost = 1\n            prompt_tokens = 0\n            completion_tokens = 0\n            for op in result["data"]:\n                if "operation" in op and op["operation"] == "ground_truth_evaluator":\n                    try:\n                        score = min(op["scores"])\n                        solved = any(op["problem_solved"])\n                    except:\n                        continue\n                if "cost" in op:\n                    cost = op["cost"]\n                    prompt_tokens = op["prompt_tokens"]\n                    completion_tokens = op["completion_tokens"]\n            scores[method].append(\n                [result["key"], score, solved, prompt_tokens, completion_tokens, cost]\n            )\n        scores[method] = sorted(scores[method], key=lambda x: x[0])\n    return scores']
## Helpful Chunks
[]
