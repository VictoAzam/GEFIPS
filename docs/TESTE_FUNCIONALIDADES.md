# 🧪 COMO TESTAR AS NOVAS FUNCIONALIDADES

## Pré-requisitos

1. Certifique-se de que o software está funcionando normalmente
2. Tenha um usuário e perfil criados
3. Algumas transações registradas (entradas e saídas)

---

## Teste 1: Orçamentos

### Passo a Passo

1. **Abra o software** e faça login
2. **Vá para a aba "Orçamentos"**
3. **Selecione mês e ano** (sugestão: mês atual)
4. **Clique em "Adicionar Orçamento"**
5. **Preencha o formulário**:
   ```
   Categoria: Alimentação
   Limite Mensal: 500.00
   Ativo: ✓
   Descrição: Orçamento para supermercado e restaurantes
   ```
6. **Clique em "Salvar"**
7. **Repita** para outras categorias (Transporte, Lazer, etc.)

### Resultado Esperado

- ✅ Tabela mostra orçamentos criados
- ✅ Coluna "Gasto" mostra o total de saídas da categoria
- ✅ Coluna "Restante" mostra a diferença
- ✅ Coluna "Status" mostra:
  - 🟢 "OK" se gasto < 75% do limite
  - 🟡 "Atenção" se gasto entre 75-100%
  - 🔴 "Excedido" se gasto > limite

### Teste Adicional

- Mude o mês para um período sem transações
- Deve mostrar gastos zerados

---

## Teste 2: Metas Financeiras

### Passo a Passo

1. **Vá para a aba "Metas"**
2. **Clique em "Adicionar Meta"**
3. **Preencha o formulário**:
   ```
   Nome da Meta: Férias 2026
   Valor Alvo: 5000.00
   Valor Atual: 1200.00
   Data Início: 01/01/2026
   Data Alvo: 15/06/2026
   Prioridade: Alta
   Descrição: Viagem para o litoral
   Meta ativa: ✓
   ```
4. **Clique em "Salvar"**
5. **Repita** para outras metas

### Resultado Esperado

- ✅ Tabela mostra metas criadas
- ✅ Barra de progresso mostra percentual (1200/5000 = 24%)
- ✅ Prioridade "Alta" aparece em vermelho
- ✅ Data alvo aparece corretamente

### Teste de Edição (Simular progresso)

1. Selecione uma meta
2. Clique em "Editar" (quando implementado)
3. Aumente o "Valor Atual"
4. Veja a barra de progresso atualizar

---

## Teste 3: Relatórios Mensais

### Passo a Passo

1. **Vá para a aba "Relatórios"**
2. **Selecione um mês com transações**
3. **Explore a aba "Gráficos Mensais"**

### Resultado Esperado

- ✅ Gráfico de barras mostra Entradas vs Saídas
- ✅ Valores aparecem acima das barras
- ✅ Gráfico de barras horizontais mostra Top 5 categorias
- ✅ Valores aparecem ao lado de cada barra

### Teste com Mês Vazio

- Selecione um mês futuro sem transações
- Deve mostrar "Sem dados" no gráfico de categorias

---

## Teste 4: Comparação Anual

### Passo a Passo

1. **Na aba "Relatórios"**
2. **Vá para "Comparação Anual"**
3. **Selecione um ano** (ex: 2026)

### Resultado Esperado

- ✅ Gráfico mostra todos os 12 meses
- ✅ Barras verdes para Entradas
- ✅ Barras vermelhas para Saídas
- ✅ Grade horizontal para facilitar leitura
- ✅ Legenda explicativa

---

## Teste 5: Resumo Mensal

### Passo a Passo

1. **Na aba "Relatórios"**
2. **Vá para "Resumo Mensal"**
3. **Selecione um mês com dados**

### Resultado Esperado

- ✅ Tabela mostra:
  - Total de Entradas (verde)
  - Total de Saídas (vermelho)
  - Saldo (verde se positivo, vermelho se negativo)
- ✅ Lista de categorias com valores
- ✅ Percentual de cada categoria no total
- ✅ Formatação em R$ correta

---

## Teste 6: Integração com Dashboard

### Passo a Passo

1. **Vá para "Dashboard"**
2. **Adicione uma despesa**:
   ```
   Tipo: Saída
   Categoria: Alimentação
   Valor: 150.00
   Data: Hoje
   Descrição: Supermercado
   ```
3. **Vá para "Orçamentos"**
4. **Verifique se o gasto foi atualizado**

### Resultado Esperado

- ✅ Gasto da categoria "Alimentação" aumenta R$ 150
- ✅ Coluna "Restante" diminui R$ 150
- ✅ Status pode mudar (OK → Atenção → Excedido)

---

## Teste 7: Persistência de Dados

### Passo a Passo

1. **Crie alguns orçamentos e metas**
2. **Feche o software**
3. **Abra novamente**
4. **Vá para as abas criadas**

### Resultado Esperado

- ✅ Orçamentos permanecem salvos
- ✅ Metas permanecem salvas
- ✅ Dados não são perdidos

---

## Teste 8: Multiusuário/Multiperfil

### Passo a Passo

1. **Crie orçamentos para o Perfil A**
2. **Mude para o Perfil B** (se tiver)
3. **Verifique orçamentos**

### Resultado Esperado

- ✅ Cada perfil tem seus próprios orçamentos
- ✅ Dados não se misturam
- ✅ Relatórios são específicos por perfil

---

## Checklist Completo 📋

### Orçamentos
- [ ] Criar orçamento
- [ ] Listar orçamentos
- [ ] Ver status visual (OK, Atenção, Excedido)
- [ ] Gastos calculados automaticamente
- [ ] Orçamento ativo/inativo funciona

### Metas
- [ ] Criar meta
- [ ] Listar metas
- [ ] Barra de progresso funciona
- [ ] Prioridades com cores corretas
- [ ] Cálculo de percentual correto

### Relatórios
- [ ] Gráficos mensais funcionam
- [ ] Comparação anual funciona
- [ ] Resumo em tabela funciona
- [ ] Mudança de período atualiza dados
- [ ] Formatação de valores em R$

### Integração
- [ ] Transações afetam orçamentos
- [ ] Dados persistem após fechar
- [ ] Perfis isolados funcionam
- [ ] Sem erros ao navegar entre abas

---

## Problemas Conhecidos (Para corrigir depois)

1. **Edição de orçamentos**: Apenas criação implementada (mensagem "em desenvolvimento")
2. **Edição de metas**: Apenas criação implementada (mensagem "em desenvolvimento")
3. **Deleção**: Confirmação funciona mas backend precisa ID do orçamento/meta

---

## Se encontrar erros 🐛

1. **Verifique o console** para mensagens de erro
2. **Anote** os passos para reproduzir
3. **Verifique** se o banco de dados foi criado (`database/financeiro.db`)
4. **Tente fechar e abrir** novamente

---

## Comandos Úteis para Debug

```powershell
# Ver logs (se configurado)
Get-Content "data\logs\app.log" -Tail 50

# Verificar banco de dados
sqlite3 database\financeiro.db ".tables"

# Ver estrutura de tabela
sqlite3 database\financeiro.db ".schema orcamentos"
sqlite3 database\financeiro.db ".schema metas_financeiras"
```

---

**Boa sorte nos testes! 🎉**
