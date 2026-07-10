% Usar UTF-8
:- encoding(utf8).

% Imports/Consults

:-consult("prob_amb2d.pl").

%:- consult("src/lib/pee/mp/procura_custo_unif.pl").
%:- consult("src/lib/pee/mp/procura_aa.pl").
:- consult("src/lib/pee/mp/procura_sofrega.pl").
%:- consult("src/lib/pee/mp/procura_mp_parcial.pl").

teste :- 
    iniciar_ambiente(8),
    inicio(Estado),
    time(resolver(Estado, Solucao)) -> % se resolver então:
        mostrar_ambiente(Solucao)
        ; % se não/ caso contrário
        writeln("Solução não encontrada.").