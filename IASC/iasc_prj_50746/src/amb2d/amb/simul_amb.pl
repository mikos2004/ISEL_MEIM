:- consult(def_amb).

% Iniciar ambiente
iniciar_ambiente(NumAccoes) :-
    gerar_transicoes(NumAccoes).

% Gerar todas as transições de estado válidas 
gerar_transicoes(NumAccoes) :-
    dimensao_ambiente(XMax, YMax),
    accoes(NumAccoes, Accoes),
    retractall(transicao_valida(_, _, _)),   
    forall((
        between(0, XMax, X), 
        between(0, YMax, Y),
        member(Accao, Accoes)
    ), (
        Posicao = (X, Y),
        simular_accao(Accao, Posicao, NovaPosicao) ->
            assert(transicao_valida(Posicao, NovaPosicao, Accao)) ; true
    )).

% Simular realização de uma acção
simular_accao((DX, DY), (X, Y), (XNovo, YNovo)) :-
    XNovo is X + DX,
    YNovo is Y + DY,
    posicao_valida((XNovo, YNovo)).

% Verificar se uma posição é válida      
posicao_valida((X, Y)) :-
    dimensao_ambiente(XMax, YMax),
    X >= 0, X < XMax,
    Y >= 0, Y < YMax,
    obstaculos(Obstaculos),
    \+ member((X, Y), Obstaculos).

% Calcular a distância entre duas posições
distancia((X1, Y1), (X2, Y2), Distancia) :-
    DX is X2 - X1,
    DY is Y2 - Y1,
    Distancia is sqrt(DX * DX + DY * DY).
    
% Mostrar ambiente e movimentos a realizar
mostrar_ambiente(Movimentos) :-
    dimensao_ambiente(XMax, YMax),
    posicao_inicial(PosInicial),
    alvos(Alvos),
    obstaculos(Obstaculos),
    nl,
    forall((
        between(0, YMax, Y), 
        between(0, XMax, X)
    ), (
        mostrar_agente(X, Y, PosInicial) ;
        mostrar_alvo(X, Y, Alvos) ;
        mostrar_obstaculo(X, Y, Obstaculos) ;
        mostrar_movimento(X, Y, Movimentos) ;
        mostrar_vazio,
        (X = XMax -> nl; true)
    )).

% Mostrar agente
mostrar_agente(X, Y, PosInicial) :-
    (X, Y) = PosInicial,
    cod_agente(CodAgente),
    put(CodAgente).

% Mostrar alvo
mostrar_alvo(X, Y, Alvos) :-
    member((X, Y), Alvos),
    cod_alvo(CodAlvo),
    put(CodAlvo).

% Mostrar obstáculo
mostrar_obstaculo(X, Y, Obstaculos) :-
    member((X, Y), Obstaculos),
    cod_obstaculo(CodObstaculo),
    put(CodObstaculo).

% Mostrar movimento
mostrar_movimento(X, Y, Movimentos) :-
    member((X, Y)-Movimento, Movimentos),
    cod_mov(Movimento, CodMov),
    write(CodMov).

% Mostrar posição vazia
mostrar_vazio :-
    cod_vazio(CodVazio),
    put(CodVazio).
