import json

import pandas
import networkx as nx
from networkx.readwrite import json_graph


url_template = 'https://physics.iitm.ac.in/researchinfo?page={}'
authorlist = []


for i in range(6):
    # we can pass a url as the first argument to pandas.read_html
    # and it returns a list of data frames
    df_list = pandas.read_html(url_template.format(i),
                               header=0,
                               index_col=0
    )
    df = df_list[0]

    # column containing author names needs to be cleaned
    df.Authors = df.Authors.str.lower()
    df.Authors = df.Authors.str.strip()
    df.Authors = df.Authors.str.replace('*', ' ')
    df.Authors = df.Authors.str.replace('and ', ',')
    df.Authors = df.Authors.str.replace('&', ',')

    # Split column containing authors on ","
    # split is a data frame i.e 2D array
    split = df['Authors'].str.split(u',', expand=True)
    split.columns = ['Authors_split_{0}'.format(i)
                     for i in range(len(split.columns))]
   
    # strip author names of whitespaces
    for column in split:
        split[column] = split[column].str.strip()

    # each row contains authors of a paper
    # the row might contains NaNs, which is why we use dropna
    for i in range(len(split)-1):
        authorlist.append(list(split.iloc[i].dropna()))


G = nx.Graph()

# link each author to the other authors on each paper
for list in authorlist:
    for pos, node1 in enumerate(list):
        for node2 in list[pos:]:
            # there might be empty strings or whitespaces in the author list
            if node1 != u'' and node2 != u'' and node1 != u' ' and node2 != u' ':
                G.add_edge(node1, node2)

# label each node with the author's name
for n in G:
    G.node[n]['name'] = n

# draw the graph using networkx's Graph object
pos = nx.spring_layout(G)
nx.draw_networkx_nodes(G, pos, node_size=100, node_color='blue')
nx.draw_networkx_edges(G, pos, edge_color='green')
nx.draw_networkx_labels(G, pos, font_color='red')

# convert the Graph object into a JSON object
# we use the JSON object using D3
d = json_graph.node_link_data(G)
json.dump(d, open('force.json', 'w'))
