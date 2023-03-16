# Schematic-Unification
The code requires pyparsing 3.0.9. To run the test suite use the following command

python main.py Test

The output should be 

Test 1 (should be unifiable)
	 unifiable
Test 2 (should be unifiable)
	 unifiable
Test 3 (should be unifiable)
	 unifiable
Test 4 (should be not unifiable)
	 not unifiable
Test 5 (should be not unifiable)
	 not unifiable
Test 6 (should be not unifiable)
	 not unifiable
Test 7 (should be unifiable)
	 unifiable
Test 8 (should be unifiable)
	 unifiable
Test 9 (should be not unifiable)
	 not unifiable
Test 10 (should be not unifiable)
	 not unifiable
Test 11 (should be unifiable)
	 unifiable

Below is an example of how to run the code on one of the example files: 

python Main.py Examples/test7.su debug 2

this command results in the following output:

Loop Unification Problem:
	f(f(X1,f(Z0,f(X1,f(X0,f(Z1,X0))))),L_1) =?= f(Y0,f(Y1,Y0))


Interpreted Class definitions:

	R_0 <== f(Y0,f(Y1,Y0))
	L_0 <== f(f(X1,f(Z0,f(X1,f(X0,f(Z1,X0))))),L_0)

==========================================================
Recursion Found 7 => 2 :
	(*7, f(X6,f(Z3,f(X6,f(X3,f(Z6,X3)))))) => (*2, f(X1,f(Z0,f(X1,f(X0,f(Z1,X0))))))
	(*7, L_7) => (*2, L_2)

Computed Bindings:
	Y0 <= *2
	Y1 <= f(X2,f(Z1,f(X2,f(X1,f(Z2,X1)))))
	*0 <= f(Y0,*1)
	*1 <= f(Y1,Y0)
	*2 <= f(X1,*3)
	*3 <= f(Z0,*4)
	*4 <= f(X1,*5)
	*5 <= f(X0,*6)
	*6 <= f(Z1,X0)
	X1 <= f(X3,f(Z2,f(X3,f(X2,f(Z3,X2)))))
	X5 <= X3
	X4 <= X2
	X0 <= *7
	Z0 <= f(X2,f(Z3,f(X2,f(X3,f(Z2,X3)))))
	Z5 <= Z3
	Z4 <= Z2
	Z1 <= f(X7,f(Z6,f(X7,f(X6,f(Z7,X6)))))

	 unifiable


The debug level can be set to a number between 0 and 3. Running without debug results in level 0 debug

python Main.py Examples/test7.su

The input files have the following form 

L_0 =?= R_0
R <== f(Y[0],f(Y[1],Y[0]))
L <== f(f(X[1],f(Z[0],f(X[1],f(X[0],f(Z[1],X[0]))))),L_0)

where the first line is the unification problem and the following lines are the 
interpretations of variables classes. The interpreted classes are writtin with _ and
the free classes with []. It is assumed that all interpreted classes are given an 
interpretation. Only one unification problem per file. 
