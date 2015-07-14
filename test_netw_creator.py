__author__ = 'sturaroa'

import networkx as nx
from collections import defaultdict
import netw_creator as nc


def test_assign_power_roles():
    G = nx.Graph()
    G.add_nodes_from(list(range(0, 15)))
    H = G.copy()

    nc.assign_power_roles(G, 4, 5, 128)
    nodes_by_role_G = defaultdict(set)
    for node in G.nodes():
        role = G.node[node]['role']
        nodes_by_role_G[role].add(node)
    # assert(nodes_by_role_G)

    nc.assign_power_roles(H, 5, 7, 128)
    nodes_by_role_H = defaultdict(set)
    for node in H.nodes():
        role = H.node[node]['role']
        nodes_by_role_H[role].add(node)
    # assert(nodes_by_role_H)

    assert len(nodes_by_role_G['generator']) == 4
    assert len(nodes_by_role_G['distribution_substation']) == 5
    assert len(nodes_by_role_H['generator']) == 5
    assert len(nodes_by_role_H['distribution_substation']) == 7
    assert set.issuperset(nodes_by_role_H['generator'], nodes_by_role_G['generator'])
    assert set.issuperset(nodes_by_role_H['distribution_substation'], nodes_by_role_G['distribution_substation'])


def test_assign_power_roles_to_subnets():
    G = nx.Graph()
    G.add_nodes_from(list(range(0, 5)), subnet=0)
    G.add_nodes_from(list(range(5, 10)), subnet=1)
    G.add_nodes_from(list(range(10, 15)), subnet=2)
    H = G.copy()

    nc.assign_power_roles_to_subnets(G, 4, 5, 128)
    nodes_by_role_G = defaultdict(set)
    for node in G.nodes():
        role = G.node[node]['role']
        nodes_by_role_G[role].add(node)
    assert(nodes_by_role_G)

    nc.assign_power_roles_to_subnets(H, 5, 7, 128)
    nodes_by_role_H = defaultdict(set)
    for node in H.nodes():
        role = H.node[node]['role']
        nodes_by_role_H[role].add(node)
    assert(nodes_by_role_H)

    assert len(nodes_by_role_G['generator']) == 4
    assert len(nodes_by_role_G['distribution_substation']) == 5
    assert len(nodes_by_role_H['generator']) == 5
    assert len(nodes_by_role_H['distribution_substation']) == 7
    assert set.issuperset(nodes_by_role_H['generator'], nodes_by_role_G['generator'])
    assert set.issuperset(nodes_by_role_H['distribution_substation'], nodes_by_role_G['distribution_substation'])


