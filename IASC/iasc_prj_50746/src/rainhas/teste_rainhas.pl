:- encoding(utf8).

:- consult('../lib/optim/hc').
:- consult('../lib/optim/hcr').
:- consult(prob_rainhas).

% Mostrar resultado obtido
mostrar_resultado(Info, Solucao) :-
    nl, writeln(Info),
    nl, writeln(Solucao),
    nl, mostrar_tabuleiro(Solucao),
    nl, num_ameacas(Solucao, NumAmeacas),
    writeln("Ameaças":NumAmeacas).

% Teste do algoritmo Hill-Climbing
teste_hc :-
    inicio(Estado),
    hc(Estado, Solucao, 100),
    mostrar_resultado("Hill-Climbing:", Solucao).

% Teste do algoritmo Hill-Climbing com reinícios aleatórios
teste_hcr :-
    inicio(Estado),
    hcr(Estado, Solucao, 100, 2000),
    mostrar_resultado("Hill-Climbing com reinícios aleatórios:", Solucao).

% Executar testes

%
%:- teste_hc.

:- teste_hcr.
