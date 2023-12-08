
# Author: tomio kobayashi
# Version: 1.1
# Date: 2023/12/8

import itertools

class DNF_Regression_solver:

    def solve(file_path):
        # def read_tab_delimited_file_to_list(file_path):
        #     with open(file_path, 'r') as f:
        #         return [line.strip().split('\t') for line in f]

        # Example usage:
        # file_path = '/kaggle/input/dnf-regression/dnf_regression.txt'
    #     file_path = '/kaggle/input/tomio5/dnf_regression.txt'
        # inp = read_tab_delimited_file_to_list(file_path)

        good_thresh = 0.8
        max_dnf_len = 8
        
        with open(file_path, 'r') as f:
            inp = [line.strip().split('\t') for line in f]


        # print(inp)

        # print(inp[1])

        numvars = len(inp[1])-1
        # print("numvars", numvars)

        dic = dict()
        true_list = []
        false_list = []
        for i in range(1, len(inp), 1):
            s = ""
            for j in range(len(inp[i]) - 1):
                s += inp[i][j]
            truefalse = inp[i][len(inp[i]) - 1]
            dic[s] = truefalse
            if truefalse == '1':
                true_list.append(s)
            else:
                false_list.append(s)

        zeros = "0" * numvars 

        dnf_perf = list()
        dnf_good = list()
        for s in range(max_dnf_len):
            len_dnf = s + 1
            l = [ii for ii in range(numvars)]
            p_list = list(itertools.combinations(l, len_dnf))
        #     print("p_list", p_list)

            true_test_pass = True
            for i in range(len(p_list)):

                search_str = zeros
                for jj in p_list[i]:
                    search_str = search_str[0:jj] + "1" + search_str[jj+1:len(search_str)]
        #         print("search_str", search_str)
        #         print("dic[search_str]", dic[search_str])
                if dic[search_str] == "0":
                    continue

                search_str2 = search_str
                count_false = 0
                for jj in p_list[i]:
                    search_str2 = search_str[0:jj] + "0" + search_str[jj+1:len(search_str)]

        #             print("search_str2", search_str2)
        #             print("dic[search_str2]", dic[search_str2])
                    if dic[search_str2] == "1":
                        break
                    count_false += 1
        #         print("count_false", count_false)
                if float(count_false)/float(len_dnf) == 1.0:
                    dnf_perf.append([inp[0][ii] for ii in p_list[i]])
                elif float(count_false)/float(len_dnf) >= good_thresh:
                    dnf_good.append([inp[0][ii] for ii in p_list[i]])

        # print("dnf_perf", dnf_perf)
        # print("dnf_good", dnf_good)


        print("")
        print("DNF with assurance - " + str(len(dnf_perf)))
        print("--------")
        # Raw Pattern
#         for s in sorted(dnf_perf):
#             print(s)
        print("(" + ") | (".join([" & ".join(a) for a in dnf_perf]) + ")")
        # Processed Pattern
        # for c in sorted(winsets):
        #     print(', '.join(map(str, c)))
        print("")
        print("DNF with high likelihood - " + str(len(dnf_good)))
        print("--------")
        
        print("(" + ") | (".join([" & ".join(a) for a in dnf_good]) + ")")
#         for s in sorted(dnf_good):
#             print(s)

# file_path = '/kaggle/input/tomio5/dnf_regression.txt'
# DNF_Regression_solver.solve(file_path)