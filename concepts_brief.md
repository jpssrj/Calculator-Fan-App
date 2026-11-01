# Calculator Fan Desktop App (.exe)

* **Autor:** Dev & Antigravity
* **Data:** 2026-11-01
* **Status:** Concluído (Multi-Lens Brainstorm Synthesis)

---

## Overview

O **Calculator Fan Desktop App** é a transposição direta da calculadora web Neubrutalista para uma aplicação desktop nativa do Windows 10 e 11 (64-bit), distribuída por meio de um instalador executável padrão de sistema.

A aplicação abandona a arquitetura cliente-servidor baseada em FastAPI/Uvicorn e adota uma integração direta entre frontend e backend via `pywebview`, consumindo o componente nativo **Microsoft Edge WebView2**. A interface (HTML5, CSS3 Neubrutalista nativo e Vanilla JavaScript) conecta-se diretamente ao motor matemático Python por uma ponte IPC bidirecional (`js_api`), sem abrir portas de rede locais (`localhost`) e sem expor o usuário a alertas de firewall do sistema operacional.

O sistema mantém paridade visual estrita com o Design System Neubrutalista original (bordas sólidas de 3.5px, sombras duras de projeção de 5px sem desfoque, microinteração mecânica tátil ao pressionar teclas, visor duplo e gaveta retrátil de fita de auditoria). Os cálculos continuam sendo avaliados com precisão de 34 dígitos decimais (padrão IEEE 754 decimal128) via módulo `decimal.Decimal` e interpretador seguro baseado na Árvore de Sintaxe Abstrata (`ast`), com tolerância zero para funções perigosas como `eval()`. A sessão permanece 100% volátil em memória, permitindo exportação opcional do histórico como recibo fiscal em `.txt` via diálogo nativo do Windows.

---

## Analysis

### 1. Arquitetura IPC Direta e Eliminação do Servidor HTTP
* **Eliminação de Sockets de Rede:** Na versão web anterior, o frontend fazia requisições `fetch()` para endpoints HTTP servidos por FastAPI e Uvicorn (`127.0.0.1:8000`). No ambiente desktop, essa abordagem acarreta sérios riscos: colisão caso a porta já esteja ocupada e exibição da tela de bloqueio do Windows Defender Firewall.
* **Ponte Nativa `window.pywebview.api`:** A comunicação passa a ocorrer por chamadas de função assíncronas serializadas internamente pelo Edge WebView2 sobre tubos de comunicação nativos C++ do Windows. O frontend chama `window.pywebview.api.calculate(expression)` e recebe o retorno diretamente em JSON, eliminando latência de rede e dependências pesadas de servidor assíncrono (Starlette, Uvicorn, AnyIO, H11).

### 2. Motor de Renderização e Suporte a WebView2
* **Aproveitamento do Runtime Nativo:** O Windows 11 e as versões modernas do Windows 10 x64 já contam com o runtime Microsoft Edge WebView2 pré-instalado em nível de sistema operacional (Evergreen).
* **Paridade Visual com CSS Nativo:** Utilizar o WebView2 preserva 100% da renderização CSS Neubrutalista já homologada (incluindo `box-shadow` duro, `clip-path` do serrilhado da fita de recibo e fontes monoespaçadas), sem as limitações e distorções gráficas inerentes a bibliotecas de GUI como Tkinter ou PyQt.
* **Isolamento de Janela de Aplicativo:** A janela é instanciada com menus de contexto desativados (`contextmenu` suprimido com preventDefault), atalhos de navegador desativados (`F5`, `Ctrl+R` para evitar perda acidental do histórico volátil) e seleção de texto restrita aos visores.
* **Nitidez Visual e DPI:** Tratamento de Per-Monitor DPI Awareness (V2) via manifesto do executável para manter bordas e traços pretos nítidos em monitores 1080p, 2K e 4K sob quaisquer escalas do Windows (125%, 150%, 200%).

### 3. Motor Matemático e Segurança Aritmética
* **Parser AST com Lista Branca Restrita:** A expressão recebida pelo método Python é processada exclusivamente por `ast.parse(expr, mode='eval')` e percorrida por um despachante restritivo. Apenas nós dos tipos `Expression`, `BinOp` (`+`, `-`, `*`, `/`, `**`, `%`), `UnaryOp` (`+`, `-`) e `Constant` numérico são autorizados.
* **Proteção contra DoS Algorítmico:** O parser rejeita árvores com mais de 50 nós sintáticos e bloqueia expoentes desproporcionais (`base ** exponent` onde `exponent > 1000`) para evitar congelamento de CPU.
* **Aritmética Exata (`decimal.Decimal`):** Operações são executadas sob contexto decimal de 34 dígitos (`getcontext().prec = 34`). Todos os números são convertidos a partir de suas representações textuais diretas para `Decimal`, impedindo imprecisões do ponto flutuante binário do JavaScript e do Python. Divisões por zero retornam mensagens de erro claras sem interrupção do processo.

