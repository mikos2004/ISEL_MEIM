% Nó do Algoritmo Melhor Primeiro

% Um Nó tem:
%   Estado, 
%   Nó Antecessor que lhe deu origem,
%   Operador responsável pela transição,
%   Profundidade do Nó,
%   G custo acumlado até o nó.

% No = Estado-NoAnt-Oper-Prof-G

% CASO PARTICULAR
% ---------------------------
% Criar um Nó a partir de um Estado
% Construtor
no(Estado-none-none-0-0, Estado).

% CASO GERAL
% ---------------------------
no(Estado-NoAnt-Oper-Prof-G, Estado, NoAnt, Oper, CustoTrans):-
    no_prof(NoAnt, ProfAnt), % qual a Profundidade do Nó Anterior
    no_g(NoAnt, GAnt), % qual o G do nó Anterior

    Prof is ProfAnt + 1,
    G is GAnt + CustoTrans.



% Obter Estado de um No
no_estado(Estado-_-_-_-_, Estado).

% Obter NoAnt de um No
no_ant(_-NoAnt-_-_-_, NoAnt).

% Obter Oper de um No
no_oper(_-_-Oper-_-_, Oper).

% Obter Prof de um No
no_prof(_-_-_-Prof-_, Prof).

% Obter G de um No
no_g(_-_-_-_-G, G).

