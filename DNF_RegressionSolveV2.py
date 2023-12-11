# Name: DNF_Regression_solver
# Author: tomio kobayashi
# Version: 2.1
# Date: 2023/12/11

import itertools

# import re
# class rdict(dict):
#     def __getitem__(self, key):
#         p = re.compile(key)
#         r = [ v for k,v in self.items() if p.search(k) ]
#         return r if len(r) > 0 else []
#     def get(self, k, d=None):
#         p = re.compile(k)
#         r = [(k, v) for k, v in self.items() if p.search(k)]
#         return r if len(r) > 1 else []
    
    
class DNF_Regression_solver:
#     This version has no good matches
# Instead, all true matches are first added, and some are removed when 
# false unmatch exists and there is no corresponding other rule
    def convTuple2bin(t, width):
        i = 1
        ret = 0
        for x in t:
            ii = i << width - x - 1
            ret = ret | ii
        return ret

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
            dic[int(s, 2)] = truefalse
            if truefalse == '1':
                true_list.append(s)
            else:
                false_list.append(s)

        dnf_perf = list()
        raw_perf = list()

        raw_perf2 = list()
        for s in range(max_dnf_len):
            len_dnf = s + 1
            l = [ii for ii in range(numvars)]
            p_list = list(itertools.combinations(l, len_dnf))

            true_test_pass = True
            for i in range(len(p_list)):
                match_and_break = False
                b = DNF_Regression_solver.convTuple2bin(p_list[i], numvars)
                for p in raw_perf2:
                    if p == b & p:
                        match_and_break = True
                        break
                if match_and_break:
                    continue
                r = [v for k,v in dic.items() if k & b == b]
                if len(r) == 0:
                    continue
                if len([f for f in r if f == "0"]) > 0:
                    continue

                raw_perf.append([ii for ii in p_list[i]])
                raw_perf2.append(b)

        fake_raw = []
        for i in range(len(raw_perf)):

            b = raw_perf2[i]
            count_false = 0
            found_true = False

            for jj in raw_perf[i]:
                jj2 = 1 << (numvars - jj - 1)
                jj3 = b ^ jj2
                rdic_res = [(k, v) for k,v in dic.items() if k & jj2 == jj2 and v == "1"]
                if len(rdic_res) == 0:
                    continue
                is_any_match = False
                for f in rdic_res:
                    if f[1] == "0":
                        continue
                    for kk in raw_perf2:
                        is_match = True
                        if kk != kk & f[0]:
                            is_match = False
                            break
                        if is_match:
                            is_any_match = True
                            break
                    if is_any_match:
                        break
                if not is_any_match:
                    fake_raw.append(raw_perf[i])
        for f in fake_raw:
            for iii in range(len(raw_perf)):
                if f == raw_perf[iii]:
                    raw_perf.pop(iii)
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