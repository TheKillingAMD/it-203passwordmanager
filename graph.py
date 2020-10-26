import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import secrets
import os

def divide_chunks(l, n): 
      
    # looping till length l 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 

string = "ayush123"
res = ''.join(format(ord(i), 'b') for i in string) 
res = res.zfill(100)
res = list(res)
res = list(divide_chunks(res, 10))
res = np.matrix(res)
G = nx.from_numpy_matrix(res)
fig = nx.draw(G)
random_hex = secrets.token_hex(8)
plt.savefig(random_hex, dpi = 75)