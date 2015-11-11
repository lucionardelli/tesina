#!/bin/sh
# Hay que hacerlo lindo a esto. Por ahora, totalmente AD-HOC
# Sin poyección ni sampling
echo '> Comienza Sin proyec ni sampling'
echo '> Comienza illustrative_example.xes'
./pach.py ../xes_logs/illustrative_example.xes --verbose --smt-iter
echo '> Comienza running-example-just-two-cases.xes'
./pach.py ../xes_logs/running-example-just-two-cases.xes --verbose --smt-iter
echo '> Comienza choice.xes'
./pach.py ../xes_logs/choice.xes --verbose --smt-iter
echo '> Comienza confDimBlocking.xes'
./pach.py ../xes_logs/confDimBlocking.xes --verbose --smt-iter
echo '> Comienza DriversLicense.xes'
./pach.py ../xes_logs/DriversLicense.xes --verbose --smt-iter
echo '> Comienza confDimStacked.xes'
./pach.py ../xes_logs/confDimStacked.xes --verbose --smt-iter

# Con poyección y/o sampling
echo ''
echo '> Comienza Con proyec y/o sampling'
echo '> Comienza log1.xes'
./pach.py ../xes_logs/log1.xes --projection 11 --smt-iter
echo '> Comienza a32.xes'
./pach.py ../xes_logs/a32.xes --projection 8 --smt-iter
#echo '> Comienza Angiogenesis-PT-01.xes'
#./pach.py ../xes_logs/Angiogenesis-PT-01.xes --projection 10 --sampling 5 50 --smt-iter
echo '> Comienza DatabaseWithMutex-PT-02.xes'
./pach.py ../xes_logs/DatabaseWithMutex-PT-02.xes --projection --smt-iter
echo '> Comienza cycles5_2.xes'
./pach.py ../xes_logs/cycles5_2.xes --projection 10 --smt-iter
echo '> Comienza a42.xes'
./pach.py ../xes_logs/a42.xes --projection 10 --smt-iter
echo '> Comienza t32.xes'
./pach.py ../xes_logs/t32.xes --projection 10  --smt-iter
echo '> Comienza Peterson-PT-2.xes'
./pach.py ../xes_logs/Peterson-PT-2.xes --projection 10  --smt-iter
echo '> Comienza telecom.xes'
./pach.py ../xes_logs/telecom.xes --projection --smt-iter
echo '> Comienza complex.enc.xes'
./pach.py ../xes_logs/complex.enc.xes --projection 10 --smt-iter
echo '> Comienza documentflow.xes'
./pach.py ../xes_logs/documentflow.xes --projection --smt-iter
echo '> Comienza FHMexampleN5.enc.xes'
./pach.py ../xes_logs/FHMexampleN5.enc.xes --projection --smt-iter
echo '> Comienza incident.xes'
./pach.py ../xes_logs/incident.xes --projection --smt-iter
echo '> Comienza receipt.xes'
./pach.py ../xes_logs/receipt.xes --projection 10 --smt-iter
echo '> Comienza svn.xes'
./pach.py ../xes_logs/svn.xes --projection --smt-iter
mv ../xes_logs/*.pnml ../pnml/smt-iterative/
