### Name: Deterministic_Regressor
# Author: tomio kobayashi
# Version: 3.1.3
# Date: 2024/01/27

import itertools
from sympy.logic import boolalg
import numpy as np

import sklearn.datasets
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix
from sklearn.model_selection import train_test_split
import pandas as pd
import random
from sympy import simplify
import copy
from collections import Counter

class Deterministic_Regressor:
# This version has no good matches
# Instead, all true matches are first added, and some are removed when 
# false unmatch exists and there is no corresponding other rule
    def __init__(self):
        self.expression_true = ""
        self.expression_false = ""
        self.true_confidence = {}
        self.false_confidence = {}
        self.all_confidence = {}
        
        self.tokens = []
        self.dic_segments = {}
        
        self.last_solve_expression = ""
        
        self.expression_opt = ""
        self.by_two = -1
        self.opt_f1 = 0.001
        
        self.children = []
        
        self.whole_rows = []
        self.test_rows = []
        self.train_rows = []
        self.classDic = {}
        self.classDicRev = {}
        self.item_counts = {}

    def remove_supersets(sets_list):
        result = []
        for s in sets_list:
            if not any(s != existing_set and s.issuperset(existing_set) for existing_set in sets_list):
                result.append(s)
        return result


    def cnf_to_dnf_str(str):
        ss = str.split("&")
        ss = [a.strip()[1:-1] if a.strip()[0] == "(" else a for a in ss]
        cnf = [[b.strip() for b in sa.strip().split("|")] for sa in ss]

        dnf = []
        for clause in cnf:
            dnf_clause = []
            for literal in clause:
                dnf_clause.append(literal)
            dnf.append(dnf_clause)
        dnfl = [list(x) for x in itertools.product(*dnf)]
        dnfl = [set(d) for d in dnfl]
        filtered_sets = Deterministic_Regressor.remove_supersets(dnfl)
        filtered_lists = [sorted(list(f)) for f in filtered_sets]
        filtered_lists = set([" & ".join(f) for f in filtered_lists])
        str = "(" + ") | (".join(sorted(filtered_lists)) + ")"
        return str
    
    
    def simplify_dnf(s, use_cnf=False, withSort=False):
        tok1 = "|"
        tok2 = "&"
        if use_cnf:
            tok1 = "&"
            tok2 = "|"
        if s.strip() == "":
            return ""
        ss = s.split(tok1)
        ss = [s.strip() for s in ss]
        ss = [s[1:-1] if s[0] == "(" else s for s in ss]
        ss = [s.split(tok2) for s in ss]
        ss = [[sss.strip() for sss in s] for s in ss]
        ss = [set(s) for s in ss]

        filtered_sets = Deterministic_Regressor.remove_supersets(ss)
        filtered_lists = [sorted(list(f)) for f in filtered_sets]
        filtered_lists = [(" " + tok2 + " ").join(f) for f in sorted(filtered_lists)] if withSort else [(" " + tok2 + " ").join(f) for f in filtered_lists]
        str = "(" + (") " + tok1 + " (").join(filtered_lists) + ")"
        return str

    def try_convert_to_numeric(text):
        if isinstance(text, str):
            if "." in text:
                try:
                    return float(text)
                except ValueError:
                    pass
            else:
                try:
                    return int(text)
                except ValueError:
                    pass
        return text

    def convTuple2bin(t, width):
        i = 1
        ret = 0
        for x in t:
            ii = i << width - x - 1
            ret = ret | ii
        return ret
    
    def myeval(__ccc___, __tokens___, ______s____):
        for __jjjj___ in range(len(__tokens___)):
            exec(__tokens___[__jjjj___] + " = " + str(__ccc___[__jjjj___]))
        return eval(______s____)
            
    def solve(self, inp_p, confidence_thresh=0, power_level=None, useUnion=False):
        
        inp = [[Deterministic_Regressor.try_convert_to_numeric(inp_p[i][j]) for j in range(len(inp_p[i]))] for i in range(len(inp_p))]
        
        
        max_power = 64
        
        all_confidence_thresh = 0
        if power_level is not None:
            if power_level > max_power or power_level < 0:
                print("power_level must be between 0 and 32")
                return

            if len(self.all_confidence) == 0:
                    all_confidence_thresh = 0  
            else:
                max_freq = max([v for k, v in self.all_confidence.items()])
                print("max_freq", max_freq)
                min_freq = min([v for k, v in self.all_confidence.items()])
                this_power = int(power_level/max_power * (max_freq-min_freq) + 0.9999999999)

                if max_freq - this_power < 0:
                    all_confidence_thresh = 0
                else:
                    all_confidence_thresh = max_freq - this_power

        else:
            all_confidence_thresh = confidence_thresh
        print("Confidence Thresh:", all_confidence_thresh)
        print("Input Records:", len(inp)-1)
        
        numvars = len(inp[0])

        tokens = inp[0]
        inp_list = [row for row in inp[1:]]
        
        res = list(range(len(inp_list)))
        expr = ""
        
        true_exp = self.expression_true
        false_exp = self.expression_false
        active_true_clauses = 0
        active_false_clauses = 0
        if all_confidence_thresh > 0:
            true_list = []
            for s in true_exp.split("|"):
                s = s.strip()
                if s in self.true_confidence:
                    if self.true_confidence[s] >= all_confidence_thresh:
                        true_list.append(s)
                        active_true_clauses += 1
            true_exp = " | ".join(true_list)
            
            false_list = []
            for s in false_exp.split("|"):
                s = s.strip()
                if s in self.false_confidence:
                    if self.false_confidence[s] >= all_confidence_thresh:
                        false_list.append(s)
                        active_false_clauses += 1
            false_exp = " | ".join(false_list)
        else:
            active_true_clauses = len(true_exp.split("|"))
            active_false_clauses = len(false_exp.split("|"))

        connector = " | " if useUnion else " & "

        if true_exp != "":
            expr = "(" + true_exp + ")"
        if true_exp != "" and false_exp != "":
            expr = expr + connector
        if false_exp != "":
            expr = expr + "not (" + false_exp + ")"
            
        print(str(active_true_clauses) + " true clauses activated")
        print(str(active_false_clauses) + " false clauses activated")
            
        expr = expr.replace(" & ", " and ").replace(" | ", " or ")
        print("Solver Expression:")
        
        print(self.replaceSegName(expr))
        
        self.last_solve_expression = expr

        if len(expr) == 0:
            print("No expression found")
            return []
        
        for i in range(len(inp_list)):
            res[i] = Deterministic_Regressor.myeval(inp_list[i], tokens, expr)
            
        if res is None:
            return []
        
        return [1 if r or r == 1 else 0 for r in res]
    
        
    def solve_direct(self, inp_p, expression):
        
        expression = expression.replace(" | ", " or ").replace(" & ", " and ")
        self.last_solve_expression = expression
           
        inp = copy.deepcopy(inp_p)
        inp = [[Deterministic_Regressor.try_convert_to_numeric(inp[i][j]) for j in range(len(inp[i]))] for i in range(len(inp))]

        numvars = len(inp[0])
        
        tokens = inp[0]
        inp_list = [row for row in inp[1:]]
        
        res = list(range(len(inp_list)))
        
        for i in range(len(inp_list)):
            res[i] = Deterministic_Regressor.myeval(inp_list[i], tokens, expression)
        return res
    
            
    def solve_with_opt(self, inp_p):
        if self.expression_opt == "":
            return [0] * (len(inp_p)-1)
        else:
            return self.solve_direct(inp_p, self.expression_opt)
    
    def replaceSegName(self, str):
        s = str
        for t in self.tokens:
            if t in s and t in self.dic_segments:
                s = s.replace(t, self.dic_segments[t])
        return s
            
            
    def generate_segment_ranks(self, df, num_segments, name, silent=False):

        df[name + '_rank'] = pd.cut(df[name], bins=num_segments, labels=False)
        df[name + '_label'] = pd.cut(df[name], bins=num_segments, labels=[f'{name} {i+1}' for i in range(num_segments)])
        min_max_per_group = df.groupby(name + '_rank')[name].agg(['max'])
        
        max_list = min_max_per_group.values.tolist()
        prev_max_str = ""
        ranks = sorted(df[name + '_rank'].unique().tolist())
        for i in range(len(max_list)):
            if i == 0:
                self.dic_segments[name + "_" + str(ranks[i])] = name + " <= " + str(max_list[i][0])
                prev_max_str = str(max_list[i][0])
            elif i == len(max_list) - 1:
                self.dic_segments[name + "_" + str(ranks[i])] = prev_max_str + " < " + name
            else:
                self.dic_segments[name + "_" + str(ranks[i])] = prev_max_str + " < " + name + " <= " + str(max_list[i][0])
                prev_max_str = str(max_list[i][0])
            
            
        if not silent:
            print("")
            print(min_max_per_group)
        
        return df

    def discretize_data(self, data_list, by_two=2, silent=False):

        result_header = data_list[0][-1]
        result_values = [d[-1] for d in data_list[1:]]
        
        headers = data_list[0][:-1]
        values = [d[:-1] for d in data_list[1:]]
        data = pd.DataFrame(values, columns=headers) 

        
        cols = [c for c in data.columns]
        for c in cols:
            countNonBool = len(data[c]) - (data[c] == 0).sum() - (data[c] == 1).sum()
            if countNonBool > 0 and pd.api.types.is_numeric_dtype(data[c]):
                result_df = self.generate_segment_ranks(data, by_two*2, c, silent=silent)
                one_hot_df = pd.get_dummies(result_df[c + '_rank'], prefix=c)
                one_hot_df = one_hot_df.astype(int)
                data = pd.concat([result_df, one_hot_df], axis=1)
        cols = [c for c in data.columns]
        new_cols = []
        for c in cols:
            countNonBool = len(data[c]) - (data[c] == 0).sum() - (data[c] == 1).sum()
            if countNonBool == 0 and pd.api.types.is_numeric_dtype(data[c]):
                new_cols.append(c)
        
        data = data.filter(items=new_cols)

        data_list = [data.columns.tolist()] + data.values.tolist()

        
        data_list[0].append(result_header)
        for i in range(len(result_values)):
            data_list[i+1].append(result_values[i])
        
        return data_list

    def reduce_rows_except_first(matrix, percentage):
        if not (0 <= percentage <= 100):
            raise ValueError("Percentage must be between 0 and 100")

        # Ensure the first row is always included
        num_rows_to_keep = max(1, int(len(matrix) * (1 - percentage / 100)))

        # Sample remaining rows
        sampled_rows = [matrix[0]] + random.sample(matrix[1:], num_rows_to_keep - 1)

