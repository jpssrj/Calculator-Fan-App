# Relatório de Revisão Arquitetural Intermediária (Stage 8 Intermediate Zoom Out Review)

* **Documento Auditado:** [`docs/designs/calculator_fan_desktop.md`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md) (Linhas 1 a 320)
* **Relatórios Prévios Integrados:** 
  * [`zoom_out_report.md`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/zoom_out_report.md) (Stage 5)
  * [`comprehension_report.md`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/comprehension_report.md) (Stage 6)
  * [`critic_report.md`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/critic_report.md) (Stage 7)
* **Avaliador:** Skeptical Architect (`egm-zoom-out`)
* **Status da Revisão:** Aprovado com Definição Estrita de Fronteiras Mínimas (Guarda contra Inflação de Escopo Reativa)

---

## 1. Avaliação de Alta Altitude e Contexto do Estágio 8

O objetivo desta revisão intermediária (**Stage 8 Intermediate Zoom Out**) é subir novamente para a altitude de 30.000 pés e avaliar o sistema como um todo após os relatórios de Compreensão (Stage 6) e Crítica (Stage 7). Em particular, o Skeptical Architect deve verificar se os apontamentos técnicos e as mitigações sugeridas pelas etapas anteriores introduziram **complexidade acidental**, **inchaço de código (bloat)** ou **quebra de fronteiras defensáveis** no utilitário.

