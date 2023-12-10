# Author: tomio kobayashi
# Version: 1.5.1
# Date: 2023/12/10

import itertools

import re
class rdict(dict):
    def __getitem__(self, key):
        p = re.compile(key)
        r = [ v for k,v in self.items() if p.search(k) ]
        return r if len(r) > 0 else []
    def get(self, k, d=None):
        p = re.compile(k)
        r = [(k, v) for k, v in self.items() if p.search(k)]
        return r if len(r) > 1 else []
    
    
class DNF_Regression_solver:

    def solve(file_path, good_thresh=0.0, allow_unmatch_for_good=False, max_dnf_len = 6):

        # Example usage:
        # file_path = '/kaggle/input/dnf-regression/dnf_regression.txt'
    #     file_path = '/kaggle/input/tomio5/dnf_regression.txt'

        with open(file_path, 'r') as f:
            inp = [line.strip().split('\t') for line in f]

        numvars = len(inp[1])-1

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

        rdic = rdict(dic)
        
        zeros = "0" * numvars 
        nonzeros = "." * numvars 

        dnf_perf = list()
        dnf_good = list()
        raw_perf = list()
        
        failed_false_tests = 0
        for s in range(max_dnf_len):
            len_dnf = s + 1
            l = [ii for ii in range(numvars)]
            p_list = list(itertools.combinations(l, len_dnf))

            true_test_pass = True
            for i in range(len(p_list)):

                match_and_break = False
                for p in raw_perf:
                    s = sorted(set(p).intersection(set(list(p_list[i]))))
                    if len(p) == len(s):
                        match_and_break = True
                        break
                if match_and_break:
                    continue
                search_str = nonzeros
                for jj in p_list[i]:
                    search_str = search_str[0:jj] + "1" + search_str[jj+1:len(search_str)]
                rdic_res = rdic[search_str]
                if len(rdic_res) == 0:
                    continue
                if len([f for f in rdic_res if f == "0"]) > 0:
                    continue
                      
#                 print("True test passed", p_list[i])
                search_str2 = search_str
                count_false = 0
                found_true = False
#                 for jj in p_list[i]:
#                     search_str2 = search_str[0:jj] + "0" + search_str[jj+1:len(search_str)]

#                     rdic_res = rdic[search_str2]
# #                     print("rdic_res", rdic_res)
#                     if len(rdic_res) == 0:
#                         continue
#                     if len([f for f in rdic_res if f == "1"]) > 0:
                        
#                         print("False Test Failed")
#                         print("search_str2", search_str2)
#                         print("rdic_res", rdic_res)
# #                         failed_false_tests[p_list[i]] = [f for f in rdic_res if f == "1"]
#                         found_true = True
#                         break

                search_str = search_str.replace(".", "0")
                for jj in p_list[i]:
                    search_str2 = search_str[0:jj] + "0" + search_str[jj+1:len(search_str)]
                    if search_str2 not in dic:
                        continue
                    if dic[search_str2] == "1":
                        found_true = True
                        break
                    count_false += 1
                if not allow_unmatch_for_good:
                    if found_true :
                        continue
                if float(count_false)/float(len_dnf) == 1.0:
                    dnf_perf.append([inp[0][ii] for ii in p_list[i]])
                    raw_perf.append([ii for ii in p_list[i]])
                elif float(count_false)/float(len_dnf) >= good_thresh:
                    dnf_good.append([inp[0][ii] for ii in p_list[i]])

#         print("")
#         dnf_perf.extend(dnf_good)
#         print("DNF with high confidence (over " + str(good_thresh) +") - " + str(len(dnf_perf)))
#         print("--------------------------------")

#         if len(dnf_perf) > 0:
#             print("(" + ") | (".join([" & ".join(a) for a in dnf_perf]) + ")")

#         perm_vars = [xx for x in dnf_perf for xx in x]
#         not_picked = [inp[0][ii] for ii in range(len(inp[0])-1) if inp[0][ii] not in perm_vars]

#         print("")
#         print("Unsolved variables - " + str(len(not_picked)) + "/" + str(numvars))
#         print("--------------------------------")
#         print(not_picked)



        print("")
        print("DNF with complete match (1.0) - " + str(len(dnf_perf)))
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
        print("DNF with complete true match but false match rate of " + str(good_thresh) +" - " + str(len(dnf_good)))
        print("--------------------------------")
        
        if len(dnf_good) > 0:
            print("(" + ") | (".join([" & ".join(a) for a in dnf_good]) + ")")
#         for s in sorted(dnf_good):
#             print(s)

        perm_vars = [xx for x in dnf_perf for xx in x]
        not_picked = [inp[0][ii] for ii in range(len(inp[0])-1) if inp[0][ii] not in perm_vars]

        print("")
        print("Unsolved variables - " + str(len(not_picked)) + "/" + str(len(perm_vars)))
        print("--------------------------------")
        print(not_picked)


file_path = '/kaggle/input/tomio9/dnf_regression.txt'
DNF_Regression_solver.solve(file_path)