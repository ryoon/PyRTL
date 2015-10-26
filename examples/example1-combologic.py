""" Example 1:  A simple combination logic block example.

    This example declares a block of hardware with three one-bit inputs,
    (a,b,c) and two one-bit outputs (sum, cout).  The logic declared is a
    simple one-bit adder and the definition uses some of the most common
    parts of PyRTL. The adder is then simulated on random data, the
    wave form is printed to the screen, and the resulting trace is
    compared to a "correct" addition.  If the result is correct then a 0
    is returned, else 1.
"""

import random
import pyrtl

# The basic idea of PyRTL is to specify the component of a some hardware block
# through the declaration of wires and operations on those wires.  The current
# working block, an instance of a class devilishly named "Block", is implicit
# in all of the below code -- it is easiest to start with the way wires work.

# --- Step 1: Define Logic -------------------------------------------------

# One of the most fundamental types in PyRTL is the "WireVector" which is acts
# very much like a python list of 1-bit wires.  Unlike a normal list though the
# number of bits is explicitly declared.
temp_x = pyrtl.WireVector(bitwidth=1, name='temp_x')

# Both arguments are in fact optional and default to having the bitwidth be
# inferred and a unique name generated by pyrtl starting with 'tmp'
temp_y = pyrtl.WireVector()


# Two special types of WireVectors are Input and Output, which are used to specify
# an interface to the hardware block.
a, b, c = pyrtl.Input(1, 'a'), pyrtl.Input(1, 'b'), pyrtl.Input(1, 'c')
sum, carry_out = pyrtl.Output(name='sum'), pyrtl.Output(1, 'carry_out')


# Okay, let's build a one-bit adder.

# First we will assemble the carry out bit. It can all be done in one line,
# but let's break that down a bit to see what is really happening.  What if
# we want to do things to the partial signals in the middle of the
# computation.  When you take "a & b" in PyRTL what that really means is
# "make an AND gate, connect one input to 'a' and the other to 'b' and return
# the result of the gate".  The result of that AND gate and other gates and
# function is also a WireVector, and can be used in any way a WireVector,
# can be used, such as be assigned to a python variable or used in another
# equation

temp1 = a & b  # temp1 IS the result of b & c (this is the first mention of temp1)
assert(isinstance(temp1, pyrtl.WireVector))

# note that logic operations, as well as most PyRTL functions return wirevectors
# as outputs which can be used without connecting them to another wire

# We can similarly make the rest of the carry out logic
temp2 = a & c
temp2_copy = temp2
temp2 = temp2 | (b & c)

# Notice here that temp2 is treated as a variable in the software sense.
# When it is assigned to, it replaces the wire that was previously in
# it's location (software folks should be familiar with this). Therefore,
# the new temp2 and the old temp2 are two different wires.
assert(temp2 is not temp2_copy)

# Sometimes, we will need to connect the result of an operation to a
# pre-allocated wirevector. One of the places we need this is when we are
# connecting circuit outputs, as we get normal WireVectors--and not Output
# WireVectors--out of a logic op. To connect the wires, we need to use the
# connect operator, which is '<<='.  This takes an already declared wire
# and "links" it to some other already declared wire.  Let's start with
# the cout bit, which is of course just the or of the two
carry_out <<= temp1 | temp2

# We could've have also created carry_out in one step. The carry_out
# bit would just have been "carry_out <<= a & b | a & c | b & c" instead

# Now lets build the sum bit
sum_copy = sum
sum <<= a ^ b ^ c

# Note that when a wire is connected to another wire, it still is the
# original wire (unlike the assignment operator we saw earlier)
assert(sum is sum_copy)

# Also, note that even though we had left out the bitwidth for sum
# when we declared it, PyRTL was able to infer that it is 1
assert (sum.bitwidth == 1)

# We can also connect normal WireVectors in the same fashion, though
# this is usually unnecessary
temp_x <<= a & b
temp_y <<= temp_x

# Now before we go onto the simulation, lets look at our handiwork. In PyRTL,
# there's an block object that stores everything in the circuit. You can access
# the working (aka current) block through pyrtl.working_block(), and for most
# things one block is all you will need.  We'll see it again later in more detail,
# but for now we can just bring the block in to see that it in fact looks like the
# hardware we described.  The format is a bit weird, but roughly translates to
# a list of gates (the 'w' gates are just wires, aka the connections made
# using <<= earlier).  The ins and outs of the gates are printed
# 'name'/'bitwidth''WireVectorType'

print('--- One Bit Adder Implementation ---')
print(pyrtl.working_block())
print()

# --- Step 2: Simulate Design  -----------------------------------------------

# Okay, let's get simulate our one-bit adder.  To keep track of the output of
# the simulation we need to make a new "SimulationTrace" and a "Simulation"
# that then uses that trace.

sim_trace = pyrtl.SimulationTrace()
sim = pyrtl.Simulation(tracer=sim_trace)

# Now all we need to do is call "sim.step" to simulate each clock cycle of our
# design.  We just need to pass in some input each cycle which is a dictionary
# mapping Inputs (the actual class instances of Input not the *names* of the
# inputs) and a value for that signal each cycle.  In this simple example we
# can just specify a random value of 0 or 1 with python's random module.  We
# call step 15 times to simulate 15 cycles.

for cycle in range(15):
    sim.step({
        a: random.choice([0, 1]),
        b: random.choice([0, 1]),
        c: random.choice([0, 1])
        })

# Now all we need to do is print the trace results to the screen. Here we use
# "render_trace" with some size information.
print('--- One Bit Adder Simulation ---')
sim_trace.render_trace(symbol_len=5, segment_size=5)

# --- Verification of Simulated Design ---------------------------------------

# Now finally, let's check the trace to make sure that sum and carry_out are actually
# the right values when compared to a python's addition operation.  Note that
# all the simulation is done at this point and we are just checking the wave form
# but there is no reason you could not do this at simulation time if you had a
# really long running design.

for cycle in range(15):
    # Note that we are doing all arithmetic on values, NOT wirevectors here.
    # We can add the inputs together to get a value for the result
    add_result = (sim_trace.trace[a][cycle] +
                  sim_trace.trace[b][cycle] +
                  sim_trace.trace[c][cycle])

    assert(isinstance(add_result, int))
    # We can select off the bits and compare
    python_sum = add_result & 0x1
    python_cout = (add_result >> 1) & 0x1
    if (python_sum != sim_trace.trace[sum][cycle] or
       python_cout != sim_trace.trace[carry_out][cycle]):
        print('This Example is Broken!!!')
        exit(1)

# You made it to the end!
exit(0)
