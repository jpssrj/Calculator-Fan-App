# Design Document: Calculator Fan Desktop App (.exe)

* **Autor:** Dev & Antigravity
* **Data:** 2026-11-01
* **Status:** Finalizado (Auditado e Aprovado por Multi-Lente EGM)
* **Contexto de Origem:** [concepts_brief.md](../../concepts_brief.md)

---

## 1. O Problema

A versão original da Calculadora Fan foi desenvolvida como uma aplicação web que depende da execução de um servidor local em Python (FastAPI/Uvicorn) e do acesso via navegador web convencional. Embora essa solução tenha atendido aos requisitos de prova de conceito, seu modelo de distribuição e execução impõe limitações operacionais severas para usuários de ambiente desktop:

1. **Fricção de Inicialização e Dependências de Ambiente:** Para utilizar a calculadora, o usuário precisa ter um interpretador Python configurado, instalar dependências via terminal e disparar um processo de servidor HTTP em segundo plano antes de abrir o navegador. Esse fluxo é inadequado para um utilitário de mesa cotidiano, que deve ser iniciado instantaneamente por um atalho ou pelo Menu Iniciar do Windows.
2. **Poluição de Espaço de Trabalho no Navegador:** Calculadoras de mesa devem operar como utilitários autônomos, focados e desacoplados de janelas de navegador, onde abas sobrecarregadas, extensões de terceiros e atalhos de navegação interferem na agilidade de digitação e na ergonomia de uso contínuo com teclado numérico.
3. **Riscos de Rede e Falsos Alertas de Sistema:** Subir um servidor HTTP local (`127.0.0.1`) exclusivamente para alimentar a interface em tela introduz riscos de colisão de portas TCP e dispara alertas invasivos do Windows Defender Firewall perguntando se o usuário autoriza conexões de rede para o aplicativo, gerando desconfiança e fricção desnecessária.

Portanto, é necessário transformar a Calculadora Fan em um aplicativo desktop nativo e autocontido para Windows 10 e 11 (64-bit), distribuído com instalador padrão de sistema, que elimine o servidor web local e mantenha paridade absoluta com a estética Neubrutalista, a ergonomia tátil e o rigor de cálculo decimal do projeto original.

---

## 2. Visão Geral

O **Calculator Fan Desktop App** é um aplicativo de mesa nativo para sistemas Windows 10 e 11 (64-bit), empacotado como um executável de inicialização rápida (`.exe`) e instalado através de um instalador padronizado de sistema (Inno Setup).

A solução preserva integralmente a identidade visual autoral baseada no Design System **Neubrutalista**, com contornos pretos sólidos (3.5px), sombras duras de bloco (5px) sem desfoque, microinteração tátil de deslocamento mecânico de tecla, visor duplo de alta legibilidade e gaveta retrátil de fita de auditoria que simula bobinas de caixa registradora com topo serrilhado.

Diferente da versão web, a camada de comunicação entre a interface visual e o motor de cálculo abandona requisições HTTP e passa a operar via ponte de comunicação direta inter-processo (IPC) em Python através do componente de sistema **Microsoft Edge WebView2** (`pywebview`). O usuário obtém uma janela de utilitário isolada, sem barras de endereço, sem menus de contexto de navegador e sem risco de recarregar acidentalmente a tela.

O motor aritmético permanece fundamentado no módulo de precisão arbitrária `decimal.Decimal` sob contexto IEEE 754 decimal128 (34 dígitos de precisão) e avaliação estrita em passada única baseada na Árvore de Sintaxe Abstrata (`ast`), sem utilização de `eval()`. O histórico de sessão é retido estritamente em memória volátil, garantindo privacidade por padrão e permitindo exportação voluntária em arquivo de texto formatado (`.txt`) simulando recibo fiscal.

---

## 3. Objetivos em Escopo

