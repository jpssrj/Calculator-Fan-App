# Relatório de Revisão Crítica (Stage 7 Critic Review)

**Documento Auditado:** [`docs/designs/calculator_fan_desktop.md`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md) (Linhas 1 a 237 - `FeatureRange`)  
**Revisores:** `egm-design`, `egm-structural`, `egm-style` (Orquestrado por `egm-synthesizer`)  
**Padrão Aplicado:** Feature Spec Standard  
**Status da Revisão:** Aprovado com Ressalvas (2 Blockers, 4 Majors, 4 Nits)

---

## 1. Resumo Executivo da Auditoria

A auditoria multivisão analisou a especificação conceitual e arquitetural do **Calculator Fan Desktop App** no intervalo das linhas 1 a 237:

* **🔴 Blocker (2):** Falhas em contratos de erro e manipulação numérica que comprometem a execução da aplicação em runtime (comportamento de notação científica indesejada com `Decimal.normalize()`, exceções de ponto flutuante não tratadas e ausência de contrato IPC para cancelamento/erros de I/O em `export_receipt_txt`).
* **🟡 Major (4):** Omissões arquiteturais e assimetrias que geram lacunas de implementação (verificação de WebView2 restrita a `HKLM` com falha offline, método `get_app_info()` incompleto, ambiguidade na normalização de vírgula decimal do Numpad ABNT2 e brechas de isolamento do WebView2 dependentes apenas de JavaScript).
* **🟢 Nit (4):** Inconsistências de nomenclatura, assertivas de performance sem embasamento de benchmark e links com caminhos absolutos locais da máquina host.

---

## 2. Achados Priorizados

### 2.1 Tratamento Incompleto de Exceções Aritméticas e Notação Científica Indesejada via `Decimal.normalize()`
* **Severidade:** 🔴 Blocker
* **Lente de Origem:** `egm-design`
* **Escopo Afetado:** Linhas 145-166 (Seção 5.3.2 - *Aritmética Determinística com decimal.Decimal*)
* **Descrição da Discrepância:** A especificação determina o uso de `.normalize()` para supressão de zeros à direita e restringe o tratamento de exceções a `decimal.DivisionByZero`. No módulo `decimal` do Python, a chamada de `.normalize()` em inteiros terminados em zero (como `Decimal('100')` ou `Decimal('10')`) converte o valor para representação científica exponencial (ex.: `1E+2` e `1E+1`), o que rompe o layout visual do display da calculadora. Além disso, operações com operandos inválidos ou limites disparam `decimal.InvalidOperation` e `decimal.Overflow`, exceções não mapeadas no documento.
* **Recomendação:** Substituir a chamada direta de `.normalize()` por rotina explícita de formatação que remova zeros decimais supérfluos sem introduzir notação exponencial para inteiros. Mapear no motor decimal todas as exceções fundamentais (`DivisionByZero`, `InvalidOperation`, `Overflow`), convertendo-as em mensagens amigáveis pelo contrato IPC (`"DIVISÃO POR ZERO"`, `"OPERAÇÃO INVÁLIDA"`, `"ESTOURO DE CAPACIDADE"`).

---

### 2.2 Ausência de Contrato IPC para Cancelamento de Salvamento e Erro de I/O (`export_receipt_txt`)
* **Severidade:** 🔴 Blocker
* **Lente de Origem:** `egm-design`
* **Escopo Afetado:** Linhas 128-140 (Seção 5.2.2) e Linhas 96-101 (Seção 5.1 - Diagrama Mermaid)
* **Descrição da Discrepância:** O contrato IPC de `export_receipt_txt` documenta unicamente o retorno de sucesso com arquivo salvo. Quando o usuário clica em "Cancelar" na caixa de diálogo nativa do Windows (`SaveFileDialog`), o método `create_file_dialog` retorna `None` ou tupla vazia. O payload retornado ao frontend nesse cenário é omitido, assim como a resposta para falhas de gravação em disco (`PermissionError`, disco cheio). Paralelamente, o diagrama Mermaid da Seção 5.1 aponta que a caixa de diálogo grava diretamente no disco (`SaveDialog -->|Grava em Disco| FileSystem`), quando na arquitetura Win32/pywebview a caixa apenas retorna o caminho selecionado para o `PythonBridge`, que é o responsável pela escrita do arquivo.
* **Recomendação:** Atualizar o contrato de `export_receipt_txt` definindo os payloads para cancelamento voluntário (`{"status": "cancelled", "saved_path": null, "error": null}`) e erro de gravação (`{"status": "error", "saved_path": null, "error": "FALHA_GRAVACAO"}`). Corrigir o fluxo no Mermaid para que o retorno da seleção volte ao `PythonBridge`, que então efetua a gravação no `FileSystem`.

---

### 2.3 Inspeção Rígida de Registro do WebView2 Restrita a `HKLM` e Indefinição de Instalação Offline
* **Severidade:** 🟡 Major
* **Lente de Origem:** `egm-design`
* **Escopo Afetado:** Linhas 195-199 (Seção 5.5.3 - *Instalador Padronizado com Inno Setup*)
* **Descrição da Discrepância:** A checagem do Inno Setup valida exclusivamente a chave de registro `HKLM\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}`. Caso o usuário possua o WebView2 instalado em nível de usuário (`HKCU`), essa verificação gerará um falso negativo e tentará reinstalar o runtime. Adicionalmente, o documento especifica a execução silenciosa do "Evergreen Bootstrapper", que requer conectividade ativa com a internet; caso o usuário instale o software em uma máquina desconectada da rede, o processo de setup falhará sem tratamento.
* **Recomendação:** Atualizar o script Pascal do Inno Setup para inspecionar ambas as chaves de registro (`HKLM` e `HKCU`, cobrindo 32 e 64 bits). Documentar o tratamento de contingência para máquinas sem conexão à internet com mensagem de pré-requisito e link oficial.

