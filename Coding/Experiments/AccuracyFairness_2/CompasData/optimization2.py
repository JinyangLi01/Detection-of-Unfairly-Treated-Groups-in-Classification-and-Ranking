"""
This script is to do experiment on the number of attribtues.

two charts: running time, number of patterns checked
y axis: running time, number of patterns checked

x axis: the number of attributes, from 2 to 13.

other parameters:
RecidivismData_att_classified.txt: 6889 rows
size threshold Thc = 30
threshold of minority group accuracy: overall acc - 20
"""



import pandas as pd
from Algorithms import pattern_count
from Algorithms import WholeProcess_0_20201211 as wholeprocess
from Algorithms import NewAlg_1_20210529 as newalg # when deterministic attributes are -1, use NewAlg_1, when -2, use NewALg_2
from Algorithms import NaiveAlg_2_20211020 as naivealg
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter

plt.rc('text', usetex=True)
plt.rc('font', family='serif')


sns.set_palette("Paired")
# sns.set_palette("deep")
sns.set_context("poster", font_scale=2)
sns.set_style("whitegrid")
# sns.palplot(sns.color_palette("deep", 10))
# sns.palplot(sns.color_palette("Paired", 9))

line_style = ['o-', 's--', '^:', '-.p']
color = ['C0', 'C1', 'C2', 'C3', 'C4']
plt_title = ["BlueNile", "COMPAS", "Credit Card"]

label = ["DUC", "Naive"]
line_width = 8
marker_size = 15
# f_size = (14, 10)

f_size = (14, 10)

def ComparePatternSets(set1, set2):
    len1 = len(set1)
    len2 = len(set2)
    if len1 != len2:
        return False
    for p in set1:
        found = False
        for q in set2:
            if newalg.PatternEqual(p, q):
                found = True
                break
        if found is False:
            return False
    return True

def thousands_formatter(x, pos):
    return int(x/1000)

def GridSearch(original_data, mis_data, all_attributes, thc, number_attributes, time_limit, only_new_alg=False):
    selected_attributes = all_attributes[:number_attributes]
    print("{} attributes: {}".format(number_attributes, selected_attributes))

    less_attribute_data = original_data[selected_attributes]
    mis_class_data = mis_data[selected_attributes]
    overall_acc = 1 - len(mis_class_data) / len(less_attribute_data)
    tha = overall_acc - 0.2

    if only_new_alg:

        print("tha = {}, thc = {}".format(tha, thc))
        pattern_with_low_accuracy1, num_calculation1, execution_time1 = newalg.GraphTraverse(less_attribute_data,
                                                                              mis_class_data, tha,
                                                                              thc, time_limit)
        print("newalg, time = {} s, num_calculation = {}".format(execution_time1, num_calculation1), "\n",
              pattern_with_low_accuracy1)
        if execution_time1 > time_limit:
            raise Exception("new alg over time")
        print("{} patterns with low accuracy: \n {}".format(len(pattern_with_low_accuracy1), pattern_with_low_accuracy1))
        return execution_time1, num_calculation1, 0, 0, pattern_with_low_accuracy1


    print("tha = {}, thc = {}".format(tha, thc))
    pattern_with_low_accuracy1, num_calculation1, execution_time1 = newalg.GraphTraverse(less_attribute_data,
                                                                                         mis_class_data, tha,
                                                                                         thc, time_limit)
    print("newalg, time = {} s, num_calculation = {}".format(execution_time1, num_calculation1), "\n", pattern_with_low_accuracy1)

    pattern_with_low_accuracy2, num_calculation2, execution_time2 = naivealg.NaiveAlg(less_attribute_data,
                                                                       mis_class_data, tha,
                                                                       thc, time_limit)
    print("naivealg, time = {} s, num_calculation = {}".format(execution_time2, num_calculation2), "\n",
          pattern_with_low_accuracy2)



    if ComparePatternSets(pattern_with_low_accuracy1, pattern_with_low_accuracy2) is False:
        raise Exception("sanity check fails!")


    print("{} patterns with low accuracy: \n {}".format(len(pattern_with_low_accuracy1), pattern_with_low_accuracy1))

    if execution_time1 > time_limit:
        raise Exception("new alg exceeds time limit")
    if execution_time2 > time_limit:
        raise Exception("naive alg exceeds time limit")

    return execution_time1, num_calculation1, execution_time2, num_calculation2, \
           pattern_with_low_accuracy1





