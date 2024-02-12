# For Reviewers
Implementation of the algorithm is now complete with 34 test examples in Example/tests

# Schematic-Unification
The code in this repository implements the unification procedure for Uniform Schematic Unification problems presented in https://arxiv.org/abs/2306.09152. While the implementation works for Simple Schematic Unification Problems, the algorithm is not guarenteed to terminate for such problems. The code requires the following libraries (for the full list see Requirements.txt):

	pyparsing 3.0.9 

	clingo 5.6.2

To run the test suite, use the following command:

	python Main.py Test

The output should be roughly as follows: 

	Test 1 Passed -- 0.015 Seconds
	Test 2 Passed -- 0.011 Seconds
	Test 3 Passed -- 0.101 Seconds
	Test 4 Passed -- 0.095 Seconds
	Test 5 Passed -- 2.751 Seconds
	Test 6 Passed -- 17.715 Seconds
	Test 7 Passed -- 0.018 Seconds
	Test 8 Passed -- 0.454 Seconds
	Test 9 Passed -- 0.51 Seconds
	Test 10 Passed -- 0.199 Seconds
	Test 11 Passed -- 0.12 Seconds
	Test 12 Passed -- 0.083 Seconds
	Test 13 Passed -- 0.215 Seconds
	Test 14 Passed -- 0.022 Seconds
	Test 15 Passed -- 0.116 Seconds
	Test 16 Passed -- 0.042 Seconds
	Test 17 Passed -- 0.011 Seconds
	Test 18 Passed -- 0.001 Seconds
	Test 19 Passed -- 0.019 Seconds
	Test 20 Passed -- 0.003 Seconds
	Test 21 Passed -- 0.001 Seconds
	Test 22 Passed -- 0.003 Seconds
	Test 23 Passed -- 30.677 Seconds
	Test 24 Passed -- 0.007 Seconds
	Test 25 Passed -- 0.002 Seconds
	Test 26 Passed -- 0.032 Seconds
	Test 27 Passed -- 0.356 Seconds
	Test 28 Passed -- 0.162 Seconds
	Test 29 Passed -- 0.077 Seconds
	Test 30 Passed -- 1.227 Seconds
	Test 31 Passed -- 0.025 Seconds
	Test 32 Passed -- 0.006 Seconds
	Test 33 Passed -- 0.014 Seconds
	Following test takes over 300 seconds
 	Test 34 Passed -- 385.923 Seconds


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

For a more complex example see test33.su which is as follows:
	## A Non-linear Uniform example that unifies

	f(X[4],L_0) =?= f(f(f(W[0],f(R_3,W[4])),R_0),f(S_0,f(W[1],W[2])))

	R <== f(f(W[0],W[4]),R_7)
	S <== f(f(E[0],f(E[3],E[2])),S_4)
	L <== f(f(X[0],f(Z[1],f(X[0],f(X[1],f(Z[0],X[1]))))),L_1)

Note that this example is Uniform, but not primitive. Thus, we need to transform it into a primitive problem before attempting to unify. Running the following command

	python Main.py Unif -f Examples/tests/test33.su --debug 1

results in the following output

	Schematic substitution is Uniform but Non-Primitive.
	Mapping used to transform Schematic substitution:
		 {W[4] ==> WRD[4],E[3] ==> ESC[3],E[2] ==> ESB[2]}
	Schematic Unification Problem:
	
		f(X[4],L_0) =?= f(f(f(W[0],f(R_3,WRD[4])),R_0),f(S_0,f(W[1],W[2])))
	
	
	Schematic Substitution:

		R_i <== f(f(W[i],WRD[i+4]),R_{i+1})
		S_i <== f(f(E[i],f(ESC[i+3],ESB[i+2])),S_{i+1})
		L_i <== f(f(X[i],f(Z[i+1],f(X[i],f(X[i+1],f(Z[i],X[i+1]))))),L_{i+1})

	==========================================================

		 unifiable --- 0.015 seconds ---

In the directory Examples/simple one finds examples that go beyond the algorithm presented in the above-mentioned paper, simple schematic unification problems. Running the following 
command 

 	python Main.py Unif -f Examples/simple/test35.su --debug 3

results in the following prompt:

 	The input schematic substitution is non-uniform. The algorithm is designed for uniform schematic substitutions only. 
  	Using a non-uniform schematic subsitutions may lead to non-stability. To continue type OK and Press Enter.


