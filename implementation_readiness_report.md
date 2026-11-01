# Relatório de Auditoria de Prontidão de Implementação (Stage 9 Implementation Readiness Test)

* **Documento Auditado:** [`docs/designs/calculator_fan_desktop.md`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md) (Linhas 238 a 320 - `DetailedRange`)  
* **Padrão Aplicado:** Implementation Readiness Standard & Intermediate Zoom Out Architectural Decisions  
* **Revisores:** `egm-implementation-readiness`, `egm-codebase-details`, `egm-style` (Orquestrado por `egm-synthesizer`)  
* **Status da Auditoria:** Concluída com Recomendações Críticas de Alinhamento (2 Blockers, 4 Majors, 2 Nits)

---

## 1. Resumo Executivo das Verificações

1. **A lista de arquivos é exaustiva, inequívoca e totalmente acionável?**  
   *Não no estado atual.* A Seção 7.1 prescreve a topologia original de 21 arquivos (com módulos fragmentados, classes de DoS desnecessárias e métodos obsoletos como `get_app_info()`), devendo ser atualizada para incorporar as decisões vinculantes do relatório arquitetural intermediário ([`intermediate_zoom_out_report.md`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/intermediate_zoom_out_report.md)), que estabeleceu a consolidação em 14 arquivos essenciais.
2. **As instruções fase a fase são específicas o suficiente para que o implementador tome zero decisões de design?**  
   *Não.* O plano deixa lacunas: omite o mecanismo de conversão de tokens AST para `Decimal(str(...))`, não define a rotina de formatação sem notação científica (herdando o bug do `Decimal.normalize()`), transfere a modelagem da máquina de estados do frontend (`app.js`) para o implementador e não prevê a resolução de caminhos estáticos em runtime empacotado (`sys._MEIPASS`).
3. **Os arquivos de teste e critérios de verificação são específicos e suficientes?**  
   *Parcialmente.* A suíte deve refletir os 2 arquivos consolidados (`tests/test_engine.py` e `tests/test_bridge_api.py`), incluindo asserções explícitas para cancelamento de diálogo nativo, injeção de dependência e falhas de I/O em disco.
4. **Dependências ausentes e premissas do instalador:**  
   Necessidade da diretiva `ArchitecturesInstallIn64BitMode=x64` no script do Inno Setup (essencial para evitar emulação 32-bit e falhas na leitura de registro em sistemas x64), além da injeção da instância de janela na ponte IPC para viabilizar testes headless.

---

## 2. Achados Priorizados

### 2.1 Alinhamento Obrigatório com a Topologia Consolidada de 14 Arquivos
* **Severidade:** 🔴 Blocker
* **Lente de Origem:** `egm-implementation-readiness` / `egm-codebase-details`
* **Escopo Afetado:** Linhas 240-265 (Seção 7.1) e Linhas 273-304 (Seção 7.2 - Fases 1 a 3)
* **Descrição da Discrepância:** A Seção 7 ainda lista a árvore de 21 arquivos, classes de DoS para operadores inexistentes e o método obsoleto `get_app_info()`.
* **Recomendação:** Ajustar a Seção 7 para a topologia consolidada de 14 arquivos aprovada no Stage 8:
  * `src/core/engine.py`: Validação e cálculo aritmético de alta precisão em passada única determinística.
  * `src/bridge/receipt.py`: Formatação de extrato em texto plano.
  * `src/ui/js/app.js`: Gerenciamento coeso de UI, eventos de clique e captura de teclado físico com normalização de vírgula.
  * `tests/test_engine.py` e `tests/test_bridge_api.py`: Suíte de testes consolidada.

---

### 2.2 Resolução de Caminhos Estáticos em Runtime Empacotado (PyInstaller `sys._MEIPASS`)
* **Severidade:** 🔴 Blocker
* **Lente de Origem:** `egm-implementation-readiness`
* **Escopo Afetado:** Linha 246 (`src/main.py`) e Linhas 306-309 (Fase 4)
* **Descrição da Discrepância:** Em binários compilados pelo PyInstaller, os assets estáticos residem em pasta temporária mapeada em `sys._MEIPASS`. O caminho relativo direto falha em runtime empacotado gerando tela em branco.
* **Recomendação:** Especificar no roteiro da Fase 2 e 4 a função auxiliar `get_asset_path(relative_path)` utilizando `sys._MEIPASS` com fallback para caminho local.

