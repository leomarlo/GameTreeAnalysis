from collections import namedtuple
import random as rd

Tree = namedtuple("Tree", ["node", "children"])


# return the subset of `xs' where `f' takes a minimum
def argmin(xs, f):
    tmp = [(x, f(x)) for x in xs]
    return {x for (x, v) in tmp if v == min([v for (x, v) in tmp])}


# Sample a subtree from the complete game tree given by argument `game', which
# must be an object whith properties `starting_pos()' (returning the starting
# position of the game) and `all_moves(pos,player)' (returning list of all
# possible moves from `pos' with `player' on move). The two players are 0 and 1.
def sample_tree(
    game,
    max_branch_number,
    max_tree_height=float("inf"),
    root_pos=None,
    player_on_move=0,
):
    if root_pos is None:
        root_pos = game.starting_pos
    if max_tree_height == 0:
        return Tree([root_pos, 0], [])
    moves = game.all_moves(root_pos, player_on_move)
    return Tree(
        [root_pos, player_on_move],
        [
            sample_tree(
                game, max_branch_number, max_tree_height - 1, pos, 1 - player_on_move
            )
            for pos in rd.sample(moves, min(len(moves), max_branch_number))
        ],
    )


# Creates an accompanying evaluation tree to a given game tree.  For every node,
# a positive score counts how many ways the player on move has to win the game,
# regardless of the strategy chosen by her opponent, and a negative score counts
# this number for the other player (one of those has to be 0).  The game object
# needs a property `eval_pos' which evaluates a given position for a given
# player on move.  If the game is not finished yet, it is expected to return 0,
# otherwise 1 if player 0 has won, -1 if player 1 has won and 0 if it is a draw.
def eval_sample(game, sample):
    if sample.children == []:
        return Tree(game.eval_pos(*sample.node), [])
    else:
        # The score can be evaluated recursively: first look if there is a child
        # with negative score, so the player on move has a winning strategy.  If
        # so, add together the value of all childs with negative score and make
        # it positive.  Otherwise take the minimum of all non-negative scores of
        # the children and make it negative, this is thought as the player on
        # move has no winning strategy but tries to minimize the number of ways
        # her opponent can win the game.
        subtrees = [eval_sample(game, subtree) for subtree in sample.children]
        score = -sum([subtree.node for subtree in subtrees if subtree.node < 0])
        if score == 0:
            score = -min([subtree.node for subtree in subtrees if subtree.node >= 0],)
        return Tree(score, subtrees)


# Here we just look at all paths in the sample tree such that at every point,
# the player on move choses a move which maximizes her score, that means
# selecting a child with minimal score since the score flips between moves.
def perfect_sequences(game, sample, evaluation):
    if sample.children == []:
        return [sample.node[0]]
    return [
        [sample.node[0]] + cont
        for i in argmin(
            range(len(sample.children)), lambda i: evaluation.children[i].node
        )
        for cont in perfect_sequences(game, sample.children[i], evaluation.children[i])
    ]

