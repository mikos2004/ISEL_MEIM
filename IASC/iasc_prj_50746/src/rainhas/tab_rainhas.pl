%------------------------------------------------------------
% Gestão do tabuleiro para o problema das raínhas
%------------------------------------------------------------

% Dimensão do tabuleiro
dim_tabuleiro(8).

% Gerar tabuleiro aleatório
% -Tab: Tabuleiro gerado
tabuleiro_aleatorio(Tab) :-
    dim_tabuleiro(DimTab),
    MaxTab is DimTab - 1,
    findall(Linha, 
            (between(0, MaxTab, _), random_between(0, MaxTab, Linha)), 
            Tab).

% Obter índice de uma coluna do tabuleiro (admite backtracking)
% +Tab: Tabuleiro
% -Col: Coluna gerada
coluna_tabuleiro(Tab, Col) :-
    max_tab(Tab, MaxTab),
    between(0, MaxTab, Col).

% Verifica a existência de uma ameaça entre posições (Linha, Coluna)
% +Tab: Tabuleiro
% +Ameaca: Par de posições Pos1-Pos2
ameaca(Tab, Ameaca) :-
    Ameaca = (Linha1, Col1)-(Linha2, Col2),
    nth0(Col1, Tab, Linha1), 
    nth0(Col2, Tab, Linha2), 
    Col1 < Col2, 
    (Linha1 = Linha2; abs(Col1 - Col2) =:= abs(Linha1 - Linha2)).

% Obter número de ameaças num tabuleiro
% +Tab: Tabuleiro
% -NumAmeacas: Número de ameaças
num_ameacas(Tab, NumAmeacas) :-
    findall(Ameaca, ameaca(Tab, Ameaca), Ameacas),
    length(Ameacas, NumAmeacas).    
    
% Mover rainha numa coluna do tabuleiro
% +Tab: Tabuleiro
% +Col: Coluna onde mover
% -NovoTab: Novo tabuleiro
mover_rainha(Tab, Col, NovoTab) :-
    nth0(Col, Tab, Linha),
    max_tab(Tab, MaxTab),
    nova_linha(MaxTab, Linha, NovaLinha),
    alterar_rainha(Tab, Col, NovaLinha, NovoTab).

% Gerar índice de nova linha de um tabuleiro por incremento,
% com rotação após índice máximo para índice 0
% +MaxTab: Índice máximo do tabuleiro
% +Linha: Linha actual
% -NovaLinha: Nova linha
nova_linha(MaxTab, MaxTab, 0) :- !.

nova_linha(_, Linha, NovaLinha) :-
    NovaLinha is Linha + 1.

% Alterar posição da raínha no tabuleiro
% +Tab: Tabuleiro
% +Col: Índice da coluna
% +Linha: Índice da linha
% -NovoTab: Novo tabuleiro
alterar_rainha(Tab, Col, Linha, NovoTab) :-
    nth0(Col, Tab, _, RestoTab),
    nth0(Col, NovoTab, Linha, RestoTab).

% Mostrar tabuleiro
% +Tab: Tabuleiro
mostrar_tabuleiro(Tab) :-
    max_tab(Tab, MaxTab),
    mostrar_tabuleiro(Tab, MaxTab).
    
mostrar_tabuleiro([], _).
mostrar_tabuleiro([Col | RestoTab], MaxTab) :-
    mostrar_linha(Col, MaxTab),
    mostrar_tabuleiro(RestoTab, MaxTab).

% Mostrar linha do tabuleiro
% +Col: Índice da coluna
% +MaxTab: Índice máximo do tabuleiro
mostrar_linha(Col, MaxTab) :-
    forall(between(0, MaxTab, X), 
        (X = Col -> write('R '); write('. '))
    ),
    nl.

% Obter maior índice do tabuleiro
% +Tab: Tabuleiro
% -MaxTab: Índice máximo do tabuleiro
max_tab(Tab, MaxTab) :-
    length(Tab, DimTab),
    MaxTab is DimTab - 1.

    
    


    