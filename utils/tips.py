

from __future__ import annotations

import random
from enum import Enum
from typing import Dict, Iterable, List, Optional, Tuple


class HealthState(str, Enum):
    CRITICO = "critico"
    ALERTA = "alerta"
    EQUILIBRADO = "equilibrado"
    INVESTIDOR = "investidor"


_STATE_LABEL: Dict[HealthState, str] = {
    HealthState.CRITICO: "Crítico",
    HealthState.ALERTA: "Alerta",
    HealthState.EQUILIBRADO: "Equilibrado",
    HealthState.INVESTIDOR: "Investidor",
}


_TIPS: Dict[HealthState, List[str]] = {
    HealthState.CRITICO: [
        "Pare imediatamente gastos não essenciais.",
        "Foque em quitar a dívida com juros mais altos primeiro (Dave Ramsey: Avalanche de Dívidas).",
        "Cancele assinaturas que você quase não usa.",
        "Cozinhar em casa costuma ser bem mais barato que delivery.",
        "Negocie suas dívidas. Muitos credores aceitam descontos para pagamento à vista.",
        "Venda itens que você não usa mais para gerar caixa emergencial.",
        "Evite usar cheque especial e cartão de crédito rotativo - juros altíssimos!",
        "Considere uma renda extra temporária até sair do vermelho.",
        "Congele totalmente gastos com lazer até regularizar as contas.",
        "Priorize: moradia, alimentação e transporte. Corte todo o resto.",
        "Use o método Snowball: pague primeiro a menor dívida para ganhar impulso psicológico (Dave Ramsey).",
        "Venda ativos que não geram renda (carro extra, eletrônicos) para quitar dívidas.",
        "Negocie com credores ANTES do vencimento - mostre proatividade.",
        "Corte cartões de crédito fisicamente para evitar novas dívidas.",
        "Trabalhe horas extras ou fins de semana temporariamente.",
        "Evite empréstimos para pagar outros empréstimos - círculo vicioso.",
        "Priorize dívidas com garantia real (casa, carro) sobre consignadas.",
        "Registre TODA despesa por 30 dias - consciência é o primeiro passo.",
        "Venda tempo ocioso: freelance, Uber, entregas, artesanato.",
        "Fuja de agiotas e pirâmides financeiras - pioram tudo.",
        "Estabeleça um orçamento de sobrevivência: apenas o essencial.",
        "Use cupons, cashback e descontos sempre que possível.",
        "Evite sair de casa com cartão - use apenas dinheiro planejado.",
        "Cancele TV a cabo, academias e clubes - prioridade é sair do buraco.",
        "Prepare marmitas para a semana toda e economize centenas.",
        "Ligue para operadoras e peça descontos ou cancelamento de serviços.",
        "Troque marcas por produtos genéricos - mesma qualidade, menor preço.",
        "Evite bares, restaurantes e cafés até regularizar as finanças.",
        "Use transporte público ou bicicleta ao invés de carro próprio.",
        "Refinancie dívidas caras por taxas menores se possível.",
        "Venda objetos de valor em brechós, OLX ou grupos de Facebook.",
        "Faça um pacto familiar: todos economizam juntos.",
        "Evite presentear em datas comemorativas - explique a situação.",
        "Busque programas de renegociação do governo ou bancos.",
        "Troque smartphone caro por básico - economize linha e aparelho.",
        "Cancele seguro do cartão de crédito e pacotes bancários desnecessários.",
        "Evite compras parceladas - juros embutidos são devastadores.",
        "Peça ajuda a familiares apenas como última opção e com plano de pagamento.",
        "Procure ONGs ou igrejas que oferecem cestas básicas temporárias.",
        "Estude finanças básicas gratuitamente no YouTube enquanto se recupera.",
        "Assuma a situação: esconder dívidas só piora. Transparência liberta.",
        "Implemente 'Jejum Financeiro': zero gastos não essenciais por 7 dias.",
        "Venda plano de saúde caro e use SUS temporariamente se possível.",
        "Adie reformas, viagens e eletrônicos novos por pelo menos 1 ano.",
        "Faça reparos você mesmo: YouTube ensina quase tudo.",
        "Evite empréstimos consignados só porque 'cabe no orçamento'.",
        "Liste TODAS as dívidas e crie um plano de ataque escrito.",
        "Celebre pequenas vitórias: cada dívida quitada é uma conquista.",
        "Visualize sua vida sem dívidas - motivação é combustível.",
        "Lembre-se: situação temporária. Disciplina traz liberdade financeira.",
    ],
    HealthState.ALERTA: [
        "Cuidado: você gastou mais do que ganhou este mês.",
        "Revise gastos fixos; veja se há algo consumindo sua renda em silêncio.",
        "Evite compras por impulso. Espere 24h antes de decidir (Warren Buffett: paciência é virtude).",
        "Analise suas faturas dos últimos 3 meses - identifique padrões de gasto.",
        "Estabeleça um limite semanal de gastos variáveis e respeite-o.",
        "Considere trocar planos de celular e internet por opções mais baratas.",
        "Use transporte público ou carona solidária quando possível.",
        "Planeje as refeições da semana para evitar desperdício e gastos extras.",
        "Cancelar um streaming por mês pode economizar centenas no ano.",
        "Renegocie contratos anuais (academia, seguros) para valores menores.",
        "Aplique a regra 50/30/20: 50% essenciais, 30% desejos, 20% poupança (Elizabeth Warren).",
        "Faça um 'detox de consumo': 30 dias sem compras não essenciais.",
        "Identifique seus 'ladrões de dinheiro': cafezinhos, lanches, apps pagos.",
        "Use envelope ou conta separada para cada categoria de gasto.",
        "Evite vitrines físicas e virtuais - exposição gera tentação.",
        "Pergunte-se antes de comprar: 'Preciso ou quero? Há alternativa mais barata?'",
        "Cancele notificações de promoções e e-mails marketing.",
        "Implemente 'Dia Sem Gastar' pelo menos 2x por semana.",
        "Troque marcas premium por intermediárias - pouca diferença, grande economia.",
        "Reavalie assinaturas mensais: você realmente usa tudo?",
        "Aprenda a dizer NÃO para convites caros de amigos.",
        "Evite supermercado com fome - lista prévia salva dinheiro.",
        "Compare preços online antes de comprar qualquer coisa.",
        "Busque lazer gratuito: parques, bibliotecas, eventos culturais públicos.",
        "Troque presente caro por artesanal ou experiência compartilhada.",
        "Elimine um vício caro por vez: cigarro, bebida, doces, café premium.",
        "Planeje compras grandes para datas promocionais (Black Friday, 13º).",
        "Use aplicativos de controle financeiro para ver gastos em tempo real.",
        "Venda ou doe roupas que não usa há 1 ano - desapego liberta.",
        "Evite parcelamentos: se não pode pagar à vista, não pode comprar.",
        "Negocie descontos em pagamentos antecipados ou à vista.",
        "Implemente 'Regra das 72h': espere 3 dias antes de compras acima de R$ 100.",
        "Troque happy hour por encontros em casa - muito mais econômico.",
        "Cancele cartões de loja - facilitam consumo desnecessário.",
        "Evite estacionamentos pagos: use transporte público para compromissos.",
        "Prepare café em casa ao invés de cafeterias todos os dias.",
        "Busque consertos ao invés de substituição (celular, roupas, sapatos).",
        "Implemente 'Fundo de Tentação': R$ 50/mês para pequenos prazeres.",
        "Evite shoppings: ambiente projetado para você gastar.",
        "Troque academia por exercícios ao ar livre ou apps gratuitos.",
        "Corte gastos invisíveis: taxas bancárias, seguros desnecessários.",
        "Reavalie seu padrão de vida: você está tentando impressionar quem?",
        "Leia 'O Homem Mais Rico da Babilônia' - princípios atemporais de economia.",
        "Automatize pagamentos fixos para evitar juros de atraso.",
        "Estabeleça meta mensal: reduzir gastos em 10% todo mês.",
        "Evite financiamentos de longo prazo - juros compostos são cruelmente.",
        "Busque segunda renda passiva ou ativa complementar.",
        "Revise seguros anualmente - concorrência pode oferecer melhores taxas.",
        "Implemente 'Desafio dos 30 dias': economize R$ 1 no dia 1, R$ 2 no dia 2...",
        "Lembre-se: pequenos vazamentos afundam grandes navios (Benjamin Franklin).",
    ],
    HealthState.EQUILIBRADO: [
        "Abra HOJE uma conta digital separada só para emergências - sem cartão.",
        "Calcule seu custo mensal total e multiplique por 6 - essa é sua meta de reserva.",
        "Configure transferência automática de 15% do salário para poupança no dia do pagamento.",
        "Cancele um gasto fixo pequeno (R$ 30-50) e direcione para investimentos.",
        "Abra conta gratuita em corretora esta semana (Clear, Rico, XP).",
        "Compre R$ 100 em Tesouro Selic pelo app do Tesouro Direto - comece agora.",
        "Liste 3 objetivos de médio prazo com valores e prazos específicos.",
        "Aumente em 5% sua contribuição para previdência privada ou INSS este mês.",
        "Leia 20 páginas de 'O Homem Mais Rico da Babilônia' por dia (termina em 1 semana).",
        "Calcule quanto R$ 500/mês rendem em 20 anos a 10% a.a. - se surpreenda.",
        "Monte planilha simples: patrimônio total menos dívidas = patrimônio líquido.",
        "Contrate seguro de vida básico (R$ 30-80/mês) se tiver dependentes.",
        "Invista R$ 200 em CDB com liquidez diária que renda mais que poupança.",
        "Defina percentual fixo: 60% viver, 20% investir, 20% aproveitar.",
        "Estude 1 vídeo sobre Fundos Imobiliários no YouTube hoje à noite.",
        "Crie alerta no celular: 'Já investi este mês?' - todo dia 5.",
        "Compare taxas de corretoras e migre para a mais barata esta semana.",
        "Abra VGBL ou PGBL se seu IR é completo - economia tributária é lucro certo.",
        "Estabeleça meta: ter 1 ano de despesas guardado em 36 meses.",
        "Congele aumentos de padrão de vida por 2 anos - invista toda diferença de renda.",
        "Baixe app Tesouro Direto e simule aposentadoria com IPCA+ - veja o poder dos juros.",
        "Invista R$ 100 em livro de finanças e aplique 1 ensinamento por semana.",
        "Configure débito automático para investimento - elimine decisão mensal.",
        "Diversifique: 50% Tesouro Selic, 30% CDB, 20% fundos - comece com R$ 500.",
        "Analise última declaração de IR: pagou muito imposto? Otimize com previdência.",
        "Assista curso gratuito B3 sobre bolsa de valores (4 horas).",
        "Estabeleça 'salário fantasma': invista como se ganhasse 20% menos.",
        "Compre seu primeiro FII de R$ 100 esta semana - aprenda fazendo.",
        "Crie meta anual: aumentar patrimônio líquido em 30% todo ano.",
        "Calcule sua taxa de poupança: (investimentos ÷ renda líquida) × 100.",
        "Meta: taxa de poupança mínima de 25% - ajuste orçamento se necessário.",
        "Implemente 'Imposto do Futuro': 10% de toda renda extra vai direto para investimentos.",
        "Reavalie plano de saúde: você usa? Cobertura adequada? Preço competitivo?",
        "Abra conta em 2 corretoras diferentes - compare custos e ferramentas.",
        "Invista em ETF de índice (BOVA11) - diversificação instantânea com R$ 100.",
        "Leia relatório gratuito de gestoras sobre cenário econômico mensal.",
        "Estabeleça revisão trimestral: 1 tarde para analisar todos os investimentos.",
        "Calcule FII: Financial Independence Index = patrimônio ÷ (despesas × 300).",
        "Meta: FII = 1,0 (300 meses = 25 anos de despesas guardadas).",
        "Invista bônus, 13º e restituição de IR 100% - não é renda regular.",
        "Estude sobre LCI/LCA isentos de IR - vantagem fiscal é retorno garantido.",
        "Entre em comunidade de finanças no Reddit ou Telegram - aprenda com pares.",
        "Implemente 'Fundo dos Sonhos': R$ 200/mês para objetivo específico de 2-5 anos.",
        "Baixe app de controle financeiro e registre TODO gasto por 60 dias.",
        "Compare rentabilidade: sua carteira bateu CDI? IPCA? Ibovespa? Ajuste se necessário.",
        "Compre ação de empresa sólida (Itaú, Petrobras, Vale) e NUNCA venda - aprenda paciência.",
        "Estude sobre rebalanceamento: ajuste carteira de 6 em 6 meses para manter proporções.",
        "Crie alarme anual: revise TODOS os contratos fixos para renegociar ou cancelar.",
        "Desafio: aumente aporte mensal em R$ 50 a cada trimestre durante 1 ano.",
        "Lembre-se: R$ 500/mês por 30 anos a 10% a.a. = R$ 1,1 milhão - comece hoje!",
    ],
    HealthState.INVESTIDOR: [
        "Aumente seu aporte mensal em 10% AGORA - você tem margem para isso.",
        "Invista TODO excedente deste mês em ações de dividendos (ITSA4, TAEE11, BBSE3).",
        "Abra conta em Avenue ou Nomad e compre US$ 500 em ETF S&P500 esta semana.",
        "Calcule sua independência financeira: patrimônio necessário = despesas mensais × 300.",
        "Diversifique 20% do portfólio em FIIs de papel (HGLG11, MXRF11) para renda mensal.",
        "Configure aporte automático semanal - R$ 500/semana supera R$ 2.000/mês (psicológico).",
        "Compre 5 ações diferentes de setores diversos - elimine risco de concentração.",
        "Meta ousada: aumentar patrimônio líquido em 50% nos próximos 12 meses.",
        "Invista R$ 2.000 em educação financeira: curso CPA-20, CEA ou CFP.",
        "Abra previdência privada VGBL e maximize dedução fiscal (12% renda bruta).",
        "Calcule: a que taxa seu dinheiro dobra? Regra dos 72: 72 ÷ taxa = anos.",
        "Rebalanceie HOJE: 40% renda fixa, 40% ações, 10% FIIs, 10% internacional.",
        "Invista em 3 ETFs diferentes: BOVA11 (Ibovespa), SMAL11 (Small Caps), IVVB11 (S&P500).",
        "Estabeleça meta de renda passiva: R$ 5.000/mês em dividendos até 2030.",
        "Compre 1 FII novo por mês - diversificação gradual e constante.",
        "Estude empresas no Site de RI e compre apenas negócios que você entende.",
        "Implemente Dollar Cost Averaging: invista SEMPRE, independente do cenário.",
        "Abra conta em corretora internacional e diversifique 30% em ativos globais.",
        "Contrate consultoria financeira por 1 sessão - valide sua estratégia (R$ 500-1.500).",
        "Invista em imóvel para alugar se tiver R$ 200mil+ parado - yield 0,5%/mês.",
        "Compre Tesouro IPCA+ 2045 e esqueça - aposentadoria garantida acima da inflação.",
        "Meta agressiva: viver só de renda passiva em 10 anos - calcule quanto precisa.",
        "Diversifique em 10+ FIIs de segmentos diferentes (logística, lajes, shoppings, papel).",
        "Invista 5% em ouro (GOLD11) como proteção contra crises sistêmicas.",
        "Compre ações no exterior: AAPL, MSFT, JNJ, PG - empresas seculares.",
        "Estabeleça 'Salário da Liberdade': quando dividendos = despesas mensais?",
        "Reinvista 100% dos dividendos - juros compostos em esteróides.",
        "Aumente exposição em Small Caps (SMLL) - maior potencial de crescimento.",
        "Invista em CRIs/CRAs de grandes incorporadoras - yield 10-14% a.a. isento de IR.",
        "Abra holding patrimonial se patrimônio > R$ 1 milhão - proteção e sucessão.",
        "Compre debêntures incentivadas de infraestrutura - IPCA+ 6% isento de IR.",
        "Invista em terrenos em cidades em crescimento - valorização de longo prazo.",
        "Estabeleça meta: 1 salário em dividendos este ano, 2 salários no próximo.",
        "Diversifique internacionalmente: 30% Brasil, 50% EUA, 10% Europa, 10% Emergentes.",
        "Compre BDRs de empresas americanas (AMZO34, GOGL34, TSLA34) - exposição ao dólar.",
        "Implemente estratégia de dividendos crescentes: só empresas que aumentam proventos anualmente.",
        "Invista em você: MBA, mestrado, certificações - aumentar renda é o melhor investimento.",
        "Abra conta em banco de investimentos (BTG, XP Private) se patrimônio > R$ 500mil.",
        "Compre COE com capital protegido ligado ao S&P500 - limite downside, mantém upside.",
        "Estude sobre Stock Options e Monte carteira vendida - renda extra mensal.",
        "Invista em Venture Capital ou Equity Crowdfunding - 5% para alto risco/retorno.",
        "Compre ações on sale após quedas - Warren Buffett: 'Seja ganancioso quando outros têm medo'.",
        "Estabeleça 'Fundo de Oportunidades': 20% em caixa para comprar crashes.",
        "Invista em REITs americanos (VNQ) - renda passiva em dólar sem gestão.",
        "Monte carteira de 30 ações diferentes - nível Warren Buffett de diversificação.",
        "Compre Bitcoin/Ethereum (máximo 3% portfólio) - proteção contra inflação monetária.",
        "Doe 1% para caridade - tax deduction e legado social (até 6% IR pessoa física).",
        "Ensine finanças para filhos com mesada investida - R$ 100/mês vira R$ 60mil em 18 anos.",
        "Revise anualmente com contador, advogado e planejador - time multidisciplinar.",
        "Lembre-se: 'Quanto mais cedo começar, menos precisa poupar' (Albert Einstein sobre juros compostos).",
    ],
}


