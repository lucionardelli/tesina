#!/bin/sh
# Hay que hacerlo lindo a esto. Por ahora, totalmente AD-HOC

# Sin poyección ni sampling
./pach.py ../xes_examples/running-example-just-two-cases.xes 
./pach.py ../xes_examples/illustrative_example.xes 
./pach.py ../xes_examples/choice.xes 
./pach.py ../xes_examples/confDimBlocking.xes 
./pach.py ../xes_examples/DriversLicense.xes 
./pach.py ../xes_examples/confDimStacked.xes 

# Con poyección, sin sampling
./pach.py ../xes_examples/log1.xes --projection
./pach.py ../xes_examples/a32.xes --projection
./pach.py ../xes_examples/Angiogenesis-PT-01.xes --projection
./pach.py ../xes_examples/DatabaseWithMutex-PT-02.xes --projection
./pach.py ../xes_examples/cycles5_2.xes --projection
./pach.py ../xes_examples/a42.xes --projection
./pach.py ../xes_examples/t32.xes --projection
./pach.py ../xes_examples/Peterson-PT-2.xes --projection
./pach.py ../xes_examples/telecom.xes --projection
