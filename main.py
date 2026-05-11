#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PageRank implementation for the assignment.

The graph is stored in sparse form and the iteration is executed in blocks
over contiguous node ranges to keep the active working set small.
"""

import sys
from collections import defaultdict
from heapq import nlargest


def read_graph_sparse(filename):
    """Read Data.txt and build a sparse graph with all node IDs from 0..max_id."""
    outgoing = defaultdict(list)
    max_node_id = -1

    try:
        with open(filename, 'r', encoding='utf-8') as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue

                parts = line.split()
                if len(parts) < 2:
                    continue

                src = int(parts[0])
                dst = int(parts[1])
                outgoing[src].append(dst)

                if src > max_node_id:
                    max_node_id = src
                if dst > max_node_id:
                    max_node_id = dst
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except ValueError as exc:
        print(f"Error parsing file: {exc}")
        sys.exit(1)

    if max_node_id < 0:
        return 0, [], [], []

    node_count = max_node_id + 1
    incoming = [[] for _ in range(node_count)]
    out_degree = [0] * node_count

    for src, dst_list in outgoing.items():
        out_degree[src] = len(dst_list)
        for dst in dst_list:
            incoming[dst].append(src)

    dangling_nodes = [node for node in range(node_count) if out_degree[node] == 0]
    return node_count, incoming, out_degree, dangling_nodes


def pagerank_sparse(node_count, incoming, out_degree, dangling_nodes,
                    damping_factor=0.85, max_iterations=100,
                    tolerance=1e-8, block_size=1024):
    """Compute PageRank using sparse adjacency lists and block-wise updates."""
    if node_count == 0:
        return []

    rank = [1.0 / node_count] * node_count
    next_rank = [0.0] * node_count

    for _ in range(max_iterations):
        prev_rank = rank[:]
        dangling_sum = sum(prev_rank[node] for node in dangling_nodes)
        base_score = (1.0 - damping_factor) / node_count
        base_score += damping_factor * dangling_sum / node_count

        max_diff = 0.0

        for block_start in range(0, node_count, block_size):
            block_end = min(block_start + block_size, node_count)
            for node in range(block_start, block_end):
                incoming_sum = 0.0
                for src in incoming[node]:
                    incoming_sum += prev_rank[src] / out_degree[src]

                value = base_score + damping_factor * incoming_sum
                next_rank[node] = value

                diff = abs(value - prev_rank[node])
                if diff > max_diff:
                    max_diff = diff

        rank, next_rank = next_rank, rank

        if max_diff < tolerance:
            break

    return rank


def main():
    input_file = "Data.txt"
    output_file = "Res.txt"

    node_count, incoming, out_degree, dangling_nodes = read_graph_sparse(input_file)
    if node_count == 0:
        print("Error: No nodes found in input file")
        sys.exit(1)

    rank = pagerank_sparse(
        node_count,
        incoming,
        out_degree,
        dangling_nodes,
        damping_factor=0.85,
        max_iterations=100,
        tolerance=1e-8,
        block_size=1024,
    )

    top_k = min(100, node_count)
    top_nodes = nlargest(top_k, range(node_count), key=rank.__getitem__)

    try:
        with open(output_file, 'w', encoding='utf-8') as handle:
            for node in top_nodes:
                handle.write(f"{node} {rank[node]:.8f}\n")
    except IOError as exc:
        print(f"Error writing output file: {exc}")
        sys.exit(1)

    print("PageRank computation completed successfully")
    print(f"Total nodes processed: {node_count}")
    print(f"Results written to '{output_file}' (Top {top_k} nodes)")
    print("\nTop 10 nodes by PageRank score:")
    for i, node in enumerate(top_nodes[:10], 1):
        print(f"  {i}. Node {node}: {rank[node]:.8f}")


if __name__ == "__main__":
    main()
