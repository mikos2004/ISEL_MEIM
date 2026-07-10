"""
Exercise 1: The Autograd Engine
================================
Every neural network learns through gradients — numbers that say
"nudge this parameter up a bit" or "push that one down." Modern
frameworks compute gradients automatically. Here, you build that
machinery yourself, from scratch.

You will implement a scalar automatic differentiation engine: a Value
class that records every computation and can walk backward through the
graph to compute derivatives via the chain rule.

This is the same idea behind PyTorch's autograd — just transparent.

At the end, you'll also build a simple character tokenizer: the bridge
between human text and the integer sequences that neural networks consume.
"""

import math


# == THINK (write your answers on paper before coding) =========
#
# Consider the expression:   c = a * b + a     (with a=2, b=3)
#
#  1. What is the value of c?
#  2. Draw the computation graph (nodes = values, edges = operations).
#     Hint: there is a multiply, then an add. How many edges
#     arrive at 'a'?
#  3. Using the chain rule, what is dc/da?  What is dc/db?
#     (Be careful — 'a' participates in TWO operations.)
#
# Write your answers down. You will check them in Test 5.
# ==============================================================


class Value:
    """A scalar value that tracks how it was computed.

    Every Value stores:
      .data         — the number itself
      .grad         — d(loss)/d(this), filled by backward()
      ._children    — the Values used to compute this one
      ._local_grads — d(this)/d(each child)  [partial derivatives]
    """
    __slots__ = ('data', 'grad', '_children', '_local_grads')

    def __init__(self, data, children=(), local_grads=()):
        self.data = data                    # valor deste nó calculado durante a transmissão
        self.grad = 0                       # derivada da perda em relação a este nó, calculada na retropropagação
        self._children = children           # filhos deste nó no grafo
        self._local_grads = local_grads     # derivada local deste nó em relação aos seus filhos

    # -- TODO 1: Addition and Multiplication -----------------------
    #
    # Return a new Value whose .data is the result of the operation.
    # Set children=(self, other) and local_grads to the partial
    # derivatives of the output with respect to each input.
    #
    # You must derive the local gradients yourself:
    #   If out = a + b,  what is d(out)/da?  d(out)/db?
    #   If out = a * b,  what is d(out)/da?  d(out)/db?
    #
    # Handle the case where 'other' is a plain number (int/float)
    # by wrapping it in a Value first.

    def __add__(self, other):
        # Verificar se other é uma instancia de Value
        other = other if isinstance(other, Value) else Value(other)
        
        data = self.data + other.data
        children = (self, other)
        
        # (derivada de self, derivada de other)
        grad = (1, 1) 

        return Value(data, children, grad)

    def __mul__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        
        data = self.data * other.data
        children = (self, other)
        grad = (other.data, self.data)

        return Value(data, children, grad)
        

    # -- TODO 2: Unary operations ----------------------------------
    #
    # Same pattern: return a new Value with correct data and the
    # local gradient.  For unary ops there is only one child (self).
    #
    # Derive each derivative yourself:
    #   x ** n    ->  d/dx = ?       (n is a constant, not a Value)
    #   log(x)    ->  d/dx = ?
    #   exp(x)    ->  d/dx = ?
    #   relu(x)   ->  d/dx = ?       (relu(x) = max(0, x))

    def __pow__(self, n):     # n is a plain number, not a Value        
        data = self.data ** n
        children = (self,)
        grad = (n * self.data ** (n - 1),)

        return Value(data, children, grad)

    def log(self):
        data = math.log(self.data)
        children = (self,)
        grad = (1/self.data,)

        return Value(data, children, grad)

    def exp(self):
        data = math.exp(self.data)
        children = (self,)
        grad = (math.exp(self.data),)

        return Value(data, children, grad)

    def relu(self):
        data = max(0, self.data)
        children = (self,)
        grad = (float(self.data>0),)

        return Value(data, children, grad)


    def tanh(self):
        data = math.tanh(self.data)
        children = (self,)
        grad = (1 - math.tanh(self.data)**2,)

        return Value(data, children, grad)

    # PROVIDED: operator wiring (uses your __add__ and __mul__)
    def __neg__(self): return self * -1
    def __radd__(self, other): return self + other
    def __sub__(self, other): return self + (-other)
    def __rsub__(self, other): return other + (-self)
    def __rmul__(self, other): return self * other
    def __truediv__(self, other): return self * other**-1   # a / b = a * (b⁻¹)
    def __rtruediv__(self, other): return other * self**-1

    # -- TODO 3: Backward pass ------------------------------------
    #
    # Compute the gradient of every node in the graph with respect
    # to this node (self).
    #
    # Algorithm:
    #   1. Build a topological ordering of all nodes reachable from
    #      self (children come before parents). Use DFS + a visited set.
    #   2. Set self.grad = 1  (the derivative of a value w.r.t. itself)
    #   3. Walk the ordering in REVERSE. For each node v, propagate
    #      v.grad to each of its children via the chain rule:
    #        child.grad += local_grad * v.grad
    #
    # Why +=  and not  = ?
    # Think about a node that feeds into two different operations.
    # Its gradient is the SUM of contributions from both paths.

    # Retropropagação
    def backward(self):
            topo = []
            # set() -> Diferencia-se de uma lista, pois não aceita repetidos
            visited = set() 
            def build_topo(v):
                if v not in visited:            # Se não foi visitado
                    visited.add(v)              # Marca como visitado
                    for child in v._children:   # Percorre os filhos desse nó "v"
                        build_topo(child)       # Constrói a ordem topológica recursivamente
                    topo.append(v)              # Depois de percorrer os filhos, acresenta o nó à ordem
            build_topo(self) # É passado um nó
            self.grad = 1    # Na retropropagação, começamos com a derivada do nó final = 1 (derivada dele mesmo).
            for v in reversed(topo): # Percorre do fim para o início
                for child, local_grad in zip(v._children, v._local_grads):
                    child.grad += local_grad * v.grad # regra da cadeia


