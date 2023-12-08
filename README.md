# DNF Test Creator

This tool automatically generates the test cases from a boolean expression (AND or OR without NOT) in the input string.  This uses the conditional probabiliy-based approach by ommiting neglectably unlikely cases where the chance of some tests pass is almost certain with only negligiable margin if a very small number of certain set of test cases have already passed due to the property of simplified DNF (connected by AND for each row).

Some Highlights
- The output size is O(n^2) (typically, O(n) < T(n) < O(2n)) to the number of variables n in the input, whereas the Cartesian product grows by O(2^n).  For example, with 11 input variables, the generated test cases are usually around 15, where as the Cartesian products grow to 2048.

- The very small number of test cases actually cover all the cartesion product patterns including below implementation mistakes
  - change of operators, like a & b & c, actually -> a & b | c, by mistake
  - omission of variables, like a & b & c, actually -> a & b | c, by mistake (mistaken additional variables cannot capture, but Cartesian product cases cannot cover them, so irrelavant)
  - replace with negation, like a & b & c, actually -> a & b * !c, by mistake
except for very unlikely patterns like this one, but it is negligiable because chance of such occurence seems to be much lower than defects that cannot be detected by Cartesian product test cases, like use of some variables that should not be used in the condition.
  - additional clause connected by OR that contains multiple negations, like a & b & c, actually -> a & b & b | a & !b & !c, by mistake
 
The high level algorithm follows as follows.

1. Convert the input to Simplified DNF form. (such as "(a & b) | (c & d)".  Expressions like "(a or (a and b)) is simplified to "a")

- {Input Expression} -> {DNF_Format(Input Expression)}

2. Generates the True cases from DNF_Format(Input Expression (each of conditions connected by OR).

- DNF_Format(Input Expression) -> PickoutTrueVariables(DNF_Format(Input Expression)) == {true cases}

3. Create False cases by extracting each of selement from each condition connected by OR)

- {true cases} -> Variable_Drop_One_At_a_Time({true cases}) == {false cases}


TIPS:

- Expressions like IF-ELSE can always be converted to AND and OR as long as the expected action is one.
- When there are multiple actions for each condition like IF A THEN DO 1 ELSE DO 2, then use IF-ELSE with different condition attached to each IF-ELSE branches.  The number of test cases grow only linearly by the number of conditions.  They only add up, but not multiply.
- For negations, use a separate variable.  For example, if there is a and !a, then use a and na as if they are different variables, for example.
