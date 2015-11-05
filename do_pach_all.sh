#!/bin/sh
# Hay que hacerlo lindo a esto. Por ahora, totalmente AD-HOC

# Sin poyección ni sampling
echo '> Comienza Sin proyec ni sampling'
echo '> Comienza illustrative_example.xes'
./pach.py ../xes_logs/illustrative_example.xes  --verbose
echo '> Comienza running-example-just-two-cases.xes'
./pach.py ../xes_logs/running-example-just-two-cases.xes  --verbose
echo '> Comienza choice.xes'
./pach.py ../xes_logs/choice.xes  --verbose
echo '> Comienza confDimBlocking.xes'
./pach.py ../xes_logs/confDimBlocking.xes  --verbose
echo '> Comienza DriversLicense.xes'
./pach.py ../xes_logs/DriversLicense.xes  --verbose
echo '> Comienza confDimStacked.xes'
./pach.py ../xes_logs/confDimStacked.xes  --verbose

# Con poyección, sin sampling
echo ''
echo '> Comienza Con proyec, sin sampling'
echo '> Comienza log1.xes'
# Con valores de projection mayor, no anda
./pach.py ../xes_logs/log1.xes --projection 11
echo '> Comienza a32.xes'
./pach.py ../xes_logs/a32.xes --projection
#echo '> Comienza Angiogenesis-PT-01.xes'
#./pach.py ../xes_logs/Angiogenesis-PT-01.xes --projection 8 --sampling 3 100
echo '> Comienza DatabaseWithMutex-PT-02.xes'
./pach.py ../xes_logs/DatabaseWithMutex-PT-02.xes --projection
echo '> Comienza cycles5_2.xes'
./pach.py ../xes_logs/cycles5_2.xes --projection
echo '> Comienza a42.xes'
./pach.py ../xes_logs/a42.xes --projection
echo '> Comienza t32.xes'
./pach.py ../xes_logs/t32.xes --projection
echo '> Comienza Peterson-PT-2.xes'
./pach.py ../xes_logs/Peterson-PT-2.xes --projection
echo '> Comienza telecom.xes'
./pach.py ../xes_logs/telecom.xes --projection
echo '> Comienza complex.enc.xes'
./pach.py ../xes_logs/complex.enc.xes --projection
echo '> Comienza documentflow.xes'
./pach.py ../xes_logs/documentflow.xes --projection
echo '> Comienza FHMexampleN5.enc.xes'
./pach.py ../xes_logs/FHMexampleN5.enc.xes --projection
echo '> Comienza incident.xes'
./pach.py ../xes_logs/incident.xes --projection
echo '> Comienza receipt.xes'
./pach.py ../xes_logs/receipt.xes --projection
echo '> Comienza svn.xes'
./pach.py ../xes_logs/svn.xes --projection
mv ../xes_logs/*.pnml ../pnml/no_smt/
