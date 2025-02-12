import networkx as nx
import math
from typing import List, Tuple, Optional
from app.models import Pool, Token

class PathFinder:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.pools: List[Pool] = []
        
    def update_pools(self, pools: List[Pool]):
        """Update the graph with new pool data"""
        self.pools = pools
        self.graph.clear()
        
        # Build graph
        for pool in pools:
            # Add edges in both directions
            # Weight is -log(price * (1-fee)) to convert multiplication to addition
            # and negative to convert max problem to min problem
            weight0 = -math.log(pool.price0 * (1 - pool.fee))
            weight1 = -math.log(pool.price1 * (1 - pool.fee))
            
            self.graph.add_edge(pool.token0.symbol, pool.token1.symbol, 
                              weight=weight0, pool=pool, forward=True)
            self.graph.add_edge(pool.token1.symbol, pool.token0.symbol, 
                              weight=weight1, pool=pool, forward=False)
    
    def find_best_path(self, from_token: str, to_token: str) -> Tuple[List[str], float]:
        """Find the best path between two tokens and return path and total price impact"""
        try:
            path = nx.shortest_path(self.graph, from_token, to_token, weight='weight')
            
            # Calculate total exchange rate
            rate = 1.0
            for i in range(len(path) - 1):
                edge = self.graph.edges[path[i], path[i+1]]
                pool = edge['pool']
                if edge['forward']:
                    rate *= pool.price0 * (1 - pool.fee)
                else:
                    rate *= pool.price1 * (1 - pool.fee)
                    
            return path, rate
            
        except (nx.NetworkXNoPath, nx.NetworkXError):
            return [], 0.0