% Usar UTF-8
:- encoding(utf8).

% Imports/Consults

:-consult("prob_amb2d.pl").

:- consult("src/lib/pee/rtaa/procura_rtaa.pl").


teste :- 
    iniciar_ambiente(8), % inicialização do ambiente
    inicio(Estado), % definição do Estado Iniciaç
    iniciar_rtaa, % iniciar a procura
    resolver_parcial(Estado).


resolver_parcial(Estado):-
    resolver_rtaa(Estado, NoFinal, 40),
    no_estado(NoFinal, EstadoFinal),
    solucao(NoFinal, Solucao),
    mostrar_ambiente(Solucao),
    !,
    (
        objetivo(EstadoFinal)
        ;
        resolver_parcial(EstadoFinal)
    ).
    