#         return sampled_rows
        return copy.deepcopy(sampled_rows)


    
    def clean_and_discretize(self, inp, by_two):
        inp = copy.deepcopy(inp)
        inp = [[Deterministic_Regressor.try_convert_to_numeric(inp[i][j]) for j in range(len(inp[i]))] for i in range(len(inp))]
        matrix = self.discretize_data(inp, by_two)
        head = matrix[0]
        return [head] + [[int(mm) for mm in m] for m in matrix[1:]]
        
    def train(self, file_path=None, data_list=None, max_dnf_len=4, error_tolerance=0.00, min_match=0.00, use_approx_dnf=False, redundant_thresh=1.00, useExpanded=True):

        # file_path: input file in tab-delimited text
        # data_list: list matrix data with header in the first row and the result in the last col
        # max_dnf_len: max length of AND clauses in output DNF.  
        #       Increasing this one is heavey especially if check_negative is True

        # Example usage:
        # file_path = '/kaggle/input/dnf-regression/dnf_regression.txt'
        # file_path = '/kaggle/input/tomio5/dnf_regression.txt'
        
        inp = None
        if file_path is not None:
            with open(file_path, 'r') as f:
                inp = [line.strip().split('\t') for line in f]
        else:
            inp = data_list
        
        print("Train Records:", len(inp)-1)
    
        inp = [[Deterministic_Regressor.try_convert_to_numeric(inp[i][j]) for j in range(len(inp[i]))] for i in range(len(inp))]

        for r in inp[1:]:
            for c in r:
                if c != 1 and c != 0:
                    print("The data contents needs to be 1 or 0", c)
                    return []
        
        imp_before_row_reduction = copy.deepcopy(inp)
        
        numvars = len(inp[1])-1

        print("Columns:")
        print(inp[0])
        self.tokens = copy.deepcopy(inp[0])
        print("")
        
        print("Uni-valued Columns:")
        numrows = len(inp)-1
        redundant_cols = set()
        for i in range(len(inp[0])-1):
