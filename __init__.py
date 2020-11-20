#%%
from game.sotf import Sotf
from rl.MCTS import MCTS
import numpy as np 
import pandas as pd 

peb = 4; arr = 6; nr_players = 3; field_size = 5;
game = Sotf(peb=peb,
            arr=arr,
            nr_players=nr_players,
            field_size=field_size,
            action_format='compressed')
MC = MCTS(game=game,
          exploration_epsilon=0.25,
          biasedness=1,
          optimizing_player=1)

leaf_node, return_path = MC.select()  # selects any leaf node
#%%
sel_node = MC.expand(node=leaf_node, return_random=True) # expands the graph 
return_path.append(sel_node)
reward = MC.rollout(edge=(leaf_node,sel_node))
MC.backpropagate(return_path=return_path, reward=reward, including_multiple_paths=True)
       
# %%
