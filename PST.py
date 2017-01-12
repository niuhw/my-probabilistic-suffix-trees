# encoding:utf-8
import re
from random import choice

'''构建概率后缀树
'''
TOTAL_SEQUENCE = ''


class TreeNode(object):
    def __init__(self):
        self.count = 1  # 统计此结点代表的字符串出现的次数
        self.name = 'root'  # 标记node的名称
        self.children = {}
        self.totalchild = 0  # 统计node子节点个数
        self.probability_vector = {}  # 转移概率向量
        self.pre_pv = {}  # 上一节点的概率向量s
        self.pre_node = None  # 上一节点


class Tree2(object):
    def __init__(self):
        self.root = TreeNode()
        self.P_min = 0.00  # 入树概率阈值
        self.gamma = 0.01  # 节点转移概率阈值
        self.alpha = 0.01  # 另一个阈值 在判断候选节点时起作用
        self.L = 2  # 树最大深度
        self.deepth = 0  # 树深度

    def build(self, sequence):
        print("------------------ line:", sequence, " ------------------")
        node = self.root
        seq_list = list(sequence)
        dis_seq_list = list(set(seq_list))
        dis_seq_list.sort(key=list(sequence).index)
        for i in range(self.L):
            # 此时获取到去重后的字符数组，c为单个字符
            for c in dis_seq_list:
                if compute_pro(c, seq_list) > self.P_min:  # 第一步验证候选节点，如果频率超过P_min，则作为候选节点
                    if c not in node.children:  # c不在子节点中
                        for b in dis_seq_list:  # 生成该节点的pre_pv list
                            node.pre_pv[b] = compute_pro(b, seq_list)
                        print("pre_pv", node.pre_pv)
                        s = c
                        print("候选节点：", s)
                        s_suffix_list = get_suffix(s, 2, sequence)

                        # 判断当前候选节点s是否符合入选条件
                        for sigma in dis_seq_list:
                            sigma_pro = compute_pro(sigma, s_suffix_list)
                            if sigma_pro > self.gamma:  # 存在一个sigma属于Σ，P(sigma|s)>gamma
                                print("sigma", sigma, "sigma_pro:", sigma_pro)
                                if sigma_pro / node.pre_pv[sigma] > self.alpha or sigma_pro / node.pre_pv[
                                    sigma] > 1 / self.alpha:
                                    # 同时满足条件P(sigma|s)/P(sigma|suff(s))>alpha or P(sigma|s)/P(sigma|suff(s))<(1/alpha)
                                    print(s, '满足新建节点条件')
                                    child = TreeNode()  # 满足条件后，添加该节点到树中
                                    node.children[s] = child
                                    node = child
                                    self.deepth += 1
                                    break
                        print('self.deepth', self.deepth)
                        print("-----------------------ok-----------------------")