If one types OK the unification process continues and resulting in the following output:

	Schematic Unification Problem:

		L_0 =?= h(Y[0],h(Y[1],Y[0]))


	Schematic Substitution:

		L_i <== h(h(L_{i+4},h(X[i+1],X[i])),L_{i+1})

	==========================================================

	Problem 1:
		L_1 =?= h(Y[1],Y[0])
		Y[0] =?= h(L_4,h(X[1],X[0]))

	==========================================================

	Problem 2:
		Y[0] =?= h(h(h(L_8,h(X[5],X[4])),L_5),h(X[1],X[0]))
		L_2 =?= h(h(h(L_8,h(X[5],X[4])),L_5),h(X[1],X[0]))
		Y[0] =?= L_2

	==========================================================

	Problem 3:
		L_3 =?= h(X[1],X[0])
		L_6 =?= h(h(h(L_12,h(X[9],X[8])),L_9),h(X[5],X[4]))
		X[3] =?= h(L_9,h(X[6],X[5]))
		X[2] =?= L_6

	==========================================================

	Problem 4:
		L_10 =?= h(h(h(L_16,h(X[13],X[12])),L_13),h(X[9],X[8]))
		X[6] =?= L_10
		L_7 =?= h(X[5],X[4])
		X[7] =?= h(L_13,h(X[10],X[9]))

	==========================================================

	Recursion Found 5 => 3 {X[10]=>X[2] , X[11]=>X[3] , X[13]=>X[5] , X[8]=>X[0] , X[14]=>X[6] , X[9]=>X[1] , X[12]=>X[4] , L_14=>L_6 , L_16=>L_8 , L_11=>L_3 , L_17=>L_9}

	Subproblem 5:
		X[11] =?= h(L_17,h(X[14],X[13]))
		L_14 =?= h(h(h(L_20,h(X[17],X[16])),L_17),h(X[13],X[12]))
		X[10] =?= L_14
		L_11 =?= h(X[9],X[8])

	Subproblem 3:
		L_3 =?= h(X[1],X[0])
		L_6 =?= h(h(h(L_12,h(X[9],X[8])),L_9),h(X[5],X[4]))
		X[3] =?= h(L_9,h(X[6],X[5]))
		X[2] =?= L_6


	Computed Bindings for subproblem 0:


	Computed Bindings for subproblem 1:
		Y[1] <= h(L_5,h(X[2],X[1]))


	Computed Bindings for subproblem 2:
		Y[0] <= h(h(L_6,h(X[3],X[2])),L_3)


	Computed Bindings for subproblem 3:
		X[1] <= h(L_7,h(X[4],X[3]))
		X[2] <= h(h(L_10,h(X[7],X[6])),L_7)
		X[0] <= L_4
		X[3] <= h(h(h(L_13,h(X[10],X[9])),L_10),h(X[6],X[5]))


	Computed Bindings for subproblem 4:
		X[6] <= h(h(L_14,h(X[11],X[10])),L_11)
		X[5] <= h(L_11,h(X[8],X[7]))
		X[4] <= L_8
		X[7] <= h(h(h(L_17,h(X[14],X[13])),L_14),h(X[10],X[9]))


The following simple schematic unification problem violates stability. Running the following 
command 

 	python Main.py Unif -f Examples/simple/test36.su --debug 1

results in the following output

	The input schematic substitution is non-uniform. The algorithm is designed for uniform schematic substitutions only. Using a non-uniform schematic subsitutions may lead to non-stability. To continue type OK and Press Enter.		
	ok
	Schematic Unification Problem:

		L_0 =?= h(Y[0],h(Y[1],Y[0]))


	Schematic Substitution:

		L_i <== h(h(X[i],h(L_{i+4},X[i])),L_{i+1})

	==========================================================

	Problem not stable (stab Bound:5, current:8):
	 	{
		X[8] =?= h(X[10],h(L_14,X[10]))
	,
		X[4] =?= L_8
	,
		X[7] =?= L_10
	,
		L_8 =?= h(L_9,X[5])
	,
		L_5 =?= h(L_6,X[2])
	,
		L_11 =?= h(X[9],h(L_13,X[9]))
	,
		L_8 =?= h(X[6],h(L_10,X[6]))
	,
		X[2] =?= h(X[4],h(L_8,X[4]))
	,
		X[7] =?= h(X[8],h(L_12,X[8]))
	,
		L_11 =?= h(L_12,X[8])
	,
		X[4] =?= h(X[6],h(L_10,X[6]))
	,
		X[5] =?= h(X[7],h(L_11,X[7]))
	}
	Do you wish to continue and update the stability point? To continue type OK and Press Enter.

We are prompted again when stability fails. If we type ok, a cycle will be detected. 
   
