# Verwsion: 1.0.0
# Last Update: 2023/12/20
# Authoer: Tomio Kobayashi

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

class DataJourneyDAG:

    def __init__(self):
        self.vertex_names = []
        self.adjacency_matrix = []
        self.adjacency_matrix_T = []
        self.size_matrix = 0
        
    def draw_selected_vertices_reverse(self, adj_matrix, selected_vertices1, selected_vertices2, title, node_labels, pos, reverse=False):
        # Create a directed graph from the adjacency matrix
        G = nx.DiGraph(adj_matrix)

        # Create a subgraph with only the selected vertices
        subgraph1 = G.subgraph(selected_vertices1)
        subgraph2 = G.subgraph(selected_vertices2)
        
        if reverse:
            subgraph1 = subgraph1.reverse()
            subgraph2 = subgraph2.reverse()


        nx.draw(subgraph1, pos, with_labels=True, labels=node_labels, node_size=600, node_color='skyblue', font_size=8, font_color='black', font_weight='bold', arrowsize=10, edgecolors='black', linewidths=1)
        # Draw selected vertices with a different color for target
        nx.draw(subgraph2, pos, with_labels=True, labels=node_labels, node_size=1000, node_color='pink', font_size=8, font_color='black', font_weight='bold', arrowsize=10, edgecolors='black', linewidths=1)

        # Display the plot
        fig = plt.figure(1, figsize=(100, 100), dpi=60)
        plt.title(title)
        plt.show()


    def data_import(self, file_path):
#         Define rows as TO and columns as FROM
        data = np.genfromtxt(file_path, delimiter='\t', dtype=str, encoding=None)

        # Extract the names from the first record
        self.vertex_names = data[0]

        # Extract the adjacency matrix
        self.adjacency_matrix = data[1:]

        # Convert the adjacency matrix to a NumPy array of integers
        self.adjacency_matrix = np.array(self.adjacency_matrix, dtype=int)

        self.adjacency_matrix_T = self.adjacency_matrix.T

        # Matrix of row=FROM, col=TO
        self.size_matrix = len(self.adjacency_matrix)


    def drawOrigins(self, target_vertex):


        # Draw the path TO the target
        res_vector = np.array([np.zeros(self.size_matrix) for i in range(self.size_matrix+1)])
        res_vector[0][target_vertex] = 1
        for i in range(self.size_matrix):
            if sum(res_vector[i]) == 0:
                break
            res_vector[i+1] = self.adjacency_matrix @ res_vector[i]

        res_vector_T = res_vector.T

        selected_vertices1 = set()
        for i in range(len(res_vector)):
            if sum(res_vector[i]) == 0:
                break
            for j in range(len(res_vector[i])):
                if j == 0:
                    continue
                if res_vector[i][j] != 0 and j != 0: 
                    selected_vertices1.add(j)

        last_pos = 0


        position = {}
        colpos = {}
        posfill = set()

        for i in range(len(res_vector)):
            colpos[i] = 0

        for i in range(len(res_vector)):
            if sum(res_vector[i]) == 0:
                break
            last_pos += 1

        done = False
        largest_j = 0
        for i in range(len(res_vector)):
            if sum(res_vector[i]) == 0:
                break
            nonzero = 0
            for j in range(len(res_vector[i])):
                if j not in selected_vertices1:
                    continue
                if j in posfill:
                    continue
                if j == 0:
                    continue
                if res_vector[i][j]:
                    posfill.add(j)
                    position[j] = ((last_pos-i), colpos[(last_pos-i)]) 
                    colpos[(last_pos-i)] += 1
                    if largest_j < j:
                        largest_j = j


        selected_vertices1 = list(selected_vertices1)

        selected_vertices2 = [target_vertex]

        node_labels = {i: name for i, name in enumerate(self.vertex_names) if i in selected_vertices1 or i in selected_vertices2}

        self.draw_selected_vertices_reverse(self.adjacency_matrix, selected_vertices1,selected_vertices2, title="Data Origins", node_labels=node_labels, pos=position)

        
    def drawOffsprings(self, target_vertex):

#         Draw the path FROM the target
        position = {}
        colpos = {}
        posfill = set()
        selected_vertices1 = set()
        res_vector = np.array([np.zeros(self.size_matrix) for i in range(self.size_matrix+1)])
        res_vector[0][target_vertex] = 1

        for i in range(len(res_vector)):
            colpos[i] = 0

        for i in range(self.size_matrix):
            if sum(res_vector[i]) == 0:
                break
            res_vector[i+1] = self.adjacency_matrix_T @ res_vector[i]
        for i in range(len(res_vector)):
            if sum(res_vector[i]) == 0:
                break
            for j in range(len(res_vector[i])):
                if res_vector[i][j] != 0 and j != self.size_matrix - 1 and j != 0: 
                    selected_vertices1.add(j)

        done = False
        largest_j = 0
        for i in range(len(res_vector)):
            if sum(res_vector[i]) == 0:
                # position[j] = (largest_j,1) 
                break
            nonzero = 0
            for j in range(len(res_vector[i])):
                if j not in selected_vertices1:
                    continue
                if j in posfill:
                    continue
                if j == 0 or j == self.size_matrix - 1:
                    continue
                if res_vector[i][j]:
                    posfill.add(j)
                    position[j] = (i, colpos[i]) 
                    colpos[i] += 1
                    if largest_j < j:
                        largest_j = j
                    # break
                    
        selected_vertices1 = list(selected_vertices1)
        selected_vertices2 = [target_vertex]

        node_labels = {i: name for i, name in enumerate(self.vertex_names) if i in selected_vertices1 or i in selected_vertices2}

        self.draw_selected_vertices_reverse(self.adjacency_matrix_T, selected_vertices1,selected_vertices2, title="Data Offsprings", node_labels=node_labels, pos=position, reverse=True)




mydag = DataJourneyDAG()
mydag.data_import('/kaggle/input/matrix2/adjacency_matrix2.txt')
for i in range(40, 45, 1):
    mydag.drawOrigins(i)
    mydag.drawOffsprings(i)
