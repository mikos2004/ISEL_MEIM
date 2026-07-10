% Gestão de Explorados do Algoritmo Melhor Primeiro

% Inicia conjunto de Explorados com um Nó
explorados_iniciar(Explorados):- % Iniciar sem passar nó
    ht_new(Explorados).

explorados_iniciar(Explorados, No):-
    explorados_iniciar(Explorados), % evita repetir o código de cima
    explorados_inserir(Explorados, No).

% Dado um conjunto de Explorados e um No, produz o No Explorado.
explorados_obter(Explorados, No, NoExp):-
    no_estado(No, Estado), % predicado que ao receber um No dá o seu Estado 
    ht_get(Explorados, Estado, NoExp).

% Inserir um No num conjunto de Explorados
explorados_inserir(Explorados, No):-
    no_estado(No, Estado),
    ht_put(Explorados, Estado, No). % Colocar no Explorados, associado ao Estado o No

explorados_enumerar(Explorados, NoExp):-
    ht_gen(Explorados, _, NoExp).