#             if i in redundant_cols:
#                 continue
            vals = [row[i] for row in inp[1:]]
            cnts = Counter(vals)
#             print("vals", vals)
#             print("cnts", cnts)
            if len(cnts) == 1:
                redundant_cols.add(i)
                print(self.tokens[i])
        print("")
        
        print("Redundant Pairs:")
        for i in range(len(inp[0])-1):
            for j in range(i+1, len(inp[0])-1):
                if j in redundant_cols:
                    break
                sames = len([1 for k in range(1, len(inp), 1) if inp[k][i] == inp[k][j]])
                if sames/numrows >= redundant_thresh:
                    print(self.tokens[j], "->",self.tokens[i])
                    redundant_cols.add(j)
        print("")
        

        
        if max_dnf_len > numvars - 1:
            max_dnf_len = numvars - 1

                
        MAX_REPS = 1500000
        
        print("Deriving expressions...")
        dnf_perf = list()
        raw_perf = list()
        raw_perf2 = list()
        dnf_perf_n = list()
        raw_perf_n = list()
        raw_perf2_n = list()

        patterns = [(1, 1), (0, 1), (1, 0), (0, 0)] if useExpanded else [(1, 1), (0, 0)]
        for pattern in patterns:
            dat_t = []
            if pattern[0] == 1:
                dat_t = [row[:-1] for row in inp[1:]]
            else:
                dat_t = [[0 if m == 1 else 1 for m in row[:-1]] for row in inp[1:]]
            res_t = []
            if pattern[1] == 1:
                res_t = [row[-1] for row in inp[1:]]
            else:
                res_t = [0 if row[-1] == 1 else 1 for row in inp[1:]]
                         
            inp_t = [copy.deepcopy(inp[0])] + [dat_t[i] + [res_t[i]] for i in range(len(dat_t))]
            dic_t = dict()
            for i in range(1, len(inp_t), 1):
                s = ""
                for j in range(len(inp_t[i]) - 1):
                    s += str(int(inp_t[i][j]))
                truefalse = inp_t[i][len(inp_t[i]) - 1]
                dic_t[int(s, 2)] = truefalse

                
            for s in range(max_dnf_len):
                len_dnf = s + 1

                l = [ii for ii in range(numvars)]
                p_list = list(itertools.combinations(l, len_dnf))

                p_list = [p for p in p_list if not any([pp in redundant_cols for pp in p])]

                print(str(len_dnf) + " variable patterns")
                if len(p_list) > MAX_REPS:
                    print("Skipping because " + str(len(p_list)) + " combinations is too many")
                    break
                true_test_pass = True
                for i in range(len(p_list)):
                    match_and_break = False
                    b = Deterministic_Regressor.convTuple2bin(p_list[i], numvars)
                    if pattern[1] == 1:
                        for p in raw_perf2:
                            if p == b & p:
                                match_and_break = True
                                break
                    else:
                        for p in raw_perf2_n:
                            if p == b & p:
                                match_and_break = True
                                break
                    if match_and_break:
                        continue
                    r = [v for k,v in dic_t.items() if k & b == b]
                    if len(r) == 0:
                        continue
                    cnt_all = len([f for f in r])
                    cnt_unmatch = len([f for f in r if f == 0])
                    if cnt_unmatch/cnt_all > error_tolerance:
                        continue
                    if (cnt_all - cnt_unmatch)/numrows < min_match:
                        continue

                    if pattern[1] == 1:
                        raw_perf.append([ii for ii in p_list[i]])
                        raw_perf2.append(b)

                        if pattern[0] == 1:
                            key = "(" + " & ".join(sorted(list(set([inp[0][ii] for ii in p_list[i]])))) + ")"
                            dnf_perf.append(sorted(list(set([inp[0][ii] for ii in p_list[i]]))))
                        else:
                            key = "(not (" + ") & not (".join(sorted(list(set([inp[0][ii] for ii in p_list[i]])))) + "))" 
                            dnf_perf.append(sorted(list(set(["not (" + inp[0][ii] + ")" for ii in p_list[i]]))))
                        self.true_confidence[key] = cnt_all - cnt_unmatch
                        
                    else:
                        raw_perf_n.append([ii for ii in p_list[i]])
                        raw_perf2_n.append(b)  
                        if pattern[0] == 1:
                            key = "(" + " & ".join(sorted(list(set([inp[0][ii] for ii in p_list[i]])))) + ")"
                            dnf_perf_n.append(sorted(list(set([inp[0][ii] for ii in p_list[i]]))))
                        else:
                            key = "(not (" + ") & not (".join(sorted(list(set([inp[0][ii] for ii in p_list[i]])))) + "))" 
                            dnf_perf_n.append(sorted(list(set(["not (" + inp[0][ii] + ")" for ii in p_list[i]]))))
                        self.false_confidence[key] = cnt_all - cnt_unmatch

        
        self.all_confidence = copy.deepcopy(self.true_confidence)
        self.all_confidence.update(self.false_confidence)