all_attributes = ['sexC', 'ageC', 'raceC', 'MC', 'priors_count_C', 'c_charge_degree', 'decile_score',
                'c_days_from_compas_C',
                'juv_fel_count_C', 'juv_misd_count_C', 'juv_other_count_C', 'start_C', 'end_C',
                  'v_decile_score_C', 'Violence_score_C', 'event_C']

Thc = 50

original_data_file = "../../../../InputData/CompasData/Preprocessed_classified/RecidivismData_17att_classified_testdata.csv"
original_data = pd.read_csv(original_data_file)
mis_data_file = "../../../../InputData/CompasData/Preprocessed_classified/RecidivismData_17att_classified_mis.csv"
mis_data = pd.read_csv(mis_data_file)


print(len(original_data))

overall_acc = 1 - len(mis_data) / len(original_data)


time_limit = 10*60
# when there are 12 attributes, naive time out
# with 11 att, naive needs 137 s
# with 10 att, naive time out > 10 min
num_att_max_naive = 9
num_att_min = 8
num_att_max = 9
execution_time1 = list()
execution_time2 = list()
num_calculation1 = list()
num_calculation2 = list()
num_pattern_skipped_mis_c1 = list()
num_pattern_skipped_mis_c2 = list()
num_pattern_skipped_whole_c1 = list()
num_pattern_skipped_whole_c2 = list()
num_patterns_found = list()
patterns_found = list()
num_loops = 1



for number_attributes in range(num_att_min, num_att_max_naive):
    print("\n\nnumber of attributes = {}".format(number_attributes))
    t1, t2, calculation1, calculation2 = 0, 0, 0, 0
    result_cardinality = 0
    for l in range(num_loops):
        t1_, calculation1_,  t2_, calculation2_, result = \
            GridSearch(original_data, mis_data, all_attributes, Thc, number_attributes, time_limit)
        t1 += t1_
        t2 += t2_
        calculation1 += calculation1_
        calculation2 += calculation2_
        if l == 0:
            result_cardinality = len(result)
            patterns_found.append(result)
            num_patterns_found.append(result_cardinality)
    t1 /= num_loops
    t2 /= num_loops
    calculation1 /= num_loops
    calculation2 /= num_loops

    execution_time1.append(t1)
    num_calculation1.append(calculation1)
    execution_time2.append(t2)
    num_calculation2.append(calculation2)



for number_attributes in range(num_att_max_naive, num_att_max):
    print("\n\nnumber of attributes = {}".format(number_attributes))
    t1, calculation1 = 0, 0
    result_cardinality = 0
    for l in range(num_loops):
        t1_, calculation1_,  _, _, result = \
            GridSearch(original_data, mis_data, all_attributes, Thc, number_attributes, time_limit, True)
        t1 += t1_
        calculation1 += calculation1_
        if l == 0:
            result_cardinality = len(result)
            patterns_found.append(result)
            num_patterns_found.append(result_cardinality)
    t1 /= num_loops
    calculation1 /= num_loops

    execution_time1.append(t1)
    num_calculation1.append(calculation1)




output_path = r'../../../../OutputData/LowAccDetection_1_withStopCond/CompasDataset/optimization.txt'
output_file = open(output_path, "w")
num_lines = len(execution_time1)

output_file.write("execution time\n")
for n in range(num_att_min, num_att_max_naive):
    output_file.write('{} {} {}\n'.format(n, execution_time1[n-num_att_min], execution_time2[n-num_att_min]))
for n in range(num_att_max_naive, num_att_max):
    output_file.write('{} {}\n'.format(n, execution_time1[n - num_att_min]))
#output_file.write('\n'.join('{} {} {}'.format(index + num_att_min, x, y) for index, x, y in enumerate(execution_time1) and execution_time2))


output_file.write("\n\nnumber of patterns checked\n")
for n in range(num_att_min, num_att_max_naive):
    output_file.write('{} {} {}\n'.format(n, num_calculation1[n-num_att_min], num_calculation2[n-num_att_min]))
for n in range(num_att_max_naive, num_att_max):
    output_file.write('{} {}\n'.format(n, num_calculation1[n-num_att_min]))

#output_file.write('\n'.join('{} {} {}'.format(index + num_att_min, x, y) for index, x, y in enumerate(num_calculation1) and num_calculation2))



output_file.write("\n\nnumber of patterns found\n")
for n in range(num_att_min, num_att_max):
    output_file.write('{} {} \n {}\n'.format(n-num_att_min, num_patterns_found[n-num_att_min], patterns_found[n-num_att_min]))