* **G1 - Aplicativo Desktop Nativo com Instalador:** Entregar um instalador executável para Windows 10 e 11 x64 que registre atalhos no Menu Iniciar, Desktop e painel de controle do sistema, com inicialização imediata e sem descompactação temporária em `%TEMP%`.
* **G2 - Eliminação de Portas de Rede e Servidor HTTP:** Substituir FastAPI e Uvicorn por uma interface IPC direta em Python através do `pywebview` e Edge WebView2, operando sem abrir portas TCP locais e sem acionar avisos do Windows Firewall.
* **G3 - Paridade Visual Neubrutalista Total:** Preservar 100% da folha de estilos CSS, microinterações táteis mecânicas, visor duplo e animações da gaveta retrátil de recibo desenvolvidas na versão original.
* **G4 - Aritmética Determinística de Alta Precisão (Zero `eval`):** Processar operações aritméticas elementares (`+`, `-`, `*`, `/`) e expressões com parênteses exclusivamente por inspeção de nós da AST e cálculo em `decimal.Decimal` com precisão de 34 dígitos, eliminando imprecisões de ponto flutuante binário e notação exponencial indesejada.
* **G5 - Ergonomia e Isolamento de Janela:** Oferecer mapeamento integral de teclado físico e Numpad (com normalização de vírgula ABNT2), suprimindo menus de contexto padrão de navegador, seleções espúrias e atalhos de reload (`F5`, `Ctrl+R`) que possam reiniciar a sessão.
* **G6 - Fita de Auditoria Volátil com Exportação Nativa:** Manter o histórico de operações em memória volátil durante a execução da janela, permitindo exportar o extrato formatado via caixa de diálogo nativa de salvamento do Windows com contratos de cancelamento e erro de I/O.

---

## 4. Fora de Escopo

* **NG1 - Suporte a Versões Legadas do Windows:** A aplicação não fornecerá suporte a Windows 7, Windows 8 ou arquiteturas de 32 bits (x86). O escopo é restrito a Windows 10 e 11 (64-bit).
* **NG2 - Suporte Multiplataforma Imediato:** Compilações para macOS e distribuições Linux não estão no escopo deste design document.
* **NG3 - Persistência Permanente em Disco:** Não haverá persistência automática de cálculos em SQLite, arquivos ocultos em `%APPDATA%` ou registros do sistema; o encerramento do aplicativo descarta o histórico não exportado voluntariamente.
* **NG4 - Expansão para Funções Científicas Complexas:** O motor matemático não incluirá funções trigonométricas, cálculo matricial ou números complexos nesta etapa.
* **NG5 - Frameworks Pesados e Pacotes Offline Gigantes:** Não serão adotados Electron, Chromium Embedded Framework (CEF) completo ou pacotes offline do WebView2 Runtime que ultrapassem 20MB no instalador final.

---

## 5. Plano Técnico

### 5.1 Arquitetura Geral do Sistema

A aplicação opera através de um executável autocontido em Python empacotado que instancia uma janela de aplicação desktop sem bordas de navegador, utilizando o runtime **Microsoft Edge WebView2** gerenciado pela biblioteca `pywebview`. A comunicação entre a interface gráfica e o núcleo aritmético ocorre exclusivamente através de uma ponte IPC interna C++/Python, eliminando qualquer socket de rede ou servidor HTTP local.

