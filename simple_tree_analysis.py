from collections import namedtuple
import random as rd

Tree = namedtuple("Tree", ["node", "children"])


def argmin(xs, f):
    tmp = [(x, f(x)) for x in xs]
    return {x for (x, v) in tmp if v == min([v for (x, v) in tmp])}


def sample_tree(
    game, max_branch_number, max_tree_height, root_pos=None, player_to_move=0
):
    if root_pos is None:
        root_pos = game.starting_pos
    if max_tree_height == 0:
        return Tree([root_pos, 0], [])
    moves = game.all_moves(root_pos, player_to_move)
    return Tree(
        [root_pos, player_to_move],
        [
            sample_tree(
                game, max_branch_number, max_tree_height - 1, pos, 1 - player_to_move
            )
            for pos in rd.sample(moves, min(len(moves), max_branch_number))
        ],
    )


def eval_sample(game, sample):
    if sample.children == []:
        return Tree(game.eval_pos(*sample.node), [])
    else:
        subtrees = [eval_sample(game, subtree) for subtree in sample.children]
        score = -sum([subtree.node for subtree in subtrees if subtree.node < 0])
        if score == 0:
            score = -min([subtree.node for subtree in subtrees if subtree.node >= 0],)
        return Tree(score, subtrees)


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

