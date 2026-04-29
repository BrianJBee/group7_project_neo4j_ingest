def get_sentiment_words(chunk):
    sentiments = []

    for token in chunk:
        if token.pos_ == 'ADJ':
            sentiments.append(token.text)
    
    head = chunk.root.head
    for child in head.children:
        if child.pos_ == 'ADJ':
            sentiments.append(child.text)

    return sentiments

def extract_aspect_sentiment(text, nlp):
    doc = nlp(text)
    results = []

    for chunk in doc.noun_chunks:
        sentiments = get_sentiment_words(chunk)

        if sentiments:
            for s in sentiments:
                sentiment = f'{s} {chunk.root.text}'
                results.append(sentiment)
    return results

