from collections import namedtuple
import copy as cp
import random as rd

Game = namedtuple("Game", ["starting_pos", "all_moves", "eval_pos"])

pebbles_per_player = 3


def all_graph_moves(pos, player_to_move):
    moves = []
    if pos[player_to_move] < pebbles_per_player:
        new_pos = pos[:]
        new_pos[player_to_move] += 1
        moves.append(new_pos)
    if pos[0] + pos[1] < 2 * pebbles_per_player:
        moves += [
            [pos[0], pos[1], pos[2] + [(i, j)]]
            for i in range(-pos[0], pos[1])
            for j in range(-pos[0], pos[1])
            if i != j and (i, j) not in pos[2] and (j, i) not in pos[2]
        ]
    return moves


def argmin(xs, f):
    tmp = [(x, f(x)) for x in xs]
    return {x for (x, v) in tmp if v == min([v for (x, v) in tmp])}


def eval_graph_pos(pos, player_to_move):
    if pos[0] + pos[1] < 2 * pebbles_per_player:
        return 0
    tmp = set(pos[2])
    while True:
        if tmp == []:
            return 0
        if all([i < 0 and j < 0 for (i, j) in tmp]):
            return -1 if player_to_move else 1
        if all([0 <= i and 0 <= j for (i, j) in tmp]):
            return 1 if player_to_move else -1
        tmp -= argmin(tmp, lambda v: len([e for e in tmp if e[1] == v]))


graph = Game([0, 0, []], all_graph_moves, eval_graph_pos)
