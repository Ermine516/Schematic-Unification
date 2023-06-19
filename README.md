# Schematic-Unification
The code in this repository implements a unification procedure for Simple Linear Loops (See https://arxiv.org/abs/2306.09152). The procedure implemented is not the same procedure discussed in the paper, but rather a variant of the Martelli-Montanari unification algorithm. The implemented algorithm can take Simple Loops or even loops with nested arithmetic progressive terms as input, but is only proven to work on Simple Linear Loops. The code requires pyparsing 3.0.9. 


To run the test suite, use the following command:

	python main.py Test

Below is an example of how to run the code on one of the example files: 

	python Main.py Amm Examples/test7.su --debug=2

this command results in the following output:

	Loop Unification Problem:
		f(f(X1,f(Z0,f(X1,f(X0,f(Z1,X0))))),L_1) =?= f(Y0,f(Y1,Y0))


	Interpreted Class definitions:

		L_0 <== f(f(X1,f(Z0,f(X1,f(X0,f(Z1,X0))))),L_1)

	==========================================================
	Recursion Found 7 => 2 :
		(*7, L_7) => (*2, L_2)
		(*7, f(X6,f(Z3,f(X6,f(X3,f(Z6,X3)))))) => (*2, f(X1,f(Z0,f(X1,f(X0,f(Z1,X0))))))


	Computed Bindings for subproblem 6:
		*6 <= f(Z1,X0)
		X0 <= *7
		Z1 <= f(X7,f(Z6,f(X7,f(X6,f(Z7,X6)))))


	Computed Bindings for subproblem 5:
		X0 <= f(X6,f(Z3,f(X6,f(X3,f(Z6,X3)))))
		*5 <= f(X0,*6)


	Computed Bindings for subproblem 4:
		X1 <= f(X3,f(Z2,f(X3,f(X2,f(Z3,X2)))))
		X4 <= X2
		X5 <= X3
		Z5 <= Z3
		Z4 <= Z2
		*4 <= f(X1,*5)


	Computed Bindings for subproblem 3:
		X1 <= f(X3,f(Z2,f(X3,f(X2,f(Z3,X2)))))
		*3 <= f(Z0,*4)
		Z0 <= f(X2,f(Z3,f(X2,f(X3,f(Z2,X3)))))


	Computed Bindings for subproblem 2:
		X1 <= f(X3,f(Z2,f(X3,f(X2,f(Z3,X2)))))
		*2 <= f(X1,*3)


	Computed Bindings for subproblem 1:
		*1 <= f(Y1,Y0)
		Y1 <= f(X2,f(Z1,f(X2,f(X1,f(Z2,X1)))))
		Y0 <= *2


	Computed Bindings for subproblem 0:
		*0 <= f(Y0,*1)
		Y0 <= f(X1,f(Z0,f(X1,f(X0,f(Z1,X0)))))


	 unifiable


The debug level can be set to a number between 0 and 3. Running without debug results in level 0 debugging:

	python Main.py Amm Examples/tests/test7.su 

The input file test7.su has the following form 

	## This example is unifiable and is handled by the
	## augmented martelli-montanari procedure
	L_0 =?= f(Y[0],f(Y[1],Y[0]))

	L <== f(f(X[1],f(Z[0],f(X[1],f(X[0],f(Z[1],X[0]))))),L_1)

The first two lines are comments. The next line is the loop unification problem. The following lines are the 
interpretations of variable classes. The interpreted classes are written with _ and
the free classes with []. It is assumed that all interpreted classes are given an 
interpretation. Only one unification problem per file. For a more complex file, see Ex1_unif.su

	f(f(S_0,f(K_0,f(S_0,f(L_5,f(M_0,L_5))))),f(f(W_4,f(M_0,f(W_4,f(S_0,f(Q_4,S_0))))),L_0)) =?= f(L_0,f(N_0,L_0))
	L <== f(f(L_10,f(Q_4,f(L_10,f(W_4,f(K_5,W_4))))),f(f(W_4,f(K_5,f(W_4,f(L_10,f(Q_4,L_10))))),f(f(L_10,f(Q_4,f(L_10,f(W_4,f(K_5,W_4))))),f(f(S_5,f(K_5,f(S_5,f(L_10,f(M_5,L_10))))),f(f(X[7],f(M_5,f(X[7],f(S_5,f(Z[7],S_5))))),L_5)))))
	W <== X[4]
	Q <== Z[4]
	S <== f(L_10,f(Q_4,f(L_10,f(W_4,f(K_5,W_4)))))
	K <== f(W_4,f(K_5,f(W_4,f(L_10,f(Q_4,L_10)))))
	M <== f(X[7],f(M_5,f(X[7],f(S_5,f(Z[7],S_5)))))
	N <== f(W_4,f(M_0,f(W_4,f(S_0,f(Q_4,S_0)))))

One can also run the following command:

	python Main.py Build Examples/tests/test1.su --debug=1 --unroll=3

This results in a partial application of the interpretation to the input terms:

	Loop Unification Problem:
		h(h(X0,h(X1,X0)),h(h(X1,h(X2,X1)),h(h(X2,h(X3,X2)),L_3))) =?= h(Y0,h(Y1,Y0))


	Interpreted Class definitions:

		L_0 <== h(h(X0,h(X1,X0)),L_1)

	==========================================================
		 unifiable

   # Experimental Feature

Using the command **--unifier**, the procedure computes a new interpretation and the appropriate bindings that make the initial terms equivalent. 
This approach works for simple examples, but it is not known if it generalizes. Below are some working examples

	python Main.py Amm Examples/tests/test1.su --debug 1 --unifier
 
 output:
	Loop Unification Problem:
		
  		h(h(X0,h(X1,X0)),L_1) =?= h(Y0,h(Y1,Y0))

	Interpreted Class definitions:

		L_0 <== h(h(X0,h(X1,X0)),L_1)

	==========================================================
	==========================================================
	Unifier Terms:

		h(h(X0,h(X1,X0)),h(h(X1,h(X2,X1)),L_0))
		h(Y0,h(Y1,Y0))

	Unifier Interpreted Class definitions:

		L_0 <== h(h(X2,h(X3,X2)),h(h(X3,h(X4,X3)),L_2))
		IA_0 <== h(X3,h(X4,X3))
		IB_0 <== L_2

	Unifier Bindings (triangular form):

		X1 <== IA_0
		X3 <== IA_2
		X0 <== IB_0
		X2 <== IB_2
		Y1 <== h(X1,h(X2,X1))
		Y0 <== L_0


   
