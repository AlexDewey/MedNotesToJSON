# MedNotesToJSON

Task: Convert synthetic medical notes to a JSON object.

Based on the following Kaggle competition: https://www.kaggle.com/competitions/medical-note-extraction-h-2-o-gen-ai-world-ny/discussion?sort=hotness

main.py runs an example of the code.

JSONevaluate.py is a method to determine the accuracy (similarity) of generated samples.

JSONcreate.py allows a user to request a conversion with either the entire text present, or segmented into parts to reduce context window issues.

LLMAPIs.py allows the user to send prompts either with a predefined return object or as a simple text response.

# Research Process

First I ran a query on the testing answers to determine how to properly structure the desired JSON output with which LLMs will be prompted to recreate.

Next, I ran many experiments switching up varying aspects of the pipeline:
1. Should I request one entire json object vs requesting in chunks to reduce the context window? Answer: One entire json object is best.
2. Which model is best, an overall powerful model, or specialized medical models. Answer: gpt-oss overall powerful model.
3. Will forcing the model to respond in an explicit JSON object improve performance. Answer: Yes

Other optimizations made focus on configuring my GPU to handle the workload faster (reducing response time from 5 minutes to 30 seconds), utilizing system v. user prompts, extra JSON processing to ensure consistency and maximizing similarity score, handling errors in JSON returns with repeated attempts for the LLM to output correct syntax.

All optimizations brought an initial accuracy of 90% to 99.5%, with many experiments leading to unusual insights.
