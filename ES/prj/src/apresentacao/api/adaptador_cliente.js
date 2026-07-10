// Adaptador do cliente para fazer chamadas à API
class AdaptadorCliente {
    constructor() {
        // URL da API
        this.baseURL = 'http://localhost:5008/api';
    }

    /**
     * Regista um novo hóspede (Pedido POST)
     * @param {Object} hospedeData - Dados do hóspede
     * @returns {Promise<Object>} Resposta da API
     */
    async registarHospede(hospedeData) {
        try {
            const response = await fetch(`${this.baseURL}/registar_hosp`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(hospedeData)
            });

            if (!response.ok) {
                throw new Error(`Erro HTTP: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Erro ao registar hóspede:', error);
            throw error;
        }
    }

    /**
     * Consulta hóspede por email (Pedido GET)
     * @param {string} email - Email do hóspede
     * @returns {Promise<Object>} Dados do hóspede
     */
    async consultarHospede(email) {
        try {
            const response = await fetch(`${this.baseURL}/consulta_hospede?email=${encodeURIComponent(email)}`);
            
            if (!response.ok) {
                throw new Error(`Erro HTTP: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Erro ao consultar hóspede:', error);
            throw error;
        }
    }

    /**
     * Confirma uma reserva (Pedido POST)
     * @param {Object} reservaData - Dados da reserva
     * @returns {Promise<Object>} Resposta da API
     */
    async confirmarReserva(reservaData) {
        try {
            const response = await fetch(`${this.baseURL}/confirm_reserva`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(reservaData)
            });

            if (!response.ok) {
                throw new Error(`Erro HTTP: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Erro ao confirmar reserva:', error);
            throw error;
        }
    }

    /**
     * Obtém quartos disponíveis (pedido GET)
     * @returns {Promise<Array>} Lista de quartos disponíveis
     */
    async obterQuartosDisponiveis() {
        try {
            const response = await fetch(`${this.baseURL}/quartos_disponiveis`);
            
            if (!response.ok) {
                throw new Error(`Erro HTTP: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Erro ao obter quartos disponíveis:', error);
            throw error;
        }
    }
}

// instância para usar na página HTML
const adaptadorCliente = new AdaptadorCliente();

// Função para lidar com o registo do hóspede
async function handleRegistarHospede(event) {
    // Prevene envio padrão do formulário
    event.preventDefault(); 
    
    try {
        // Junta os dados do form
        const hospedeData = {
            nomeCompleto: document.getElementById('nome_completo').value,
            numDocumento: document.getElementById('cc_number').value,
            validadeDoc: document.getElementById('doc_validade').value,
            birthDate: document.getElementById('data_nascimento').value,
            nacionalidade: document.getElementById('nacionalidade').value,
            email: document.getElementById('email').value,
            telemovel: document.getElementById('telemovel').value,
            preferencias: ''
        };

        // Validar campos obrigatórios
        const camposObrigatorios = [
            'nomeCompleto', 'numDocumento', 'validadeDoc', 
            'birthDate', 'nacionalidade', 'email', 'telemovel'
        ];
        
        for (const campo of camposObrigatorios) {
            if (!hospedeData[campo]) {
                alert(`Por favor, preencha o campo ${campo}`);
                return;
            }
        }

        // Chamar a API para registar
        const resultado = await adaptadorCliente.registarHospede(hospedeData);
        
        if (resultado.success) {
            alert('Hóspede registado com sucesso! ID: ' + resultado.idHospede);
        } else {
            alert('Erro: ' + resultado.message);
        }
    } catch (error) {
        alert('Erro ao registar hóspede: ' + error.message);
    }
}

// Função para lidar com a confirmação da reserva
async function handleConfirmarReserva(event) {
    event.preventDefault();
    
    try {
        // dados da reserva
        const idHospede = sessionStorage.getItem('idHospede');
        if (!idHospede) {
            alert('Por favor, registe o hóspede primeiro');
            return;
        }

        // dados do quarto selecionado
        const quartoSelect = document.getElementById('select_quartos');
        const quartoValue = quartoSelect.value;
        
        // Extrair número do quarto
        let numeroQuarto = null;
        let tipoQuarto = null;
        
        if (quartoValue.includes('-')) {
            [numeroQuarto, tipoQuarto] = quartoValue.split('-');
        } else {
            tipoQuarto = quartoValue;
        }

        const reservaData = {
            idHospede: parseInt(idHospede),
            numeroQuarto: numeroQuarto ? parseInt(numeroQuarto) : null,
            tipoQuarto: tipoQuarto,
            servicosAdicionais: document.getElementById('select_servicos').value,
            dataEntradaPrev: document.getElementById('data_entrada').value,
            dataSaidaPrev: document.getElementById('data_saida').value,
            notas: document.getElementById('observacoes').value
        };

        // Validar campos obrigatórios
        if (!reservaData.tipoQuarto || !reservaData.dataEntradaPrev || !reservaData.dataSaidaPrev) {
            alert('Por favor, preencha todos os campos obrigatórios da reserva');
            return;
        }

        // Calcular número de dias
        const dataEntrada = new Date(reservaData.dataEntradaPrev);
        const dataSaida = new Date(reservaData.dataSaidaPrev);
        const diffTime = Math.abs(dataSaida - dataEntrada);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays <= 0) {
            alert('A data de saída deve ser posterior à data de entrada');
            return;
        }

        reservaData.numeroDias = diffDays;

        // Chamar a API para confirmar reserva
        const resultado = await adaptadorCliente.confirmarReserva(reservaData);
        
        if (resultado.success) {
            alert(`Reserva confirmada com sucesso!\nID da Reserva: ${resultado.idReserva}\nValor Total: €${resultado.valorTotalPrev.toFixed(2)}`);
            
            // Limpar sessão e formulário
            sessionStorage.removeItem('idHospede');
            document.querySelector('form').reset();
        } else {
            alert('Erro: ' + resultado.message);
        }
    } catch (error) {
        alert('Erro ao confirmar reserva: ' + error.message);
    }
}

// Carregar quartos disponíveis quando a página carrega
async function carregarQuartosDisponiveis() {
    try {
        const quartos = await adaptadorCliente.obterQuartosDisponiveis();
        const selectQuartos = document.getElementById('select_quartos');
        
        // Limpar opções existentes (menos a primeira)
        while (selectQuartos.options.length > 1) {
            selectQuartos.remove(1);
        }
        
        // Adicionar quartos disponíveis
        quartos.forEach(quarto => {
            const option = document.createElement('option');
            option.value = `${quarto.numero}-${quarto.tipo}`;
            option.textContent = `Quarto ${quarto.numero} - ${quarto.tipo.toUpperCase()} - €${quarto.precoBase}/noite`;
            selectQuartos.appendChild(option);
        });
    } catch (error) {
        console.error('Erro ao carregar quartos:', error);
    }
}

// Adicionar evento ao botão de registar hóspede
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    
    // Encontrar todos os botões de confirm
    const botoesConfirmar = document.querySelectorAll('.confirm-button');
    
    if (botoesConfirmar.length > 0 && form) {
        // Primeiro botão - Registar Hóspede
        botoesConfirmar[0].addEventListener('click', function(event) {
            if (this.textContent.includes('Registar Hóspede')) {
                handleRegistarHospede(event);
            }
        });
        
        // Segundo botão - Confirmar Reserva
        if (botoesConfirmar.length > 1) {
            botoesConfirmar[1].addEventListener('click', function(event) {
                if (this.textContent.includes('Confirmar Reserva')) {
                    handleConfirmarReserva(event);
                }
            });
        }
    }
    
    // Carregar quartos disponíveis
    carregarQuartosDisponiveis();
});