# ==============================================================
# TESTS
# ==============================================================
if __name__ == "__main__":
    print("=" * 60)
    print(" Exercise 1: The Autograd Engine")
    print("=" * 60)
    print()

    # --- Part A: Autograd ---

    a, b = Value(2.0), Value(3.0)
    assert (a + b).data == 5.0
    assert (a * b).data == 6.0
    print("  [pass] addition and multiplication forward")

    a = Value(3.0)
    assert (a + 1).data == 4.0
    assert (2 * a).data == 6.0
    assert (a / 2).data == 1.5
    print("  [pass] mixed operations (Value with plain numbers)")

    a = Value(2.0)
    assert abs(a.exp().data - math.exp(2)) < 1e-10
    assert abs(a.log().data - math.log(2)) < 1e-10
    assert (a ** 3).data == 8.0
    assert Value(3.0).relu().data == 3.0
    assert Value(-2.0).relu().data == 0.0
    print("  [pass] pow, log, exp, relu")

    a = Value(2.0)
    assert abs(a.log().exp().data - 2.0) < 1e-10
    print("  [pass] exp(log(x)) round-trip")

    # == Check your THINK answers ==============================
    # Test 5 computes c = a*b + a with a=2, b=3.
    # Did you predict dc/da = 4 and dc/db = 2? Sim
    # If not, re-draw the graph before proceeding.
    # ==========================================================

    a, b = Value(2.0), Value(3.0)
    c = a * b + a
    c.backward()
    assert a.grad == 4.0, f"dc/da should be 4.0, got {a.grad}"
    assert b.grad == 2.0, f"dc/db should be 2.0, got {b.grad}"
    print("  [pass] backward: dc/da=4, dc/db=2  (matches your prediction?)")

    # Numerical gradient check — the gold standard for verifying
    # that analytical gradients are correct.
    def f(xv):
        return math.log(xv * 3.0 + xv ** 2)
    x = Value(2.0)
    y = Value(3.0)
    z = (x * y + x ** 2).log()
    z.backward()
    eps = 1e-5
    numerical = (f(2.0 + eps) - f(2.0 - eps)) / (2 * eps)
    assert abs(x.grad - numerical) < 1e-4
    print("  [pass] numerical gradient check")

    print("\n  Part A complete.\n")

    # --- Part B: Character Tokenizer ---

    # == THINK =================================================
    # Our vocabulary will have 27 tokens (a-z plus a special
    # BOS token).  If a random model assigns equal probability
    # to each token, what is -log(1/27)? 
    # 
    # aprox. 3.30
    #
    # Calculate it now. This is the loss you should expect
    # BEFORE any training.  You'll verify this in Exercise 5.
    # ==========================================================

    import os, random
    random.seed(42)
    if not os.path.exists('input.txt'):
        import urllib.request
        url = 'https://raw.githubusercontent.com/karpathy/makemore/refs/heads/master/names.txt'
        urllib.request.urlretrieve(url, 'input.txt')
    docs = [l.strip() for l in open('input.txt').read().strip().split('\n') if l.strip()]
    random.shuffle(docs)

    # -- TODO 4: Build the vocabulary --------------------------
    #
    # Create three variables:
    #   uchars     — a sorted list of unique characters across all docs
    #   BOS        — integer token ID for Beginning-of-Sequence
    #               (assign it the next ID after all characters)
    #   vocab_size — total number of tokens (characters + BOS)

    uchars = sorted(set(''.join(docs)))
    BOS = len(uchars) # tal como nos slides aula02, valor de BOS é a length de uchars
    vocab_size = len(uchars) + 1 # 1 -> token BOS
    
    print(f"Lista ordenada com os caracteres de todos os documentos: \n{uchars}")

    # -- TODO 5: Encode and decode -----------------------------
    #
    # encode(text) -> list[int]  : each character -> its index in uchars
    # decode(ids)  -> str        : each token ID  -> its character (skip BOS)
    def encode(text):
        """

        Args:
            text: _description_

        Returns:
            _description_
        """
        listInt = []
        for c in text:
            listInt.append(uchars.index(c))

        return listInt

    def decode(token_ids):
        """

        Args:
            token_ids (_type_): _description_

        Returns:
            _description_
        """

        word = ""
        for i in token_ids:
            if i == len(uchars):
                continue
            word += uchars[i]

        return word
        


    assert vocab_size == 27 and BOS == 26
    assert encode("abc") == [0, 1, 2]
    assert decode(encode("hello")) == "hello"
    print("  [pass] vocabulary, encode, decode")

    print(f"\n  Dataset: {len(docs)} names, {vocab_size} tokens")
    print(f"  Example: '{docs[0]}' -> {encode(docs[0])}")

    print("\n" + "=" * 60)
    print(" Exercise 1 complete!")
    print("=" * 60)


# == EXPLORE (optional) ========================================
#
# 1. Add a tanh() method to Value (CHECK).  
#    Derive its local gradient.
#    Verify with the numerical gradient check pattern from Test 6.
#
# 2. Our tokenizer maps each character to one token.  Real LLMs
#    use subword tokenization (BPE).  Why?  What problems does
#    character-level have for real text?
#    (Hint: think about vocabulary size vs. sequence length.)
#
# 3. Every Value stores references to its children and gradients.
#    For a computation with N operations, what is the memory cost?
#    How might you reduce it when you don't need gradients
#    (i.e., during inference)?  This is what PyTorch's
#    torch.no_grad() does.
# ==============================================================
