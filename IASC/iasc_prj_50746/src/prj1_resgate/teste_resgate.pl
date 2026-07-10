:- encoding(utf8).
:- consult("prob_resgate.pl").

:- consult("../lib/pee/mp/procura_aa.pl").
%:- consult("../lib/pee/mp/procura_custo_unif.pl").
%:- consult("../lib/pee/mp/procura_sofrega.pl").

teste :-
    % Limpa túneis segurados de execuções anteriores
    reset_tuneis_segurados,
    inicio(Estado),
    % resolve o problema e calcula o tempo
    time(resolver(Estado, Solucao)),
    % Escreve a solução encontrada
    write('['), nl, % começo a lista
    escrever_solucao_formatada(Solucao),
    write(']'), nl. % finaliza a lista


% Função para escrever a Solução de forma legível
% --------------------------------------------------------------
% se a lista da Solução for vazia, não faz nada
escrever_solucao_formatada([]).
% caso para o último elemento da Solução
escrever_solucao_formatada([Elemento]) :-
    % espaço | elemento | nova linha
    write(' '), writeq(Elemento), nl.
escrever_solucao_formatada([Elemento|Resto]) :-
    % espaço | elemento | virgula| nova linha
    write(' '), writeq(Elemento), write(','), nl,
    escrever_solucao_formatada(Resto).