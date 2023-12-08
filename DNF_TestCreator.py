# Clean Class Version (bug fixed, debug codes removed) 1.3
# author: tomio kobayashi
# version 1.3
# published date: 2023/12/8

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
        
    def solve(inp):

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

#         inp = inp.replace("*"," and ").replace("+", " or ")
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

#         for i in range(len(winsets)):
#             winsets[i].append([i])
                
        
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
        # Processed Pattern
        # for c in sorted(winsets):
        #     print(', '.join(map(str, c)))
        print("")
        print("Suggested False Test Cases - " + str(len(losesets)))
        print("--------")
        
        for s in sorted(losesets):
            print(s)
        # Decided to merge with goodsets as they seem just as important
#         for s in sorted(goodsets):
#             print(s)
        # for c in sorted(losesets):
        #     print(', '.join(map(str, c)))

#         # This part is optional because of unlikely false negative cases as long as non-optional cases are tested
#         print("")
#         print("Suggested False Cases (optionally needed when some variables appear multiple times) - " + str(len(goodsets)))
#         print("--------")

#         for s in sorted(goodsets):
#             print(s)
#         # for c in sorted(goodsets):
#         #     print(', '.join(map(str, c)))

        print("")
#         print(len([r for r in res if r]))


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