# Projeto VivaFit

Este repositório contém um exemplo de módulo Odoo.

# Partes realizadas do Teste

- Check-in de alunos é manual; instrutores não têm visibilidade de créditos restantes! **Ok**
- Cancelamentos com menos de 4h devem consumir crédito; acima de 4h devolvem crédito automaticamente! **Ok**
- Turmas têm capacidade; lista de espera promove aluno automaticamente quando um cancela! **Ok**
- Alunos corporativos: faturamento mensal por consumo consolidado, com relatórios por centro de custo! **OK**

## Entidade de relacionamento para visualização

![](img/Entidade_relacionamento.png)

# Realatório de utilização!

- Obs: Passo a Passo!
- **Pagina Principal Nela contem os alunos cadastrados!**

![](img/abaprincipal.png)

## Operacional com as opções:
- Opção aluno que tem a mesma funcionalidade da pagina principal como cadastrar e marcar opção se é aluno ou istrutor!
- Opção Turma direciona para parte de consulta de turmas, cadastro e edição!
- Opção Diário (Checkin) direciona para aba de Checkin, Cancelamento e agendamento!

![](img/operacional.png)

## Cadastro com as opções:
- Nome, email e telefone, opção se é instrutor ou aluno.
- **Aluno tem a opção de Créditos com saldo e validade**

![](img/Cadastro.png)

## Turmas com as opções:

- Visão das turmas, Cadastrar nova Turma ou editar alguma turma clicando diretamente na existente!

![](img/abaturma.png)
#
![](img/cadastroturma.png)

**Obs ao clicar na lista mostra as inscrições e lista de espera como na imagem a seguir!**

![](img/listadeespera.png)

# Diário (Check-in) Têm as opções a seguir:

![](img/checkin.png)

- **Obs ao clicar em novo vai direcionar para proxima tela ->**

- Nessa tela tem as opçoes de Check-in como: Turma, data e hora, confirmar presença, cancelar com a regra das 4h! 

![](img/opçoesdecheck.png)

# Relatorio de faturamento!

- **Ao clicar em Faturamento vai direcionar para proxima tela ->**

![](img/faturamento.png)

- **Com as opções de filtragem como periodo!**

![](img/relatorio.png)