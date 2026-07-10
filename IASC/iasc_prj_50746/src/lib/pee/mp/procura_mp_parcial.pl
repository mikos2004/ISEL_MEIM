% ALGORITMO MELHOR PRIMEIRO PARCIAL

% É produzida uma solução parcial, pois a procura é limitada com uma dada profundidade máxima
% NOTAS: "asserta" mete no começo e "assertz" no fim

:- consult(procura_mp).
:- multifile finalizar_procura/1.

resolver(EstadoInicial, Explorados, NoFinal, ProfMax):-
    % abstração para limitação da profundidade máxima
    iniciar_prof_max(ProfMax),
    iniciar_procura(EstadoInicial, Fronteira, Explorados),
    procura_mp(Fronteira, Explorados, NoFinal).

iniciar_prof_max(ProfMax):-
    retractall(prof_max(_)),
    assert(prof_max(ProfMax)).

finalizar_procura(No):-
    % Esta clausula extende a que foi criada no "procura_mp"
    prof_max(ProfMax),
    no_prof(No, Prof),
    Prof > ProfMax.