```mermaid
flowchart TD
    subgraph UI ["Interface Gráfica Nativa (Edge WebView2)"]
        HTML["Chassi & Visores Neubrutalistas\n(src/ui/index.html)"]
        CSS["Design System Neubrutalista\n(src/ui/css/style.css)"]
        Controller["Gerenciador de Estado, Teclado & Fita\n(src/ui/js/app.js)"]
    end

    subgraph Bridge ["Camada de Integração IPC (pywebview js_api)"]
        JSAPI["window.pywebview.api\n(Ponte Assíncrona IPC)"]
        PythonBridge["DesktopBridgeApi\n(src/bridge/api.py)"]
        ReceiptFmt["Formatador de Recibo Textual\n(src/bridge/receipt.py)"]
        SaveDialog["Caixa de Diálogo do Windows\n(window.create_file_dialog)"]
    end

    subgraph Core ["Motor Matemático Python (Aritmética Exata)"]
        Engine["Avaliador AST & Decimal Exato\n(src/core/engine.py - 34 dígitos)"]
    end

    Controller -->|Cliques Virtuais / Numpad ABNT2| Controller
    Controller -->|Chamada IPC: calculate(expr)| JSAPI
    JSAPI -->|Interop Nativo WebView2| PythonBridge
    PythonBridge -->|Expressão Sanitizada| Engine
    Engine -->|Resultado em String Formatada| PythonBridge
    PythonBridge -->|Retorno Assíncrono JSON| JSAPI
    JSAPI -->|Renderização de Display| Controller

    Controller -->|Chamada IPC: export_receipt_txt(tape, hint)| JSAPI
    JSAPI --> PythonBridge
    PythonBridge -->|Abre Diálogo Nativo| SaveDialog
    SaveDialog -->|Caminho Escolhido ou None| PythonBridge
    PythonBridge -->|Formata Recibo| ReceiptFmt
    PythonBridge -->|Grava em Disco se Confirmado| FileSystem["Arquivo .txt de Recibo no Windows"]
    PythonBridge -->|Retorno de Status: success / cancelled / error| JSAPI
```

### 5.2 Contrato da Interface IPC (`DesktopBridgeApi`)

O frontend em JavaScript comunica-se com a instância de `DesktopBridgeApi` através do objeto global `window.pywebview.api`. A classe é instanciada com injeção de dependência da janela ativa para permitir testes automatizados desacoplados:

```python
class DesktopBridgeApi:
    def __init__(self, window=None):
        self._window = window
```

#### 1. Método: `calculate(expression: str) -> dict`
* **Parâmetro:** `expression` (string contendo a expressão a ser calculada com separador decimal em ponto, ex: `"25.5 * (4 + 6) / 2"`).
* **Retorno em Caso de Sucesso:**
  ```json
  {
    "status": "success",
    "result": "127.5",
    "expression": "25.5 * (4 + 6) / 2",
    "error": null
  }
  ```
* **Retorno em Caso de Erro de Validação ou Operação:**
  ```json
  {
    "status": "error",
    "result": null,
    "expression": "10 / 0",
    "error": "DIVISÃO POR ZERO"
  }
  ```

#### 2. Método: `export_receipt_txt(tape_entries: list, filename_hint: str) -> dict`
* **Parâmetros:**
  * `tape_entries`: lista de objetos contendo `[{"timestamp": "14:32:05", "expression": "10 + 20", "result": "30"}, ...]`.
  * `filename_hint`: sugestão de nome inicial para o arquivo (ex.: `"recibo_calculadora.txt"`).
* **Mecanismo:** Dispara `self._window.create_file_dialog(webview.SAVE_DIALOG, directory='', save_filename=filename_hint, file_types=('Text Files (*.txt)', '*.txt'))`.
* **Retorno em Caso de Sucesso na Gravação:**
  ```json
  {
    "status": "success",
    "saved_path": "C:\\Users\\Usuario\\Documents\\recibo_calculadora.txt",
    "error": null
  }
  ```
* **Retorno em Caso de Cancelamento Voluntário pelo Usuário:**
  ```json
  {
    "status": "cancelled",
    "saved_path": null,
    "error": null
  }
  ```
* **Retorno em Caso de Falha de I/O em Disco:**
  ```json
  {
    "status": "error",
    "saved_path": null,
    "error": "FALHA_GRAVACAO"
  }
  ```

### 5.3 Motor Matemático de Alta Precisão e Segurança (AST + `decimal.Decimal`)

O motor aritmético é implementado de forma coesa em passada única no módulo `src/core/engine.py`:

