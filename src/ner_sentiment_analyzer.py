from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline

# tokenizer = AutoTokenizer.from_pretrained("Davlan/bert-base-multilingual-cased-ner-hrl")
# model = AutoModelForTokenClassification.from_pretrained("Davlan/bert-base-multilingual-cased-ner-hrl")
# nlp = pipeline("ner", model=model, tokenizer=tokenizer)

pipe = pipeline("text-generation", model="Universal-NER/UniNER-7b-all")

