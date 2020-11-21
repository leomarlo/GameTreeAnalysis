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
                        N=0, # number of roll-outs for this node
                        terminal=False,
                        leads_to_terminal=False, # unless there is only one state
                        leaf=True,
                        # uct=0,  # not needed at the moment
                        N_children=0,
                        N_leads_to_terminal_child_edges=0,
                        depth=0,
                        parents=[],
                        N_parents=0,
                        current_player=int(self.game.state_hash[0]))
      
    def expand(self, node, return_random=True):
        # check whether node is terminal
        # undo leaf status of that node.
        current_depth = self.g.nodes[node]['depth']
        self.game.initialize_from_state(node)
        opts = self.game.options()
        children = 0
        # t = self.g.nodes[node]['N']
        leafs = []
        for child, action in opts.items():
            
            if child in self.g.nodes:
                # in this game cycles are forbidden. Check whether its a cycle or just multiple paths joining.
                
                # if its not a cycle, then add the edge, but not the node.
                # if it is a cycle, then add neither the edge nor the node.

                # check for cycles:
                condition, _ = self.exists_path(source=child,target=node)
                if condition:
                    continue

                self.g.add_edge(u_of_edge=node,
                            v_of_edge=child,
                            leads_to_terminal=False,
                            action=action)
                # increment the N_parents of the 'child' node.
                self.g.nodes[child]['parents'].append(node)
                self.g.nodes[child]['N_parents'] += 1

                # check whether the terminal conditions should be added.
                if self.g.nodes[child]["leads_to_terminal"]:
                    self.g.edges[(node,child)]["leads_to_terminal"] = True
                    self.g.nodes[node]['N_leads_to_terminal_child_edges'] += 1
                    self.propagate_leads_to_terminal(node=node)
            else:
                # add first node and then edge
                self.g.add_node(node_for_adding=child,
                                rewards=np.zeros(self.nr_players),
                                N=0,
                                # uct=self.calc_uct(w=0,N=0,t=t),
                                terminal=False,  # all nodes are initially terminal 
                                leads_to_terminal=False,
                                N_children=0,
                                N_leads_to_terminal_child_edges=0,
                                leaf=True,
                                depth=current_depth+1,
                                parents=[node],
                                N_parents=1,
                                current_player=int(child[0]))
                self.g.add_edge(u_of_edge=node,
                                v_of_edge=child,
                                leads_to_terminal=False,
                                action=action)
                leafs.append(child)
            # note that there might be elements in opts that do not get here.
            # so children is not just len(opts)
            children += 1
        
        self.g.nodes[node]['N_children']=children

        if children==0:
            self.g.nodes[node]['terminal']=True
            self.g.nodes[node]['leaf'] = True
            return None
        else:
            # it has children
            if len(leafs)>0:
                # and at least one leaf
                self.g.nodes[node]['leaf'] = False
                if return_random:
                    return random.choice(leafs) 
                else:
                    return None
            else:
                # it has children but no leafs (all edges are going back to the tree itself)
                self.g.nodes[node]['leaf'] = False
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
        next_nodes = [e[1] for e in self.g.out_edges(nbunch=node) if not self.g.edges[e]["leads_to_terminal"]]
        next_wghts = np.array([self.get_weight(reward=self.g.nodes[n]['rewards'][self.optimizing_player-1],
                                               N=self.g.nodes[n]['N'])
                               for n in next_nodes])
        # np.array([self.g.nodes[n]['rewards'][self.optimizing_player-1]/self.g.nodes[n]['N'] + self.exploration_epsilon for n in next_nodes]) ** self.biasedness
        next_node = random.choices(next_nodes, weights=next_wghts, k=1)[0]
        return self.select(node=next_node, return_path=return_path)


    def rollout(self, edge, limit_no_actions=0):
        self.game.initialize_from_state(state_hash=edge[0])
        _, _, game_over, _ = self.game.step(action=self.g.edges[edge]['action'])
        if game_over:
            self.g.nodes[edge[1]]['terminal']=True
            self.g.edges[edge]['leads_to_terminal']=True
            self.g.nodes[edge[0]]['N_leads_to_terminal_child_edges'] += 1
            self.propagate_leads_to_terminal(node=edge[0])
            return np.array(tweeze_rewards(self.game.rewards))
        else:
            while not game_over:
                opts = self.game.options()
                chos = random.choice([o for o in opts])
                _, _, game_over, _ = self.game.step(action=opts[chos])
            return np.array(tweeze_rewards(self.game.rewards))
    

    def create_tree(self, max_iter=100):
        for i in range(max_iter):
            node, rewards = self.iteration()
            print( node, rewards)


    def iteration(self):
        leaf_node, return_path = self.select()  # selects any leaf node
        if not leaf_node:
            print('leaf node is none??')
            return None
        sel_node = self.expand(node=leaf_node, return_random=True) # expands the graph 
        if not sel_node:
            print('sel_node is none??')
        return_path.append(sel_node)
        rewards = self.rollout(edge=(leaf_node,sel_node))
        self.backpropagate(return_path=return_path, rewards=rewards, including_multiple_paths=True)
        return sel_node, rewards
       

    def backpropagate(self, return_path, rewards, including_multiple_paths=False):
        if not including_multiple_paths:
            for node in reversed(return_path):
                # increment the reward to each node including the selected node
                self.g.nodes[node]["rewards"] = np.add(self.g.nodes[node]["rewards"], rewards) 
                # increment the number of rollouts for that path.
                self.g.nodes[node]["N"] += 1
        else:
            node = return_path[-1]  
            self.backpropagate_multiple_paths(node=node,
                                              rewards=rewards,
                                              return_path=return_path,
                                              on_path=len(return_path)-1)
            

    def backpropagate_multiple_paths(self, node, rewards, return_path, on_path):
        self.g.nodes[node]["rewards"] = np.add(self.g.nodes[node]["rewards"], rewards) 
        self.g.nodes[node]["N"] += 1
        parents = self.g.nodes[node]['parents']
        if len(parents)==0 or on_path==0:
            return None
        for parent in parents:
            if on_path is None:
                # node is not on return path, but parent might be
                if parent not in return_path:
                    # parent doesnt lie in return path
                    self.backpropagate_multiple_paths(node=parent, rewards=rewards, return_path=return_path, on_path=None)
                else:
                    # parent lies in return path
                    # do not call the backpropagate_multiple here!!!
                    pass
            else:
                index = on_path - 1
                if parent == return_path[index]:
                    # parent lies on return path
                    self.backpropagate_multiple_paths(node=parent, rewards=rewards, return_path=return_path, on_path=index)
                else:
                    # parent doesnt lie on return path
                    self.backpropagate_multiple_paths(node=parent, rewards=rewards, return_path=return_path, on_path=None)


    def propagate_leads_to_terminal(self, node):
        condition = self.g.nodes[node]['N_children'] == self.g.nodes[node]['N_leads_to_terminal_child_edges']
        if condition:
            self.g.nodes[node]["leads_to_terminal"] = True
            for edge in self.g.in_edges(nbunch=node):
                self.g.edges[edge]["leads_to_terminal"] = True
                self.g.nodes[edge[0]]['N_leads_to_terminal_child_edges'] += 1
                self.propagate_leads_to_terminal(node=edge[0])



    def exists_path(self, source, target):
        try: 
            path = nx.bidirectional_dijkstra(self.g, source, target)
            return True, path
        except:
            return False, []

    def calc_uct(self, w, N, t):
        return (w/(N+self.exploration_epsilon)) + self.exploration_coef * np.sqrt( np.log(t) / (N+self.exploration_epsilon))

    def get_weight(self, reward, N):
        pre_biased = self.exploration_epsilon
        if N!=0:
             pre_biased += reward / N
        return pre_biased ** self.biasedness

def tweeze_rewards(rewards):
    return [(r+1)/2 for r in rewards]


    
# %%
