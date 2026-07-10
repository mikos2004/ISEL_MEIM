:- consult("procura_mp.pl").

% CUSTO UNIFORME é f(n) = g(n)
% Não tira partido de conhecimento do domínio do problema

avaliar(No, F) :-
    no_g(No, G),
    F = G.