1. **Parser Seguro com Abstract Syntax Tree (`ast`):**
   * A string recebida é analisada por `ast.parse(expr, mode='eval')`.
   * Um despachante recursivo inspeciona cada nó da árvore e permite exclusivamente:
     * `ast.Expression`: Nó raiz da expressão.
     * `ast.BinOp`: Operações binárias de adição (`ast.Add`), subtração (`ast.Sub`), multiplicação (`ast.Mult`) e divisão (`ast.Div`).
     * `ast.UnaryOp`: Operações unárias positivas (`ast.UAdd`) e negativas (`ast.USub`).
     * `ast.Constant` / `ast.Num`: Literais numéricos estritamente inteiros ou decimais.
   * **Rejeição Rígida de Nós Ilegais:** Qualquer tentativa de utilizar funções (`ast.Call`), atributos (`ast.Attribute`), identificadores ou variáveis (`ast.Name`), listas, laços, expoentes ou importações levanta imediatamente `SecuritySyntaxError`.
   * **Conversão Estrita via String:** Operandos numéricos em `ast.Constant` são convertidos via `Decimal(str(node.value))` para garantir que literais decimais não sofram coerção intermediária para ponto flutuante binário do Python.

2. **Aritmética Determinística com `decimal.Decimal` e Formatação Numérica Limpa:**
   * Contexto de precisão aritmética global definido com `decimal.getcontext().prec = 34` (padrão IEEE 754 decimal128).
   * Tratamento de exceções centrais da biblioteca padrão (`decimal.DivisionByZero`, `decimal.InvalidOperation`, `decimal.Overflow`), convertendo-as em mensagens amigáveis em português (`"DIVISÃO POR ZERO"`, `"OPERAÇÃO INVÁLIDA"`, `"ESTOURO DE CAPACIDADE"`).
   * **Rotina de Formatação sem Notação Científica:**
     Para evitar que inteiros terminados em zero (como `Decimal('100')`) sejam convertidos indevidamente para representação científica (`1E+2`) pelo método `Decimal.normalize()`, adota-se a rotina:
     ```python
     def format_decimal(val: Decimal) -> str:
         s = f"{val:f}"
         return s.rstrip('0').rstrip('.') if '.' in s else s
     ```

### 5.4 Camada de Apresentação e Interação Desktop (WebView2)

1. **Isolamento de Janela no Runtime e no Frontend:**
   * A inicialização no Python em `src/main.py` configura `debug=False`, `gui='edgechromium'`, `resizable=False`, `zoomable=False` e `easy_drag=False`, desativando nativamente atalhos de desenvolvedor (`F12`, `Ctrl+Shift+I`) e aceleradores de navegação.
   * O frontend suprime o evento de menu de contexto (`contextmenu`) e atalhos de recarregamento (`F5`, `Ctrl+R`) no DOM.
   * Seleção de texto (`user-select: none`) é aplicada globalmente, mantendo-se habilitada apenas nos caracteres numéricos dos visores para fins de cópia manual.

2. **Design System Neubrutalista Puro:**
   * Bordas pretas sólidas de `3.5px solid #000000`.
   * Sombras rígidas em bloco de `5px 5px 0px #000000` sem desfoque.
   * Estado `:active` de botões com deslocamento mecânico tátil (`transform: translate(3px, 3px)` e redução da sombra para `2px 2px 0px #000000`).
   * Paleta cromática funcional: fundo marfim pastel retrô (`#FEFCE8`), visor duplo ciano elétrico (`#C4F1F9`), botão de execução em verde neon (`#00F5D4`), controle em rosa choque (`#FF0055`) e operadores em amarelo canário (`#FFE600`) e lilás (`#A78BFA`).
   * Gaveta retrátil de fita de histórico com recorte superior serrilhado em CSS `clip-path`, carimbo de data/hora, botão de resgate (*Recall*) que reintroduz o resultado no visor principal e botão de exportação em `.txt`.

