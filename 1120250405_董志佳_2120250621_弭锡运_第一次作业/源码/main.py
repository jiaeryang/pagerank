
"""
作业用的 PageRank 实现。

图结构采用稀疏存储，迭代阶段按连续节点分块计算，
目的是控制活跃工作集大小，降低内存压力。

实现说明：
1. 使用“入边邻接表”代替稠密矩阵，减少内存占用。
2. 保留 0..max_id 范围内所有节点编号，避免漏掉孤立编号。
3. 分块更新分数，提升大图上的缓存局部性。
"""

import sys
from collections import defaultdict
from heapq import nlargest


def read_graph_sparse(filename):
    """读取边列表并构建 PageRank 所需的稀疏结构。

    返回值：
        node_count: 节点总数，按 max_id + 1 推断。
        incoming: incoming[v] 表示所有指向 v 的源节点列表。
        out_degree: out_degree[u] 表示 u 的出度。
        dangling_nodes: 出度为 0 的悬挂节点列表。
    """
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
                # 第一遍先只记录出边，等节点总数确定后再统一构建入边表。
                outgoing[src].append(dst)

                if src > max_node_id:
                    max_node_id = src
                if dst > max_node_id:
                    max_node_id = dst
    except FileNotFoundError:
        print(f"错误：未找到文件 '{filename}'")
        sys.exit(1)
    except ValueError as exc:
        print(f"错误：解析输入文件失败：{exc}")
        sys.exit(1)

    if max_node_id < 0:
        return 0, [], [], []

    node_count = max_node_id + 1
    # incoming/out_degree 使用定长数组并按节点编号直接索引，
    # 迭代阶段开销更低，避免哈希结构带来的额外成本。
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
    """基于稀疏入边表计算 PageRank。

    每个节点的更新公式：
        PR(v) = base_score + d * sum(PR(u) / out_degree(u))
    其中 u 为所有指向 v 的节点。

    base_score 已包含两部分：
    - 随机跳转项 (1 - d) / N
    - 悬挂节点质量再分配项 d * dangling_sum / N
    """
    if node_count == 0:
        return []

    # 标准做法：初始分数均匀分配。
    rank = [1.0 / node_count] * node_count
    # 作为写缓冲区循环复用，避免每轮都重新分配内存。
    next_rank = [0.0] * node_count

    for _ in range(max_iterations):
        # 冻结上一轮结果：本轮统一从 prev_rank 读取，向 next_rank 写入。
        prev_rank = rank[:]

        # 悬挂节点没有外链，需要把其概率质量均匀回灌到所有节点。
        dangling_sum = sum(prev_rank[node] for node in dangling_nodes)

        # 本轮所有节点共享的常量项。
        base_score = (1.0 - damping_factor) / node_count
        base_score += damping_factor * dangling_sum / node_count

        # 使用 L-infinity 范数（最大绝对差）判断收敛。
        max_diff = 0.0

        # 按连续区间分块处理，降低活跃工作集规模。
        for block_start in range(0, node_count, block_size):
            block_end = min(block_start + block_size, node_count)
            for node in range(block_start, block_end):
                incoming_sum = 0.0
                for src in incoming[node]:
                    # 这里可以安全除以 out_degree[src]：
                    # 出度为 0 的节点不可能出现在任何节点的入边来源中。
                    incoming_sum += prev_rank[src] / out_degree[src]

                value = base_score + damping_factor * incoming_sum
                next_rank[node] = value

                diff = abs(value - prev_rank[node])
                if diff > max_diff:
                    max_diff = diff

        rank, next_rank = next_rank, rank

        # 当本轮最大变化量小于阈值时提前停止。
        if max_diff < tolerance:
            break

    return rank


def main():
    # 作业要求的输入输出文件名。
    input_file = "Data.txt"
    output_file = "Res.txt"

    node_count, incoming, out_degree, dangling_nodes = read_graph_sparse(input_file)
    if node_count == 0:
        print("错误：输入文件中未找到有效节点")
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
    # 用堆选出前 k 个节点，避免对全部节点做完整排序。
    top_nodes = nlargest(top_k, range(node_count), key=rank.__getitem__)

    try:
        with open(output_file, 'w', encoding='utf-8') as handle:
            for node in top_nodes:
                handle.write(f"{node} {rank[node]:.8f}\n")
    except IOError as exc:
        print(f"错误：写入输出文件失败：{exc}")
        sys.exit(1)

    print("PageRank 计算完成")
    print(f"处理节点总数：{node_count}")
    print(f"结果已写入 '{output_file}'（前 {top_k} 个节点）")
    print("\nPageRank 前 10 名节点：")
    for i, node in enumerate(top_nodes[:10], 1):
        print(f"  {i}. 节点 {node}：{rank[node]:.8f}")


if __name__ == "__main__":
    main()
