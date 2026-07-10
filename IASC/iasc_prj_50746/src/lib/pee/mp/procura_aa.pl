:- consult("procura_mp.pl").

% Procura A* é f(n) = g(n) + h(n)
% Minimização de custo global

avaliar(No, F) :-
    no_g(No, G),
    no_estado(No, Estado),
    heuristica(Estado, H),
    F is G + H.