3. **Máquina de Estados e Captura de Teclado no Frontend (`app.js`):**
   * Captura eventos de clique virtual e teclas físicas do teclado alfanumérico e Numpad (`0-9`, `.`, `,`, `+`, `-`, `*`, `/`, `Enter`, `=`, `Backspace`, `Escape`).
   * **Normalização Imediata da Vírgula ABNT2:** Ao digitar `,` ou clicar na vírgula, o caractere é imediatamente normalizado para ponto (`.`) no estado interno antes da exibição e do envio pela ponte IPC.
   * **Regras de Transição de Estado:**
     * Tecla `Escape` ou botão `AC` limpa totalmente os visores (*All Clear*).
     * Tecla `Backspace` remove o último caractere digitado.
     * Operadores consecutivos substituem o operador anterior, exceto o sinal de subtração quando usado como unário negativo.
     * Ao teclar fisicamente, a classe CSS `.is-pressed` é acionada momentaneamente no botão correspondente da tela, garantindo sincronia tátil.

### 5.5 Empacotamento, DPI Awareness e Ciclo de Vida do Aplicativo

1. **Resolução de Assets e Compilação PyInstaller (`--onedir`):**
   * O ponto de entrada `src/main.py` resolve arquivos estáticos via rotina compatível com o PyInstaller:
     ```python
     def get_asset_path(relative_path: str) -> str:
         base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
         return os.path.join(base_path, relative_path)
     ```
   * O arquivo `.spec` inclui os assets de `src/ui/` e o ícone `build_scripts/assets/app_icon.ico`.
   * A compilação em `--onedir` garante abertura imediata sem a latência de descompactação de 2 a 4 segundos do modo `--onefile`.

2. **Per-Monitor DPI Awareness (V2):**
   * O manifesto do executável declara suporte a DPI Awareness Per-Monitor V2, assegurando nitidez em telas de alta densidade sob escalas de 125%, 150% ou 200%.

3. **Instalador Padronizado com Inno Setup (`setup.iss`):**
   * Compilado com a diretiva `ArchitecturesInstallIn64BitMode=x64` para garantir instalação limpa em `{autopf}\Calculator Fan` em sistemas de 64 bits.
   * Cria atalhos no Menu Iniciar e Desktop com desinstalador registrado no painel de controle do Windows.
   * **Verificação de Registro do WebView2:**
     A função Pascal `InitializeSetup()` inspeciona as chaves de registro do WebView2 Evergreen em `HKLM64`, `HKLM32` e `HKCU`:
     `SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}`
     Caso o runtime esteja ausente, o instalador exibe uma mensagem informativa nativa orientando a atualização do sistema e fornecendo o link oficial da Microsoft, abortando a instalação de forma segura e sem dependências de rede complexas.

4. **Ciclo de Encerramento Limpo:**
   * O evento `window.events.closed` no Python invoca a liberação do WebView2 e chama `sys.exit(0)`, prevenindo processos órfãos em segundo plano no Gerenciador de Tarefas do Windows.

---

## 6. Alternativas Consideradas

### 6.1 Manter Servidor FastAPI e Uvicorn em Background dentro do Executável
* **Mecanismo Avaliado:** Inicializar o servidor FastAPI em `http://127.0.0.1:8000` em segundo plano dentro do executável e conectar a WebView nessa URL local.
* **Motivo da Rejeição:** Dispara alertas invasivos do Windows Defender Firewall perguntando se o usuário autoriza conexões de rede locais, além de gerar risco de colisão se a porta TCP estiver em uso por outro processo na máquina. A ponte IPC direta em memória elimina portas e alertas.

### 6.2 Reescrever a Interface do Usuário em GUI Nativa Python (Tkinter / PyQt6)
* **Mecanismo Avaliado:** Descartar o HTML/CSS e redesenhar os componentes com widgets nativos de Tkinter ou PyQt.
* **Motivo da Rejeição:** Impossibilidade de replicar com facilidade as sombras projetadas duras sem blur (5px), bordas de 3.5px, recortes serrilhados em SVG/CSS da fita e microinterações mecânicas táteis, além do acréscimo de mais de 80MB de dependências com PyQt6. O WebView2 consome o motor do Edge já instalado no Windows mantendo paridade estética perfeita.

