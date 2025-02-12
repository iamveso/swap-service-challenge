from typing import Tuple
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("agg")


def get_name_details(details: str) -> Tuple[str, str, float]:
    parts = details.split(" ")
    token1 = parts[0]
    token2 = parts[2]
    
    
    # Extract and clean the percentage
    if len(parts) < 4:
        percentage_value = 0.0
    elif len(parts) > 4: #likely an error
        return "","",0
    else:
        percentage = parts[3]  # Extract "0.01%"
        percentage_value = float(percentage.strip("%")) / 100  # Remove "%" #currently not checking for errors in conversion

    # Clean up tokens (remove extra spaces)
    token1 = token1.strip()
    token2 = token2.strip()
    return token1, token2, percentage_value

def save_graph(graph: nx.DiGraph, filename="static/graph.png"):
    """Save the NetworkX graph as an image."""
    if graph is None or graph.number_of_nodes() == 0:
        raise ValueError("Graph is empty or not initialized.")

    fig, ax = plt.subplots(figsize=(50, 30))  # Create a figure explicitly
    
    pos = nx.spring_layout(graph)  # Compute positions for visualization
    nx.draw(graph, pos, with_labels=True, node_color="lightblue", edge_color="gray", font_size=8, ax=ax)

    plt.savefig(filename, format="png")
    plt.close(fig)