import networkx as nx
import matplotlib.pyplot as plt
import yaml

# Creates an empty graph - edges are bi-directional
# G = nx.DiGraph() creates a directional graph
G = nx.Graph()

# Add nodes
# Single node
G.add_node(1)

# multiple nodes
G.add_nodes_from([2, 3])

# nodes with attributes
G.add_nodes_from([
    (4, {"color": "red"}),
    (5, {"color": "green"}),
])

H = nx.path_graph(10)
G.add_nodes_from(H)

# Now add edges
G.add_edge(1, 2)
e = (2, 3)
G.add_edge(*e)  # unpack edge tuple*

G.add_edges_from(H.edges)

# Now do more stuff
G.clear()

G.add_edges_from([(1, 2), (1, 3)])
G.add_node(1)
G.add_edge(1, 2)
G.add_node("spam")        # adds node "spam"
G.add_nodes_from("spam")  # adds 4 nodes: 's', 'p', 'a', 'm'
G.add_edge(3, 'm')
G.add_edge(2, 'm')

print(G.number_of_nodes())
print(G.number_of_edges())
print("===========")

DG = nx.DiGraph()
DG.add_edge(2, 1)   # adds the nodes in order 2, 1
DG.add_edge(1, 3)
DG.add_edge(2, 4)
DG.add_edge(1, 2)
print(list(DG.nodes))
print(list(DG.edges))
print("===========")

# The assert keyword lets you test if a condition in your code returns True, if not, the program will raise an AssertionError.
# successors == neighbours
assert list(DG.successors(2)) == [1, 4]
assert list(DG.edges) == [(2, 1), (2, 4), (1, 3), (1, 2)]

print("===========")
print(list(G.nodes))
print(list(G.edges))
print(list(G.adj[1]))  # or
print(list(G.neighbors(1)))
print(G.degree[1])  # the number of edges incident to 1
print("===========")
print(G.edges([2, 'm']))
print(G.degree([2, 3]))
print("===========")


G.clear()
H.clear()

G.add_edge(1, 2)
G.add_edge(2, 3)
G.add_edge(3, 1)
H = nx.DiGraph(G)   # create a DiGraph using the connections from G, NB G is undirected
print(list(H.edges()))

H = nx.DiGraph()   # create a DiGraph directed graph
H.add_edge(1, 2)
H.add_edge(2, 3)
H.add_edge(3, 1)
print(list(H.edges()))
print("===========")

edgelist = [(0, 1), (1, 2), (2, 3)]
H = nx.Graph(edgelist)
print(list(H.edges()))
print("===========")

FG = nx.Graph()
FG.add_weighted_edges_from([(1, 2, 0.125), (1, 3, 0.75), (2, 4, 1.2), (3, 4, 0.375)])
for n, nbrs in FG.adj.items():
   for nbr, eattr in nbrs.items():
       wt = eattr['weight']
       if wt < 0.5: print(f"({n}, {nbr}, {wt:.3})")
print("===========")
FG = nx.DiGraph()
FG.add_weighted_edges_from([(1, 2, 0.125), (1, 3, 0.75), (2, 4, 1.2), (3, 4, 0.375)])
for n, nbrs in FG.adj.items():
   for nbr, eattr in nbrs.items():
       wt = eattr['weight']
       if wt < 0.5: print(f"({n}, {nbr}, {wt:.3})")
print("===========")

for (u, v, wt) in FG.edges.data('weight'):
    if wt < 0.5:
        print(f"({u}, {v}, {wt:.3})")
print("===========")


# Adding attributes
G = nx.Graph(day="Friday")
print(G.graph)
G.graph['day'] = "Monday"
print(G.graph)

G.add_node(1, time='5pm')
G.add_nodes_from([3], time='2pm')
print(G.nodes[1])
G.nodes[1]['room'] = 714
print(G.nodes.data())
print(G.graph)

G.add_edge(1, 2, weight=4.7 )
G.add_edges_from([(3, 4), (4, 5)], color='red')
G.add_edges_from([(1, 2, {'color': 'blue'}), (2, 3, {'weight': 8})])
G[1][2]['weight'] = 4.7
G.edges[3, 4]['weight'] = 4.2
print(G.edges.data())
inpFilePath = "Z:\\Projects\\Research\\0200-GRACE\\DataExtraction\\GMLs\\networkx_tutorial_ex01.gml"
nx.write_gml(G, inpFilePath)
dictTest = nx.to_dict_of_dicts(G)
inpFilePath = "Z:\\Projects\\Research\\0200-GRACE\\DataExtraction\\GMLs\\networkx_tutorial_ex01.yaml"
with open(inpFilePath, 'w', encoding='utf-8') as f_yaml:
    yaml.dump(dictTest, f_yaml, sort_keys=False)

print("===========")

G = nx.petersen_graph()
subax1 = plt.subplot(121) # nrows = 1, ncols = 2, index = 1
nx.draw(G, with_labels=True, font_weight='bold')
subax2 = plt.subplot(122) # nrows = 1, ncols = 2, index = 1
nx.draw_shell(G, nlist=[range(5, 10), range(5)], with_labels=True, font_weight='bold')
plt.show()

inpFilePath = "Z:\\Projects\\Research\\0200-GRACE\\DataExtraction\\GMLs\\networkx_tutorial_ex02.gml"
nx.write_gml(G, inpFilePath)
inpFilePath = "Z:\\Projects\\Research\\0200-GRACE\\DataExtraction\\GMLs\\networkx_tutorial.yaml"
nx.write_yaml(G, inpFilePath)

pause = True