#         print("size of false dnf " + str(len(dnf_perf_n)))
        
        set_dnf_true = set(["(" + s + ")" for s in [" & ".join(a) for a in dnf_perf]])
        set_cnf_false = set(["(" + s + ")" for s in [" & ".join(a) for a in dnf_perf_n]])

        self.expression_true = " | ".join(set_dnf_true)
        self.expression_true = Deterministic_Regressor.simplify_dnf(self.expression_true)
        self.expression_false = " | ".join(set_cnf_false)
        self.expression_false = Deterministic_Regressor.simplify_dnf(self.expression_false)
        

            
        print("")
        print("TRUE DNF - " + str(len(set_dnf_true)))
        print("--------------------------------")

        if len(set_dnf_true) > 0:
            print(self.replaceSegName(self.expression_true))
            
        print("")
        print("FALSE DNF - " + str(len(set_cnf_false)))
        print("--------------------------------")
        if len(set_cnf_false) > 0:
            print(self.replaceSegName(self.expression_false))
            
        perm_vars = list(set([xx for x in dnf_perf for xx in x] + [xx for x in dnf_perf_n for xx in x]))
        
        not_picked = [self.replaceSegName(inp[0][ii]) for ii in range(len(inp[0])-1) if inp[0][ii] not in perm_vars]

        print("")
        print("Unsolved variables - " + str(len(not_picked)) + "/" + str(len(inp[0])-1))
        print("--------------------------------")
        print(not_picked)
        print("")
        
        return imp_before_row_reduction


    def optimize_params(self, test_data, answer, elements_count_penalty=1.0, useUnion=False):
        
        inp = test_data
        best_ee_sofar = -1
        ct_now = 0

        MAX_POWER_LEVEL = 64
        jump = int(MAX_POWER_LEVEL/2)
        ct_opt = 0
        expr_opt = ""
        opt_precision_sofar = 0
        opt_recall_sofar = 0
        opt_f1_sofar = 0
        opt_match_rate_sofar = 0
        
        doexit = False
        for i in range(100):
            print("")
            print("")
            print("##### Power Level", ct_now, "######")
        
            best_ee = 0
            win_expr = ""
            opt_precision = 0
            opt_recall = 0
            opt_f1 = 0
            opt_match_rate = 0
            res = self.solve(inp, power_level=ct_now, useUnion=useUnion)

            if len(res) == 0:
                print("#################################")
                print("")
                print("SORRY NO SOLUTION FOUND")
                print(str(sum([1 if answer[i] == res[i] else 0 for i in range(len(answer))])) + "/" + str(len(res)), " records matched")
                print("")
                print("#################################")
                print("")
                return None, None
            else:

                win_expr = self.last_solve_expression
                num_match = sum([1 if answer[i] == res[i] else 0 for i in range(len(answer))])
                print(str(num_match) + "/" + str(len(res)), " records matched " + f" ({num_match/len(res)*100:.2f}%)")        
                precision = precision_score(answer, res)
                recall = recall_score(answer, res)
                f1 = f1_score(answer, res)
                print(f"Precision: {precision * 100:.2f}%")
                print(f"Recall: {recall * 100:.2f}%")
                print(f"F1 Score: {f1 * 100:.2f}%")
                ee = (f1 +min(precision,recall))/2-(len(self.last_solve_expression.split("&"))+len(self.last_solve_expression.split("|")))/3000*elements_count_penalty
                ee = 0 if ee < 0 else ee
                print(f"Effectiveness & Efficiency Score: {ee * 100:.3f}%")
                best_ee = ee
                opt_precision = precision
                opt_recall = recall
                opt_f1 = f1
                opt_match_rate = num_match/len(res)
                if best_ee_sofar < best_ee:
                    ct_opt = ct_now
                    best_ee_sofar = best_ee
                    ct_now = ct_now + jump
                    expr_opt = win_expr
                    opt_precision_sofar = opt_precision
                    opt_recall_sofar = opt_recall
                    opt_f1_sofar = opt_f1
                    opt_match_rate_sofar = opt_match_rate
                    if ct_now > MAX_POWER_LEVEL or f1 == 1:
                        doexit = True
                elif jump == 1 or expr_opt == win_expr:
                    doexit = True
                elif ct_now == 0:
                    print("#################################")
                    print("")
                    print("SORRY NO SOLUTION FOUND")
                    print(str(sum([1 if answer[i] == res[i] else 0 for i in range(len(answer))])) + "/" + str(len(res)), " records matched")
                    print("")
                    print("#################################")
                    print("")
                    return None, None
                else:
                    jump = int(jump/2)
                    ct_now = ct_now - jump
                
            if doexit:
                print("")
                print("#################################")
                print("")
                print("OPTIMUM POWER LEVEL is", ct_opt)
                print("")
                print(f"Precision: {opt_precision_sofar * 100:.2f}%")
                print(f"Recall: {opt_recall_sofar * 100:.2f}%")
                print(f"F1 Score: {opt_f1_sofar * 100:.2f}%")
                print(f"Effectiveness & Efficiency Score: {best_ee_sofar * 100:.3f}%")
                print("Expression:")
                print(self.replaceSegName(expr_opt))
                print("")
                print("#################################")
                print("")
        
                self.expression_opt = expr_opt
                self.opt_f1 = f1
                
                return ct_opt

    def optimize_compact(self, test_data, answer, cnt_out=20, useUnion=False):

        inp = test_data
        
        print("Analysis started")
        false_clauses = sorted([(v, k) for k, v in self.false_confidence.items()], reverse=True)
        true_clauses = sorted([(v, k) for k, v in self.true_confidence.items()], reverse=True)
        
        
        all_clauses = sorted([(v, k) for k, v in self.all_confidence.items()], reverse=True)
        
        final_expr = ""
        best_ee = -1
        
        true_exps = []
        false_exps = []
