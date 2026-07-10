% ALg PROCURA PROFUNDIDADE (RAC AUT - pt1 slide 14)

% + -> na documentação significa param de entrada
% - -> na documentação significa param de saida

% Base da Procura
% procura_prof(+Caminho, -CaminhoFinal)

% Formato de nó (RAC AUT - pt1 slide 8)
% No: Estado-Operador
%:- consult('prj_50746/src/blocos/teste_blocos_pee.pl').

% CASO PARTICULAR
% ----------------------

% procura_prof(Caminho, CaminhoFinal) : -    %"Juntar : e -"
%    Caminho = [No | _],
%    No = Estado-Operador,
%    objetivo(Estado),
%    CaminhoFinal = Caminho.

% o estado for o objetivo acaba
procura_prof(Caminho, Caminho) :-
    Caminho = [Estado-_ | _],
    objetivo(Estado).

% CASO GERAL
% ----------------------
procura_prof(Caminho, CaminhoFinal) :-
    % Gerar sucessor
    sucessor(Caminho, CaminhoSucessor), % com um caminho gera uma caminho sucessor
    procura_prof(CaminhoSucessor, CaminhoFinal). % com esse caminho procura até chegar ao final

% Predicado Sucessor
sucessor([No | RestoCaminho], CaminhoSucessor):-
    No = Estado-_,
    transicao(Estado, EstadoSucessor, Operador),
    \+ explorado(EstadoSucessor, [No | RestoCaminho]), % o caminho ainda não foi explorado
    CaminhoSucessor = [EstadoSucessor-Operador, No | RestoCaminho].
    % Desta forma, o CaminhoSucessor fica com o Operador que 
    % efetua a transição entre o Estado do Nó Atual e o Estado do Nó Sucessor.
    % Coloca-se o Nó Sucessor no começo da lista do CaminhoSucessor

explorado(Estado, Caminho):-
    % Se o Caminho tiver um Nó com o Estado associado ao seu par
    % Estado-Operador, significa que esse estado está explorado
    member(Estado-_, Caminho).
    

% resolver(+EstadoInicial, -Solucao)
resolver(EstadoInicial, Solucao):-
    procura_prof([EstadoInicial-none], Caminho),
    reverse(Caminho, Solucao).    