### Diagnóstico de Saúde Arquitetural:
1. **Núcleo Arquitetural Sólido:** A substituição da pilha cliente-servidor FastAPI/Uvicorn por uma janela desktop nativa via Microsoft Edge WebView2 (`pywebview`), integrada a um interpretador aritmético seguro baseado em nós da AST com `decimal.Decimal` e empacotamento PyInstaller `--onedir` com Inno Setup, permanece sendo a rota arquitetural mais enxuta, veloz e elegante para resolver o problema raiz.
2. **O Risco da "Inflação de Escopo Reativa":** Ao analisar os relatórios das etapas 6 e 7, identificou-se a tentação comum em auditorias de software: responder a lacunas pontuais propondo novas camadas de abstração, embutindo instaladores pesados para cobrir casos extremos (edge-cases de 0,1%), ou modelando contratos detalhados para métodos que não deveriam existir.
3. **Imposição de Fronteiras Mínimas:** O papel deste relatório é aplicar a lâmina de Ockham e o princípio YAGNI (*You Aren't Gonna Need It*), podando qualquer complexidade especulativa antes que ela contamine o plano de implementação detalhado.

---

## 2. Achados Estruturados e Avaliação das Mitigações (Critic & Comprehension)

### 2.1 Rejeição a Bundling e Fallbacks Complexos de Instalação Offline do WebView2
* **Severidade:** 🔴 Blocker Arquitetural (se acatada a sugestão de bundling offline) / 🟡 Major (no design atual)
* **Escopo Afetado:** Seção 5.5.3 ([`calculator_fan_desktop.md#L195-L199`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L195-L199)), Comprehension Achado #2 e Critic Achado #2.3.
* **Evidência & Discussão:**
  * No Stage 6 e Stage 7, questionou-se a ausência do instalador oficial `MicrosoftEdgeWebview2Setup.exe` na pasta `build_scripts/assets/` e o comportamento do instalador caso a máquina esteja sem conexão à internet.
  * Houve a sugestão de embutir um instalador offline (Fixed Version) ou automatizar downloads silenciosos complexos em scripts Pascal do Inno Setup.
* **Racional do Skeptical Architect (Simplicidade & YAGNI):**
  * Tentar incluir o pacote offline do WebView2 aumentaria o tamanho do instalador de ~15MB para mais de 160MB. Isso violaria frontalmente o objetivo de projeto **NG5** (*"Não serão adotados frameworks pesados... prevenindo o aumento excessivo do instalador"*).
  * O target do projeto é estritamente **Windows 10 e Windows 11 (64-bit)** ([`calculator_fan_desktop.md#L47`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L47)). Desde meados de 2021, o Microsoft Edge WebView2 Evergreen vem pré-instalado em nível de sistema operacional em praticamente 100% das máquinas corporativas e domésticas suportadas pelo Windows Update.
  * Criar fluxos de download silencioso resiliente a falhas em Pascal no Inno Setup adiciona enorme fragilidade ao processo de build para tratar uma fração insignificante de usuários.
* **Fronteira Mínima Defensável:**
  * O Inno Setup deve inspecionar de forma limpa as chaves de registro em `HKLM` e `HKCU` (cobrindo 32 e 64 bits).
  * Se o runtime for encontrado (cenário de 99,9% dos casos), a instalação prossegue sem qualquer intervenção de rede.
  * Se o runtime NÃO for encontrado, o instalador simplesmente exibe uma caixa de mensagem nativa amigável informando a dependência do sistema e apontando o link oficial da Microsoft, abortando a instalação sem tentar downloads mágicos em segundo plano.

---

### 2.2 Eliminação Radical de `get_app_info()` em vez de Formalização de Schema Especulativo
* **Severidade:** 🟡 Major
* **Escopo Afetado:** Seção 5.2.3 ([`calculator_fan_desktop.md#L142-L144`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L142-L144)), Comprehension Achado #1 e Critic Achado #2.4.
* **Evidência & Discussão:**
  * O Stage 6 apontou assimetria de documentação (falta de schema JSON) e ausência de consumo no frontend para o método `get_app_info()`.
  * O Stage 7 recomendou: *"Remover get_app_info() formalmente da especificação OU fornecer seu schema JSON explícito caso seja retido para fins de telemetria interna"*.
* **Racional do Skeptical Architect (Simplicidade & YAGNI):**
  * Não há "OU". Este é um utilitário de calculadora de mesa sem tela de configurações ("About Modal"), sem rotina de handshake de inicialização e sem servidor de telemetria.
  * Documentar schemas para `python_version`, `ready: true`, criar testes unitários para validar se o dicionário possui tais chaves e escrever código para expor metadados que a interface nunca lê é o clássico desperdício de engenharia (código morto pré-planejado).
* **Fronteira Mínima Defensável:**
  * **Excluir sumariamente** o método `get_app_info()` do contrato da ponte IPC (`DesktopBridgeApi`) e do plano de fases. A API exposta deve ter exatamente dois métodos utilitários: [`calculate(expression)`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L107) e [`export_receipt_txt(tape_entries, filename_hint)`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L128).

---

### 2.3 Prevenção contra Sobre-engenharia na Correção de Notação Científica e Exceções Decimais
* **Severidade:** 🟡 Major
* **Escopo Afetado:** Seção 5.3.2 ([`calculator_fan_desktop.md#L161-L166`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L161-L166)) e Critic Achado #2.1.
* **Evidência & Discussão:**
  * O Stage 7 identificou acertadamente um Blocker funcional: `Decimal('100').normalize()` converte o valor para representação científica `1E+2` em Python, quebrando a estética e a leitura do visor. Além disso, operações inválidas podem disparar exceções de biblioteca como `decimal.InvalidOperation` e `decimal.Overflow`.
* **Racional do Skeptical Architect (Simplicidade na Mitigação):**
  * A correção é indispensável, mas **não deve ensejar a criação de um subsistema de formatação numérica** ou de pipelines de transformação de strings.
  * Em Python, evitar a notação exponencial e remover zeros decimais irrelevantes de um `Decimal` requer uma rotina de apenas 2 a 3 linhas (ex.: formatar com `{:f}` e tratar supressão de zeros à direita apenas se houver separador decimal).
  * Da mesma forma, não é necessário criar uma árvore de 5 exceções customizadas em um arquivo separado. A captura de erros aritméticos do motor deve se apoiar diretamente na hierarquia da biblioteca padrão (`decimal.DecimalException`), mapeando-a para mensagens amigáveis em português (`"DIVISÃO POR ZERO"`, `"OPERAÇÃO INVÁLIDA"`, `"ESTOURO DE CAPACIDADE"`).
* **Fronteira Mínima Defensável:**
  * Tratar a formatação diretamente em uma função pura e compacta no motor de cálculo (`src/core/engine.py`), sem arquivos adicionais de formatadores ou bibliotecas externas.

---

### 2.4 Extirpação Definitiva de Defesas Especulativas de DoS e Operadores Inexistentes na AST
* **Severidade:** 🟡 Major
* **Escopo Afetado:** Seção 5.3.1 ([`calculator_fan_desktop.md#L153-L159`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L153-L159)), Seção 7.1 ([`calculator_fan_desktop.md#L248`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L248)) e Stage 5 Achado #2.1.
* **Evidência & Discussão:**
  * O design document ainda mantém autorização para `ast.Pow` (`**`) e `ast.Mod` (`%`), mitigação de DoS limitando a 50 nós, teto para expoentes maiores que 1000 e a classe `ExponentTooLargeError`.
* **Racional do Skeptical Architect (Causa-Raiz):**
  * A interface da Calculadora Fan possui apenas botões para Adição (`+`), Subtração (`-`), Multiplicação (`*`) e Divisão (`/`). Não há botão de exponenciação ou módulo.
  * Permitir potenciação apenas para ter que criar guardas de DoS e exceções personalizadas de limite de expoente é uma contradição de arquitetura em um utilitário desktop monousuário.
* **Fronteira Mínima Defensável:**
  * Remover sumariamente `ast.Pow`, `ast.Mod`, as verificações de contagem de nós e a classe `ExponentTooLargeError`.
  * A whitelist da AST deve autorizar estritamente: `ast.Expression`, `ast.BinOp` (`Add`, `Sub`, `Mult`, `Div`), `ast.UnaryOp` (`UAdd`, `USub`) e `ast.Constant` numérico. Qualquer outra estrutura é rejeitada imediatamente por sintaxe inválida.

---

### 2.5 Racionalização da Árvore de Arquivos (De 21 para 14 Arquivos) e Avaliação AST em Passada Única
* **Severidade:** 🟡 Major
* **Escopo Afetado:** Seção 5.1 ([`calculator_fan_desktop.md#L77-L81`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L77-L81)), Seção 7.1 ([`calculator_fan_desktop.md#L240-L266`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L240-L266)) e Stage 5 Achado #2.2.
* **Evidência & Discussão:**
  * O documento divide o núcleo Python em 4 arquivos (`exceptions.py`, `ast_validator.py`, `decimal_engine.py`, `receipt_generator.py`) e divide a interface em 2 arquivos JavaScript (`app.js`, `keyboard.js`), além de separar testes em 3 arquivos pequenos, totalizando 21 arquivos.
  * O fluxo arquitetural propõe duas passagens: valida os nós na AST e depois repassa a árvore para o motor decimal avaliá-la novamente.
* **Racional do Skeptical Architect (Simplicidade & Coesão):**
  * Para um aplicativo com 1 tela, 2 visores e 20 botões, 21 arquivos representam sobre-engenharia de repositório.
  * Validar e avaliar a AST em uma única passada recursiva determinística em um arquivo unificado (`src/core/engine.py`) elimina código duplicado de travessia de nós e simplifica a suíte de testes.
  * Consolidar os listeners de clique e teclado em um único arquivo de frontend (`src/ui/js/app.js`) elimina o risco de colisões no escopo global do WebView.
* **Fronteira Mínima Defensável:**
  * Consolidar a arquitetura em **14 arquivos essenciais**:
    1. `requirements.txt`
    2. `README.md`
    3. `src/__init__.py`
    4. `src/main.py`
    5. `src/core/__init__.py`
    6. `src/core/engine.py` (Unifica validação de nós AST, cálculo `Decimal` e formatação limpa em passada única)
    7. `src/bridge/__init__.py`
    8. `src/bridge/api.py` (Contrato IPC com `calculate` e `export_receipt_txt`)
    9. `src/bridge/receipt.py` (Formatação do extrato de texto da fita)
    10. `src/ui/index.html`
    11. `src/ui/css/style.css`
    12. `src/ui/js/app.js` (Interface unificada: botões virtuais, Numpad físico e normalização de vírgula)
    13. `build_scripts/calculator_fan.spec`
    14. `build_scripts/installer_inno.iss`
  * Suíte de testes correspondente consolidada em `tests/test_engine.py` e `tests/test_bridge_api.py`.

---

### 2.6 Desacoplamento da Janela na Ponte IPC (`DesktopBridgeApi`) vs Estado Global
* **Severidade:** 🟡 Major
* **Escopo Afetado:** Seção 5.2.2 ([`calculator_fan_desktop.md#L132`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L132)), Comprehension #5 e Critic #2.2 e #2.10.
* **Evidência & Discussão:**
  * O método `export_receipt_txt` utiliza a chamada direta `webview.windows[0].create_file_dialog()`.
* **Racional do Skeptical Architect (Simplicidade & Testabilidade):**
  * Acessar `webview.windows[0]` acopla o domínio a uma variável estática global de biblioteca. Isso complica testes unitários automatizados, que precisariam criar janelas virtuais ou manipular listas globais de terceiros.
* **Fronteira Mínima Defensável:**
  * A classe `DesktopBridgeApi` deve receber a referência da janela via injeção de dependência opcional em seu construtor:
    ```python
    class DesktopBridgeApi:
        def __init__(self, window=None):
            self._window = window
    ```
  * Em tempo de execução, o `src/main.py` injeta a janela criada. Em testes unitários com pytest, um objeto `Mock()` simples permite testar salvamento e cancelamento sem abrir nenhuma UI.

---

### 2.7 Isolamento Nativo no Runtime do `pywebview` vs Cascata de Listeners no JavaScript
* **Severidade:** 🟢 Nit
* **Escopo Afetado:** Seção 5.4.1 ([`calculator_fan_desktop.md#L169-L173`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L169-L173)) e Critic Achado #2.6.
* **Evidência & Discussão:**
  * O Stage 7 destacou que atalhos de desenvolvedor como `F12`, `Ctrl+Shift+I` e atalhos de impressão/zoom do Edge WebView2 são capturados pelo processo host C++ antes de chegarem ao JavaScript da página.
* **Racional do Skeptical Architect (Aproveitar a Plataforma):**
  * Tentar interceptar todas as combinações possíveis de teclas no DOM em JavaScript é uma batalha perdida que gera dezenas de linhas de código frágil.
  * O próprio `pywebview` possui configurações nativas que instruem o WebView2 a desativar DevTools e aceleradores indesejados (`webview.start(debug=False, gui='edgechromium')`).
* **Fronteira Mínima Defensável:**
  * Configurar o isolamento diretamente na inicialização do Python em `src/main.py`, mantendo no JavaScript apenas a supressão do menu de contexto básico (`contextmenu`) e o impedimento de reload acidental (`F5`, `Ctrl+R`).

---

## 3. Matriz de Fronteiras Mínimas Defensáveis (Minimal Defensible Boundaries)

| Dimensão Arquitetural | Proposta Atual no Documento | Apontamento Stages 6 & 7 | Fronteira Mínima Defensável (Skeptical Architect) | Vantagem de Simplicidade |
| :--- | :--- | :--- | :--- | :--- |
| **Dependência WebView2** | Instalação silenciosa sem declarar asset | Questionada ausência de pacote offline | **Checagem de registro (`HKLM`/`HKCU`) + alerta informativo.** Sem downloads mágicos nem bundling de 150MB. | Preserva o Non-Goal NG5 e mantém instalador enxuto (< 20MB). |
| **Superfície da Ponte IPC** | 3 métodos (`calculate`, `export_receipt_txt`, `get_app_info`) | Schema de `get_app_info()` incompleto | **Remoção sumária de `get_app_info()`.** Apenas 2 métodos mantidos: `calculate` e `export_receipt_txt`. | Elimina código morto sem consumidor na interface. |
| **Operadores do Motor AST** | Suporte a `Pow`, `Mod`, limites de DoS (50 nós, exp 1000) | Identificado acoplamento e complexidade | **Restringir estritamente a `+`, `-`, `*`, `/`** e unários. Remover classes de DoS e limites de expoente. | Extirpa a causa-raiz de estouro de memória sem código de proteção defensivo. |
| **Formatação Decimal** | `Decimal.normalize()` gerando `1E+2` | Blocker funcional identificado | **Rotina direta de 3 linhas de formatação** sem notação científica + captura de `decimal.DecimalException`. | Corrige o bug sem criar classes/formatadores externos. |
| **Topologia do Código-Fonte** | 21 arquivos previstos (4 módulos no core, 2 scripts JS) | Fragmentação de responsabilidades | **Consolidação em 14 arquivos essenciais.** Motor AST em passada única (`engine.py`) e JS coeso (`app.js`). | 35% menos arquivos, zero repetição de percurso AST e build mais direto. |
| **Acoplamento da Janela** | `webview.windows[0].create_file_dialog` | Fragilidade em testes headless | **Injeção de dependência:** `DesktopBridgeApi(window=window)`. | Permite mockar a janela em testes unitários sem abrir UI. |
| **Tratamento de Vírgula Decimal**| Indefinição entre tecla `,` e parse AST | Tecla `,` vira tupla na AST | **Normalização imediata na entrada (`app.js`)** convertendo `,` em `.` antes da chamada IPC. | 1 linha de sanitização; motor sempre recebe sintaxe decimal válida. |
