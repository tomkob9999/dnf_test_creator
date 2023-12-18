# author: tomio kobayashi
# version 2.0.5
# published date: 2023/12/19

import re
import copy

class DNF_Test_Creater:

    #     This needs to be separate function because the condition 
    #     variables cannot have conflict with function variables.  Thus "__XXX__" format is used to prevent naming conflicts.    
    def myeval(__ccc___, __tokens___, __inp___):
            for __jjjj___ in range(len(__tokens___)):
                exec(__tokens___[__jjjj___] + " = " + str(__ccc___[__jjjj___]))
            return eval(__inp___ + " >= 1")

    def convList2bin(t, width):
#         [1, 3] -> 0b0101
        i = 1
        ret = 0
        for iii in range(len(t)):
            if t[iii] == 1:
                ii = i << width - iii - 1
                ret = ret | ii
        return ret


    def convList2bin2(t, width):
#         ["0", "1", "0", "1"] -> 0b0101
        return int("".join(t), 2)
        

    def convBin2Pos(x, width):
#         "0101" --> [1, 3]
        return sorted([i for i in range(width) if x & (1 << width - i - 1)])

    def convBin2Pos0(x, width):
#         "0101" --> [0, 2]
        return sorted([i for i in range(width) if x & (1 << width - i - 1) == 0])
    
    def offbit(inp, off, width):
#         b1111, 2 --> b1101 
        return inp ^ (1 << width - off - 1)

    def convBin2List2(x, width):
#         b1010 -> ["1", "0", "1", "0"]
        return ["1" if x & (1 << width - i - 1) else "0" for i in range(width)]

    def solve(inp, rank_depth=0, evil_neg_lvl=0):

        tokens = re.split('[*+]', inp.replace("&", "*").replace("|", "+").replace(" ","").replace(')', '').replace('(', ''))
        
        # variables that appear more than once
        dups = set()
        ss = sorted(tokens)
        for i in range(len(ss)-1):
            if ss[i] == ss[i+1] and ss[i] not in dups:
                dups.add(ss[i])
        
        tokens = list(dict.fromkeys(tokens))
        patterns = [2 for t in tokens]
        clist2 = []
        numvars = len(tokens)
        wincl= []
    
        trueghost = {}
        for i in range(rank_depth):
            trueghost[i] = set()
        res = [0] * 2**numvars

        fullbin = 2**numvars - 1
        for i in range(2**numvars):
            l = DNF_Test_Creater.convBin2List2(i, numvars)
            clist2.append(i)
            res[i] = DNF_Test_Creater.myeval(l, tokens, inp)

            wins = []
            for j in range(len(tokens)):
                if l[j]:
                    wins.append(tokens[j])

            if res[i]:
                wincl.append(i)
                
        dicres = dict([(clist2[i], res[i]) for i in range(len(clist2))])
        dicrank = dict([(clist2[i], 99) for i in range(len(clist2))])
        dicTup = dict([(clist2[i], DNF_Test_Creater.convBin2List2(clist2[i], numvars)) for i in range(len(clist2))])

        winwin = list()
#         create Rank 0 positive sets (DNF)
        for w in sorted([(len(DNF_Test_Creater.convBin2Pos(w, numvars)), w) for w in wincl]):
            found = False
            for ww in winwin:
                if w[1] & ww == ww:
                    found = True
            if not found:
                winwin.append(w[1])
                
        for s in winwin:
            dicrank[s] = 0
#         create Rank 0 negative sets
        for k in [k for k, v in dicrank.items() if v == 0]:
            pospos = DNF_Test_Creater.convBin2Pos(k, numvars)
            for p in pospos:
                dicrank[DNF_Test_Creater.offbit(k, p, numvars)] = 0
            
        trueghost_all = set()

#         add one change to the previous rank
        for i in range(rank_depth):
            for k in [k for k, v in dicrank.items() if v == i]:
                tup = dicTup[k]
                for j in range(len(tup)):
                    tup2 = copy.deepcopy(tup)
                    tup2[j] = "1" if tup2[j] == "0" else "0"
                    offb = DNF_Test_Creater.convList2bin2(tup2, numvars)
                    if dicrank[offb] > i + 1:
                        dicrank[offb] = i + 1

        listrank = sorted([[k, v] for k, v in dicrank.items()], reverse=True)

        print("")
        print("Full-Combination Test Dataset - " + str(len(clist2)))
        print(" including true cases - " + str(len([r for r in res if r])))
        print("=========")


        lenall = 0
        for n in range(rank_depth+1):
            ml = sorted([f for f in listrank if f[1] == n and dicres[f[0]]], reverse=True)
            print("RANK - " + str(n))
            print("-------------------------")
            print("Suggested True Test Dataset - " + str(len(ml)))
            lenall += len(ml)
            print("--------")
            # Raw Pattern
            for f in ml:
                print([tokens[t] for t in DNF_Test_Creater.convBin2Pos(f[0], numvars)])
            print("")
            ml2 = sorted([f for f in listrank if f[1] == n and not dicres[f[0]]], reverse=True)
            print("Suggested False Test Dataset - " + str(len(ml2)))
            lenall += len(ml2)
            print("--------")
            for f in ml2:
                print([tokens[t] for t in DNF_Test_Creater.convBin2Pos(f[0], numvars)])
            print("")

        print("")
        print("Tab Delimited Results - " + str(lenall))
        print("--------")
        
        ss = ""
        for t in tokens:
            ss += t + "\t"
        ss += "Result\tRank"
        print(ss)

        for n in range(rank_depth+1):
            # Raw Pattern
            for f in [f for f in listrank if f[1] == n and dicres[f[0]]]:
                print("\t".join(DNF_Test_Creater.convBin2List2(f[0], numvars)) + "\t" + ("1" if dicres[f[0]] else "0") + "\t" + str(dicrank[f[0]]))
            for f in [f for f in listrank if f[1] == n and not dicres[f[0]]]:
                print("\t".join(DNF_Test_Creater.convBin2List2(f[0], numvars)) + "\t" + ("1" if dicres[f[0]] else "0") + "\t" + str(dicrank[f[0]]))



inp = "(a & (b | ((g | k) & i)) & c) | (d & (e | (h & j) & f))" # 15/2048 (11)


DNF_Test_Creater.solve(inp, 0)