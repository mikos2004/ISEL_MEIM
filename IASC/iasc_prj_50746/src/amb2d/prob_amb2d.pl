:- consult("amb/simul_amb.pl").

%- Predicaddo transicao
%

transicao(Estado, NovoEstado, Acao, CustoTrans):-
    transicao_valida(Estado, NovoEstado, Acao),
    distancia(Estado, NovoEstado, CustoTrans).

inicio(Estado):-
    posicao_inicial(Estado).


objetivo(Estado):-
    % Devolve uma lista que têm os alvos e portanto podemos usar qualquer um como o primeiro.
    alvos([Estado | _]).

heuristica(Estado, H):-
    objetivo(EstadoObjetivo),
    distancia(Estado, EstadoObjetivo, H).