### 6.3 Distribuição em Arquivo Único Portátil (`--onefile` no PyInstaller)
* **Mecanismo Avaliado:** Compilar um binário único `calculator_fan.exe` sem instalador.
* **Motivo da Rejeição:** A cada abertura, o Windows precisa descompactar dezenas de megabytes em `%TEMP%`, adicionando um atraso de 2 a 4 segundos que degrada o uso instantâneo da calculadora e aciona alertas de antivírus heurístico. O modo `--onedir` com instalador Inno Setup oferece abertura imediata e distribuição limpa.

### 6.4 Embutir Pacote Offline do WebView2 Runtime no Instalador
* **Mecanismo Avaliado:** Baixar e incluir o Fixed Version Runtime do WebView2 dentro do instalador Inno Setup para cobertura em máquinas sem internet.
* **Motivo da Rejeição:** O runtime offline elevaria o tamanho do instalador de ~15MB para mais de 160MB, violando o Non-Goal NG5. Como o target é estritamente Windows 10/11 x64, onde o WebView2 é componente padrão de sistema operacional atualizado, a verificação de registro com alerta amigável é a solução mais enxuta e defensável.

---

## 7. Plano Detalhado de Implementação

### 7.1 Lista Unificada de Arquivos do Projeto (Topologia Consolidada em 14 Arquivos)

| Arquivo | Ação | Racional Técnico |
| :--- | :--- | :--- |
| `requirements.txt` | Criar | Declara dependências de produção (`pywebview>=5.0.0`), empacotamento (`pyinstaller>=6.0.0`) e testes (`pytest>=8.0.0`). |
| `README.md` | Criar | Documentação técnica completa, comandos de inicialização em desenvolvimento, testes automatizados e compilação do executável e do instalador. |
| `src/__init__.py` | Criar | Inicializador de pacote Python para o módulo raiz do código-fonte. |
| `src/main.py` | Criar | Ponto de entrada: resolve caminhos com `sys._MEIPASS`, instancia a janela com dimensões 400x640px, bloqueio de DevTools/zoom, injeta janela na `DesktopBridgeApi` e amarra encerramento limpo via `sys.exit(0)`. |
| `src/core/__init__.py` | Criar | Inicializador de pacote para o motor aritmético. |
| `src/core/engine.py` | Criar | Motor aritmético determinístico em passada única: validação de nós permitidos da AST (`Add`, `Sub`, `Mult`, `Div`, `UAdd`, `USub`), aritmética exata com `Decimal(str(...))` sob 34 dígitos e formatação sem notação científica. |
| `src/bridge/__init__.py` | Criar | Inicializador de pacote para a camada IPC. |
| `src/bridge/api.py` | Criar | Classe `DesktopBridgeApi` com construtor `(window=None)` e métodos `calculate(expr)` e `export_receipt_txt(tape, hint)` com schemas formais de `success`, `cancelled` e `error`. |
| `src/bridge/receipt.py` | Criar | Formatador de extrato de auditoria em texto plano UTF-8 simulando recibo fiscal com largura fixa de 36 colunas, cabeçalho, carimbo de hora e rodapé. |
| `src/ui/index.html` | Criar | Estrutura semântica HTML5 acessível com chassi Neubrutalista, visor duplo, grade de teclas e gaveta retrátil da fita de recibo. |
| `src/ui/css/style.css` | Criar | Design System Neubrutalista puro: bordas pretas de 3.5px, sombras duras de 5px, deslocamento mecânico tátil (`:active`), paleta cromática saturada e serrilhado em CSS `clip-path`. |
| `src/ui/js/app.js` | Criar | Gerenciador unificado de interface: cliques virtuais, captura de teclado e Numpad, normalização de vírgula ABNT2, máquina de estados da calculadora e integração assíncrona com `window.pywebview.api`. |
| `build_scripts/calculator_fan.spec` | Criar | Configuração do PyInstaller em modo `--onedir` e `--noconsole`, incluindo dados estáticos de `src/ui/` e ícone `.ico`. |
| `build_scripts/installer_inno.iss` | Criar | Script Inno Setup x64 (`ArchitecturesInstallIn64BitMode=x64`) com atalhos no Menu Iniciar/Desktop e função Pascal de checagem do WebView2 no Registro. |
| `build_scripts/assets/app_icon.ico` | Criar | Ícone oficial da aplicação com camadas de resolução 16x16, 32x32, 48x48 e 256x256. |
| `tests/__init__.py` | Criar | Inicializador de pacote para testes automatizados. |
| `tests/test_engine.py` | Criar | Testes unitários do motor aritmético: precisão IEEE 754 decimal128 (`0.1 + 0.2 == 0.3`), precedência de operadores, parênteses, ausência de notação exponencial em inteiros e bloqueio de nós perigosos. |
| `tests/test_bridge_api.py` | Criar | Testes unitários da ponte IPC: cálculo assíncrono, injeção de dependência da janela com Mock e validação dos retornos de sucesso, cancelamento e erro de salvamento de recibo. |

