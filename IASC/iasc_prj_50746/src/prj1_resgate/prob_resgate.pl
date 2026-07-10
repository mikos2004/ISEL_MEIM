:- consult("simul_amb.pl").

% Transição entre estados
%------------------------------------------------------------
% Usa o predicado transicao_valida do simulador.
% Cada transição representa uma ação executável no ambiente.

transicao(Estado, NovoEstado, Accao, CustoTrans) :-
    transicao_valida(Estado, NovoEstado, Accao, CustoTrans).

% Estado inicial
inicio(Estado) :-
    estado_inicial(Estado).

% Objetivo
objetivo_problema(Estado) :-
    objetivo(Estado).

% Heurística
%------------------------------------------------------------
% A heurística define o custo restante até cumprir a missão.
% A heuristica combina:
%   - a distância até o nó de um sobrevivente ainda não resgatado
%   - as penalizações causadas pelas deadlines
%   - o custo estimado para regressar à entrada

heuristica(estado(Pos, Sobreviv, _, _, Tempo), H) :-
    % obtem a lista completa de sobreviventes
    findall(S, sobrevivente(_, S, _, _), Todos),
    % faz uma lista com os sobreviventes ainda por resgatar
    subtract(Todos, Sobreviv, Restantes),

    % Decide qual estratégia de heurística usar
    (Restantes = [] ->
        % se já resgatou todos, só falta voltar à entrada
        distancia_ate(Pos, entrada, D),
        H is D
    ;
        % se ainda faltam sobreviventes:
        % Calcula heurística considerando os sobreviventes restantes
        heuristica_sobreviventes(Pos, Restantes, Tempo, H)
    ).


% Cálculo heurístico auxiliar
%------------------------------------------------------------
% Heurística baseada no sobrevivente mais próximo

heuristica_sobreviventes(Pos, Restantes, TempoAtual, H) :-
    % Para cada sobrevivente restante, calcula uma estimativa de custo
    findall(Estimativa,
        (
            % Verifica se o sobrevivente está na lista dos Restantes
            member(S, Restantes),
            % Obtém as informações do sobrevivente: localização, deadline, peso
            sobrevivente(No, S, Deadline, Peso),
            % Calcula a distância da posição atual até o sobrevivente
            distancia_ate(Pos, No, D),
            % Calcula a penalização se chegar ao sobrevivente no tempo atual + distância
            atraso_penalizacao(TempoAtual + D, Deadline, Peso, Penal),
            % Estimativa total = distância + penalização esperada
            Estimativa is D + Penal
        ),
        % as Estimativas ficam numa lista
        ListaEstimativas),
    
    % obtém a menor estimativa que é o caso mais otimista)
    min_list(ListaEstimativas, H).


% Distância entre dois nós
%------------------------------------------------------------
distancia_ate(A, B, D) :-
    (conectado(A, B, Dist, _) ->
        % se existe uma ligação direta entre A e B: usa a distância real
        D = Dist
    ;
        % Se não há ligação direta, assume uma distância grande mas finita
        D = 10
    ).