class Tree(object):
    def __init__(self):
        self.root = TreeNode()
        self.P_min = 0.00  # 入树概率阈值
        self.gamma = 0.01  # 节点转移概率阈值
        self.alpha = 0.01  # 另一个阈值 在判断候选节点时起作用
        self.L = 3  # 树最大深度L，即L阶PST
        self.current_deepth = 1  # 当前树深度
        self.pre_node_len = 0  # 判断叶节点是否向上回溯，该值为上一次处理序列的长度

    def build(self, sequence):
        print("------------------ sequence:", sequence, " ------------------")
        seq_list = list(sequence)
        dis_seq_list = list(set(seq_list))
        dis_seq_list.sort(key=list(sequence).index)
        dis_seq_list.remove('$')
        print('获取到有序去重字符集:', dis_seq_list)

        '''
        add_pst为递归函数，该函数的主要作用是递归构造PST
        需要传入当前node节点，总序列sequence,以及候选节点list：candidate_list
        '''

        def add_pst(node, sequence, candidate_list):
            if len(candidate_list) == 0:
                # 如果是根节点传入，将候选节点设置为去重后的字符集
                candidate_list = dis_seq_list
                # 计算转移概率
                for candidate_p in dis_seq_list:
                    node.probability_vector[candidate_p] = compute_pro(candidate_p, sequence)
            else:
                # total_count为查找到的、以候选字符串作为后缀的字符串的数量
                total_count = 0
                for single_tag in dis_seq_list:
                    find_str = node.name + single_tag
                    total_count += find_str_count(find_str, TOTAL_SEQUENCE)
                for single_tag in dis_seq_list:
                    node.probability_vector[single_tag] = float(
                        find_str_count(node.name + single_tag, TOTAL_SEQUENCE)) / float(
                        total_count)

            for candidate_r in candidate_list:
                # 遍历候选字符列表
                if candidate_r in dis_seq_list:
                    print("候选字符在去重列表中，表示又一次从根节点开始,树深需要置为1,同时node恢复为root")
                    self.current_deepth = 1
                    node = self.root

                if compute_pro(candidate_r, sequence) > self.P_min:
                    # 此时candidate_r为出现概率大于P_min的候选节点
                    # 切换支点
                    print("上次处理：", self.pre_node_len, "本次长度:", len(candidate_r))
                    if node is not self.root and (self.pre_node_len >= len(candidate_r)):
                        # 如果上一次保存候选序列的长度大于该序列长度，说明此时节点需要向上回溯
                        node = node.pre_node
                    self.pre_node_len = len(candidate_r)
                    print("********符合条件:", candidate_r, "树深度:", len(candidate_r), "节点名：", node.name)
                    child = TreeNode()
                    child.pre_node = node
                    child.name = candidate_r
                    node.children[candidate_r] = child
                    node = child
                    q = []
                    for x in dis_seq_list:
                        # 给每一个候选节点增加前缀，增加的前缀为去重字符集dis_seq_list的遍历
                        str_x_r = ''
                        str_x_r = x + candidate_r
                        q.append(str_x_r)
                    # 此时获得的q，是通过合法候选字符（P>P_min）构造好的前缀数组
                    print("当前字符：", candidate_r, " 候选序列：", q)
                    if len(candidate_r) < self.L:  # if self.current_deepth < self.L:
                        # 树在本分支上的深度自增，步长为1；但此时用的是字符集长度计算 todo:如果表示一次行为的符号不是一个字母或符号，需要review
                        # self.current_deepth += 1
                        add_pst(node, sequence, q)

        root_node = self.root
        add_pst(root_node, sequence, [])


def compute_pro(s, total_sequence):
    '''计算s在total_sequence中出现的概率'''
    return float(total_sequence.count(s)) / float(len(total_sequence.replace('$', '')))


def compute_list_pro(s, sequence_list):
    '''计算s在sequence_list出现的概率'''
    return float(sequence_list.count(s)) / float(len(sequence_list))


def get_suffix_list(seq, length, str):
    '''返回在str中，长度为1，起始字符为seq的字符串'''
    for i in range(length - 1):
        seq = seq + '.'
    result = re.findall(seq, str)
    print(result)
    result = map(lambda x: x[-1], result)

    return list(result)


def gen_tree(input_file):
    '''生成PST'''
    tree = Tree()
    global TOTAL_SEQUENCE
    with open(input_file) as f:
        for line in f:
            # 增加'$'用来区别是否是完整后缀  todo:PST是否需要？
            line = line.strip() + '$'
            TOTAL_SEQUENCE += line
        tree.build(TOTAL_SEQUENCE)
    return tree


def find_str_count(x, total_str):
    start = 0
    count = 0
    while True:
        index = total_str.find(x, start)
        # if search string not found, find() returns -1
        # search is complete, break out of the while loop
        if index == -1:
            break
        # move to next possible start position
        start = index + 1
        count += 1
    return count

if __name__ == '__main__':
    txt = 'pst_data.txt'
    pkl = 'pst_result.pkl'
    tree = gen_tree(txt)
    print(tree.root.children['a'].children['ca'].children['cca'].probability_vector)
    print("------------------------------------------------------------------")
