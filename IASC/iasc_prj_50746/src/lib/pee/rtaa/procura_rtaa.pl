% Consulta a procura melhor primeiro parcial
:- consult('../mp/procura_mp_parcial'). 

% Definição do precidado h para a heuristica dinâmica com 1 argumento.
:- dynamic h/1.

% Procura feitas por troços, com várias procuras até encontrar a melhor solução
iniciar_rtaa :-
    % nova hash table para o h dos nós fechados
    ht_new(HFechados),
    % memoriza o h dos nó fechados
    memorizar_h(HFechados).

resolver_rtaa(Estado, NoU, ProfMax) :-
    % Indicando a Profundidade Máxima, resolvemos o problema, 
    % passando o estado, geranddo um conjunto de Explorados 
    resolver(Estado, Explorados, NoU, ProfMax),
    % avaliar NoU passanddo F de U.
    avaliar(NoU, FU),
    % obtemos a heuristica dos nós fechados
    h(HFechados),
    % para cada nó V dos explorados, atualizamos o 
    % seu H em função do F U que é o último. 
    foreach(explorados_enumerar(Explorados, NoV),
            actualizar_h(HFechados, NoV, FU)),
    memorizar_h(HFechados).

memorizar_h(HFechados) :-
    % Limpar qualquer registo
    retractall(h(_)),   
    % passamos o novo valor do h dos Fechados.
    assert(h(HFechados)).

actualizar_h(HFechados, NoV, FU) :-
    % obter g do nó
    no_g(NoV, GV),
    % h(v) = g(v) + h(u) - g(v)
    HV is FU - GV,
    no_estado(NoV, EstadoV),
    ht_put(HFechados, EstadoV, HV).

avaliar(No, F) :-
    no_g(No, G),
    no_estado(No, Estado),
    obter_heuristica(Estado, H),
    F is G + H.

obter_heuristica(Estado, H) :-
    % se o Estado já existir na lista os Fechados 
    % obtemos a heuristica associada.
    % Se não existir, uso a heuristica original.
    h(HFechados),
    ht_get(HFechados, Estado, H),
    !.

obter_heuristica(Estado, H) :-
    heuristica(Estado, H).