:- consult(def_amb).


% estado(Posicao, SobreviventesResgatados, Chaves, Bateria, Tempo).

% Gerar todas as transições válidas
transicao_valida(Estado, NovoEstado, Acao, Custo) :-
    accao(Estado, Acao, NovoEstado, Custo).

%------------------------------------------------------------
% Definição das ações possíveis
%------------------------------------------------------------

% Mover entre nós

accao(
    % Estado
    estado(Pos, Sobreviv, Chaves, Bateria, Tempo),
    % Acao (Mover da Pos atual para Dest)
    mover(Pos, Dest),
    % Novo Estado (Dest passa a ser Pos atual) e muda o valor de bateria e tempo
    estado(Dest, Sobreviv, Chaves, BateriaNova, TempoNovo),
    % Custo
    Custo
) :-
    % Pré-Condições para poder executar a ação

    % verifica se está Pos e Dest estão conectados
    conectado(Pos, Dest, Dist, TipoLigacao),
    % verifica se o robô tem bateria
    Bateria > 0,
    % verifica se o robô pode passar pela ligação
    pode_passar(TipoLigacao, Chaves),
    % calcula o custo do movimento baseado no tipo de ligação e distância
    custo_movimento(TipoLigacao, Dist, Custo),

    % Efeitos da Bateria
    % --------------------------
    BateriaNova is Bateria - Custo,
    % Verifica se ainda há bateria suficiente após o movimento
    BateriaNova >= 0,
    TempoNovo is Tempo + Custo.

% Resgatar sobrevivente -----------------------
accao(
    % estado
    estado(Pos, Sobreviv, Chaves, Bateria, Tempo),
    % acão (resgatar um sobrevivente)
    resgatar(Sobrevivente),
    % novo estado (Com lista dos Sobreviventes atualizados)
    estado(Pos, NovoSobreviv, Chaves, Bateria, TempoNovo),
    % custo
    Custo
) :-
    % Pré-Condições para poder executar a ação

    % Verifica se há um sobrevivente na posição atual com este nome (Sobrevivente)
    sobrevivente(Pos, Sobrevivente, Deadline, Peso),
    % Verifica se o sobrevivente ainda não foi resgatado
    \+ member(Sobrevivente, Sobreviv),

    % Efeitos

    % Tempo do resgate faz atualziar o Tempo
    TempoNovo is Tempo + 1,
    % Calcula o Custo devido à penalização do Deadline
    atraso_penalizacao(Tempo, Deadline, Peso, Custo),
    % Adiciona o sobrevivente à lista de sobreviventes resgatados
    append(Sobreviv, [Sobrevivente], NovoSobreviv).

% Apanhar chave
accao(
    % estado
    estado(Pos, Sobreviv, Chaves, Bateria, Tempo),
    % acao (Apanhar chave)
    apanhar(Chave),
    % estado
    estado(Pos, Sobreviv, NovoChaves, Bateria, TempoNovo),
    % Custo
    1
) :-
    % pré-condições

    % verificar se a chave existe
    chave(Pos, Chave),
    % verificar se o robô aina não apanhou a chave
    \+ member(Chave, Chaves),

    % Efeitos

    % tempo atualizado por apanhar a chave
    TempoNovo is Tempo + 1,
    % adicionar a chave à lista de Chaves do Robô
    append(Chaves, [Chave], NovoChaves).

% Recarregar bateria
accao(
    % estado (ignora-se o valor da Bateria)
    estado(Pos, Sobreviv, Chaves, _, Tempo),
    % acao
    recarregar,
    % bateria volta para o valor máximo (12)
    estado(Pos, Sobreviv, Chaves, 12, TempoNovo),
    % custo de recarregar
    2
) :-
    % verificar se o robô está numa estação
    estacao(Pos),

    % Efeitos

    % tempo atualiza devido ao atraso causado pela recarga
    TempoNovo is Tempo + 2.

% Segurar túneis arriscados (reduz custo futuro de ligação)
accao(
    % Estado
    estado(Pos, Sobreviv, Chaves, Bateria, Tempo),
    % segurar o túnel entre Pos e Dest
    segurar_tunel(Pos, Dest),
    % novo estado
    estado(Pos, Sobreviv, Chaves, BateriaNova, TempoNovo),
    % Custo
    3
) :-
    % Pré-Condições

    % verificar se a ligação entre Pos e Dedst é arriscada
    conectado(Pos, Dest, _, arriscado),
    % verificar se há bateria suficiente para segurar o túnel (>= 3)
    Bateria >= 3,

    % Efeitos

    % reduz a bateria
    BateriaNova is Bateria - 3,
    % atualiza o tempo
    TempoNovo is Tempo + 3,
    % verifica se o túnel não está segurado
    \+ tunel_segurado(Pos, Dest),
    % adiciona ao final da base de dados o túnel para marcá-lo como segurado
    assertz(tunel_segurado(Pos, Dest)).



% Predicados auxiliares

% O robô pode passar na ligação?
% pode_passar(TipoLigacao, Chaves)
pode_passar(normal, _).
pode_passar(arriscado, _).
pode_passar(estacao, _).
pode_passar(porta_trancada(Chave), Chaves) :- member(Chave, Chaves).

% Custo de movimento (depende do tipo e se túnel foi segurado)
% custo_movimento(TipoLigacao, Dist, Custo)
custo_movimento(arriscado, Dist, Custo) :-
    % if, then, else
    (tunel_segurado(_, _) -> 
    % se algum túnel foi segurado, o custo é metade da distância
        Custo is Dist / 2 
    ;
    % se não, o custo é o dobro pelo risco 
        Custo is Dist * 2
    ).

% situações que o custo é igual a Distância
custo_movimento(normal, Dist, Dist).
custo_movimento(estacao, Dist, Dist).
custo_movimento(porta_trancada(_), Dist, Dist).

% Penalização por atraso
atraso_penalizacao(TempoAtual, Deadline, Peso, Custo) :-
    (TempoAtual =< Deadline ->
        % se resgatou a tempo (dentro do prazo)
        Custo = 1 
    ;
        % resgate com atraso

        % calcula quanto tempo passou do prazo
        Atraso is TempoAtual - Deadline,
        % custo com penalização = custo base + (atraso × peso)
        Custo is 1 + Atraso * Peso
    ).

% Reset da base de dados com os túneis segurados
reset_tuneis_segurados :-
    retractall(tunel_segurado(_, _)).
