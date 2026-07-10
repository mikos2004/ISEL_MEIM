% Fronteira Melhor primeiro~

% Inicia-se uma fronteira dado um Nó
fronteira_iniciar(Fronteira, No) :-
    % (Heap que é a lista ordenada, Prioridade, Chave a ligar à prioridade)
    singleton_heap(Fronteira, 0, No).
    

% Dado um Nó e uma Fronteira, obtem-se o Resto da Fronteira.
fronteira_obter(Fronteira, No, RestoFronteira) :-
    get_from_heap(Fronteira, _, No, RestoFronteira).
    

% Insere-se um novo Nó na Fronteira, com o valor F de um Nó e 
% originamos uma Nova Fronteira.
% F -> valor de avaliação do Nó
fronteira_inserir(Fronteira, F, No, NovoFronteira) :-
    add_to_heap(Fronteira, F, No, NovoFronteira).
    