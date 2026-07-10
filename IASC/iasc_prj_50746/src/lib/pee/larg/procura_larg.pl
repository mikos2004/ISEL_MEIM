% ALg PROCURA PROFUNDIDADE (RAC AUT - pt1 slide 21)


% CASO PARTICULAR
% ----------------------

% O algoritmo mantem uma lista de vários caminhos
% como começa a procurar pelos Nós menos profundos
% o primeiro caminho com solução será a melhor solução

/*
Problema de otimização, pois Caminho ficava otimizado para ser aceite como uma variável qualquer dada a forma ordenada com que o Prolog processa a informação.
Devido a isso definimos logo Caminho para que depois possamos usar o seu Estado.

procura_larg(Caminhos, Caminho)
    % Se um dos Caminhos tiver um nó com o objetivo, o caminho é a solução
    Caminhos = [Caminho | _],
    Caminho = [Estado-_ | _],
    objetivo(Estado).
*/

procura_larg([Caminho | _], Caminho) :- 
    % Se um dos Caminhos tiver um nó com o objetivo, o caminho é a solução
    Caminho = [Estado-_ | _],
    objetivo(Estado).

% CASO GERAL
% ----------------------
procura_larg(Caminhos, CaminhoFinal):-
    Caminhos = [Caminho | RestoCaminhos], % Caminho seguido de vários caminhos
    findall(
        CaminhoSuc, 
        sucessor(Caminho, Caminhos, CaminhoSuc), 
        % recebe um Caminho e os Caminhos Acumulados e 
        % produz o Caminho Sucessor.
        CaminhosSuc
    ),
    % O restantes caminhos são colocados no fim da lista dos caminhos sucessores
    append(RestoCaminhos, CaminhosSuc, NovosCaminhos),
    procura_larg(NovosCaminhos, CaminhoFinal).
    
    
%sucessor(+Caminho, +Caminhos, -CaminhosSucessor)
sucessor([No | RestoCaminho], Caminhos, CaminhosSuc):-
    No = Estado-_,
    transicao(Estado, EstadoSuc, Operador),
    \+ explorado(EstadoSuc, Caminhos), % Garantimos que este estado ainda não foi explorado durante a definição do Caminho.
   % Erro --> CaminhoSuc = [EstadoSuc-Operador, No | RestoCaminho].
    CaminhosSuc = [EstadoSuc-Operador, No | RestoCaminho].

explorado(Estado, Caminhos):-
    % Se o Caminho tiver um Nó com o Estado associado ao seu par
    % Estado-Operador, significa que esse estado está explorado
    member(Caminho, Caminhos), % se um Estado já está na lista de Caminhos
    member(Estado-_, Caminho).


% resolver(+EstadoInicial, -Solucao)
resolver(EstadoInicial, Solucao):-
    procura_larg([[EstadoInicial-none]], Caminho),
    reverse(Caminho, Solucao).   