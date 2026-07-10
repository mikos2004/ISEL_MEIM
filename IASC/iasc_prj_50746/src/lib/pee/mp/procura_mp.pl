:- consult("procura_base.pl").


resolver(EstadoInicial, Solucao) :-
    % A partir do EstadoInicial, inicia-se a fronteira e a lista de explorados
    iniciar_procura(EstadoInicial, Fronteira, Explorados),
    % Procura o nó final, dada a fronteira e a lista de explorados
    procura_mp(Fronteira, Explorados, NoFinal),
    % encontrado o nó final, gera-se a solucao
    solucao(NoFinal, Solucao).

iniciar_procura(EstadoInicial, Fronteira, Explorados):-
    no(No, EstadoInicial),
    % colocar nó incial na fronteira e na lista de explorados
    fronteira_iniciar(Fronteira, No),
    explorados_iniciar(Explorados, No).

procura_mp(Fronteira, Explorados, NoFinal):-
    % Obter o primeiro Nó
    fronteira_obter(Fronteira, No, RestoFronteira),
    (
        % -> // se então, se não
        finalizar_procura(No) ->
            % Finaliza a Procura se o No for o NoFinal  
            NoFinal = No % se então
            ; % Se não
            % Continua procura
            continuar_procura(No, RestoFronteira, Explorados, NoFinal)
    ).

continuar_procura(No, Fronteira, Explorados, NoFinal) :-
    expandir(No, Sucessores), % expande o no, gera os sucessores
    % memoriza os sucessores da fronteira, gerando uma nova fronteira e atualiza os explorado.
    memorizar(Sucessores, Fronteira, NovaFronteira, Explorados),
    % continua a procura com a nova fronteira e os explorados atualizados.
    procura_mp(NovaFronteira, Explorados, NoFinal).

finalizar_procura(No):-
    % Verifica se o Estado do Nó é o Estado que corresponde ao objetivo
    no_estado(No, Estado),
    objetivo(Estado).