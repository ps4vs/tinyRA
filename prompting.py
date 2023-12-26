import outlines

examples = [
    ("The food was disgusting", "negative"),
    ("the dishes are very good", "positive"),
    ("the waiter is very rude", "negative"),
    ("there are limited bad options", "positive")
]

@outlines.prompt
def labelling(to_label, examples):
    """you are a sentiment labelling assistant.
    
    {% for example in examples %}
    {{ example[0] }} // {{ example[1] }}
    {% endfor %}
{{ to_label }~} //
    """
    
    model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")
    prompt = labelling("just awesome", examples)
    print(prompt)
    # answer = outlines.generate.continuation(model, max_tokens=100)(prompt)
    
# given premise, can we get to the conclusion
# can we build a machine which takes premise, program to find conlcusion

# will our system stop?