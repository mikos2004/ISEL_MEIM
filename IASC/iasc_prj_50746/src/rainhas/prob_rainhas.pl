%------------------------------------------------------------
% Problema das raínhas
%------------------------------------------------------------

:- consult(tab_rainhas).

% Estado inicial
% Definido como um tabuleiro aleatório
% -Tab: Tabuleiro
inicio(Tab) :-
    estado_aleat(Tab).

% Estado aleatório
% Definido como um tabuleiro aleatório
% -Tab: Tabuleiro
estado_aleat(Tab) :-
    tabuleiro_aleatorio(Tab).

% Objectivo do problema
% Definido como um tabuleiro sem ameaças
% +Tab: Tabuleiro
objectivo(Tab) :-
    num_ameacas(Tab, 0).

% Transição de estado
% +Tab: Tabuleiro
% -NovoTab: Novo tabuleiro
transicao(Tab, NovoTab) :-
    coluna_tabuleiro(Tab, Col),
    mover_rainha(Tab, Col, NovoTab).

% Obter valor de um tabuleiro
% O valor decresce em função do número de ameaças,
% sendo máximo (0) quando não existem ameaças
% +Tab: Tabuleiro
% -Valor: Valor do tabuleiro
valor(Tab, Valor) :-
    num_ameacas(Tab, NumAmeacas),
    Valor is -NumAmeacas.