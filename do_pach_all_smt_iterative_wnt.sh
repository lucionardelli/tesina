!/bin/sh
 Hay que hacerlo lindo a esto. Por ahora, totalmente AD-HOC
printf '\n\n> SIN SMT <' >> smt-iterative-complexities.out
date >> smt-iterative-complexities.out

# Sin poyección ni sampling
echo '> Comienza Sin proyec ni sampling'
echo '> Comienza DriversLicense.xes'
./pach.py ../xes_logs/DriversLicense.xes --smt-iter 30  ../negative_logs/DriversLicense.negatives.xes >> smt-iterative-complexities.out
echo '> Comienza choice.xes'
./pach.py ../xes_logs/choice.xes --smt-iter 30  ../negative_logs/choice.negatives.xes >> smt-iterative-complexities.out
echo '> Comienza confDimBlocking.xes'
./pach.py ../xes_logs/confDimBlocking.xes --smt-iter 30  ../negative_logs/confDimBlocking.negatives.xes >> smt-iterative-complexities.out
echo '> Comienza confDimStacked.xes'
./pach.py ../xes_logs/confDimStacked.xes --smt-iter 30  ../negative_logs/confDimStacked.negatives.xes >> smt-iterative-complexities.out

# Con poyección y/o sampling
echo ''
echo '> Comienza Con proyec y/o sampling'
echo '> Comienza incident.xes'
./pach.py ../xes_logs/incident.xes --projection --smt-iter 30  ../negative_logs/incident.negatives.xes >> smt-iterative-complexities.out
echo '> Comienza svn.xes'
./pach.py ../xes_logs/svn.xes --projection --smt-iter 30  ../negative_logs/svn.negatives.xes >> smt-iterative-complexities.out
echo '> Comienza FHMexampleN5.enc.xes'
./pach.py ../xes_logs/FHMexampleN5.enc.xes --projection --smt-iter 30  ../negative_logs/FHMexampleN5.enc.negatives.xes >> smt-iterative-complexities.out
echo '> Comienza receipt.xes'
./pach.py ../xes_logs/receipt.xes --projection --smt-iter 30  ../negative_logs/receipt.negatives.xes >> smt-iterative-complexities.out
echo '> Comienza documentflow.xes'
./pach.py ../xes_logs/documentflow.xes --projection --smt-iter 30  ../negative_logs/documentflow.negatives.xes >> smt-iterative-complexities.out
echo '> Comienza a32.xes'
./pach.py ../xes_logs/a32.xes --projection 8 --smt-iter 30  ../negative_logs/a32.negatives.xes >> smt-iterative-complexities.out
echo '> Comienza cycles5_2.xes'
./pach.py ../xes_logs/cycles5_2.xes --projection --smt-iter 30  ../negative_logs/cycles5_2.negatives.xes >> smt-iterative-complexities.out
echo '> Comienza DatabaseWithMutex-PT-02.xes'
./pach.py ../xes_logs/DatabaseWithMutex-PT-02.xes --projection --smt-iter 30  ../negative_logs/DatabaseWithMutex-PT-02.negatives.xes >> smt-iterative-complexities.out
echo '> Comienza t32.xes'
./pach.py ../xes_logs/t32.xes --projection 10  --smt-iter 30  ../negative_logs/t32.negatives.xes >> smt-iterative-complexities.out
#Trazas negativas muy grandes, no pueden siquiera parsearse
#echo '> Comienza a42.xes'
#./pach.py ../xes_logs/a42.xes --projection 10 --smt-iter 30  ../negative_logs/a42.negatives.xes >> smt-iterative-complexities.out
#echo '> Comienza telecom.xes'
#./pach.py ../xes_logs/telecom.xes --projection --smt-iter 30  ../negative_logs/telecom.negatives.xes >> smt-iterative-complexities.out
#echo '> Comienza complex.enc.xes'
#./pach.py ../xes_logs/complex.enc.xes --projection 10 --smt-iter 30  ../negative_logs/complex.enc.negatives.xes >> smt-iterative-complexities.out
mv ../xes_logs/*.pnml ../pnml/smt_iterative/negatives/
