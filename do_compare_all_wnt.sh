#!/bin/sh
# Hay que hacerlo lindo a esto. Por ahora, totalmente AD-HOC
printf '\n\n> COMPARMOS NO-SMT, SMT ITERATIVE Y SMT MATRIX CON INFORMACION NEGATIVA <' >> comparative.complexities.out
date >> comparative.complexities.out

# Sin poyección ni sampling
echo '> Comienza Sin proyec ni sampling'
echo '> Comienza DriversLicense.xes'
./comparator.py ../xes_logs/DriversLicense.xes --smt-matrix 300 --smt-iter 30  --negative ../negative_logs/DriversLicense.negatives.xes >> comparative.complexities.out
echo '> Comienza choice.xes'
./comparator.py ../xes_logs/choice.xes --smt-matrix 300 --smt-iter 30  --negative ../negative_logs/choice.negatives.xes >> comparative.complexities.out
echo '> Comienza confDimBlocking.xes'
./comparator.py ../xes_logs/confDimBlocking.xes --smt-matrix 300 --smt-iter 30  --negative ../negative_logs/confDimBlocking.negatives.xes >> comparative.complexities.out
echo '> Comienza confDimStacked.xes'
./comparator.py ../xes_logs/confDimStacked.xes --smt-matrix 300 --smt-iter 30  --negative ../negative_logs/confDimStacked.negatives.xes >> comparative.complexities.out

# Con poyección y/o sampling
echo ''
echo '> Comienza Con proyec y/o sampling'
echo '> Comienza incident.xes'
./comparator.py ../xes_logs/incident.xes --projection --smt-matrix 300 --smt-iter 30  --negative ../negative_logs/incident.negatives.xes >> comparative.complexities.out
echo '> Comienza svn.xes'
./comparator.py ../xes_logs/svn.xes --projection --smt-matrix 300 --smt-iter 30  --negative ../negative_logs/svn.negatives.xes >> comparative.complexities.out
echo '> Comienza FHMexampleN5.enc.xes'
./comparator.py ../xes_logs/FHMexampleN5.enc.xes --projection --smt-matrix 300 --smt-iter 30  --negative ../negative_logs/FHMexampleN5.enc.negatives.xes >> comparative.complexities.out
echo '> Comienza receipt.xes'
./comparator.py ../xes_logs/receipt.xes --projection --smt-matrix 300 --smt-iter 30  --negative ../negative_logs/receipt.negatives.xes >> comparative.complexities.out
echo '> Comienza documentflow.xes'
./comparator.py ../xes_logs/documentflow.xes --projection --smt-matrix 300 --smt-iter 30  --negative ../negative_logs/documentflow.negatives.xes >> comparative.complexities.out
echo '> Comienza a32.xes'
./comparator.py ../xes_logs/a32.xes --projection 8 --smt-matrix 300 --smt-iter 30  --negative ../negative_logs/a32.negatives.xes >> comparative.complexities.out
echo '> Comienza cycles5_2.xes'
./comparator.py ../xes_logs/cycles5_2.xes --projection --smt-matrix 300 --smt-iter 30  --negative ../negative_logs/cycles5_2.negatives.xes >> comparative.complexities.out
echo '> Comienza DatabaseWithMutex-PT-02.xes'
./comparator.py ../xes_logs/DatabaseWithMutex-PT-02.xes --projection --smt-matrix 300 --smt-iter 30  --negative ../negative_logs/DatabaseWithMutex-PT-02.negatives.xes >> comparative.complexities.out
echo '> Comienza t32.xes'
./comparator.py ../xes_logs/t32.xes --projection 10  --smt-matrix 300 --smt-iter 30  --negative ../negative_logs/t32.negatives.xes >> comparative.complexities.out
#Trazas negativas muy grandes, no pueden siquiera parsearse
#echo '> Comienza a42.xes'
#./comparator.py ../xes_logs/a42.xes --projection 10 --smt-matrix 300 --smt-iter 30  --negative ../negative_logs/a42.negatives.xes >> comparative.complexities.out
#echo '> Comienza telecom.xes'
#./comparator.py ../xes_logs/telecom.xes --projection --smt-matrix 300 --smt-iter 30  --negative ../negative_logs/telecom.negatives.xes >> comparative.complexities.out
#echo '> Comienza complex.enc.xes'
#./comparator.py ../xes_logs/complex.enc.xes --projection 10 --smt-matrix 300 --smt-iter 30  --negative ../negative_logs/complex.enc.negatives.xes >> comparative.complexities.out
mv ../xes_logs/*.pnml ../pnml/comparator/negatives/
