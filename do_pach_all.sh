#!/bin/sh
# Hay que hacerlo lindo a esto. Por ahora, totalmente AD-HOC
printf '\n\n> SIN SMT <' >> smt-iterative-complexities.out
date >> no-smt-complexities.out

# Sin poyección ni sampling
echo '> Comienza Sin proyec ni sampling'
echo '> Comienza illustrative_example.xes'
./pach.py ../xes_logs/illustrative_example.xes >> no-smt-complexities.out
echo '> Comienza running-example-just-two-cases.xes'
./pach.py ../xes_logs/running-example-just-two-cases.xes >> no-smt-complexities.out
echo '> Comienza choice.xes'
./pach.py ../xes_logs/choice.xes >> no-smt-complexities.out
echo '> Comienza confDimBlocking.xes'
./pach.py ../xes_logs/confDimBlocking.xes >> no-smt-complexities.out
echo '> Comienza DriversLicense.xes'
./pach.py ../xes_logs/DriversLicense.xes >> no-smt-complexities.out
echo '> Comienza confDimStacked.xes'
./pach.py ../xes_logs/confDimStacked.xes >> no-smt-complexities.out

# Con poyección y/o sampling
echo ''
echo '> Comienza Con proyec y/o sampling'
echo '> Comienza log1.xes'
./pach.py ../xes_logs/log1.xes --projection 11 >> no-smt-complexities.out
echo '> Comienza a32.xes'
./pach.py ../xes_logs/a32.xes --projection 8 >> no-smt-complexities.out
echo '> Comienza Angiogenesis-PT-01.xes'
./pach.py ../xes_logs/Angiogenesis-PT-01.xes --projection 10 --sampling 5 50 >> no-smt-complexities.out
echo '> Comienza DatabaseWithMutex-PT-02.xes'
./pach.py ../xes_logs/DatabaseWithMutex-PT-02.xes --projection >> no-smt-complexities.out
echo '> Comienza cycles5_2.xes'
./pach.py ../xes_logs/cycles5_2.xes --projection >> no-smt-complexities.out
echo '> Comienza a42.xes'
./pach.py ../xes_logs/a42.xes --projection 10 >> no-smt-complexities.out
echo '> Comienza a42.xes SIN LÍMITE DE PROJ PERO SIN CHECK'
./pach.py ../xes_logs/a42.xes --projection 10 --no-sanity >> no-smt-complexities.out
echo '> Comienza t32.xes'
./pach.py ../xes_logs/t32.xes --projection 10  >> no-smt-complexities.out
echo '> Comienza t32.xes LÍMITE DE PROJ PERO SIN CHECK'
./pach.py ../xes_logs/t32.xes --projection --no-sanity >> no-smt-complexities.out
echo '> Comienza Peterson-PT-2.xes SIN CHECK'
./pach.py ../xes_logs/Peterson-PT-2.xes --projection 10 --no-sanity >> no-smt-complexities.out
echo '> Comienza telecom.xes'
./pach.py ../xes_logs/telecom.xes --projection >> no-smt-complexities.out
echo '> Comienza complex.enc.xes'
./pach.py ../xes_logs/complex.enc.xes --projection 10 >> no-smt-complexities.out
echo '> Comienza documentflow.xes'
./pach.py ../xes_logs/documentflow.xes --projection >> no-smt-complexities.out
echo '> Comienza FHMexampleN5.enc.xes'
./pach.py ../xes_logs/FHMexampleN5.enc.xes --projection >> no-smt-complexities.out
echo '> Comienza incident.xes'
./pach.py ../xes_logs/incident.xes --projection >> no-smt-complexities.out
echo '> Comienza receipt.xes'
./pach.py ../xes_logs/receipt.xes --projection >> no-smt-complexities.out
echo '> Comienza svn.xes'
./pach.py ../xes_logs/svn.xes --projection >> no-smt-complexities.out
mv ../xes_logs/*.pnml ../pnml/no_smt/
