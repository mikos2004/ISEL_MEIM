% DEFINIÇÃO DO PROBLEMA
% ----------------------

% Representação da mesa e da pilha
% Pilha-Mesa
% Pliha: [Bloco | RestoBlocos]

% Empilhar um bloco numa mesa com uma pilha
empilhar(Pilha-Mesa, [Bloco | Pilha]-NovaMesa):-
    select(Bloco, Mesa, NovaMesa). % Verdade se Mesa sem o Bloco for igual a NovaMEsa

% desempilhar o bloco da pilha na mesa
desempilhar([Bloco | RestoPilha]-Mesa, 
        RestoPilha-[Bloco | Mesa]).
    
