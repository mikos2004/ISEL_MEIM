%------------------------------------------------------------
% Teste do Problema da Criação de Horários
%------------------------------------------------------------

:- encoding(utf8).
:- consult('../lib/optim/hc').
:- consult('../lib/optim/hcr').
:- consult(prob_horario).

/*mostrar_estado(Estado, Iteracao) :-
    valor(Estado, Valor),
    calcular_penalidade_forte(Estado, PF),
    calcular_penalidade_fraca(Estado, PFR),
    format("Iteração ~w: Valor=~w, PF=~w, PFR=~w~n", [Iteracao, Valor, PF, PFR]).
*/

% Mostrar resultado
mostrar_resultado(Info, Solucao) :-
    nl, writeln(Info),
    nl, writeln('Horário:'),
    mostrar_horario(Solucao),
    nl,  
    valor(Solucao, Valor),
    calcular_penalidade_forte(Solucao, PF),
    calcular_penalidade_fraca(Solucao, PFR),
    format("Valor: ~w~n", [Valor]),
    format("Penalidade Forte: ~w~n", [PF]),
    format("Penalidade Fraca: ~w~n", [PFR]).


mostrar_horario(Atribuicoes) :-
    nl,
    format("~w~t~12+ ~w~t~8+ ~w~t~8+ ~w~n", ['Dia', 'Hora', 'Aula', 'Sala']),
    writeln("---------------------------------------------------------"),
    % Converter para termos ordenáveis, ordenar, e reconverter
    maplist(atribuicao_para_chave, Atribuicoes, AtribuicoesComChave),
    keysort(AtribuicoesComChave, OrdenadasComChave),
    maplist(chave_para_atribuicao, OrdenadasComChave, AtribuicoesOrdenadas),
    forall(member(Atrib, AtribuicoesOrdenadas),
           (   Atrib = atribuicao(Aula, Dia, Hora, Sala),
               format("~w~t~12+ ~w~t~8+ ~w~t~8+ ~w~n", [Dia, Hora, Aula, Sala])
           )).

% Converter atribuicao para termo ordenável Chave-atribuicao
atribuicao_para_chave(atribuicao(Aula, Dia, Hora, Sala), Chave-atribuicao(Aula, Dia, Hora, Sala)) :-
    valor_dia(Dia, ValDia),
    Chave is ValDia * 100 + Hora.  % Dia mais significativo que Hora

% Reconverter de volta para atribuicao
chave_para_atribuicao(_-Atribuicao, Atribuicao).

% Mapear dias para valores numéricos para ajudar a ordenar
valor_dia(segunda, 1).
valor_dia(terca, 2).
valor_dia(quarta, 3).
valor_dia(quinta, 4).
valor_dia(sexta, 5).

% Teste do algoritmo Hill-Climbing
/*teste_hc :-
    inicio(Estado),
    hc(Estado, Solucao, 500),  % 500 iterações
    mostrar_resultado("Hill-Climbing:", Solucao).*/

% Teste do algoritmo Hill-Climbing com reinícios aleatórios
teste_hcr :-
    inicio(Estado),
    hcr(Estado, Solucao, 200, 20),  % 200 iterações, 20 reinícios
    mostrar_resultado("Hill-Climbing com reinícios aleatórios:", Solucao).