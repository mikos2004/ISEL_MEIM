% ALg STRIPS (RAC AUT - pt1 slide 26)

% + -> na documentação significa param de entrada
% - -> na documentação significa param de saida

% strips(+Estado, +ListaObj, +SeqAcoes, -SeqAcoesFinal)

%:- consult('D:\\ISEL\\MEIM\\IASC\\prj_50746\\src\\blocos\\blocos_strips.pl').
:- consult('prj_50746/src/blocos/blocos_strips.pl'). % -> desde da raiz do prj


% Condicao Particular - Fim da tabela do sldie 26 (começar pelo objetivo)
strips(_, [], SeqAcoes, SeqAcoes).

% Casos Gerais
% 1º Caso da Tabela slide 26
strips(Estado, [I | R], SeqAcoes, SeqAcoesFinal):-
    condicao(I), % Sub-Objetivo que é uma condicao
    member(I, Estado), % Inicio é membro do Estado
    strips(Estado, R, SeqAcoes, SeqAcoesFinal). % resolver a lista Objetivos

% 2º Caso da Tabela slide 26
strips(Estado, [I | R], SeqAcoes, SeqAcoesFinal):-
    condicao(I), % Sub-Objetivo que é uma condicao
    \+ member(I, Estado), % Inicio não é membro do Estado
    acao(Acao, _, Efeitos), % qualquer que seja a Acao querenos os Efeitos, nao querendo os Preconds
    member(I, Efeitos),% Escolher uma acção cujos efeitos incluam o sub-objetivo
    strips(Estado, [Acao, I | R], SeqAcoes, SeqAcoesFinal). % resolver a lista Objetivos

% 3º Caso da Tabela slide 26
strips(Estado, [I | R], SeqAcoes, SeqAcoesFinal):-
    acao(I, Precond, Efeitos), % sub-objetivo é uma Acao
    subset(Precond, Estado), % Se as Preconds da Acao são satisfeitas no estado (são um subconjunto)
    subtract(Estado, Precond, EstadoAux), % retiramos essas condições do estado
    append(EstadoAux, Efeitos, NovoEstado), % Juntar Efeitos ao Estado
    strips(NovoEstado, R, [I | SeqAcoes], SeqAcoesFinal). % juntar Ação ao plano e resolver a lista Objetivos

% 4º Caso da Tabela slide 26
strips(Estado, [I | R], SeqAcoes, SeqAcoesFinal):-
    acao(I, Precond, _), % sub-objetivo é uma acao
    \+ subset(Precond, Estado), % Se as Preconds da Acao são satisfeitas no estado (são um subconjunto)
    append(Precond, [I | R], NovaListaObj), % acresentamos as condicões ao inicio da Lista de Objs
    strips(Estado, NovaListaObj, SeqAcoes, SeqAcoesFinal). % resolver a lista Objetivos


planear(Estado, ListaObj, Plano):-
    strips(Estado, ListaObj, [], SeqAcoes),
    reverse(SeqAcoes, Plano).