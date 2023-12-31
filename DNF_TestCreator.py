# author: tomio kobayashi
# version 1.3.2
# published date: 2023/12/12

import re
import copy

class DNF_Test_Creater:

    def prt(pinp, poup, p):
        if p == len(pinp):
            return

        x = []
        for i in range(pinp[p]):
            xx = [0] * pinp[p]
            xx[i] = 1
            x.append(xx)

        poup.append(x)
        DNF_Test_Creater.prt(pinp, poup, p+1)


    def prt2(poup, p):
        if p == len(poup) - 1:
            return poup[p]

        x = []
        for i in range(len(poup[p])):
            pp = DNF_Test_Creater.prt2(poup, p+1)
            for ppp in pp:

                s = poup[p][i] + ppp
                x.append(s)        
        return x

    def cartesian_params(inp):
        oup = []    
        DNF_Test_Creater.prt(inp, oup, 0)
        for i in range(len(oup)):
            if len(oup[i]) == 2:
                oup[i] = [[1], [0]]

        return DNF_Test_Creater.prt2(oup, 0)

    #     This needs to be separate function because the condition 
    #     variables cannot have conflict with function variables.  Thus "__XXX__" format is used to prevent naming conflicts.    
    def myeval(__ccc___, __tokens___, __inp___):
            for __jjjj___ in range(len(__tokens___)):
                exec(__tokens___[__jjjj___] + " = " + str(__ccc___[__jjjj___]))
            return eval(__inp___ + " >= 1")
        
    def solve(inp, evil_neg_lvl=0):

        tokens = re.split('[*+]', inp.replace("&", "*").replace("|", "+").replace(" ","").replace(')', '').replace('(', ''))
        
        # variables that appear more than once
        dups = set()
        ss = sorted(tokens)
        for i in range(len(ss)-1):
            if ss[i] == ss[i+1] and ss[i] not in dups:
                dups.add(ss[i])
        
        tokens = list(dict.fromkeys(tokens))
        patterns = [2 for t in tokens]
        clist = DNF_Test_Creater.cartesian_params(patterns)

        res = [0] * len(clist)
        winsets = []
        losesets = []

        for i in range(len(clist)):

            res[i] = DNF_Test_Creater.myeval(clist[i], tokens, inp)

            wins = []
            for j in range(len(tokens)):
                if clist[i][j]:
                    wins.append(tokens[j])

            if res[i]:
                winsets.append(sorted(wins))
            else:
                losesets.append(sorted(wins))

        staying = True
        while staying:
            staying = False

            for i in range(len(winsets)-1):
                for j in range(i+1, len(winsets), 1):
                    this_ind = i
                    next_ind = j
                    s = sorted(set(winsets[this_ind]).intersection(set(winsets[next_ind])))
                    if winsets[this_ind] == s:
                        winsets.pop(next_ind)
                        staying = True
                        break
                    elif winsets[next_ind] == s:
                        winsets.pop(this_ind)
                        staying = True
                        break
                if staying:
                    break

        losesets = list()
        goodsets = list()
        usedtokens = set()

        evil_true_negator = [list()] * (evil_neg_lvl+1)
        evil_false_negator = [list()] * (evil_neg_lvl+1+1)

        evil_true_negator[0] = copy.deepcopy(winsets)
        for xx in range(evil_neg_lvl):

            evil_true_negator[xx+1] = list()
            for i in range(len(evil_true_negator[xx])):
                winc = set(evil_true_negator[xx][i])

                for c in sorted(tokens):
                    if c not in winc:
                        tryc = copy.deepcopy(evil_true_negator[xx][i])
                        tryc.append(c)
                        evil_true_negator[xx+1].append(sorted(tryc))
                        continue
                        
            new_evil = []
            sorted_evil = sorted(evil_true_negator[xx+1])
            
            if len(sorted_evil) > 0:
                new_evil.append(sorted_evil[0])
                for s in range(1, len(sorted_evil), 1):
                    if sorted_evil[s] != sorted_evil[s-1]:
                        new_evil.append(sorted_evil[s])
            evil_true_negator[xx+1] = new_evil
        
        all_evil_true_negator = []
        for i in range(1, len(evil_true_negator), 1):
            for k in evil_true_negator[i]:
                all_evil_true_negator.append(k)
        all_evil_true_negator.sort()
        
        all_evil_true_negator2 = []
        if len(all_evil_true_negator) > 0:
            all_evil_true_negator2.append(all_evil_true_negator[0])
            for i in range(1, len(all_evil_true_negator), 1):
                if all_evil_true_negator[i] != all_evil_true_negator[i-1]:
                    all_evil_true_negator2.append(all_evil_true_negator[i])
        all_evil_true_negator = all_evil_true_negator2

                
        for i in range(len(winsets)):
            for j in range(len(winsets[i])):

                ww = copy.deepcopy(winsets[i])
                popped = ww.pop(j)
                NotExists = True

                if winsets[i][j] not in usedtokens or winsets[i][j] in dups:
                    for ls in losesets:
                        if ww == ls:
                            NotExists = False
                            break
                    if NotExists:
                        losesets.append(ww)
                        usedtokens.add(popped)
                else:
                    for ls in goodsets:
                        if ww == ls:
                            NotExists = False
                            break
                    if NotExists:
                        goodsets.append(ww)


        evil_false_negator[0] = copy.deepcopy(losesets)
        for xx in range(evil_neg_lvl):
            evil_false_negator[xx+1] = list()
            for i in range(len(evil_false_negator[xx])):
                winc = evil_false_negator[xx][i]

                for c in range(len(winc)):
                    tryc = copy.deepcopy(winc)
                    tryc.pop(c)
                    evil_false_negator[xx+1].append(tryc)
                    continue
                        
            new_evil = []
            sorted_evil = sorted(evil_false_negator[xx+1])
            if len(sorted_evil) > 0:
                new_evil.append(sorted_evil[0])
                for s in range(1, len(sorted_evil), 1):
                    if sorted_evil[s] != sorted_evil[s-1]:
                        new_evil.append(sorted_evil[s])
            evil_false_negator[xx+1] = new_evil
            
        all_evil_false_negator = []
        for i in range(1, len(evil_false_negator), 1):
            for k in evil_false_negator[i]:
                all_evil_false_negator.append(k)
        all_evil_false_negator.sort()
        all_evil_false_negator2 = []
        if len(all_evil_false_negator) > 0:
            all_evil_false_negator2.append(all_evil_false_negator[0])
            for i in range(1, len(all_evil_false_negator), 1):
                if all_evil_false_negator[i] != all_evil_false_negator[i-1]:
                    all_evil_false_negator2.append(all_evil_false_negator[i])
        all_evil_false_negator = all_evil_false_negator2

        print("")
        print("Number of Cartesian Product-Based Test Cases - " + str(len(clist)))
        print(" including true cases - " + str(len([r for r in res if r])))
        print("=========")

        print("")
        print("Suggested True Test Cases - " + str(len(winsets)))
        print("--------")
        # Raw Pattern
        for s in sorted(winsets):
            print(s)
        print("")
        print("Suggested False Test Cases - " + str(len(losesets)) )
        print("--------")
        
        for s in sorted(losesets):
            print(s)

        cnt1 = len(all_evil_true_negator)
        cnt2 = len(all_evil_false_negator)

        print("")
        print("Optional Malignant True Cases (level=" + str(evil_neg_lvl) + ") - " + str(cnt1))
        print("--------")
        for s in all_evil_true_negator:
            print(s)
        print("")
        print("Optional Malignant False Errors (level=" + str(evil_neg_lvl) + ") - " + str(cnt2))
        print("--------")
        for s in all_evil_false_negator:
            print(s)
        print("")

        print("Tab Delimited Results - " + str(len(losesets)))
        print("--------")
        
        ss = ""
        for t in tokens:
            ss += t + "\t"
        ss += "Result"
        print(ss)
            
        for s in sorted(winsets):
            ss = ""
            for t in tokens:
                if t in s:
                    ss += str("1\t")
                else:
                    ss += str("0\t")
            ss += "TRUE"
            print(ss)
        for s in sorted(losesets):
            ss = ""
            for t in tokens:
                if t in s:
                    ss += str("1\t")
                else:
                    ss += str("0\t")
            ss += "FALSE"
            print(ss)

        print("")
        print("Normally not needed, but good to do after all the basic sets are tested.")
        print("Also, they help to find malignant errors - " + str(cnt1+cnt2))
        print("------------------------")
            
        for k in all_evil_true_negator:
            ss = ""
            for t in tokens:
                if t in k:
                    ss += str("1\t")
                else:
                    ss += str("0\t")
            ss += "TRUE"
            print(ss)

        for k in all_evil_false_negator:
            ss = ""
            for t in tokens:
                if t in k:
                    ss += str("1\t")
                else:
                    ss += str("0\t")
            ss += "FALSE"
            print(ss)



inp = "(a & (b | ((g | k) & i)) & c) | (d & (e | (h & j) & f))"
# DNF_Test_Creater.solve(inp, evil_neg_lvl=1)
DNF_Test_Creater.solve(inp)
