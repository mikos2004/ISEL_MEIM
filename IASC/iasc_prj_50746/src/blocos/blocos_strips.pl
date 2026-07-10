% ISEL | DEI | MEIM | IASC
% Miguel Alcobia 50746

% Blocos Strips

%---------------------------------
% DEFINIÇÂO DO MUNDO DOS BLOCOS

% Condições -> condicao(X) onde X é uma condição
condicao(sobre(_,_)). % Bloco X está sobre Y
condicao(mesa(_)). % X está sobre a mesa
condicao(livre(_)). % X não não nenhum bloco empilhado sobre ele

% AÇÕES VÁLIDAS
% acao(Operador, PreCond, Efeitos)

% Operador: (operador origina a ação)
%   - Nome : Descricao do operador
%   - Pre-condições : Pre-condicoes e lista de remocao
%   - Efeitos : Lista de adição

acao(empilhar(X,Y), [livre(Y), mesa(X), livre(X)], [sobre(X,Y), livre(X)]).

% ALTERNATIVA:
% ----------------
% acao(Operador, Precond, Efeitos) ":-" ("" pq o VSCODE estava a dar erro de sintaxe no comentario)
%   Operador = empilhar (X, Y),
%   Precond =  [livre(Y), mesa(X), livre(X)],
%   Efeito = [sobre(X,Y), livre(X)]


acao(desempilhar(Y,X), [sobre(Y, X), livre(Y)], [mesa(Y), livre(Y), livre(X)]).
