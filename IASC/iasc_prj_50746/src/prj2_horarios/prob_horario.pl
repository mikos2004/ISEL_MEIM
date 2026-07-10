%------------------------------------------------------------
% Problema de Agendamento de Horários
% Definição do problema para Hill-Climbing
%------------------------------------------------------------

:- consult(dom_horario).

% Estado: lista de atribuicoes
% atribuicao(Aula, Dia, Hora, Sala)

% Estado inicial
% -----------------
inicio(Estado) :-
    findall(Aula, aula(Aula, _, _, _, _), Aulas),
    atribuir_aleatorio(Aulas, Estado).

% Estado aleatório
% ---------------------
% Atribui as aulas e forma aleatória
estado_aleat(Estado) :-
    % Obter todas as aulas
    findall(Aula, aula(Aula, _, _, _, _), Aulas),
    atribuir_aleatorio(Aulas, Estado).

% Atribuir aulas de forma aleatória
% ---------------------
% atribuir_aleatorio(Aulas, Estado)
atribuir_aleatorio([], []).
atribuir_aleatorio([Aula|Resto], [atribuicao(Aula, Dia, Hora, Sala)|Estado]) :-
    % obter todos os dias
    todos_dias(Dias),
    % obter todas as horas
    todas_horas(Horas),
    % todas as salas
    todas_salas(Salas),
    % random _member(X, List) - escolhe um elemento X da Lista de forma aleatoria
    % obter dia aleatorio
    random_member(Dia, Dias),
    % obter hora aleatorio
    random_member(Hora, Horas),
    % obter sala aleatorio
    random_member(Sala, Salas),
    atribuir_aleatorio(Resto, Estado).

% Objectivo
%-----------------
% Verifica se o horário não tem conflitos
% Não haver conflitos é igual às penalidaes fortes serem 0
objectivo(Estado) :-
    calcular_penalidade_forte(Estado, 0).

% Transição
%---------------------
% Cria um novo estado a partir do Estado com um operador de vizinhança
transicao(Estado, NovoEstado) :-
    % obtem um operador da lista dos Operadores
    random_member(Operador, [mover_aula, trocar_aulas, alterar_sala]),
    % chama Operador(Estado, Novo Estado) para criar NovoEstado
    call(Operador, Estado, NovoEstado).

%-----------------------------
% OPERADORES
%-----------------------------

% Operador 1: Mover uma aula para novo slot
% ---------------------------------------------
% Coloca uma aula num novo dia, hora e sala aleatórios
mover_aula(Estado, NovoEstado) :-
    % Seleciona a aula
    member(atribuicao(Aula, _, _, _), Estado),
    % obter os dias
    todos_dias(Dias),
    % obter as horas
    todas_horas(Horas),
    % obter as salas
    todas_salas(Salas),
    % Obter um novo dia
    random_member(NovoDia, Dias),
    % Obter uma nova Hora para a aula
    random_member(NovaHora, Horas),
    % Obter uma nova sala para aula
    random_member(NovaSala, Salas),
    % Efeturar substituição
    substituir_atribuicao(Estado, Aula, atribuicao(Aula, NovoDia, NovaHora, NovaSala), NovoEstado).

% Operador 2: Trocar duas aulas de lugar
% ---------------------------------------------
% Trocar o horário e a sala entre duas Aulas diferentes.
trocar_aulas(Estado, NovoEstado) :-
    select(atribuicao(Aula1, Dia1, Hora1, Sala1), Estado, EstadoTemp),
    select(atribuicao(Aula2, Dia2, Hora2, Sala2), EstadoTemp, _),
    % verificar que são aulas diferentes
    Aula1 \= Aula2,
    % Trocar os parâmetros das aulas:
    % Usar um Estado temporário para efetuar a primeira troca
    substituir_atribuicao(Estado, Aula1, atribuicao(Aula1, Dia2, Hora2, Sala2), TempEstado),
    % Criar o Novo Estado sobre o Estado temporário
    substituir_atribuicao(TempEstado, Aula2, atribuicao(Aula2, Dia1, Hora1, Sala1), NovoEstado).

% Operador 3: Alterar apenas a sala de uma aula
% ----------------------------------------------------------
% Altera apenas a sala de uma aula, mantendo o horário.
alterar_sala(Estado, NovoEstado) :-
    % Seleciona a aula
    member(atribuicao(Aula, Dia, Hora, _), Estado),
    % Obtem toddas as Salas
    todas_salas(Salas),
    % Obter uma nova sala aleatoriamente
    random_member(NovaSala, Salas),
    % Efetuar substituição
    substituir_atribuicao(Estado, Aula, atribuicao(Aula, Dia, Hora, NovaSala), NovoEstado).

