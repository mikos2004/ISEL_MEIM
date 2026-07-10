% DEFINIÇÃO DAS TRANSIÇÕES POSSÌVEIS
% ----------------------

% :- consult('prj_50746/src/lib/pee/prof/procura_prof.pl').
:- consult('src/lib/pee/larg/procura_larg.pl').
:- consult('src/blocos/blocos_pee.pl').

% :- set_prolog_flag(optimise_unify, false).


% DEFINIÇÃO DAS TRANSIÇÕES POSSÌVEIS
% ---------------------------------------

% transicao(Estado, EstadoSuc, Operador)
transicao(Estado, EstadoSuc, empilhar):- 
    empilhar(Estado, EstadoSuc).

transicao(Estado, EstadoSuc, desempilhar):- 
    desempilhar(Estado, EstadoSuc).


inicio([c,b,a]-[]). % Define o estado inicial
objetivo([a,b,c]-[]). % Define se um estado é objetivo


teste:-
    inicio(EstadoInicial),
    resolver(EstadoInicial, Solucao),
    forall(
        member(Estado-Operador, Solucao),
        writeln(Operador:Estado)    
    ).