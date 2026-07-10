:- consult(no).
:- consult(fronteira).
:- consult(solucao).
:- consult(explorados).

expandir(No, Sucessores):-
    findall(NoSuc, sucessor(No, NoSuc), Sucessores).

sucessor(No, NoSuc):-
    no_estado(No, Estado), 
    transicao(Estado, EstadoSuc, Operador, CustoTrans),
    no(NoSuc, EstadoSuc, No, Operador, CustoTrans).

% CASO PARTICULAR
% -----------------
memorizar([], Fronteira, Fronteira, _).

% CASO GERAL
% -----------------
memorizar([NoSuc | RestoSucessores], Fronteira, NovaFronteira, Explorados) :-
    explorado(NoSuc, Explorados),
    memorizar(RestoSucessores, Fronteira, NovaFronteira, Explorados).

memorizar([NoSuc | RestoSucessores], Fronteira, NovaFronteira, Explorados) :-
    avaliar(NoSuc, F),
    fronteira_inserir(Fronteira, F, NoSuc, FronteiraSucessor),
    explorados_inserir(Explorados, NoSuc),
    memorizar(RestoSucessores, FronteiraSucessor, NovaFronteira, Explorados).

explorado(No, Explorados):-
    explorados_obter(Explorados, No, NoExp),
    no_g(No, G),
    no_g(NoExp, GExp),
    G >= GExp.