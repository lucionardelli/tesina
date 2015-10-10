#!/bin/sh
# Hay que hacerlo lindo a esto. Por ahora, totalmente AD-HOC

# Sin poyección ni sampling
echo '> Comienza Sin proyec ni sampling'
echo '> Comienza illustrative_example.xes'
./pach.py ../xes_examples/illustrative_example.xes  --verbose
echo '> Comienza running-example-just-two-cases.xes'
./pach.py ../xes_examples/running-example-just-two-cases.xes  --verbose
echo '> Comienza choice.xes'
./pach.py ../xes_examples/choice.xes  --verbose
echo '> Comienza confDimBlocking.xes'
./pach.py ../xes_examples/confDimBlocking.xes  --verbose
echo '> Comienza DriversLicense.xes'
./pach.py ../xes_examples/DriversLicense.xes  --verbose
echo '> Comienza confDimStacked.xes'
./pach.py ../xes_examples/confDimStacked.xes  --verbose

# Con poyección, sin sampling
echo ''
echo '> Comienza Con proyec, sin sampling'
echo '> Comienza log1.xes'
./pach.py ../xes_examples/log1.xes --projection
echo '> Comienza a32.xes'
./pach.py ../xes_examples/a32.xes --projection
echo '> Comienza Angiogenesis-PT-01.xes'
./pach.py ../xes_examples/Angiogenesis-PT-01.xes --projection
echo '> Comienza DatabaseWithMutex-PT-02.xes'
./pach.py ../xes_examples/DatabaseWithMutex-PT-02.xes --projection
echo '> Comienza cycles5_2.xes'
./pach.py ../xes_examples/cycles5_2.xes --projection
echo '> Comienza a42.xes'
./pach.py ../xes_examples/a42.xes --projection
echo '> Comienza t32.xes'
./pach.py ../xes_examples/t32.xes --projection
echo '> Comienza Peterson-PT-2.xes'
./pach.py ../xes_examples/Peterson-PT-2.xes --projection
echo '> Comienza telecom.xes'
./pach.py ../xes_examples/telecom.xes --projection
