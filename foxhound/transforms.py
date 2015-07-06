import numpy as np
import pandas as pd
from collections import Counter

from utils import numpy_array    
from rng import np_rng, py_rng   

def LenClip(X, n):
    """
    LenClip clips the length of sequences of text to a standard character length.

    Parameters
    ----------
    X: array-like, shape (n_samples, )
        for textRNN's, the elements of X are sequences of text (i.e. 
        a single movie review from IMDB)

    n: int
        length at which to clip the sequence of text

    Returns
    -------
    Xc: array-like, shape (n_samples, )
        sequences of text, clipped at N characters
    """
    Xc = []
    for x in X:
        words = x.split(' ')
        lens = [len(word)+1 for word in words]
        lens[0] -= 1
        lens[-1] -= 1
        lens = np.cumsum(lens).tolist()
        words = [w for w, l in zip(words, lens) if l < n]
        xc = ' '.join(words)
        Xc.append(xc)
    return Xc

def OneHot(X, n=None, negative_class=0.):
    X = np.asarray(X).flatten()
    if n is None:
        n = np.max(X) + 1
    Xoh = np.ones((len(X), n)) * negative_class
    Xoh[np.arange(len(X)), X] = 1.
    return Xoh

def SeqPadded(seqs, placement="front"):
    """
    SeqPadded pads a group of tokenized sequences to the sequence with the maximum length.

    Parameters
    ----------
    seqs: array-like
        tokenized sequences, each which are probably not the same length.
        seqs is an output of Vectorizer.transform() call.

    placement: string, default "front"
        where the padding should happen. 

        "front" would return something like

        >>> SeqPadded(seqs, placement="front")

        [0, 0, 0, ......, 256, 15, 3, 888, 13]

        where as "back" would return something like

        >>> SeqPadded(seqs, placement="back")

        [256, 15, 3, 888, 13, ......, 0, 0, 0]

    Returns
    -------
    seqs_padded_T: array-like, shape (max_len, n_samples)
        In the case of text RNN's,

        - each column of this 2D array represents a sample text sequence
        - the column will be padded with 0's (in the front or back) which the RNN reads as a PAD.
    """
    lens = map(len, seqs)
    max_len = max(lens)
    seqs_padded = []
    for seq, seq_len in zip(seqs, lens):
        n_pad = max_len - seq_len 
        if placement == "front":
            seq = [0] * n_pad + seq
        else:
            seq = seq + [0] * n_pad    
        seqs_padded.append(seq)
    return np.asarray(seqs_padded).transpose(1, 0)

def FlatToImg(X, w, h, c):
	if not numpy_array(X):
		X = np.asarray(X)	
	return X.reshape(-1, w, h, c)	

def ImgToConv(X):
    if not numpy_array(X):
        X = np.asarray(X)
    return X.transpose(0, 3, 1, 2)

def Standardize(X):
    if not numpy_array(X):
        X = np.asarray(X)
    return X / 127.5 - 1.

def ZeroOneScale(X):
    if not numpy_array(X):
        X = np.asarray(X)
    return X / 255.

def Fliplr(X):
    Xt = []
    for x in X:
        if py_rng.random() > 0.5:
            x = np.fliplr(x)
        Xt.append(x)
    return Xt

def Reflect(X):
	Xt = []
	for x in X:
		if py_rng.random() > 0.5:
			x = np.flipud(x)
		if py_rng.random() > 0.5:
			x = np.fliplr(x)
		Xt.append(x)
	return Xt

def FlipVertical(X):
	Xt = []
	for x in X:
		if py_rng.random() > 0.5:
			x = np.flipud(x)
		Xt.append(x)
	return Xt

def FlipHorizontal(X):
	Xt = []
	for x in X:
		if py_rng.random() > 0.5:
			x = np.fliplr(x)
		Xt.append(x)
	return Xt

def Rot90(X):
    Xt = []
    for x in X:
        x = np.rot90(x, py_rng.randint(0, 3))
        Xt.append(x)
    return Xt

def ColorShift(X, p=1/3., scale=20):
    Xt = []
    for x in X:
        x = x.astype(np.int16)
        x[:, :, 0] += (py_rng.random() < p)*py_rng.randint(-scale, scale)
        x[:, :, 1] += (py_rng.random() < p)*py_rng.randint(-scale, scale)
        x[:, :, 2] += (py_rng.random() < p)*py_rng.randint(-scale, scale)
        x = np.clip(x, 0, 255).astype(np.uint8)
        Xt.append(x)
    return Xt

def Patch(X, pw, ph):
    Xt = []
    for x in X: 
        w, h = x.shape[:2]
        i = py_rng.randint(0, w-pw)
        j = py_rng.randint(0, h-ph)
        Xt.append(x[i:i+pw, j:j+pw])
    return Xt

def SeqDelete(X, p_delete):
    Xt = []
    for x in X:
        Xt.append([w for w in x if py_rng.random() > p_delete])
    return Xt

def SeqPatch(X, p_size):
    Xt = []
    for x in X:
        l = len(x)
        n = int(p_size*l)
        i = py_rng.randint(0, l-n)
        Xt.append(x[i:i+n])
    return Xt

def CenterCrop(X, pw, ph):
    Xt = []
    for x in X: 
        w, h = x.shape[:2]
        i = int(round((w-pw)/2.))
        j = int(round((h-ph)/2.))
        Xt.append(x[i:i+pw, j:j+pw])
    return Xt

def StringToCharacterCNNRep(X, max_len, encoder):
    nc = len(encoder)+1
    Xt = []
    for x in X:
        x = [encoder.get(c, 0) for c in x]
        x = one_hot(x, n=nc)
        l = len(x)
        if l != max_len:
            x = np.concatenate([x, np.zeros((max_len-l, nc))])
        Xt.append(x)
    return np.asarray(Xt).reshape(len(Xt), 1, max_len, nc)

def StringToCharacterCNNRNNRep(X, encoder):
    nc = len(encoder)+1
    Xt = []
    max_len = max([len(x) for x in X])
    for x in X:
        x = [encoder.get(c, 0) for c in x]
        x = one_hot(x, n=nc)
        l = len(x)
        if l != max_len:
            x = np.concatenate([np.zeros((max_len-l, nc)), x])
        Xt.append(x)
    return np.asarray(Xt).reshape(len(Xt), 1, max_len, nc)