%------------------------------------------------------------
% Algoritmo Hill-Climbing com reinícios aleatórios
%
% hcr(+MelhorEstadoActual, -MelhorEstadoFinal, +NIter, +NRep)
%
% MelhorEstadoActual: Melhor estado actual
% MelhorEstadoFinal: Melhor estado obtido
% NIter: Número de iterações
% NRep: Número de repetições
%------------------------------------------------------------

:- consult(hc).

% Fim das reptições
hcr(MelhorEstado, MelhorEstado, _, 0).

% Repetir procuras com reinícios aleatórios
hcr(MelhorEstadoActual, MelhorEstadoFinal, NIter, NRep) :-
    estado_aleat(EstadoInicial),
    hc(EstadoInicial, MelhorEstado, NIter), % obter melhor estado c/ nº ded iter
    manter_melhor(MelhorEstadoActual, MelhorEstado, MelhorEstadoN),
    NovoNRep is NRep - 1,
    hcr(MelhorEstadoN, MelhorEstadoFinal, NIter, NovoNRep).

% Manter o melhor estado de dois estados
manter_melhor(Estado1, Estado2, MelhorEstado) :-
    valor(Estado1, Aval1),
    valor(Estado2, Aval2),
    (
        Aval1 > Aval2 -> 
            MelhorEstado = Estado1 ;
            MelhorEstado = Estado2           
    ).
