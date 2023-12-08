
        print("")
        print("DNF with perfect match - " + str(len(dnf_perf)))
        print("--------")
        # Raw Pattern
        for s in sorted(dnf_perf):
            print(s)
        # Processed Pattern
        # for c in sorted(winsets):
        #     print(', '.join(map(str, c)))
        print("")
        print("DNF with good match - " + str(len(dnf_good)))
        print("--------")
        for s in sorted(dnf_good):
            print(s)


file_path = '/kaggle/input/tomio5/dnf_regression.txt'
DNF_Regression_solver.solve(file_path)