---

### 7.2 Roteiro Sequencial de Implementação

#### Fase 1: Ambiente de Dependências e Núcleo Aritmético Exato (Core)
1. **Configuração do Ambiente:**
   - Criar `requirements.txt` com as dependências `pywebview>=5.0.0`, `pyinstaller>=6.0.0` e `pytest>=8.0.0`.
   - Criar `src/__init__.py`, `src/core/__init__.py` e `tests/__init__.py`.
2. **Implementação do Motor Aritmético Unificado:**
   - Criar `src/core/engine.py` contendo:
     - Função `evaluate_expression(expr: str) -> str`.
     - Despachante recursivo inspecionando nós `ast.Expression`, `ast.BinOp` (`Add`, `Sub`, `Mult`, `Div`), `ast.UnaryOp` (`UAdd`, `USub`) e `ast.Constant`.
     - Conversão de operandos numéricos estritamente via string: `Decimal(str(node.value))`.
     - Contexto decimal com precisão 34 dígitos (`decimal.getcontext().prec = 34`).
     - Função de formatação `format_decimal(val)` suprimindo zeros redundantes sem introduzir notação exponencial.
     - Captura de `decimal.DivisionByZero` (`"DIVISÃO POR ZERO"`), `decimal.InvalidOperation` (`"OPERAÇÃO INVÁLIDA"`) e `decimal.Overflow` (`"ESTOURO DE CAPACIDADE"`).
3. **Verificação da Fase 1:**
   - Criar `tests/test_engine.py` e executar `python -m pytest tests/test_engine.py -v`.
   - Critério de aprovação: 100% de sucesso em testes de precisão (`0.1 + 0.2 == 0.3`, `100 / 10 == 10`), precedência (`2 + 3 * 4 == 14`), parênteses, divisão por zero e rejeição de chamadas perigosas (`__import__`, `eval`, `open`).

#### Fase 2: Camada de Integração IPC e Ponto de Entrada Desktop (Bridge & Main)
1. **Desenvolvimento do Formatador de Recibo e Ponte IPC:**
   - Criar `src/bridge/__init__.py`.
   - Criar `src/bridge/receipt.py` com a função `format_receipt_text(tape_entries: list) -> str`, formatando extrato com cabeçalho de recibo fiscal em ASCII/UTF-8 de 36 colunas com timestamps e alinhamento à direita para resultados.
   - Criar `src/bridge/api.py` implementando `DesktopBridgeApi` com:
     - Construtor `__init__(self, window=None)`.
     - Método `calculate(expression: str) -> dict`.
     - Método `export_receipt_txt(tape_entries: list, filename_hint: str) -> dict`, retornando status formal de `success` (com `saved_path`), `cancelled` (se retorno do diálogo for nulo) ou `error` (se ocorrer `IOError`/`PermissionError`).
