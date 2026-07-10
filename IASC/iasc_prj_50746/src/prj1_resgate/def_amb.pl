%------------------------------------------------------------
% DEFINIÇÃO DO AMBIENTE: Missão de Resgate no Complexo Subterrâneo
%------------------------------------------------------------
%
% ESTADO DO AGENTE: 
%	- Posição atual 
%	- Conjunto de sobreviventes resgatados 
%	- Chaves apanhadas - Nível de bateria (máx: 12) 
%	- Tempo acumulado 
%
% AÇÕES DISPONÍVEIS:
%	- Mover entre nós (consome bateria/tempo) 
%	- Resgatar sobreviventes (+ penalização se após deadline) 
%	- Apanhar chaves 
%	- Destrancar portas 
%	- Recarregar bateria em estações 
%	- Segurar túneis arriscados (reduz custo futuro) 
%	
% OBJETIVO:
%	- Resgatar TODOS os sobreviventes e voltar à ENTRADA minimizando: 
%		Tempo total + Penalizações por atraso 
%
% MAPA EXEMPLO:
%
%	NÓS: 
%		Entrada, C1, C2, C3, C4, C5, C6, C7, EstaçãoA, EstaçãoB 
%	
%	CARACTERÍSTICAS ESPECIAIS: 
%		- Túneis arriscados: C3-C4, C6-C7 (podem ser segurados) 
%		- Porta trancada: C5-C6 (precisa chave kA em C2) 
%		- Estações de recarga: EstaçãoA (C3), EstaçãoB (C5) 
%		
% SOBREVIVENTES (com deadlines): 
%	s1 (C1: deadline=20, peso=3) 
%	s2 (C4: deadline=18, peso=5) (mais urgente) 
%	s3 (C6: deadline=25, peso=2) 
%	s4 (C7: deadline=30, peso=4)
%------------------------------------------------------------

% Nós/locais do mapa
%----------------------------
%   - entrada - entrada que é o ponto onde o robot começa e deve terminar
%   - c1 a c7 - cavernas onde há sobreviventes/obstáculos
%   - estacaoA e estacaoB - estacções de recarga que a caverna tem
nos([entrada, c1, c2, c3, c4, c5, c6, c7, estacaoA, estacaoB]).

% Ligação entre nós
%----------------------
% ligacao(No1, No2, CustoBase, Tipo)
%   - No1 e No2 - nós a ligar
%   - CustoBase - custo da ligação
%   - Tipo - tipo da ligação:
%                   [normal, arriscado, porta_tranca(chave), estacao]
ligacao(entrada, c1, 3, normal).
ligacao(c1, c2, 4, normal).
ligacao(c2, c3, 2, normal).
ligacao(c3, c4, 5, arriscado).
ligacao(c4, c5, 3, normal).
ligacao(c5, c6, 2, porta_trancada(kA)).
ligacao(c6, c7, 4, arriscado).
ligacao(c3, estacaoA, 1, estacao).
ligacao(c5, estacaoB, 1, estacao).

% Tornar ligações bidirecionais
%-------------------------------------
% Ao conectar o caminho podemos dizer que ele é
% bidirecional: Se há uma ligação de A->B
% existe também B-> A
conectado(A, B, C, T) :- 
    ligacao(A, B, C, T).
conectado(A, B, C, T) :- 
    ligacao(B, A, C, T).


% sobrevivente(No, Nome, Deadline, Peso)
%--------------------------------------------
%   - No: Nó onde se encontram
%   - Nome: Nome do sobrevivente
%   - Deadline: tempo que tem para ser salvo
%   - Peso: Peso associado ao resgate
sobrevivente(c1, s1, 20, 3).
sobrevivente(c4, s2, 18, 5).
sobrevivente(c6, s3, 25, 2).
sobrevivente(c7, s4, 30, 4).

% Chaves
% --------------------
% chave(pos, nome)
%   - pos: posição da chave
%   - nome: nome da chave
chave(c2, kA).

% Estações de recarga
%   - servem para recarregar a Bateria
% ------------------------
% estacao(nome)
%   - nome: nome da estação
estacao(estacaoA).
estacao(estacaoB).

% Estado inicial
% ----------------------
% estado(Posicao, SobreviventesResgatados, Chaves, Bateria, Tempo)
%   - Bateria: bateria do robô
%   - Tempo: tempo decorrido
estado_inicial(estado(entrada, [], [], 12, 0)).

% Objetivo: todos resgatados e agente na entrada
objetivo(estado(entrada, Sobreviventes, _, _, _)) :-
    % criamos a lista Todos que após o findall
    % filtra o nome "S" de todos os predicados sobrevivente
    findall(S, sobrevivente(_, S, _, _), Todos),
    % Verifica se Todos é subconjunto da lista de SobreviventesResgatados
    %   - se for verdade, alcançou-se o objetivo
    subset(Todos, Sobreviventes).


%:- dynamic tunel_segurado/2.