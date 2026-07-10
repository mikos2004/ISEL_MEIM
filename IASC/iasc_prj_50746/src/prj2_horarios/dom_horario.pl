%------------------------------------------------------------
% Domínio do Problema da Criação de Horários
% Definição das entidades: dias, hora, aulas, turmas, professores, salas
%------------------------------------------------------------

% Dia
% -------------
%   - nome - nome do dia da semana
dia(segunda).
dia(terca).
dia(quarta).
dia(quinta).
dia(sexta).

% Hora
% --------
% Cada hora representa um período de 2 horas.
%   - hora - hora quem o segmento começa.

hora(8).  % 8h-10h
hora(10). % 10h-12h  
hora(14). % 14h-16h
hora(16). % 16h-18h

% Salas disponíveis
% -----------------------
% sala(Nome, Capacidade)
%   - Nome da Sala
%   - Capacidade - quantos alunos a sala suporta
sala(sala_a101, 30).
sala(sala_a102, 25).
sala(sala_b201, 40).
sala(sala_b202, 35).
sala(sala_c301, 50).

% Professores
% ------------------
%   - nome - Nome do professor
professor(prof_joao).
professor(prof_maria).
professor(prof_carlos).
professor(prof_ana).

% Turmas
% ---------------
%   - nome - Nome da turma
%   - tamanho - nº de alunos
turma(turma_1, 25).
turma(turma_2, 30).
turma(turma_3, 20).

% Aulas
% -------------------
% aula(Id, Turma, Professor, Tipo, Duracao)
%   - Id - Id da aula,
%   - turma - Nome da Turma
%   - Professor - Nome do prof
%   - Tipo - tipo da Aula
%   - Duracao - Duração em número de slots (cada slot = 2 horas)
aula(a1, turma_1, prof_joao, teorica, 1).
aula(a2, turma_1, prof_maria, pratica, 1).
aula(a3, turma_2, prof_carlos, teorica, 1).
aula(a4, turma_2, prof_ana, pratica, 1).
aula(a5, turma_3, prof_carlos, teorica, 1).
aula(a6, turma_3, prof_ana, pratica, 1).

% Preferências de professores
% -----------------------------------
% prof_pref(Professor, Dia, Hora, Peso)
%   - Professor - nome do professor
%   - Dia - dia que prefere
%   - Hora - hora que prefere
%   - Peso - valor da preferência 
%       Peso: 1 = preferido, 
%            -1 = indesejado, 
%             0 = neutro
prof_pref(prof_joao, segunda, 8, 1).
prof_pref(prof_joao, sexta, 16, -1).
prof_pref(prof_maria, terca, 14, 1).
prof_pref(prof_maria, quarta, 8, -1).

% Obter todas as salas
todas_salas(Salas) :- 
    findall(Sala, sala(Sala, _), Salas).

% Obter todos os dias
todos_dias(Dias) :- 
    findall(Dia, dia(Dia), Dias).

% Obter todas as horas
todas_horas(Horas) :- 
    findall(Hora, hora(Hora), Horas).

% Obter capacidade de uma sala
capacidade_sala(Sala, Capacidade) :- 
    sala(Sala, Capacidade).

% Obter tamanho de uma turma
tamanho_turma(Turma, Tamanho) :- 
    turma(Turma, Tamanho).

% Verificar se sala tem capacidade para turma
sala_adequada(Sala, Turma) :-
    capacidade_sala(Sala, Cap),
    tamanho_turma(Turma, Tam),
    Tam =< Cap.

% Duração de uma aula em slots
duracao_aula(Aula, Duracao) :- 
    aula(Aula, _, _, _, Duracao).

% Verificar que Turma tem determinada aula
turma_aula(Aula, Turma) :- 
    aula(Aula, Turma, _, _, _).

% Professor de uma determinada aula
professor_aula(Aula, Professor) :- 
    aula(Aula, _, Professor, _, _).