---

### 2.3 Conversão Estrita de Tokens AST e Formatação Decimal sem Notação Científica
* **Severidade:** 🟡 Major
* **Lente de Origem:** `egm-codebase-details`
* **Escopo Afetado:** Linhas 249-250 (Seção 7.1) e Linhas 279-280 (Fase 1)
* **Descrição da Discrepância:** O plano omite que literais decimais na AST precisam ser instanciados via string `Decimal(str(node.value))` para evitar coerção prévia para float binário. Além disso, a formatação precisa evitar notação exponencial para inteiros terminados em zero (`Decimal('100') -> 100`).
* **Recomendação:** Formalizar na Fase 1 a rotina `format_decimal(val)` e o mapeamento de `decimal.DecimalException` para mensagens amigáveis em português.

---

### 2.4 Especificação da Máquina de Estados da Calculadora no Frontend (`app.js`)
* **Severidade:** 🟡 Major
* **Lente de Origem:** `egm-implementation-readiness`
* **Escopo Afetado:** Linha 256 (Seção 7.1) e Linha 300 (Fase 3)
* **Descrição da Discrepância:** O plano não detalha as regras de transição de estado da calculadora (substituição de operadores consecutivos, normalização imediata de vírgula para ponto, comportamento das teclas `C` / `CE` / `Backspace` e encadeamento de operações após cálculo).
* **Recomendação:** Descrever explicitamente a máquina de estados e o fluxo de eventos no roteiro da Fase 3.

---

### 2.5 Injeção da Instância de Janela e Contratos de I/O na Ponte IPC
* **Severidade:** 🟡 Major
* **Lente de Origem:** `egm-codebase-details`
* **Escopo Afetado:** Linha 253 (Seção 7.1) e Linhas 287-289 (Fase 2)
* **Descrição da Discrepância:** A classe `DesktopBridgeApi` deve receber a janela via construtor `DesktopBridgeApi(window=None)` para viabilizar testes automatizados sem interface gráfica aberta. Além disso, os schemas de retorno para cancelamento voluntário (`status: cancelled`) e erro de escrita em disco devem ser explícitos.
* **Recomendação:** Formalizar o construtor com injeção de dependência e os retornos JSON de `export_receipt_txt` no roteiro da Fase 2.

---

### 2.6 Diretiva x64 e Verificação Robusta de Registro no Inno Setup
* **Severidade:** 🟡 Major
* **Lente de Origem:** `egm-implementation-readiness`
* **Escopo Afetado:** Linha 259 (Seção 7.1) e Linhas 310-312 (Fase 4)
* **Descrição da Discrepância:** O script `installer_inno.iss` precisa conter `ArchitecturesInstallIn64BitMode=x64` para evitar compilação em 32-bit e redirecionamentos para `WOW6432Node`. A checagem Pascal deve inspecionar `HKLM64`, `HKLM32` e `HKCU`.
* **Recomendação:** Fornecer as diretivas de 64 bits e a rotina Pascal no roteiro da Fase 4.

---

### 2.7 Parâmetros de Travamento Estético da Janela no `src/main.py`
* **Severidade:** 🟢 Nit
* **Lente de Origem:** `egm-style`
* **Escopo Afetado:** Linha 246 (Seção 7.1) e Linha 291 (Fase 2)
* **Descrição da Discrepância:** Dimensões fixas devem vir acompanhadas dos parâmetros de bloqueio de redimensionamento e desativação de DevTools: `resizable=False`, `easy_drag=False`, `zoomable=False` e `debug=False`.
* **Recomendação:** Adicionar a listagem explícita dos parâmetros na Fase 2.

---

### 2.8 Padronização Idiomática do Título da Seção 7
* **Severidade:** 🟢 Nit
* **Lente de Origem:** `egm-style`
* **Escopo Afetado:** Linha 238
* **Descrição da Discrepância:** Formato bilíngue no título principal (`## 7. Detailed Implementation Plan (Plano Detalhado de Implementação)`).
* **Recomendação:** Harmonizar para `## 7. Plano Detalhado de Implementação`.
