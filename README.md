# Schematic-Unification
The code in this repository implements a unification procedure for Linear Primitive Schematic Unification (See https://arxiv.org/abs/2306.09152).  The implemented algorithm Non-linear Non-primitive schematic unification problems as input (though the bindings of the schematic substitutions cannot refer to each other). However, the algorithm  is only proven to work for linear primitive problems. The code requires the following libraries (for the full list see Requirements.txt):

	pyparsing 3.0.9 

	clingo 5.6.2

To run the test suite, use the following command:

	python Main.py Test

The output should be roughly as follows: 

	Test 1 Passed -- 0.008 Seconds
	Test 2 Passed -- 0.005 Seconds
	Test 3 Passed -- 0.04 Seconds
	Test 4 Passed -- 0.055 Seconds
	Test 5 Passed -- 1.215 Seconds
	Test 6 Passed -- 7.937 Seconds
	Test 7 Passed -- 0.007 Seconds
	Test 8 Passed -- 0.295 Seconds
	Test 9 Passed -- 0.272 Seconds
	Test 10 Passed -- 0.107 Seconds
	Test 11 Passed -- 0.079 Seconds
	Test 12 Passed -- 0.028 Seconds
	Test 13 Passed -- 0.094 Seconds
	Test 14 Passed -- 0.007 Seconds
	Test 15 Passed -- 0.039 Seconds
	Test 16 Passed -- 0.029 Seconds
	Test 17 Passed -- 0.022 Seconds
	Test 18 Passed -- 0.001 Seconds
	Test 19 Passed -- 0.016 Seconds
	Test 20 Passed -- 0.003 Seconds
	Test 21 Passed -- 0.002 Seconds
	Test 22 Passed -- 0.007 Seconds

Below is an example of how to run the code on one of the example files: 

	python Main.py Unif -f Examples/tests/test7.su --debug=2

this command results in the following output:

	Schematic Unification Problem:

	L_0 =?= f(Y[0],f(Y[1],Y[0]))

This is the problem as written in the input file

	Schematic Substitution:

		L_i <== f(f(X[i+1],f(Z[i],f(X[i+1],f(X[i],f(Z[i+1],X[i]))))),L_{i+1})

This is the schematic substitution based on what was presented in the input file.

	==========================================================

	Recursion Found 13 => 8 {X[8]=>X[3] , X[11]=>X[6] , Z[13]=>Z[8] , Z[10]=>Z[5] , X[10]=>X[5] , X[13]=>X[8] , L_13=>L_8 , Z[12]=>Z[7] , X[12]=>X[7] , Z[8]=>Z[3] , Z[11]=>Z[6]}

This is the cycle found during search together with the mapping from problem 13 to problem 8

	Subproblem 13:
		Z[10] =?= Z[8]
		X[11] =?= f(X[13],f(Z[12],f(X[13],f(X[12],f(Z[13],X[12])))))
		X[8] =?= X[10]
		Z[8] =?= Z[10]
		X[10] =?= X[8]
		L_13 =?= f(Z[10],f(X[11],f(X[10],f(Z[11],X[10]))))

	Subproblem 8:
		X[6] =?= f(X[8],f(Z[7],f(X[8],f(X[7],f(Z[8],X[7])))))
		X[3] =?= X[5]
		Z[5] =?= Z[3]
		L_8 =?= f(Z[5],f(X[6],f(X[5],f(Z[6],X[5]))))
		X[5] =?= X[3]
		Z[3] =?= Z[5]

These are the the problems which are equivalent. Below are all the bindings which 
did not end up in a subproblem (irrelevant bindings):

	Computed Bindings for subproblem 0:


	Computed Bindings for subproblem 1:
		Y[1] <= f(X[2],f(Z[1],f(X[2],f(X[1],f(Z[2],X[1])))))


	Computed Bindings for subproblem 2:
		Y[0] <= f(f(X[3],f(Z[2],f(X[3],f(X[2],f(Z[3],X[2]))))),L_3)


	Computed Bindings for subproblem 3:
		Z[0] <= f(X[4],f(Z[3],f(X[4],f(X[3],f(Z[4],X[3])))))


	Computed Bindings for subproblem 4:
		X[1] <= f(X[3],f(Z[2],f(X[3],f(X[2],f(Z[3],X[2])))))
		X[4] <= X[2]
		X[2] <= X[4]
		Z[4] <= Z[2]
		Z[2] <= Z[4]


	Computed Bindings for subproblem 5:


	Computed Bindings for subproblem 6:
		Z[1] <= f(X[7],f(Z[6],f(X[7],f(X[6],f(Z[7],X[6])))))


	Computed Bindings for subproblem 7:
		X[0] <= f(X[6],f(Z[5],f(X[6],f(X[5],f(Z[6],X[5])))))


	Computed Bindings for subproblem 8:
		Z[5] <= f(X[9],f(Z[8],f(X[9],f(X[8],f(Z[9],X[8])))))
		Z[3] <= Z[5]


	Computed Bindings for subproblem 9:
		Z[7] <= Z[9]
		Z[9] <= Z[7]
		X[6] <= f(X[10],f(Z[9],f(X[10],f(X[9],f(Z[10],X[9])))))
		X[7] <= X[9]
		X[9] <= X[7]


	Computed Bindings for subproblem 10:


	Computed Bindings for subproblem 11:
		Z[6] <= f(X[12],f(Z[11],f(X[12],f(X[11],f(Z[12],X[11])))))


	Computed Bindings for subproblem 12:
		X[3] <= f(f(X[13],f(Z[12],f(X[13],f(X[12],f(Z[13],X[12]))))),L_13)
		X[5] <= X[3]


The debug level can be set to a number between -1 and 6. Running without debug results in level 0 debugging:

	python Main.py Unif -f Examples/tests/test7.su 

The input file test7.su has the following form 

	## A linear Primitive example that unifies

	L_0 =?= f(Y[0],f(Y[1],Y[0]))

	L <== f(f(X[1],f(Z[0],f(X[1],f(X[0],f(Z[1],X[0]))))),L_1)

The first line is a comment. The next line is the linear primitive unification problem. The following line is the  
schematic substitution. Variable classes in the domain of the schematic substitution are written with _ and otherwise 
with []. For more complex examples test17.su

	## A linear Primitive example that unifies
	## Recursion has multiple self references

	L_0 =?=  h(h(Y[0],h(Y[1],Y[0])),h(h(R[0],R[1]),R[0]))

	L <== h(h(h(h(h(X[0],h(X[1],X[0])),h(h(R[2],R[3]),R[2])),h(h(W[0],W[1]),W[0])),L_1),h(L_1,h(Q[0],h(h(Y[2],h(Y[3],Y[2])),h(h(Z[0],Z[1]),Z[0])))))





   
