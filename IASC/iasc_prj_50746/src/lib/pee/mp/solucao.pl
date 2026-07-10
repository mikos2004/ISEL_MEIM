% Solução Melhor primeiro~

% A solução é uma sequência de Nós (excluindo o Estado Incial)

solucao(NoFinal, Solucao) :-
    % A partir do Nó final a lista e acumulação vai 
    % acumular os vários nós até chegar ao Estado Incial
    % Esta lista lista origina a solução
    gerar_solucao(NoFinal, [], Solucao).

% CASO PARTICULAR (atingir o nó raiz que não tem antecessor)
gerar_solucao(NoFinal, Caminho, Caminho) :-
    no_ant(NoFinal, none),
    !. % Em alternativa, o nó tem Antecssor

% CASO Geral
gerar_solucao(No, Caminho, Solucao) :-
    no_ant(No, NoAnt),
    no_estado(NoAnt, EstadoAnt),
    no_oper(No, Oper),
    CaminhoParcial = [EstadoAnt-Oper | Caminho],
    gerar_solucao(NoAnt, CaminhoParcial, Solucao).


    