#         print("len(all_clauses)", len(all_clauses))
#         print("len(true_clauses)", len(true_clauses))
#         print("len(false_clauses)", len(false_clauses))
        if len(all_clauses) > 0:
            
            cnt = 0
            for i in range(1, len(all_clauses), 1):
                cnt = cnt + 1
                if cnt_out < cnt:
                    break
                    
                if i % 10 == 0:
                    print(str(i) + "/" + str(len(all_clauses)) + " completed" )

                expr = ""
                temp_true_exps = copy.deepcopy(true_exps)
                temp_false_exps = copy.deepcopy(false_exps)
                true_added = True
                if all_clauses[i][1] in self.true_confidence:
                    temp_true_exps.append(all_clauses[i][1])
                else:
                    true_added = False
                    temp_false_exps.append(all_clauses[i][1])
                    
                true_expression = "(" + " | ".join(temp_true_exps) + ")"
                false_expression = "not (" + " | ".join(temp_false_exps) + ")"
            
                connector = " | " if useUnion else " & "
        
                if len(temp_true_exps) > 0:
                    expr = true_expression 
                if len(temp_true_exps) > 0 and len(temp_false_exps) > 0:
                    expr = expr + connector
                if len(temp_false_exps) > 0:
                    expr = expr + false_expression
                    
                expr = expr.replace(" & ", " and ").replace(" | ", " or ")
                res = self.solve_direct(inp, expr)
                precision = precision_score(answer, res)
                recall = recall_score(answer, res)
                f1 = f1_score(answer, res)
                ee = (f1 + min(precision,recall))/2
                ee = 0 if ee < 0 else ee
                if best_ee < ee:
