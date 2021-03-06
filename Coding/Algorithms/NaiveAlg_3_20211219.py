"""
difference from alg_2:
change undertermined from -1 to -2, since medical dataset has -1 values but no smaller values!!!

!!!ATTENTION!!!
when non-deterministic attributes are -2, use this script.
When they are -1, use NaiveAlg_2!!!

"""

from itertools import combinations
import pandas as pd
import pattern_count
import time



def Prepatation(filename):
    mc = pd.read_csv(filename)
    mcdes = mc.describe()
    attributes = mcdes.columns.values
    return mc, mcdes, attributes


def DFSattributes(cur, last, comb, pattern, all_p, mcdes, attributes):
    # print("DFS", attributes)
    if cur == last:
        # print("comb[{}] = {}".format(cur, comb[cur]))
        # print("{} {}".format(int(mcdes[attributes[comb[cur]]]['min']), int(mcdes[attributes[comb[cur]]]['max'])))
        for a in range(int(mcdes[attributes[comb[cur]]]['min']), int(mcdes[attributes[comb[cur]]]['max']) + 1):
            s = pattern.copy()
            s[comb[cur]] = a
            all_p.append(s)
        return
    else:
        # print("comb[{}] = {}".format(cur, comb[cur]))
        # print("{} {}".format(int(mcdes[attributes[comb[cur]]]['min']), int(mcdes[attributes[comb[cur]]]['max'])))
        for a in range(int(mcdes[attributes[comb[cur]]]['min']), int(mcdes[attributes[comb[cur]]]['max']) + 1):
            s = pattern.copy()
            s[comb[cur]] = a
            DFSattributes(cur + 1, last, comb, s, all_p, mcdes, attributes)


def AllPatternsInComb(comb, NumAttribute, mcdes, attributes):  # comb = [1,4]
    # print("All", attributes)
    all_p = []
    pattern = [-2] * NumAttribute
    DFSattributes(0, len(comb) - 1, comb, pattern, all_p, mcdes, attributes)
    return all_p


def num2string(pattern):
    st = ''
    for i in pattern:
        if i != -2:
            st += str(i)
        st += '|'
    st = st[:-1]
    return st


def PatternEqual(m, P):
    length = len(m)
    if len(P) != length:
        return False
    for i in range(length):
        if m[i] != P[i]:
            return False
    return True


def P1DominatedByP2(P1, P2):
    length = len(P1)
    for i in range(length):
        if P1[i] == -2:
            if P2[i] != -2:
                return False
        if P1[i] != -2:
            if P2[i] != P1[i] and P2[i] != -2:
                return False
    return True


# coverage of P among dataset D
def cov(P, D):
    cnt = 0
    for d in D:
        if P1DominatedByP2(d, P):
            cnt += 1
    return cnt



# whether a pattern P is dominated by MUP M
# except from P itself
def PDominatedByM(P, M):
    for m in M:
        if PatternEqual(m, P):
            continue
        if P1DominatedByP2(P, m):
            return True, m
    return False, None


def NaiveAlg(whole_data, mis_class_data, Tha, Thc, time_limit):
    print("start naive alg")
    time1 = time.time()

    pc_mis_class = pattern_count.PatternCounter(mis_class_data, encoded=False)
    pc_mis_class.parse_data()

    pc_whole_data = pattern_count.PatternCounter(whole_data, encoded=False)
    pc_whole_data.parse_data()


    whole_data_frame = whole_data.describe()
    attributes = whole_data_frame.columns.values.tolist()
    NumAttribute = len(attributes)
    index_list = list(range(0, NumAttribute))  # list[1, 2, ...13]

    num_patterns = 0
    pattern_with_low_accuracy = []
    num_patterns_skipped_by_size = 0
    num_patterns_computed_acc = 0
    all_have_small_size = True
    num_att = 0
    for num_att in range(1, NumAttribute + 1):
        # print("----------------------------------------------------  num_att = ", num_att)
        all_have_small_size = True
        comb_num_att = list(combinations(index_list, num_att))  # list of combinations of attribute index, length num_att
        overTime = False
        for comb in comb_num_att:
            if time.time() - time1 > time_limit:
                overTime = True
                break
            patterns = AllPatternsInComb(comb, NumAttribute, whole_data_frame, attributes)
            for p in patterns:
                p_ = num2string(p)
                num_patterns += 1
                whole_cardinality = pc_whole_data.pattern_count(p_)
                if whole_cardinality < Thc:
                    num_patterns_skipped_by_size += 1
                    continue
                all_have_small_size = False
                mis_class_cardinality = pc_mis_class.pattern_count(p_)
                accuracy = (whole_cardinality - mis_class_cardinality) / whole_cardinality
                num_patterns_computed_acc += 1
                if accuracy < Tha:
                    if PDominatedByM(p, pattern_with_low_accuracy)[0] is False:
                        # allDominatedByCurrentCandidateSet = False
                        pattern_with_low_accuracy.append(p)
        if overTime:
            print("naive alg overtime")
            break

        # stop condition: if all patterns have a size smaller than the threshold, stop searching
        if all_have_small_size:
            break

    time2 = time.time()
    execution_time = time2 - time1
    print("num_patterns_skipped_by_size = {}, num_patterns_computed_acc = {}".format(num_patterns_skipped_by_size,
                                                     num_patterns_computed_acc))
    if all_have_small_size and num_att < NumAttribute:
        print("stop condition satisfied with {} attributes\n".format(num_att))
    return pattern_with_low_accuracy, num_patterns, execution_time

