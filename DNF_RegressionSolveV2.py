# Name: DNF_Regression_solver
# Author: tomio kobayashi
# Version: 2.0
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
#     This version has no good matches
# Instead, all true matches are first added, and some are removed when 
# false unmatch exists and there is no corresponding other rule

    def solve(file_path):

        # Example usage:
        # file_path = '/kaggle/input/dnf-regression/dnf_regression.txt'
    #     file_path = '/kaggle/input/tomio5/dnf_regression.txt'

        with open(file_path, 'r') as f:
            inp = [line.strip().split('\t') for line in f]

        numvars = len(inp[1])-1

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
                      
                search_str2 = search_str
                count_false = 0
                found_true = False
                raw_perf.append([ii for ii in p_list[i]])

        fake_raw = []
        for i in range(len(raw_perf)):

            search_str = nonzeros
            for jj in raw_perf[i]:
                search_str = search_str[0:jj] + "1" + search_str[jj+1:len(search_str)]
            count_false = 0
            found_true = False

            for jj in raw_perf[i]:
                search_str2 = search_str[0:jj] + "0" + search_str[jj+1:len(search_str)]

                rdic_res = rdic.get(search_str2)
                if len(rdic_res) == 0:
                    continue
                for f in rdic_res:
                    if f[1] == "0":
                        continue
                    is_any_match = False
                    for kk in raw_perf:
                        is_match = True
                        for mm in kk:
                            if f[0][mm:mm+1] == "0":
                                is_match = False
                                break
                        if is_match:
                            is_any_match = True
                            break
                    if not is_any_match:
                        fake_raw.append()
        for f in fake_raw:
            for iii in range(len(raw_perf)):
                if f == raw_perf[iii]:
                    raw_perf.pop[iii]
                    break

        for dn in raw_perf:
            dnf_perf.append([inp[0][ii] for ii in dn])

        print("")
        print("DNF - " + str(len(dnf_perf)))
        print("--------------------------------")

        if len(dnf_perf) > 0:
            print("(" + ") | (".join([" & ".join(a) for a in dnf_perf]) + ")")


        perm_vars = [xx for x in dnf_perf for xx in x]
        not_picked = [inp[0][ii] for ii in range(len(inp[0])-1) if inp[0][ii] not in perm_vars]

        print("")
        print("Unsolved variables - " + str(len(not_picked)) + "/" + str(len(perm_vars)))
        print("--------------------------------")
        print(not_picked)



file_path = '/kaggle/input/tomio2/dnf_regression.txt'
DNF_Regression_solver.solve(file_path)