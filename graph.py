import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def divide_chunks(l, n): 
      
    # looping till length l 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 


def plot(string):
    res = ''.join(format(ord(i), 'b') for i in string) 
    res = res.zfill(100)
    res = list(res)
    res = list(divide_chunks(res, 10))
    res = np.matrix(res)
    G = nx.from_numpy_matrix(res)
    fig = nx.draw(G)
    return fig



# G = nx.DiGraph(res)
# pos = [[0,0], [0,1], [1,0], [1,1]]
# nx.draw(G,pos)
# plt.show()
