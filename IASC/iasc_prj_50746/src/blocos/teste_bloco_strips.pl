:- consult('src/lib/strips/strips.pl').
:- consult('blocos_strips.pl').

teste :-
    Estado = [mesa(a), sobre(b,a), livre(b)],
    ListaObj = [mesa(b), sobre(a,b), livre(a)],
    planear(Estado, ListaObj, Plano),
    writeln(Plano).