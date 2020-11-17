#%%
import networkx as nx
import numpy as np
import random

class MCTS():
    def __init__(self, 
                 game,
                 exploration_epsilon=0.25,
                 biasedness=1,
                 optimizing_player=1):

        self.game = game
        self.exploration_epsilon = exploration_epsilon
        self.exploration_coef = np.sqrt(2)
        self.biasedness = biasedness  # determines how much the selection of nodes is biased towards strength. 0 is equality, 1 is proportional to strenght, >1 is superlinearly related.

        self.g = nx.DiGraph()
        self.nr_players = self.game.nr_players
        self.root = self.game.state_hash
        self.optimizing_player = optimizing_player

        self.g.add_node(node_for_adding=self.game.state_hash, 
                        rewards= np.zeros(self.nr_players),
                        N=0,
                        terminal=False,
                        leads_to_terminal=False, # unless there is only one state
                        leaf=True,
                        # uct=0,  # not needed at the moment
                        depth=0,
                        parent=None,
                        current_player=int(self.game.state_hash[0]))
      
    def expand(self, node, return_random=True):
        # check whether node is terminal
        # undo leaf status of that node.
        current_depth = self.g.nodes[node]['depth']
        self.game.initialize_from_state(node)
        opts = self.game.options()
        if len(opts)==0:
            self.g.nodes[node]['terminal']==True
        # t = self.g.nodes[node]['N']
        children = []
        for child, action in opts.items():
            self.g.add_edge(u_of_edge=node,
                            v_of_edge=child,
                            leads_to_terminal=False,
                            action=action)
            if child in self.g.nodes:
                if self.g.nodes[child]["leads_to_terminal"]:
                    self.g.edges[(node,child)]["leads_to_terminal"] = True
                continue
            self.g.add_node(node_for_adding=child,
                            rewards= np.zeros(self.nr_players),
                            N=0,
                            # uct=self.calc_uct(w=0,N=0,t=t),
                            terminal=False,  # all nodes are initially terminal 
                            leads_to_terminal=False,
                            leaf=True,
                            depth=current_depth+1,
                            parent=node,
                            current_player=int(child[0]))
            children.append(child)
        
        if len(children)>0:
            self.game.nodes[node]['leaf'] = False
            if return_random:
                return random.choice(children) 
            else:
                return None
        else:
            return None
        

    def select(self,node=None, return_path=[]):
        """ node must not be terminal.
        assumes a given tree.
        """
        if not node:
            node = self.root
        return_path.append(node)
        if self.g.nodes[node]["terminal"]:
            return None, return_path
        if self.g.nodes[node]["leaf"]:
            return node, return_path
        next_nodes = [e[1] for e in self.g.out_edges(n=node) if not self.g.edges[e]["leads_to_terminal"]]
        next_wghts = np.array([self.g.nodes[n]['rewards'][self.optimizing_player-1]/self.g.nodes[n]['N'] + self.exploration_epsilon for n in next_nodes]) ** self.biasedness
        next_node = random.choices(next_nodes, weights=next_wghts, k=1)[0]
        self.select(node=next_node, return_path=return_path)
        return None


    def rollout(self, node):
        self.game.initialize_from_state(node)
        game_over = False
        while not game_over:
            opts = self.game.options()
            chos = random.choice([o for o in opts])
            _, _, game_over, _ = self.game.step(action=opts[chos])
        return np.array(tweeze_rewards(self.game.rewards))
    

    def create_tree(self, max_iter=100):
        for i in range(max_iter):
            node, reward = self.iteration()
            print( node, reward)

    def iteration(self):
        leaf_node, return_path = self.select()  # selects any leaf node
        if not leaf_node:
            print('leaf node is none??')
            return None
        sel_node = self.expand(node=leaf_node, return_random=True) # expands the graph 
        if not sel_node:
            print('sel_node is none??')
        return_path.append(sel_node)
        reward = self.rollout(node=sel_node)
        self.backpropagate(return_path=return_path, reward=reward)
        return sel_node, reward
       
    def backpropagate(self, return_path, reward):
        for node in reversed(return_path):
            self.g.nodes[node]["reward"] = np.add(self.g.nodes[node]["reward"], reward) 
            self.g.nodes[node]["N"] += 1


    def calc_uct(self, w, N, t):
        return (w/(N+self.exploration_epsilon)) + self.exploration_coef * np.sqrt( np.log(t) / (N+self.exploration_epsilon))



def tweeze_rewards(rewards):
    return [(r+1)/2 for r in rewards]


    
# %%