#                     if true_added:
#                         print("true clause added")
#                     else:
#                         print("false clause added")
                    best_ee = ee

                    final_expr = expr
                
                    true_exps = temp_true_exps
                    false_exps = temp_false_exps
                
                    cnt = 0
        else:
            print("#################################")
            print("")
            print("SORRY NO SOLUTION FOUND")
            print("")
            print("#################################")
            print("")
            return

        if final_expr != "":
            
            print("Assessment of the optimal solution")
            res = self.solve_direct(inp, final_expr)

            if len(res) > 0:
                print("")
                print("#### DERIVED OPTIMUM EXPRESSION ####")
                print("")
                precision = precision_score(answer, res)
                recall = recall_score(answer, res)
                f1 = f1_score(answer, res)
                print(str(sum([1 if answer[i] == res[i] else 0 for i in range(len(answer))])) + "/" + str(len(res)), " records matched " + f" ({sum([1 if answer[i] == res[i] else 0 for i in range(len(answer))])/len(res)*100:.2f}%)")
                print(f"Precision: {precision * 100:.2f}%")
                print(f"Recall: {recall * 100:.2f}%")
                print(f"F1 Score: {f1 * 100:.2f}%")

                self.opt_f1 = f1
                
                print(self.replaceSegName(final_expr))
                
                print("")
                
                self.expression_opt = final_expr
                
                return final_expr
            
            
    def random_split_matrix(matrix, divide_by=2):
        matrix = copy.deepcopy(matrix)
        rows = list(matrix)  # Convert to list for easier shuffling
        random.shuffle(rows)  # Shuffle rows in-place
        split_index = len(rows) // divide_by  # Integer division for equal or near-equal halves
        return rows[:split_index], rows[split_index:]

    def train_and_optimize(self, data_list=None, max_dnf_len=4, error_tolerance=0.00, 
                       min_match=0.00, use_approx_dnf=False, redundant_thresh=1.00, elements_count_penalty=1.0, 
                           use_compact_opt=False, cnt_out=20, useUnion=False, useExpanded=True):
        
        print("Training started...")
        
        headers = data_list[0]
        data_list2 = data_list[1:]
        
        train_data, valid_data = Deterministic_Regressor.random_split_matrix(data_list2)

        train_inp = [headers] + train_data
        
        self.train(data_list=train_inp, max_dnf_len=max_dnf_len, 
                        error_tolerance=error_tolerance, min_match=min_match, use_approx_dnf=use_approx_dnf, redundant_thresh=redundant_thresh, useExpanded=useExpanded)

        print("Optimization started...")
        inp = [headers] + valid_data
           
        inp = [[Deterministic_Regressor.try_convert_to_numeric(inp[i][j]) for j in range(len(inp[i]))] for i in range(len(inp))]
                
        answer = [int(inp[i][-1]) for i in range(1, len(inp), 1)]
        inp = [row[:-1] for row in inp]
             
        if use_compact_opt:
            return self.optimize_compact(inp, answer, cnt_out=cnt_out, useUnion=useUnion)
        else:
            return self.optimize_params(inp, answer, elements_count_penalty=1.0, useUnion=useUnion)
    
    def train_and_optimize_bulk(self, data_list, expected_answers, max_dnf_len=4, error_tolerance=0.02,  
                   min_match=0.03, use_approx_dnf=False, redundant_thresh=1.00, elements_count_penalty=1.0, use_compact_opt=False, cnt_out=20, useUnion=False, useExpanded=True):

        self.children = [Deterministic_Regressor() for _ in range(len(expected_answers))]
        
        cnt_recs = len(expected_answers[0])

        for i in range(len(self.children)):
            if self.classDic is not None and len(self.classDic) > 0:
                print("")
                print("=====================================================================================")
                print("Start training class", self.classDic[i], "(" + str(self.item_counts[self.classDic[i]]) + "/"+ str(cnt_recs) + ")")
                print("")
            else:
                print("Child", i)
            
            self.children[i].dic_segments = copy.deepcopy(self.dic_segments)
            d_list = copy.deepcopy(data_list)
            d_list[0].append("res")
            
            for k in range(len(d_list)-1):
                d_list[k+1].append(expected_answers[i][k])
            self.children[i].train_and_optimize(data_list=d_list, max_dnf_len=max_dnf_len, error_tolerance=error_tolerance, 
                    min_match=min_match, use_approx_dnf=use_approx_dnf, redundant_thresh=redundant_thresh, 
                                                elements_count_penalty=elements_count_penalty, use_compact_opt=use_compact_opt, cnt_out=cnt_out, useUnion=useUnion, useExpanded=useExpanded)

            
            
    def solve_with_opt_bulk(self, inp_p):
        res = []
        for c in self.children:
            r = c.solve_with_opt(inp_p)
            if r == None or len(r) == 0:
                r == [0] * (len(inp_p)-1)
            res.append(r)
            
        return res
    
    def solve_with_opt_class(self, inp_p):
        
        res = self.solve_with_opt_bulk(inp_p)
        
        dic_f1 = {i: self.children[i].opt_f1 for i in range(len(self.children))}
        
        len_rows = len(res[0])
        len_res = len(res)
        new_res = [0] * len_rows
        for i in range(len_rows):
            numbers = [s[1] for s in sorted([(random.random()*dic_f1[i], i) for i in range(len_res)], reverse=True)]
            for k in range(len(numbers)):
                if res[numbers[k]][i] == 1:
                    new_res[i] = self.classDic[numbers[k]]
                    break
                if k == len(numbers) - 1:
                    new_res[i] = self.classDic[numbers[k]]
                    

        return new_res
    
    def train_and_optimize_class(self, data_list, expected_answers, max_dnf_len=4, error_tolerance=0.00, 
               min_match=0.00, use_approx_dnf=False, redundant_thresh=1.00, elements_count_penalty=1.0, use_compact_opt=False, cnt_out=20, useUnion=False, useExpanded=True):

        # Use Counter to perform group-by count
        cnt_recs = len(expected_answers)
        self.item_counts = Counter(expected_answers)
        classList = sorted([item for item, count in self.item_counts.items()])
        classList = [(i, classList[i]) for i in range(len(classList))]
        self.classDic = {c[0]: c[1] for c in classList}
        self.classDicRev = {c[1]: c[0] for c in classList}
        answers = [[0 for _ in range(len(expected_answers))] for _ in range(len(classList))]
        for i in range(len(answers[0])):
            answers[self.classDicRev[expected_answers[i]]][i] = 1

        self.train_and_optimize_bulk(data_list=data_list, expected_answers=answers, max_dnf_len=max_dnf_len, error_tolerance=error_tolerance, 
                    min_match=min_match, use_approx_dnf=use_approx_dnf, redundant_thresh=redundant_thresh, 
                                     elements_count_penalty=elements_count_penalty, use_compact_opt=use_compact_opt, cnt_out=cnt_out, useUnion=useUnion, useExpanded=useExpanded)
    
    def prepropcess(self, whole_rows, by_two, splitter=3):
        self.whole_rows = self.clean_and_discretize(whole_rows, by_two)
        headers = self.whole_rows
        data = self.whole_rows[1:]
        random.shuffle(data)  # Shuffle rows in-place
        split_index = len(data) // splitter  # Integer division for equal or near-equal halves
        self.test_rows = data[:split_index]
        self.train_rows = data[split_index:]
    
    def get_train_dat_wo_head(self):
        return [row[:-1] for row in self.train_rows]
    def get_train_res_wo_head(self):
        return [row[-1] for row in self.train_rows]
    def get_train_dat_with_head(self):
        return [self.whole_rows[0][:-1]] + [row[:-1] for row in self.train_rows]
    def get_train_datres_wo_head(self):
        return self.train_rows
    def get_train_datres_with_head(self):
        return [self.whole_rows[0]] + self.train_rows
    
    def get_test_dat_wo_head(self):
        return [row[:-1] for row in self.test_rows]
    def get_test_res_wo_head(self):
        return [row[-1] for row in self.test_rows]
    def get_test_dat_with_head(self):
        return [self.whole_rows[0][:-1]] + [row[:-1] for row in self.test_rows]
    def get_test_datres_wo_head(self):
        return self.test_rows[1:]
    def get_test_datres_with_head(self):
        return [self.whole_rows[0]] + self.test_rows
    

    def show_stats(predicted, actual, average="weighted", elements_count_penalty=1.0):
        
        if len(predicted) != len(actual):
            print("The row number does not match")
            return
        answer = actual
        res = predicted
        precision = precision_score(answer, res, average=average, labels=np.unique(res))
        recall = recall_score(answer, res, average=average, labels=np.unique(res))
        f1 = f1_score(answer, res, average=average, labels=np.unique(res))
        print("")
        print("####### PREDICTION STATS #######")
        print("")
        print(str(sum([1 if answer[i] == res[i] else 0 for i in range(len(answer))])) + "/" + str(len(res)), " records matched" + f" ({sum([1 if answer[i] == res[i] else 0 for i in range(len(answer))])/len(res)*100:.2f}%)")
        print(f"Precision: {precision * 100:.2f}%")
        print(f"Recall: {recall * 100:.2f}%")
        print(f"F1 Score: {f1 * 100:.2f}%")
        print("")
        print("##############")
        print("")
