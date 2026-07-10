class AgenteAprendRef:
    def __init__(self, ambiente, mec_aprend):
        self.ambiente = ambiente
        self.mec_aprend = mec_aprend
        self.s = None
    
    def executar(self, num_episodios):
        num_passos_episodio = []
        for num_episodio in range(num_episodios):
            print(f"\nEpisódio: {num_episodio + 1}")
            self.s = self.ambiente.reiniciar()
            num_passos = 0
            while not self.fim_episodio():
                self.passo_episodio()
                num_passos += 1
            num_passos_episodio.append(num_passos)
        return num_passos_episodio
    
    def fim_episodio(self):
        _, r = self.ambiente.observar()
        return r > 0
    
    def passo_episodio(self):
        self.a = self.mec_aprend.selecionar_accao(self.s)
        self.ambiente.actuar(self.a)
        sn, r = self.ambiente.observar()
        self.mec_aprend.aprender(self.s, self.a, r, sn)
        self.s = sn
        self.ambiente.mostrar()