2. **Ponto de Entrada e Resolução de Assets:**
   - Criar `src/main.py` contendo a rotina `get_asset_path(relative_path)` com `sys._MEIPASS`.
   - Instanciar janela `webview.create_window` com título `"Calculator Fan"`, dimensões 400x640px, `resizable=False`, `easy_drag=False`, `zoomable=False` e amarrar `DesktopBridgeApi(window)`.
   - Iniciar aplicação com `webview.start(debug=False, gui='edgechromium')` e vincular evento `closed` para `sys.exit(0)`.
3. **Verificação da Fase 2:**
   - Criar `tests/test_bridge_api.py` e rodar `python -m pytest tests/test_bridge_api.py -v`.
   - Critério de aprovação: Validação com mock de janela para retornos de cálculo, salvamento com arquivo gravado e cancelamento de diálogo.

#### Fase 3: Interface Gráfica Neubrutalista e Interatividade Unificada (UI)
1. **Estrutura HTML e Estilos CSS Neubrutalistas:**
   - Criar `src/ui/index.html` com marcação semântica, display duplo (`main-display` e `sub-display`), teclado 4x5 e gaveta lateral de fita de auditoria com botão de resgate (*Recall*) e exportação de recibo.
   - Criar `src/ui/css/style.css` com bordas pretas de 3.5px, sombras duras de 5px, estados `:active` táteis de afundamento mecânico, paleta de cores de alto contraste e recorte serrilhado em SVG/CSS da bobina de papel.
2. **Lógica de Interface e Máquina de Estados:**
   - Criar `src/ui/js/app.js` unificando cliques em tela e teclas físicas (alfanumérico e Numpad).
   - Normalizar imediatamente a vírgula ABNT2 para ponto (`expression.replace(/,/g, '.')`).
   - Implementar regras de transição de estado da calculadora: substituição de operadores consecutivos, botão `AC` para limpeza total, `Backspace` para exclusão de caractere e injeção do valor no visor pelo botão *Recall*.
   - Suprimir atalhos de navegador (`contextmenu`, `F5`, `Ctrl+R`).
   - Sincronizar pressionamento de teclado físico adicionando temporariamente a classe `.is-pressed` ao botão da interface.
3. **Verificação da Fase 3:**
   - Executar `python src/main.py` e verificar renderização visual com paridade de 100%, digitação por Numpad físico e resgate de histórico na fita de recibo.

#### Fase 4: Automação de Build e Instalador Windows (Build Scripts)
1. **Ícone e Especificação do PyInstaller:**
   - Gerar `build_scripts/assets/app_icon.ico` com múltiplos tamanhos de resolução (16x16, 32x32, 48x48, 256x256).
   - Criar `build_scripts/calculator_fan.spec` em modo `--onedir`, `--windowed` (`--noconsole`), vinculando a pasta `src/ui/` e o ícone.
   - Executar compilação com `pyinstaller build_scripts/calculator_fan.spec --clean --noconfirm` e verificar integridade da pasta `dist/calculator_fan/`.
2. **Script do Inno Setup x64:**
   - Criar `build_scripts/installer_inno.iss` com `ArchitecturesInstallIn64BitMode=x64`, definindo diretório padrão `{autopf}\Calculator Fan`, atalhos no Menu Iniciar e Desktop, e desinstalador registrado.
   - Implementar função Pascal `InitializeSetup()` inspecionando chaves `HKLM64`, `HKLM32` e `HKCU` do WebView2 Evergreen, alertando o usuário e cancelando instalação com segurança se ausente.
   - Compilar instalador gerando `dist/CalculatorFan_Setup_x64.exe`.
3. **Verificação da Fase 4:**
   - Testar a instalação em diretório de teste do Windows 10/11 x64, verificar abertura instantânea a partir do atalho no Menu Iniciar e desinstalação completa e sem resíduos.

#### Fase 5: Documentação e Auditoria Final
1. **Documentação Técnica:**
   - Criar `README.md` completo com diagrama Mermaid de arquitetura, tabela de atalhos de teclado, instruções de desenvolvimento local e passos para geração do executável e instalador.
2. **Auditoria Final:**
   - Executar a suíte de testes com `python -m pytest tests/ -v`.