### 4. Empacotamento, Distribuição e Ciclo de Vida
* **Modo `--onedir` no PyInstaller:** O empacotamento em pasta única (`--onedir`) com flag `--noconsole` é adotado para garantir inicialização a frio em menos de 0.5 segundo, contornando a lentidão e falsos positivos de antivírus heurístico típicos da extração contínua em `%TEMP%` gerada pelo modo `--onefile`.
* **Instalador Inno Setup (`setup.iss`) com Verificação de Runtime:** Gera um instalador profissional com atalhos no Menu Iniciar, ícone no Desktop e entrada padronizada no "Adicionar ou Remover Programas" do Windows. O instalador inspeciona a chave de registro do WebView2 (`HKLM\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}`) e, caso ausente, aciona o bootstrapper oficial silencioso do WebView2 Evergreen.
* **Encerramento Determinado:** A vinculação do evento `window.events.closed` garante que o encerramento da interface execute a limpeza de threads e termine o processo com `sys.exit(0)`, sem deixar instâncias órfãs consumindo memória em background no Gerenciador de Tarefas.

---

## Goals vs. Non-Goals

### In-Scope Goals
* Construir um aplicativo executável nativo Windows 10/11 x64 com instalador formal gerado via Inno Setup.
* Eliminar o FastAPI/Uvicorn em favor de uma integração direta de IPC nativo com `pywebview` e motor Microsoft Edge WebView2.
* Reutilizar e manter fidelidade visual de 100% do layout Neubrutalista original (bordas 3.5px, sombras 5px, microinterações mecânicas, visor duplo e gaveta retrátil).
* Manter o motor aritmético seguro baseado em AST + `decimal.Decimal` com precisão de 34 dígitos (padrão IEEE 754 decimal128).
* Suportar operação integral via teclado físico e teclado numérico (Numpad) com feedback visual sincronizado.
* Manter o histórico da fita de auditoria volátil em memória por padrão, com recurso de exportação manual em arquivo `.txt` via diálogo nativo do Windows (`SaveFileDialog`).
* Garantir suporte a telas de alta densidade de pixels (Per-Monitor DPI Awareness).

### Out-of-Scope Non-Goals
* Suporte a sistemas legados anteriores ao Windows 10 (ex.: Windows 7, Windows 8, Windows XP).
* Compilação ou suporte a sistemas operacionais macOS ou Linux nesta fase.
* Persistência permanente em banco de dados relacional ou arquivos de configuração ocultos em `%APPDATA%`.
* Implementação de funções científicas avançadas (matrizes, cálculo diferencial, trigonometria).
* Utilização de frameworks web pesados com etapas de build adicionais (Electron, Node.js, React).

---

## Alternatives Weighed

1. **Manter Servidor FastAPI/Uvicorn em Background dentro do Executável:**
   * *Rejeitado.* Rodar um servidor HTTP local em `127.0.0.1` acarreta abertura de portas TCP desnecessárias, risco de conflito de portas com outros serviços da máquina e alertas invasivos do Windows Defender Firewall perguntando se o usuário autoriza conexões de rede para o aplicativo.
2. **Reescrever a Interface com GUI Nativa em Python (Tkinter / CustomTkinter / PyQt6):**
   * *Rejeitado.* Frameworks de interface de usuário nativa em Python não possuem suporte simples para os recursos visuais já desenvolvidos em CSS Neubrutalista (como sombras duras em ângulo específico sem blur, bordas espessas uniformes, clip-path serrilhado para simular bobina de papel de recibo e animações `:active`). A reescrita geraria retrabalho substancial e degradação visual do produto original.
3. **Distribuição em Arquivo Único (`--onefile` no PyInstaller):**
   * *Rejeitado.* O modo de arquivo único obriga a descompactação contínua de dezenas de megabytes de binários e bibliotecas no diretório `%TEMP%` do Windows a cada inicialização, adicionando atraso perceptível de 2 a 4 segundos na abertura do aplicativo e elevando o risco de falsos positivos em antivírus heurísticos. A combinação de `--onedir` com instalador padrão Inno Setup oferece inicialização instantânea e distribuição organizada.
4. **Empacotamento com Electron:**
   * *Rejeitado.* O Electron embute uma instância completa do Chromium e do Node.js, elevando o tamanho do instalador para mais de 150MB e o consumo de memória RAM para mais de 200MB, além de exigir uma camada adicional de comunicação para acionar o motor matemático em Python. O `pywebview` consome o WebView2 já presente no Windows, mantendo o executável enxuto.

---

## Key Decisions & Staging for Next Steps

* **Decisão 1 (Ponte Desktop):** Utilizar `pywebview` consumindo Microsoft Edge WebView2 nativo com a classe de ponte `DesktopBridgeApi` mapeada em `window.pywebview.api`.
* **Decisão 2 (Estrutura de Código):** Organizar o código em `src/core/` (motor matemático AST e gerador de recibo), `src/bridge/` (API IPC e diálogos de sistema), `src/ui/` (HTML, CSS Neubrutalista e JS de controle) e `build_scripts/` (especificação do PyInstaller e instalador Inno Setup).
* **Decisão 3 (Empacotamento e Entrega):** Adotar compilação PyInstaller no modo `--onedir` e `--noconsole`, empacotada por um instalador Inno Setup (`setup.iss`) direcionado a Windows 10/11 x64 com checagem de runtime WebView2.
* **Decisão 4 (Exportação Nativa de Recibo):** O botão de exportação da fita acionará o método IPC `export_receipt_txt()` que chamará a caixa de diálogo nativa do Windows para salvar o arquivo de texto em local escolhido pelo usuário.
