# Author: tomio kobayashi
# Version: 1.3.2
# Date: 2023/12/09


import itertools

class DNF_Regression_solver:

    def solve(file_path, good_thresh=0.7, allow_unmatch_for_good=False, max_dnf_len = 15):
        # def read_tab_delimited_file_to_list(file_path):
        #     with open(file_path, 'r') as f:
        #         return [line.strip().split('\t') for line in f]

        # Example usage:
        # file_path = '/kaggle/input/dnf-regression/dnf_regression.txt'
    #     file_path = '/kaggle/input/tomio5/dnf_regression.txt'
        # inp = read_tab_delimited_file_to_list(file_path)

#         good_thresh = 0.7 # TRESH_HOLD THAT THE FALSE MATCH SHOULD BE CONSIDERED AS GOOD
        
        with open(file_path, 'r') as f:
            inp = [line.strip().split('\t') for line in f]


        # print(inp)

        # print(inp[1])

        numvars = len(inp[1])-1
        # print("numvars", numvars)

        if numvars - 1 < max_dnf_len:
            max_dnf_len = numvars - 1
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
        
        raw_perf = list()
        for s in range(max_dnf_len):
            len_dnf = s + 1
            l = [ii for ii in range(numvars)]
            p_list = list(itertools.combinations(l, len_dnf))
        #     print("p_list", p_list)

            true_test_pass = True
            for i in range(len(p_list)):

                match_and_break = False
                for p in raw_perf:
                    s = sorted(set(p).intersection(set(list(p_list[i]))))
#                     print("compare p", p)
#                     print("compare list(p_list[i])", list(p_list[i]))
#                     print("compare s", s)
                    if len(p) == len(s):
#                         print("matched and break")
                        match_and_break = True
                        break
                if match_and_break:
                    continue
                search_str = zeros
                for jj in p_list[i]:
                    search_str = search_str[0:jj] + "1" + search_str[jj+1:len(search_str)]
        #         print("search_str", search_str)
        #         print("dic[search_str]", dic[search_str])
                if dic[search_str] == "0":
                    continue

                search_str2 = search_str
                count_false = 0
                found_true = False
                for jj in p_list[i]:
                    search_str2 = search_str[0:jj] + "0" + search_str[jj+1:len(search_str)]

        #             print("search_str2", search_str2)
        #             print("dic[search_str2]", dic[search_str2])
                    if dic[search_str2] == "1":
                        found_true = True
                        break
                    count_false += 1
        #         print("count_false", count_false)
                if not allow_unmatch_for_good:
                    if found_true :
                        continue
                if float(count_false)/float(len_dnf) == 1.0:
                    dnf_perf.append([inp[0][ii] for ii in p_list[i]])
                    raw_perf.append([ii for ii in p_list[i]])
                elif float(count_false)/float(len_dnf) >= good_thresh:
                    dnf_good.append([inp[0][ii] for ii in p_list[i]])

        # print("dnf_perf", dnf_perf)
        # print("dnf_good", dnf_good)


        print("")
        print("DNF with perfect match (1.0) - " + str(len(dnf_perf)))
        print("--------------------------------")
        # Raw Pattern
#         for s in sorted(dnf_perf):
#             print(s)
        if len(dnf_perf) > 0:
            print("(" + ") | (".join([" & ".join(a) for a in dnf_perf]) + ")")
        # Processed Pattern
        # for c in sorted(winsets):
        #     print(', '.join(map(str, c)))
        print("")
        print("DNF with good match (over " + str(good_thresh) +") - " + str(len(dnf_good)))
        print("--------------------------------")
        
        if len(dnf_good) > 0:
            print("(" + ") | (".join([" & ".join(a) for a in dnf_good]) + ")")
#         for s in sorted(dnf_good):
#             print(s)

        perm_vars = [xx for x in dnf_perf for xx in x]
        not_picked = [inp[0][ii] for ii in range(len(inp[0])-1) if inp[0][ii] not in perm_vars]

        print("")
        print("Variables that were not picked up - " + str(len(not_picked)) + "/" + str(len(perm_vars)))
        print("--------------------------------")
        print(not_picked)




file_path = '/kaggle/input/tomio9/dnf_regression.txt'
DNF_Regression_solver.solve(file_path)