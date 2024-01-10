# Name: DNF_Regression_solver
# Author: tomio kobayashi
# Version: 2.1.5
# Date: 2024/01/11

import itertools
from sympy.logic import boolalg

class DNF_Regression_solver:
# This version has no good matches
# Instead, all true matches are first added, and some are removed when 
# false unmatch exists and there is no corresponding other rule
    def convTuple2bin(t, width):
        i = 1
        ret = 0
        for x in t:
            ii = i << width - x - 1
            ret = ret | ii
        return ret

    def solve(file_path, max_dnf_len=6, check_negative=True, check_false=True):

# file_path: input file in tab-delimited text
# check_negative: enable to check the negative conditions or not.  This one is very heavy.
# max_dnf_len: max length of AND clauses in output DNF.  
#       Increasing this one is heavey especially if check_negative is True
# drop_fake: enable to drop the clause that met the true condition, but not false condition.  This one is heavy.

        # Example usage:
        # file_path = '/kaggle/input/dnf-regression/dnf_regression.txt'
        # file_path = '/kaggle/input/tomio5/dnf_regression.txt'

        with open(file_path, 'r') as f:
            inp = [line.strip().split('\t') for line in f]

        numvars = len(inp[1])-1

        if check_negative:
            for i in range(numvars):
                inp[0].insert(i+numvars, "n_" + inp[0][i])
            for j in range(1, len(inp), 1):
                for i in range(numvars):
                    inp[j].insert(i+numvars,"0" if inp[j][i] == "1" else "1")
            numvars *= 2

        if max_dnf_len > numvars - 1:
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
        
        for dn in raw_perf:
            dnf_perf.append([inp[0][ii] for ii in dn])

            
        dnf_perf_n = list()
        raw_perf_n = list()
        raw_perf2_n = list()
        if check_false:
            for s in range(max_dnf_len):
                len_dnf = s + 1
                l = [ii for ii in range(numvars)]
                p_list = list(itertools.combinations(l, len_dnf))

                true_test_pass = True
                for i in range(len(p_list)):
                    match_and_break = False
                    b = DNF_Regression_solver.convTuple2bin(p_list[i], numvars)
                    for p in raw_perf2_n:
                        if p == b & p:
                            match_and_break = True
                            break
                    if match_and_break:
                        continue
                    r = [v for k,v in dic.items() if k & b == b]
                    if len(r) == 0:
                        continue
                    if len([f for f in r if f == "1"]) > 0:
                        continue

                    raw_perf_n.append([ii for ii in p_list[i]])
                    raw_perf2_n.append(b)
        
        for dn in raw_perf_n:
            dnf_perf_n.append([inp[0][ii] for ii in dn])

        set_dnf_true = set([" (" + s + ") " for s in [" & ".join(a) for a in dnf_perf]])
        dnf_common = None
        set_dnf_false = None
        if check_false:
            set_dnf_false = set(str(boolalg.to_dnf("(" + ") & (".join([" | ".join(a) for a in [[a[2:] if a[0:2] == "n_" else "n_" + a for a in aa] for aa in dnf_perf_n]]) + ")")).split("|"))
            dnf_common = set_dnf_true & set_dnf_false
        else:
            dnf_common = set_dnf_true
            
        if check_false:
            print("")
            print("DNF COMMON - " + str(len(dnf_common)))
            print("--------------------------------")

            if len(dnf_common) > 0:
                print("|".join(dnf_common))
            
        print("")
        print("DNF TRUE - " + str(len(set_dnf_true)))
        print("--------------------------------")

        if len(set_dnf_true) > 0:
            print("|".join(set_dnf_true))

        if check_false:
            print("")
            print("DNF FALSE - " + str(len(set_dnf_false)))
            print("--------------------------------")
            if len(set_dnf_false) > 0:
                print("|".join(set_dnf_false))
            
        perm_vars = list(set([xx for x in dnf_perf for xx in x] + [xx for x in dnf_perf_n for xx in x]))
        not_picked = [inp[0][ii] for ii in range(len(inp[0])-1) if inp[0][ii] not in perm_vars]

        print("")
#         print("Unsolved variables - " + str(len(not_picked)) + "/" + str(len(perm_vars)))
        print("Unsolved variables - " + str(len(not_picked)) + "/" + str(len(inp[0])-1))
        print("--------------------------------")
        print(not_picked)



file_path = '/kaggle/input/tomio2/dnf_regression.txt'
DNF_Regression_solver.solve(file_path)