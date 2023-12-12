# DNF Test Creator

This tool automatically generates the test cases from a boolean expression (AND or OR without NOT) in the input string.  This uses the property of subsets of only AND that some input cases are guaranteed to be met if their subsets (for true cases) or supersets (for false cases) have been already met.  In this manner, only a handful cases happen to be needed to supercede the rest.

The tool was developed mainly to use in black box testing where the logic in the specification is used as input.  Nonetheless, this can be used in the white box testing or unit tests by developers.

The initial motive of creating this tool was my answer to those who expect testers to perform all-pattern tests, which use Cartesian product patterns in effect, and such an approach will be guaranteed to be surrendered by the testers because such all-pattern test case volume grows exponentially, and humans or regular automated test machines only prove to be useless against such sheer volume.  (Scientists and engineers have officially surrendered to deal with exponential growth items for ages, and instead tried to discover ways to work around NP or control the growth.)

Some Highlights
- The output size is O(n) to the number of variables n in the input, whereas the Cartesian product grows by O(2^n).  For example, with 11 input variables, the tool generates typically about 15, whereas the Cartesian products grow to 2048.

- The linearly grown handleful of test cases cover realistically sufficient patterns including below implementation mistakes
  - change of operators, like a & b & c, actually -> a & b | c, by mistake
  - omission of variables, like a & b & c, actually -> a & b | c, by mistake (mistaken additional variables cannot capture, but Cartesian product cases cannot cover them, so irrelavant)
  - replace with negation, like a & b & c, actually -> a & b * !c, by mistake
- except for very rare erroneous patterns like adding certain negative conditions that cause true to false, like a & b & c, actually -> a & b & c & !d by mistake
    
- Converting a bool expression into DNF is a known NP problem, so the run time of generation grows exponentially to the number of variables.  The Python standard SymPy library to_dnf() got stuck when the variables are above 10 in my enviroment.  I use my own algorithm instead, and it takes about 1 min for 13 varaiables.  It is much faster than SymPy, but sill it becomes quite heavy at 13 or 14 variables (which can be a pain but nothing compared to the test effort which can takes days, weeks or months for large, yet off-the-point, set of test cases)  
 
The high level algorithm follows as follows.

1. Convert the input to Simplified DNF form. (such as "(a & b) | (c & d)".  Expressions like "(a or (a and b)) is simplified to "a")

- {Input Expression} -> {Simplified_DNF(Input Expression)}

2. Generates the true cases from Simplified_DNF(Input Expression) where each condition is connected by OR).

- Simplified_DNF(Input Expression) -> Converted_To_Row_Set(DNF_Format(Input Expression)) == {true cases}

3. Create False cases by extracting each of selement from each condition connected by OR)

- {true cases} -> Variable_Droppped_One_At_a_Time({true cases}) == {false cases}


TIPS:

- Only & or * (as AND), | and + (as OR) can be used as bool operators.
- The tab delimited text at the bottom of the output text can be used to be pasted on Excel to create test cases.  It saves quite an effort and copying mistakes than typing based on outputs.
- Expressions like IF-ELSE can always be converted to AND and OR as long as the expected action is one.
- When there are multiple actions for each condition like IF A THEN DO 1 ELSE DO 2, then use IF-ELSE with different condition attached to each IF-ELSE branches.  The number of test cases grow only linearly by the number of conditions.  They only add up, but not multiply.
- For negations, use a separate variable.  For example, if there is a and !a, then use a and na as if they are different variables, for example.
- Don't use the malignant test patterns usually.  They are only needed to find hidden unexpected negation implementation errors in the usual setting.  Instead, focus on other types of tests like calculation or variations within conditions.  However, after all the basic sets have been tested, they are useful to find malignant bugs.  Those detection indicates the implementation has some quality issue as it probably indicates the variable scopes are not well defined or controled.
- THE TOOL CAN BE USED TO TEST YOUR BOOLEAN EXPRESSIONS AS WELL, NOT TO MENTION.


HOW TO RUN:

You can copy the Pythothon script on your favorite Jupyter-like notebook, or run the script from the command line. (I often use Kaggle due to laziness and convenience)

inp = "(a*b)+(a*b*c)"

DNF_Test_Creater.solve(inp)

NOTE:
  The latest version added negation levels for both true and false cases.  It is known that the basic test cases can be beat with using negations.  For example, for (a, b, c), "1 1 0" == False cannot lead to "1 0 0" == False if (a, b, !c) condition is used either by mistake, or maliciously.  It comes the notion of nth true/false orders.  Order indicates how much apart (number of variables difference) from the basic set, which are the true cases and the false cases made by flipping one of the variables in each true case.  The parameters allow to generate the test cases based on the number of orders expected.  But the number of such test cases will increase exponentially to the number of orders.


 -----------------------


# DNF Regression Solver

This script does the inversion of the above.  The above one goes DNF -> datasets, and this one goes datasets -> DNF.  It finds the bool expression from the input data like Linear Regression finds coefficients of covectors.  It does not use either linear regression or decision tree logic, though.  Instead, it looks for DNF by matching the true and false identitity records, which is the essence used in DNF Test Creator as well.  The runtime has degraded from linear to non-linear since 1.4 upgrade to accomodate realistic data that do not contain Cartesian product of variable values.


HOW TO RUN:

file_path = '/kaggle/input/tomio5/dnf_regression.txt'

DNF_Regression_solver.solve(file_path)

The input file is a tab-delimited text file where the fields are conditions indicated by 1 or 0, and the last field (or column) indicates the result as sampled below.  Also, a sample file dnf_regression.txt is in the repository.

a	b	c	d	e	f	g	Res

1	1	1	1	1	1	1	1

1	1	1	1	1	1	0	1

1	1	1	1	1	0	1	1

