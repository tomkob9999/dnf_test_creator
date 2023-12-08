# dnf_test_creator

This tool automatically generates the test cases from a boolean expression (AND or OR without NOT) in the input string.

Some Highlights
- The output size is O(n^2) to the number of variables (typically less than 2n) in the input whereas the Cartesian product grows by O(2^n).

- The very small number of test cases actually cover all the cartesion product patterns including below implementation mistakes
  - change of operators, like a & b & c, actually -> a & b | c, by mistake
  - omission of variables, like a & b & c, actually -> a & b | c, by mistake (mistaken additional variables cannot capture, but Cartesian product cases cannot cover them, so irrelavant)
  - replace with negation, like a & b & c, actually -> a & b * !c, by mistake
except for very unlikely patterns like this one, but it is negligiable because chance of such occurence seems to be much lower than defects that cannot be detected by Cartesian product test cases, like use of some variables that should not be used in the condition.
  - additional clause connected by OR that contains multiple negations, like a & b & c, actually -> a & b & b | a & !b & !c, by mistake
 
The high level algorithm follows overall as follows.

1. Convert the input to Simplified DNF form. (such as "(a & b) | (c & d)".  Expressions like "(a or (a and b)) is simplified to "a")

{Input Expression} -> DNF_Format(Input Expression)
3. Generates the True cases from DNF_Format(Input Expression (each of conditions connected by OR).

DNF_Format(Input Expression) -> True cases
4. Create False cases by extracting each of selement from each condition connected by OR)

True cases -> One_Variable_Dropped(True cases) = False Cases
