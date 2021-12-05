# -*- coding: utf-8 -*-
"""8Queens-CQM.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1X_4kAEchuiB2ueUdBBDctdHPgYmd1dx_

# 8 Queens Problem - Solving using DWave Constrained Quadratic Model
###### By Mario Guzzi

## Problem

Problem: On a standard 8 X 8 chess board, place 8 queens, anywhere on the board, such that no two queens are in conflict with each other (i.e. no queen can take any other queen using standard chess movement rules for a Queen piece).

If you have not tried to solve this problem manually on a chess board, you will find that it is a difficult problem to solve. 

## CQM vs BQM

This solution was originally created as a BQM (Binary Quadratic Model) as a QUBO. The CQM model abstracts solving the quadratic mathematics required to implement constraints in a QUBO by allowing us to express constraints more naturally with the quadratic equations implemented under the hood.

The code and efforts required to implement a solver using CQM is minimum and demonstrated below compared to creating it as a QUBO.

## Model

8 X 8 binary variables are defined. Each variable is associated to one of the squares on the board. Each indicate if its suqare is occupied (=1) or not (=0) by a Queen chess piece.

## Constraints: Letting the Quantum Computer solve the problem

The constraints tell the DWave quantum annealer what is valid and not valid without hinting as to how to solve the problem. 

(e.g. Although we "know" that solving the problem means that you can only put one queen on any row, we will allow the computer to consider 0 as a possibility and let it figure out the solution).

>1 - There must be exactly NQ (=8 by default) queens on the board.
>> The sum of all the binary variables must be == NQ

>2 - No two queens can occupy the same row on the board
>> The sum of all binary variables in any given row must be <= 1

>3 - No two queens can occupy the same column on the board
>> The sum of all binary variables in any given column must be <= 1

>4 - No two queens can occupy the same diagonal on the board
>> The sum of all binary variables in any given diagonal must be <= 1

## Variations

Two parameters can be changed:

NQ = Number of Queens

N = Number of squares on a side of the square board

One can increase the problem to placing 32 queens on a 32 x 32 board. Some variations may lead to "No feasible" solutions. 

We challenge one to find a real life solution to a problem setup for which the quantum computer fails at finding a solution.

## Usage

First assign your Leap API token below and run the notebook. The first time you run the notebook, the Ocean SDK will get installed in the VM.

Results are presented at the end in the form of a board. Up to 10 variations are presented.
"""

token=None

import dimod
from dwave.system import LeapHybridCQMSampler
import numpy as np

# Create a CQM to solve the 8 Queens Problem

NQ = 8                    # Number of Queens to place: Objective
N = 8                     # Number of squares across and down on the board
time_limit = 5            # Hybrid Sampler Time Limit
problabel = "NQueensCQM"  # Label for the leap dashboard

# Define a blank cqm model

cqm = dimod.CQM()

# Function to reate a Variable name for a given square position on the chess board

def varname( r=1, c=1 ):
  return "square_r"+str(r)+"_c"+str(c)

# Lists of variable numbers and their label

vlabels = [varname(r,c) for r in range(N) for c in range(N)]
vnum = np.array([[ r*N+c for c in range(N)] for r in range(N)])
rvnum = vnum[:, ::-1]

# Create board of binary variables for the CQM model

variables = [ dimod.Binary(varname(r,c)) for r in range(N) for c in range(N)]
board = { (r,c) : variables[r*N+c] for c in range(N) for r in range(N) }

# Create lists of variables on all diagonals of more than 1 square

diags = []
for a in [vnum,rvnum]:
  for k in range(-(N-2),N-1):
    diags.append(np.diag(a,k=k).tolist())
    #print( np.diag(vnum,k=k))

# Model verification

verify = False
if ( verify == True ):
  print("Diagonals:", diags)
  print("Variable Labels:",vlabels)
  print("Regular board Variable numbers:\n", vnum)
  print("Reverse board variable numbers:\n", rvnum)
  print("CQM Variables assigned to the board:\n",board)

# Objective : There is no objective function 
#             Although one may consider placing NQ queens on the board to be the objective, 
#             we preferred to implement it as a constraint instead

# Constraints 

# 1 - Must have 8 queens on board

cqm.add_constraint( sum(board[r,c] for r in range(N) for c in range(N)) == NQ, label="board_total" )

# 2 - Each column can have at most one queen

for c in range(N):
  cqm.add_constraint( sum( board[r,c] for r in range(N) ) <= 1, label=f"col_{c}_total" )

# 3 - Each row can have at most one queen

for r in range(N):
  cqm.add_constraint( sum( board[r,c] for c in range(N) ) <= 1, label=f"row_{r}_total" )

# 4 - Each diagonal can have at most one queen

for i,d in enumerate(diags):
  cqm.add_constraint( sum( variables[v] for v in d ) <= 1, label=f"diag_{i}_total" )

# Call the solver and obtain results
sampler = LeapHybridCQMSampler(token=token)
raw_sampleset = sampler.sample_cqm(cqm, time_limit=time_limit,label=problabel)

feasible_sampleset = raw_sampleset.filter(lambda d: d.is_feasible)
num_feasible = len(feasible_sampleset)

print(str(num_feasible)+" Feasible samples")
if num_feasible > 0:
    best_samples = \
        feasible_sampleset.truncate(min(10, num_feasible))
else:
    print("Warning: Did not find feasible solution")
    best_samples = raw_sampleset.truncate(10)

print(" \n" + "=" * 30 + "BEST SAMPLE SET" + "=" * 30)
print(best_samples)

#for s in best_samples:
#  print(s)

for i,s in enumerate(best_samples):
  print("Result "+str(i+1)+"    =====================")
  for r in range(N):
    for c in range(N):
      v = s[varname(r,c)]
      q = '.'
      if ( v > 0.0 ): q = 'W'
      print( '|.'+ q + '.', end='' )     
    print( '|')
  print("=================================")