% Substituir atribuição de uma aula
% ----------------------------
% substituir_atribuicao(Estado, Aula, NovaAtrib, NovoEstado)
%   - Estado - estado atual
substituir_atribuicao([], _, _, []).
substituir_atribuicao([atribuicao(A, _, _, _)|Resto], Aula, NovaAtrib, [NovaAtrib|Resto]) :-
    % Ao encontrar a aula que queremos (A = Aula), corta
    % Substitui pela NovaAtrib e mantém o Resto da lista como NovoEstado
    A == Aula, !.
substituir_atribuicao([Atrib|Resto], Aula, NovaAtrib, [Atrib|NovoResto]) :-
    % Mantém a atribuição atual (Atrib) no NovoEstado
    % Continua a procurar no resto da lista
    substituir_atribuicao(Resto, Aula, NovaAtrib, NovoResto).

% Valor
% ------------------------
% Calcula o valor de qualidade de um horário.
% O valor é calculado como: -1 * (PenalidadeForte * 100 + PenalidadeFraca)
%
% "-1" , porque "inverte" a função. Ou seja, muitos conflitos dão um valor 
% muito negativo e poucos conflitos dão um valor pouco negativo. 
%
% Como as Penalidades Fortes são mais importantes que as Fracas, por isso
% multiplicamos por 100 para valorizar o peso que têm.
%
% Quanto maior o valor final, melhor a qualidade do horário.
valor(Estado, Valor) :-
    calcular_penalidade_forte(Estado, PenalidadeForte),
    calcular_penalidade_fraca(Estado, PenalidadeFraca),
    Valor is -1 * (PenalidadeForte * 100 + PenalidadeFraca).

% Cálculo de penalidades fortes (conflitos)
% ------------------------------------------------
% calcular_penalidade_forte(Estado, Penalidade)
% Penalidades fortes são sobreposições (de sala, hora, professores).
calcular_penalidade_forte(Estado, Penalidade) :-
    % Acresentamos 1 à lista de Conflitos, caso existam
    findall(1, (
        member(atribuicao(A1, D1, H1, S1), Estado),
        member(atribuicao(A2, D2, H2, S2), Estado),
        % Verificar que são aulas diferentes
        A1 \= A2,
        % verificar a existência de conflito
        conflito_forte(D1, H1, S1, A1, D2, H2, S2, A2)
    ), Conflitos),
    % Penalidade é a quantidade de Conflitos existentes
    length(Conflitos, Penalidade).

%------------------------------------
% Tipos de conflitos fortes
%------------------------------------

% Mesma sala no mesmo horário
conflito_forte(Dia, Hora, Sala, Aula1, Dia, Hora, Sala, Aula2) :-
    Aula1 \= Aula2.

% Mesma turma no mesmo horário  
conflito_forte(Dia, Hora, _, Aula1, Dia, Hora, _, Aula2) :-
    Aula1 \= Aula2,
    turma_aula(Aula1, Turma),
    turma_aula(Aula2, Turma).

% Mesmo professor no mesmo horário
conflito_forte(Dia, Hora, _, Aula1, Dia, Hora, _, Aula2) :-
    Aula1 \= Aula2,
    professor_aula(Aula1, Prof),
    professor_aula(Aula2, Prof).

% Sala inadequada para a turma
conflito_forte(_, _, Sala, Aula1, _, _, _, _) :-
    turma_aula(Aula1, Turma),
    \+ sala_adequada(Sala, Turma).

% Cálculo de penalidades fracas (preferências)
% ------------------------------------------------------
% Calcula a penalidade fraca baseada em preferências não satisfeitas.
% Portanto, apenas preferências negativas (horários indesejados) é que contam.

calcular_penalidade_fraca(Estado, Penalidade) :-
    findall(Peso, (
        % Para cada atribuição
        member(atribuicao(Aula, Dia, Hora, _), Estado),
        % Obtemos o professor
        professor_aula(Aula, Prof),
        % verificamos as preferencias do professor
        (prof_pref(Prof, Dia, Hora, Peso) -> true; Peso = 0),
        % Apenas preferências negativas
        Peso < 0
    ), Penalidades),
    % Se a lista de penalidaeds está vazia
    (Penalidades = [] -> 
        % Então não há penalidades
        Penalidade = 0
    ; % Caso contrário:
        % Soma-se as penalidades
        sum_list(Penalidades, Soma),
        % Converte-se para positivo
        Penalidade is -Soma
    ).