def classify_health(receita: float, despesa: float, saldo: float) -> HealthState:
    """Classifica a saúde financeira conforme as faixas solicitadas."""
    receita = float(receita)
    despesa = float(despesa)
    saldo = float(saldo)

    # Faixa 1: saldo total negativo
    if saldo < 0:
        return HealthState.CRITICO

    # Faixa 2: queimando caixa no mes
    if despesa > receita:
        return HealthState.ALERTA

    sobra = receita - despesa
    if receita <= 0:
        # Sem receita para medir percentual; fallback conservador
        return HealthState.ALERTA if despesa > 0 else HealthState.EQUILIBRADO

    margem = sobra / receita
    if 0 <= margem <= 0.20:
        return HealthState.EQUILIBRADO
    return HealthState.INVESTIDOR


def random_tip(state: HealthState) -> str:
    tips = _TIPS.get(state, [])
    if not tips:
        return "Mantenha o foco nas finanças."
    return random.choice(tips)


def format_currency(value: float) -> str:
    return f"R$ {value:,.2f}"


def build_feedback(
    receita: float,
    despesa: float,
    saldo: float,
    *,
    top_expense: Optional[Tuple[str, float]] = None,
    last_month_expense: Optional[float] = None,
) -> Dict[str, object]:
    """Gera feedback textual e dicas extras.

    Args:
        receita: total de receitas do mês atual.
        despesa: total de despesas do mês atual.
        saldo: saldo total atual (pode incluir meses anteriores).
        top_expense: (categoria, valor) para destacar a maior despesa do mês.
        last_month_expense: total de despesas do mês anterior para comparação.
    Returns:
        dict com estado, rótulo, dica principal e extras opcionais.
    """
    state = classify_health(receita, despesa, saldo)
    tip = random_tip(state)
    extras: List[str] = []

    if top_expense and len(top_expense) == 2:
        categoria, valor = top_expense
        extras.append(
            f"Atenção: maior despesa foi {categoria} ({format_currency(valor)}). Tente reduzir isso."
        )

    if last_month_expense is not None and last_month_expense > 0:
        limite = last_month_expense * 1.10
        if despesa > limite:
            crescimento = ((despesa / last_month_expense) - 1) * 100
            extras.append(
                f"Seus gastos subiram {crescimento:.1f}% em relação ao mês passado. Houve algo atípico?"
            )

    return {
        "estado": state.value,
        "rotulo": _STATE_LABEL[state],
        "dica": tip,
        "extras": extras,
    }


__all__ = [
    "HealthState",
    "classify_health",
    "random_tip",
    "build_feedback",
    "format_currency",
]
