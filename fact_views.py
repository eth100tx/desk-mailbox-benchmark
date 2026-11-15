"""Paired textual views for three policy constraints. Uses exercise vocabulary only."""
from itertools import product
import numpy as np

# A semantic target is a description in a second view of the fictional event.
# These descriptions are never appended to the context at prediction time.
TOPIC = [
    ("sealed supplier bid", ["supplier offer", "sealed vendor quote", "bid amount"], True),
    ("storage reserve threshold", ["storage floor", "minimum storage bid", "reservation price"], True),
    ("procurement evaluation", ["bidder ranking", "evaluation margin", "selection order"], True),
    ("ordinary desk logistics", ["meeting time", "training session", "public agenda"], False),
]
RELEASE = [
    ("restricted to desk", ["internal", "private", "unreleased"], True),
    ("available publicly", ["published", "public", "posted for everyone"], False),
]
DISCLOSURE = [
    ("concrete value present", ["is 42.61", "equals 9.20", "lists Rowan ahead of Elm"], True),
    ("value not supplied", ["omitted", "pending", "amount withheld"], False),
]

def fit_facts(mode, embed):
    axes = TOPIC, RELEASE, DISCLOSURE
    prototypes = [np.stack([embed(entry[0]) for entry in axis]) for axis in axes]
    contexts,targets,bits = [],[],[]
    for event in product(*axes):
        # Cycle wording without changing truth. All 16 fact combinations occur.
        for variant in range(3):
            topic,release,disclosure = [entry[1][variant] for entry in event]
            contexts.append(embed(f"{release} {topic} {disclosure}"))
            targets.append(np.concatenate([embed(entry[0]) for entry in event]))
            bits.append(all(entry[2] for entry in event))
    x=np.stack(contexts)
    y=np.stack(targets) if mode=="facts" else np.asarray(bits)*2-1
    weights=x.T@np.linalg.solve(x@x.T+0.5*np.eye(len(x)),y)
    def predict(text):
        predicted=embed(text)@weights
        if mode=="facts":
            margins=[]
            for vector,axis,centers in zip(np.split(predicted,3),axes,prototypes):
                similarities=centers@vector
                matching=[entry[2] for entry in axis]
                margins.append(max(similarities[matching])-max(similarities[np.logical_not(matching)]))
            # A single failed constraint should move the evidence below threshold.
            margin=min(margins)
        else:
            margin=float(predicted)
        return float(1/(1+np.exp(-4*(margin-0.1))))
    return predict