---

### 2.4 Assimetria Estrutural e Contrato Indefinido no Método `get_app_info()`
* **Severidade:** 🟡 Major
* **Lente de Origem:** `egm-structural`
* **Escopo Afetado:** Linhas 142-144 (Seção 5.2.3 - *Método get_app_info*)
* **Descrição da Discrepância:** Ao contrário dos métodos `calculate` e `export_receipt_txt`, que detalham parâmetros, fluxos e schemas JSON completos de retorno, `get_app_info()` apresenta apenas uma linha descritiva informal sem demonstrar assinatura, campos retornados ou tipos de dados. Além disso, o método não possui chamadas documentadas no frontend (Seções 5.1 e 5.4).
* **Recomendação:** Remover `get_app_info()` formalmente da especificação (conforme apontado também no Zoom Out) por falta de consumidor, ou fornecer seu schema JSON explícito caso seja retido para fins de telemetria interna.

---

### 2.5 Ambiguidade na Normalização de Entrada Decimal (Vírgula vs Ponto no Numpad ABNT2)
* **Severidade:** 🟡 Major
* **Lente de Origem:** `egm-design`
* **Escopo Afetado:** Linhas 181-184 (Seção 5.4.3) e Linha 108 (Seção 5.2.1)
* **Descrição da Discrepância:** A Seção 5.4.3 prevê a captura de eventos de teclado físico para ponto (`.`) e vírgula (`,`), comum no teclado numérico brasileiro ABNT2. Contudo, o validador AST (Seção 5.3) processa a expressão matemática sob sintaxe Python em modo `eval`, onde a presença de vírgula gera nós do tipo `ast.Tuple`, que são rejeitados de forma rígida com `SecuritySyntaxError`. O documento omite onde ocorre a sanitização dessa tecla antes da avaliação.
* **Recomendação:** Explicitar que a camada de frontend (`app.js`) normaliza a vírgula para ponto (`.`) antes de despachar a string pela ponte IPC, garantindo que o backend receba unicamente literais decimais válidos.

---

### 2.6 Isolamento Incompleto de Janela Confiando Apenas em Manipuladores de Eventos JS
* **Severidade:** 🟡 Major
* **Lente de Origem:** `egm-design`
* **Escopo Afetado:** Linhas 169-173 (Seção 5.4.1 - *Isolamento de Janela*)
* **Descrição da Discrepância:** A restrição contra menus de contexto e atalhos de navegação foi alocada unicamente no código JavaScript da página (`contextmenu`, `keydown` interceptando `F5`/`Ctrl+R`). No runtime do Edge WebView2, diversos atalhos de sistema e desenvolvedor (como `F12`, `Ctrl+Shift+I`, zoom via teclado e atalhos de impressão `Ctrl+P`) são interceptados pelo processo do navegador antes da propagação para o JavaScript.
* **Recomendação:** Configurar a desativação de DevTools e aceleradores indesejados diretamente na inicialização do `pywebview` / WebView2 no Python (`debug=False`, `gui='edgechromium'`).

---

### 2.7 Assertivas de Performance Não Fundamentadas e Fluff Textual de Marketing
* **Severidade:** 🟢 Nit
* **Lente de Origem:** `egm-style`
* **Escopo Afetado:** Linhas 18, 26, 36 (G1), 174, 178, 190, 214, 228
* **Descrição da Discrepância:** O texto inclui asserções categóricas de tempo de resposta sem comprovação empírica ("inicialização a frio em menos de 0.5 segundo", "comunicação em microssegundos"), além de termos promocionais ("contornos pretos expressivos", "microinteração de afundamento mecânico").
* **Recomendação:** Substituir a meta arbitrária de 0.5s por redação neutra e verificável ("inicialização rápida sem tempo de descompactação temporária") e utilizar termos técnicos objetivos.

---

### 2.8 Assimetria Idiomática nos Cabeçalhos das Seções
* **Severidade:** 🟢 Nit
* **Lente de Origem:** `egm-structural`
* **Escopo Afetado:** Linhas 10, 22, 34, 45, 55, 57, 103, 205, 209
* **Descrição da Discrepância:** As seções principais (H2) utilizam formato bilíngue inglês/português (ex.: `## 1. The Problem (O Problema)`), enquanto todas as subseções (H3 e H4) são redigidas exclusivamente em português.
* **Recomendação:** Padronizar os títulos de seção para um único padrão idiomático consistente em português.

---

### 2.9 Link Quebrável com Caminho Absoluto Local do Usuário
* **Severidade:** 🟢 Nit
* **Lente de Origem:** `egm-structural`
* **Escopo Afetado:** Linha 6
* **Descrição da Discrepância:** O metadado "Contexto de Origem" referencia um arquivo local via protocolo `file:///` com caminho absoluto da máquina do autor (`file:///C:/Users/Pichau/.../concepts_brief.md`).
* **Recomendação:** Substituir o caminho absoluto por um link relativo ou basename limpo: `[concepts_brief.md](../../concepts_brief.md)`.

---

### 2.10 Divergência na Nomenclatura da API entre Texto e Diagrama Mermaid
* **Severidade:** 🟢 Nit
* **Lente de Origem:** `egm-structural`
* **Escopo Afetado:** Linha 74 vs Linha 132
* **Descrição da Discrepância:** No diagrama Mermaid a chamada é anotada como `webview.windows.create_file_dialog`, enquanto no texto da Seção 5.2.2 é descrita como `webview.windows[0].create_file_dialog`.
* **Recomendação:** Harmonizar a sintaxe no nó do diagrama Mermaid para `window.create_file_dialog`.