def test_create_k_to_n_dep():
    nodes_a = [
        ('a0', {'x': 0, 'y': 0, 'role': 'power'}),
        ('a1', {'x': 0, 'y': 1, 'role': 'power'}),
        ('a2', {'x': 0, 'y': 2, 'role': 'power'}),
        ('a3', {'x': 0, 'y': 3, 'role': 'power'})
    ]

    nodes_a_with_roles = [
        ('D0', {'x': 0, 'y': 0, 'role': 'distribution_substation'}),
        ('G0', {'x': 0, 'y': 1, 'role': 'generator'}),
        ('T0', {'x': 0, 'y': 2, 'role': 'transmission_substation'}),
        ('D1', {'x': 0, 'y': 3, 'role': 'distribution_substation'})
    ]

    nodes_b_1cc = [
        ('C0', {'x': 1, 'y': 0, 'role': 'controller'}),
        ('R0', {'x': 1, 'y': 1, 'role': 'relay'}),
        ('R1', {'x': 1, 'y': 2, 'role': 'relay'}),
        ('C1', {'x': 1, 'y': 3, 'role': 'controller'})
    ]

    nodes_b_2cc = [
        ('C0', {'x': 1, 'y': 0, 'role': 'controller'}),
        ('R0', {'x': 1, 'y': 1, 'role': 'relay'}),
        ('R1', {'x': 1, 'y': 2, 'role': 'relay'}),
        ('R2', {'x': 1, 'y': 3, 'role': 'relay'})
    ]

    A = nx.DiGraph()
    A.add_nodes_from(nodes_a)

    A_with_roles = nx.DiGraph()
    A_with_roles.add_nodes_from(nodes_a_with_roles)

    B_1cc = nx.DiGraph()
    B_1cc.add_nodes_from(nodes_b_1cc)

    B_2cc = nx.DiGraph()
    B_2cc.add_nodes_from(nodes_b_2cc)

    # k is the number of control centers supporting each power node
    # n is the number of power nodes that each control center supports

    # 1 control center supporting everything

    I = nc.create_k_to_n_dep(A, B_2cc, 1, 4, power_roles=False, prefer_nearest=True)
    wanted_edges = [('a0', 'C0'), ('a0', 'R0'),
                    ('a1', 'C0'), ('a1', 'R0'),
                    ('a2', 'C0'), ('a2', 'R1'),
                    ('a3', 'C0'), ('a3', 'R2'),
                    ('C0', 'a0'), ('R0', 'a1'), ('R1', 'a2'), ('R2', 'a3')]
    assert sorted(I.edges()) == sorted(wanted_edges)

    I = nc.create_k_to_n_dep(A_with_roles, B_2cc, 1, 4, power_roles=True, prefer_nearest=True)
    wanted_edges = [('D0', 'C0'), ('D0', 'R0'),
                    ('G0', 'C0'), ('G0', 'R0'),
                    ('T0', 'C0'), ('T0', 'R1'),
                    ('D1', 'C0'), ('D1', 'R2'),
                    ('C0', 'D0'), ('R0', 'D0'), ('R1', 'D1'), ('R2', 'D1')]
    assert sorted(I.edges()) == sorted(wanted_edges)

    I_0 = nc.create_k_to_n_dep(A, B_2cc, 1, 4, power_roles=False, prefer_nearest=False, seed=128)
    I_1 = nc.create_k_to_n_dep(A, B_2cc, 1, 4, power_roles=False, prefer_nearest=False, seed=128)
    wanted_out_degrees = {'a0': 2, 'a1': 2, 'a2': 2, 'a3': 2, 'C0': 1, 'R0': 1, 'R1': 1, 'R2': 1}
    assert I_0.out_degree(['a0', 'a1', 'a2', 'a3', 'C0', 'R0', 'R1', 'R2']) == wanted_out_degrees
    assert sum(I_0.in_degree(['a0', 'a1', 'a2', 'a3']).values()) == 4
    assert sum(I_0.in_degree(['R0', 'R1', 'R2']).values()) == 4
    assert sum(I_0.in_degree(['C0']).values()) == 4
    assert sorted(I_0.edges()) == sorted(I_1.edges())

    I_0 = nc.create_k_to_n_dep(A_with_roles, B_2cc, 1, 4, power_roles=True, prefer_nearest=False, seed=128)
    I_1 = nc.create_k_to_n_dep(A_with_roles, B_2cc, 1, 4, power_roles=True, prefer_nearest=False, seed=128)
    wanted_out_degrees = {'D0': 2, 'G0': 2, 'T0': 2, 'D1': 2, 'C0': 1, 'R0': 1, 'R1': 1, 'R2': 1}
    assert I_0.out_degree(['D0', 'G0', 'T0', 'D1', 'C0', 'R0', 'R1', 'R2']) == wanted_out_degrees
    assert sum(I_0.in_degree(['D0', 'G0', 'T0', 'D1']).values()) == 4
    assert sum(I_0.in_degree(['R0', 'R1', 'R2']).values()) == 4
    assert sum(I_0.in_degree(['C0']).values()) == 4
    assert sorted(I_0.edges()) == sorted(I_1.edges())

    # 2 control centers each supporting all power nodes

    I = nc.create_k_to_n_dep(A, B_1cc, 1, 2, power_roles=False, prefer_nearest=True)
    wanted_edges = [('a0', 'C0'), ('a0', 'R0'),
                    ('a1', 'C0'), ('a1', 'R0'),
                    ('a2', 'C1'), ('a2', 'R1'),
                    ('a3', 'C1'), ('a3', 'R1'),
                    ('C0', 'a0'), ('R0', 'a1'), ('R1', 'a2'), ('C1', 'a3')]
    assert sorted(I.edges()) == sorted(wanted_edges)

    I = nc.create_k_to_n_dep(A_with_roles, B_1cc, 1, 2, power_roles=True, prefer_nearest=True)
    wanted_edges = [('D0', 'C0'), ('D0', 'R0'),
                    ('G0', 'C0'), ('G0', 'R0'),
                    ('T0', 'C1'), ('T0', 'R1'),
                    ('D1', 'C1'), ('D1', 'R1'),
                    ('C0', 'D0'), ('R0', 'D0'), ('R1', 'D1'), ('C1', 'D1')]
    assert sorted(I.edges()) == sorted(wanted_edges)

    I_0 = nc.create_k_to_n_dep(A, B_1cc, 1, 2, power_roles=False, prefer_nearest=False, seed=128)
    I_1 = nc.create_k_to_n_dep(A, B_1cc, 1, 2, power_roles=False, prefer_nearest=False, seed=128)
    wanted_out_degrees = {'a0': 2, 'a1': 2, 'a2': 2, 'a3': 2, 'C0': 1, 'R0': 1, 'R1': 1, 'C1': 1}
    assert I_0.out_degree(['a0', 'a1', 'a2', 'a3', 'C0', 'R0', 'R1', 'C1']) == wanted_out_degrees
    assert sum(I_0.in_degree(['a0', 'a1', 'a2', 'a3']).values()) == 4
    assert sum(I_0.in_degree(['R0', 'R1']).values()) == 4
    assert sum(I_0.in_degree(['C0', 'C1']).values()) == 4
    assert sorted(I_0.edges()) == sorted(I_1.edges())

    I_0 = nc.create_k_to_n_dep(A_with_roles, B_1cc, 1, 2, power_roles=True, prefer_nearest=False, seed=128)
    I_1 = nc.create_k_to_n_dep(A_with_roles, B_1cc, 1, 2, power_roles=True, prefer_nearest=False, seed=128)
    wanted_out_degrees = {'D0': 2, 'G0': 2, 'T0': 2, 'D1': 2, 'C0': 1, 'R0': 1, 'R1': 1, 'C1': 1}
    assert I_0.out_degree(['D0', 'G0', 'T0', 'D1', 'C0', 'R0', 'R1', 'C1']) == wanted_out_degrees
    assert sum(I_0.in_degree(['D0', 'G0', 'T0', 'D1']).values()) == 4
    assert sum(I_0.in_degree(['R0', 'R1']).values()) == 4
    assert sum(I_0.in_degree(['C0', 'C1']).values()) == 4
    assert sorted(I_0.edges()) == sorted(I_1.edges())

    # 2 control centers each supporting half of the power network

    I = nc.create_k_to_n_dep(A, B_1cc, 2, 4, power_roles=False, prefer_nearest=True)
    wanted_edges = [('a0', 'C0'), ('a0', 'C1'), ('a0', 'R0'),
                    ('a1', 'C0'), ('a1', 'C1'), ('a1', 'R0'),
                    ('a2', 'C0'), ('a2', 'C1'), ('a2', 'R1'),
                    ('a3', 'C0'), ('a3', 'C1'), ('a3', 'R1'),
                    ('C0', 'a0'), ('R0', 'a1'), ('R1', 'a2'), ('C1', 'a3')]
    assert sorted(I.edges()) == sorted(wanted_edges)

    I = nc.create_k_to_n_dep(A_with_roles, B_1cc, 2, 4, power_roles=True, prefer_nearest=True)
    wanted_edges = [('D0', 'C0'), ('D0', 'C1'), ('D0', 'R0'),
                    ('G0', 'C0'), ('G0', 'C1'), ('G0', 'R0'),
                    ('T0', 'C0'), ('T0', 'C1'), ('T0', 'R1'),
                    ('D1', 'C0'), ('D1', 'C1'), ('D1', 'R1'),
                    ('C0', 'D0'), ('R0', 'D0'), ('R1', 'D1'), ('C1', 'D1')]
    assert sorted(I.edges()) == sorted(wanted_edges)

    I_0 = nc.create_k_to_n_dep(A, B_1cc, 2, 4, power_roles=False, prefer_nearest=False, seed=128)
    I_1 = nc.create_k_to_n_dep(A, B_1cc, 2, 4, power_roles=False, prefer_nearest=False, seed=128)
    wanted_out_degrees = {'a0': 3, 'a1': 3, 'a2': 3, 'a3': 3, 'C0': 1, 'R0': 1, 'R1': 1, 'C1': 1}
    assert I_0.out_degree(['a0', 'a1', 'a2', 'a3', 'C0', 'R0', 'R1', 'C1']) == wanted_out_degrees
    assert sum(I_0.in_degree(['a0', 'a1', 'a2', 'a3']).values()) == 4
    assert sum(I_0.in_degree(['R0', 'R1']).values()) == 4
    assert sum(I_0.in_degree(['C0', 'C1']).values()) == 8
    assert sorted(I_0.edges()) == sorted(I_1.edges())

    I_0 = nc.create_k_to_n_dep(A_with_roles, B_1cc, 2, 4, power_roles=True, prefer_nearest=False, seed=128)
    I_1 = nc.create_k_to_n_dep(A_with_roles, B_1cc, 2, 4, power_roles=True, prefer_nearest=False, seed=128)
    wanted_out_degrees = {'D0': 3, 'G0': 3, 'T0': 3, 'D1': 3, 'C0': 1, 'R0': 1, 'R1': 1, 'C1': 1}
    assert I_0.out_degree(['D0', 'G0', 'T0', 'D1', 'C0', 'R0', 'R1', 'C1']) == wanted_out_degrees
    assert sum(I_0.in_degree(['D0', 'G0', 'T0', 'D1']).values()) == 4
    assert sum(I_0.in_degree(['R0', 'R1']).values()) == 4
    assert sum(I_0.in_degree(['C0', 'C1']).values()) == 8
    assert sorted(I_0.edges()) == sorted(I_1.edges())

