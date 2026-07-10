:- consult("procura_mp.pl").

% PROCURA SOFREGA  é f(n) = h(n)
% Não tem em conta o custo do percurso explorado
% Minimização de custo local

avaliar(No, F) :-
    no_estado(No, Estado),
    heuristica(Estado, H),
    F = H.