from flask import Flask, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app) 

MAX_WEIGHT = 30
ITEMS = [
    {"nome": "Saco de dormir", "peso": 15, "pontos": 15},
    {"nome": "Corda", "peso": 3, "pontos": 7},
    {"nome": "Canivete", "peso": 2, "pontos": 10},
    {"nome": "Tocha", "peso": 5, "pontos": 5},
    {"nome": "Garrafa", "peso": 9, "pontos": 8},
    {"nome": "Comida", "peso": 20, "pontos": 17}
]

class AlgoritmoGenetico:
    def __init__(self, pop_size, generations, mutation_rate):
        self.pop_size = pop_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.num_items = len(ITEMS)

    def criar_individuo(self):
        return [random.choice([0, 1]) for _ in range(self.num_items)]

    def calcular_fitness(self, individuo):
        peso_total = sum(individuo[i] * ITEMS[i]['peso'] for i in range(self.num_items))
        pontos_total = sum(individuo[i] * ITEMS[i]['pontos'] for i in range(self.num_items))
        
        if peso_total > MAX_WEIGHT:
            return 0 
        return pontos_total

    def selecao_torneio(self, populacao, fitnesses):
        melhor = None
        melhor_fitness = -1
        for _ in range(3):
            idx = random.randint(0, self.pop_size - 1)
            if fitnesses[idx] > melhor_fitness:
                melhor = populacao[idx]
                melhor_fitness = fitnesses[idx]
        return melhor

    def crossover(self, pai1, pai2):
        ponto = random.randint(1, self.num_items - 1)
        filho1 = pai1[:ponto] + pai2[ponto:]
        filho2 = pai2[:ponto] + pai1[ponto:]
        return filho1, filho2

    def mutacao(self, individuo):
        for i in range(self.num_items):
            if random.random() < self.mutation_rate:
                individuo[i] = 1 - individuo[i] 
        return individuo

    def executar(self):
        populacao = [self.criar_individuo() for _ in range(self.pop_size)]
        
        historico_fitness = []
        melhor_global = None
        melhor_fitness_global = -1

        for gen in range(self.generations):
            fitnesses = [self.calcular_fitness(ind) for ind in populacao]

            melhor_gen_fitness = max(fitnesses)
            idx_melhor = fitnesses.index(melhor_gen_fitness)
            
            if melhor_gen_fitness > melhor_fitness_global:
                melhor_fitness_global = melhor_gen_fitness
                melhor_global = list(populacao[idx_melhor])

            historico_fitness.append(melhor_fitness_global)

            nova_populacao = [list(melhor_global)]

            while len(nova_populacao) < self.pop_size:
                pai1 = self.selecao_torneio(populacao, fitnesses)
                pai2 = self.selecao_torneio(populacao, fitnesses)

                filho1, filho2 = self.crossover(pai1, pai2)

                filho1 = self.mutacao(filho1)
                filho2 = self.mutacao(filho2)

                nova_populacao.extend([filho1, filho2])

            populacao = nova_populacao[:self.pop_size]

        peso_final = sum(melhor_global[i] * ITEMS[i]['peso'] for i in range(self.num_items))
        itens_selecionados = [ITEMS[i]['nome'] for i in range(self.num_items) if melhor_global[i] == 1]

        return {
            "cromossomo": "".join(map(str, melhor_global)),
            "peso_total": peso_final,
            "pontuacao_total": melhor_fitness_global,
            "itens": itens_selecionados,
            "evolucao": historico_fitness
        }

@app.route('/api/executar', methods=['POST'])
def rodar_ag():
    dados = request.json
    pop_size = int(dados.get('pop_size', 50))
    generations = int(dados.get('generations', 100))
    mutation_rate = float(dados.get('mutation_rate', 0.05))

    ag = AlgoritmoGenetico(pop_size, generations, mutation_rate)
    resultado = ag.executar()
    
    return jsonify(resultado)

if __name__ == '__main__':
    app.run(debug=True, port=5000)