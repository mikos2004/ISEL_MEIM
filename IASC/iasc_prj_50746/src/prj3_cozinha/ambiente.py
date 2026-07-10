from accao import AccaoCozinha

"""
Ambiente para otimizar de tempo no para cozinhar um prato de massa

Estado: (agua, massa, tempo_total)

Cada tarefa:    0 = não iniciado, 
                1 = em andamento, 
                2 = concluído
"""
class AmbienteCozinha:

    # Tempos de cada tarefa (em minutos)
    TEMPOS = {
        AccaoCozinha.INICIAR_AGUA: 5,
        AccaoCozinha.INICIAR_MASSA: 10,
        AccaoCozinha.ESPERAR: 1,
        AccaoCozinha.FINALIZAR: 0
    }
    
    def __init__(self):
        self.reiniciar()
       
    def reiniciar(self):
        """Reinicia o ambiente para estado inicial"""
        self.estado = (0, 0, 0)
        self.tarefas_em_andamento = {}
        self.finalizado = False
        self.recompensa_penaliizada = 0  
        return self.estado_para_str(self.estado)
    
    def observar(self):
        """Retorna estado atual e recompensa"""
        # Verifica se há recompensa por ação inválida
        if self.recompensa_penaliizada != 0:
            r_invalida = self.recompensa_penaliizada
            self.recompensa_penaliizada = 0  # Reset
            estado_str = self.estado_para_str(self.estado)
            return estado_str, r_invalida
        
        if self.finalizado:
            agua, massa, tempo_total = self.estado
            if massa == 2:
                recompensa_final = 100
                estado_str = self.estado_para_str(self.estado)
                return estado_str, recompensa_final   
            else:
                estado_str = self.estado_para_str(self.estado)
                return estado_str, -1
        
        estado_str = self.estado_para_str(self.estado)
        return estado_str, 0
    
    def actuar(self, accao):
        """Executa uma ação no ambiente"""
        
        print()
        print("="*15)
        print(f">>> Ação realizada: {accao} | temp_accao: {self.TEMPOS[accao]}")
        
        if self.finalizado:
            return

        if accao != AccaoCozinha.FINALIZAR:
            self.avancar_tempo()

        agua, massa, tempo_total = self.estado
        
        if accao == AccaoCozinha.FINALIZAR:
            if massa == 2:
                self.finalizado = True
                print("Finalização válida!")
            else:
                print(f"Finalização antecipada! Massa={massa}")
                # Penalidade por finalização antecipada
                self.recompensa_penaliizada = -10
            
            self.estado = (agua, massa, tempo_total)
            return
        
        if accao == AccaoCozinha.ESPERAR:
            # Ação ESPERAR é sempre válida
            return
        
        # Não pode iniciar tarefa que já está em andamento
        if accao in self.tarefas_em_andamento:
            print(f"Ação inválida: {accao.name} já está em andamento!")
            # Penalidade por tentar iniciar tarefa já em andamento
            self.recompensa_penaliizada = -10
            self.estado = (agua, massa, tempo_total)
            return
        
        # Dependência água-massa
        if accao == AccaoCozinha.INICIAR_MASSA and agua != 2:
            print(f"Dependência quebrada: Água={agua} (precisa ser 2)")
            # Penalidade por quebrar dependência
            self.recompensa_penaliizada = -10
            self.estado = (agua, massa, tempo_total)
            return
        
        # Não pode iniciar tarefa já concluída
        if (accao == AccaoCozinha.INICIAR_AGUA and agua == 2) or \
           (accao == AccaoCozinha.INICIAR_MASSA and massa == 2):
            print(f"Ação inválida: {accao.name} já está concluída!")
            # Penalidade por tentar iniciar tarefa já concluída
            self.recompensa_penaliizada = -10
            self.estado = (agua, massa, tempo_total)
            return
        
        # Inicia a nova tarefa
        self.tarefas_em_andamento[accao] = self.TEMPOS[accao]
        
        # Atualiza estado para "em andamento"
        if accao == AccaoCozinha.INICIAR_AGUA and agua == 0:
            agua = 1
        elif accao == AccaoCozinha.INICIAR_MASSA and massa == 0:
            massa = 1
        
        self.estado = (agua, massa, tempo_total)
    
    def avancar_tempo(self):
        """
        Avançar o tempo nas tarefas _em andamento_
        """
        agua, massa, tempo_total = self.estado

        novas_tarefas = {}
            
        for tarefa, minutos_restantes in list(self.tarefas_em_andamento.items()):
            minutos_restantes -= 1
            
            if minutos_restantes <= 0:
                if tarefa == AccaoCozinha.INICIAR_AGUA:
                    agua = 2
                elif tarefa == AccaoCozinha.INICIAR_MASSA:
                    massa = 2
            else:
                novas_tarefas[tarefa] = minutos_restantes
        
        self.tarefas_em_andamento = novas_tarefas
        tempo_total += 1
        self.estado = (agua, massa, tempo_total)
    
    def mostrar(self):
        """Mostra estado atual da receita"""
        agua, massa, tempo_total = self.estado
        
        print(f"\n=== Tempo: {tempo_total} ===")
        print(f"Água: {self.estado_tarefa_str(agua)}")
        print(f"Massa: {self.estado_tarefa_str(massa)}")
        
        if self.tarefas_em_andamento:
            print("Tarefas em andamento:")
            for tarefa, tempo_rest in self.tarefas_em_andamento.items():
                print(f"  - {tarefa.name}: {tempo_rest} min restantes")
        
        if self.finalizado:
            print("** PRATO FINALIZADO **")
    
    def estado_tarefa_str(self, estado_tarefa):
        """Mapeia o valor do estado para uma string correspondente"""
        if estado_tarefa == 0:
            return "Não iniciado"
        elif estado_tarefa == 1:
            return "Em andamento"
        else:
            return "Concluído"
    
    def mostrar_politica(self, politica):
        """Mostrar politica no formato similar ao 7x1"""
        print("\nPolítica:")
        estados_ordenados = sorted(politica.keys())
        for estado_str in estados_ordenados:
            accao = politica.get(estado_str)
            if accao:
                accao_str = accao.name if hasattr(accao, 'name') else str(accao)
                print(f"Estado {estado_str} -> {accao_str}")
        print()
    
    def mostrar_valor(self, valor):
        """Mostrar valor do estado normalizado para 0-1"""
        print("\nValor:")
        estados_ordenados = sorted(valor.keys())
        
        if valor:
            valores = list(valor.values())
            v_min = min(valores)
            v_max = max(valores)
            range_val = v_max - v_min if v_max != v_min else 1
        else:
            v_min = 0
            range_val = 1
        
        for estado_str in estados_ordenados:
            vs = valor.get(estado_str)
            if vs is not None:
                vs_normalizado = (vs - v_min) / range_val if range_val > 0 else 0.5
                print(f"Estado {estado_str}: {vs_normalizado:.2f}")
        print()

    def estado_para_str(self, estado_tupla):
        agua, massa, tempo_total = estado_tupla
        
        if tempo_total <= 10:
            tempo_str = "A"
        else:
            tempo_str = "B"
        
        return f"{agua}{massa}{tempo_str}"
    
    def str_para_estado(self, estado_str):
        """Converte string do estado para um tuplo"""
        return (
            int(estado_str[0]),  # agua
            int(estado_str[1]),  # massa
            int(estado_str[2:])  # tempo_total
        )