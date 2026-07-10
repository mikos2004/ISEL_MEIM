%------------------------------------------------------------
% Algoritmo Hill-Climbing
%
% hc(+Estado, -Solucao, +NIter)
%
% Estado: Estado inicial
% Solucao: Solução obtida
% NIter: Número de iterações
%------------------------------------------------------------

% Fim das iterações
hc(Estado, Estado, 0) :- !.

% Objectivo atingido
hc(Estado, Estado, _) :-
    objectivo(Estado).

% Iterar procura
hc(Estado, Solucao, NIter) :-
    sucessores(Estado, Sucessores),
    avaliar(Sucessores, AvalSuc),
    max_member(AvalMaxSuc, AvalSuc),
    valor(Estado, ValorEstado),
    gerar_solucao(ValorEstado-Estado, AvalMaxSuc, Solucao, NIter).

% Estado atingido é o melhor
gerar_solucao(ValorEstado-Estado, AvalSuc-_, Estado, _) :-
    ValorEstado >= AvalSuc.

% Estado atingido não é o melhor
gerar_solucao(_, _-EstadoSuc, Solucao, NIter) :-
    NIterSuc is NIter - 1,
    hc(EstadoSuc, Solucao, NIterSuc).

% Sucessores de um estado
sucessores(Estado, Sucessores) :-
    findall(EstadoSuc, transicao(Estado, EstadoSuc), Sucessores).

% Avaliar estados de uma lista de estados
% gerando uma lista de pares valor-estado
avaliar([], []).
avaliar([Estado | Resto], [Valor-Estado | RestoAval]) :-
    valor(Estado, Valor),
    avaliar(Resto, RestoAval).

