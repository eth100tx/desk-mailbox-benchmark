"""Small student/EMA-teacher model for paired views of fictional desk events."""
from itertools import product
import numpy as np
from fact_views import TOPIC, RELEASE, DISCLOSURE

def train(encode, direct=False):
    rng=np.random.default_rng(2412)
    axes=(TOPIC,RELEASE,DISCLOSURE)
    contexts,withheld,bits=[],[],[]
    for event in product(*axes):
        for i in range(3):
            contexts.append(encode(" ".join(field[1][i] for field in event)))
            # The second view is an independently worded statement of each field.
            withheld.append([encode(field[1][(i+1)%3]) for field in event])
            bits.append(all(field[2] for field in event))
    x,y=np.stack(contexts),np.stack(withheld)
    dim,latent=x.shape[1],32
    initial=rng.normal(0,1/np.sqrt(latent),(dim,latent))
    student=initial.copy()
    teacher=student.copy()
    heads=rng.normal(0,1/np.sqrt(latent),(3,latent,latent))
    head=rng.normal(0,1/np.sqrt(latent),latent)
    def normalized(a,axis=-1):
        return a/np.maximum(np.linalg.norm(a,axis=axis,keepdims=True),1e-8)
    def backnorm(g,v):
        unit=normalized(v)
        return (g-(g*unit).sum(axis=-1,keepdims=True)*unit)/np.maximum(np.linalg.norm(v,axis=-1,keepdims=True),1e-8)
    for _ in range(240):
        hidden=x@ student
        if direct:
            p=1/(1+np.exp(-hidden@head))
            delta=(p-np.asarray(bits))/len(x)
            dh=delta[:,None]*head
            head-=0.8*(hidden.T@delta)
        else:
            pred=np.einsum("nl,alh->nah",hidden,heads)
            target=normalized(y@teacher)
            dp=backnorm(-target/(len(x)*3),pred)
            dh=np.einsum("nah,alh->nl",dp,heads)
            heads-=0.8*np.einsum("nl,nah->alh",hidden,dp)
        # Anchor the student to initial random features to stabilize a tiny corpus.
        student-=0.8*(x.T@dh+0.001*(student-initial))
        teacher=0.99*teacher+0.01*student
    centers=[]
    for axis in axes:
        centers.append(np.stack([normalized(np.mean([normalized(encode(p)@teacher)
                        for p in entry[1]],axis=0)) for entry in axis]))
    diagnostic=dict(train_contexts=len(x),latent_width=latent,epochs=240,
                    teacher_context_std=float((x@teacher).std(axis=0).mean()),
                    target_rank=int(np.linalg.matrix_rank(y.reshape(-1,dim)@teacher)))
    def predict(text):
        hidden=encode(text)@student
        if direct:
            return float(1/(1+np.exp(-hidden@head)))
        margins=[]
        for axis,matrix,centroids in zip(axes,heads,centers):
            similarities=centroids@normalized(hidden@matrix)
            good=np.array([entry[2] for entry in axis])
            margins.append(similarities[good].max()-similarities[~good].max())
        return float(1/(1+np.exp(-4*min(margins))))
    return predict,diagnostic
