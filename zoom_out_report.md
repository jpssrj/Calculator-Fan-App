# Relatório de Revisão Arquitetural: Zoom Out (Skeptical Architect)

* **Documento Auditado:** [`docs/designs/calculator_fan_desktop.md`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L1-L320)
* **Linhas Auditadas:** 1 a 320
* **Avaliador:** Skeptical Architect (`egm-zoom-out`)
* **Status da Revisão:** Aprovado com Ressalvas (Nenhum Blocker; 4 apontamentos Major e 2 Nits de simplificação / YAGNI identificados)

---

## 1. Visão Geral de Alto Nível (High-Altitude Assessment)

A decisão central de substituir o servidor FastAPI/Uvicorn por uma janela desktop nativa via Microsoft Edge WebView2 (`pywebview`) é arquiteturalmente sólida, defensável e pragmática. Ela ataca as causas-raiz do problema original: elimina sockets TCP locais, remove alertas do Windows Defender Firewall, elimina riscos de colisão de portas e preserva 100% dos estilos CSS Neubrutalistas sem reinventar a UI em Tkinter ou PyQt. A escolha de compilação `--onedir` combinada com Inno Setup também é adequada para evitar a latência de extração do `--onefile`.

Contudo, a auditoria sob a lente de minimalismo e YAGNI identificou camadas desnecessárias de complexidade herdadas de modelos mentais de desenvolvimento web/cloud, hiper-fragmentação de módulos e métodos especulativos sem consumidor real.

---

## 2. Achados Estruturados

### 2.1 Cascata de Complexidade e Defesa de DoS Especulativa no Parser AST
* **Severidade:** 🟡 Major
* **Escopo Afetado:** Seção 5.3 ([`calculator_fan_desktop.md#L149-L160`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L149-L160)) e Seção 7.1 ([`calculator_fan_desktop.md#L248`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L248), [`#L262`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L262))
* **Evidência no Documento:**
  * Linha 153 inclui `ast.Pow` (`**`) e `ast.Mod` (`%`) na lista branca de operadores binários.
  * Linhas 158-159 definem defesas contra DoS algorítmico: limite de 50 nós sintáticos e rejeição de potenciação com expoente maior que 1000 ou menor que -1000.
  * Linha 248 cria a exceção `ExponentTooLargeError`.
  * Linha 262 prevê testes unitários específicos para validar contagem de nós e limite de expoente.
* **Racional de Simplicidade (Violação YAGNI):**
  A Calculadora Fan é um utilitário desktop focado exclusivamente em 4 operações aritméticas elementares (`+`, `-`, `*`, `/`) com parênteses. Não há operador de potência na interface de teclas da calculadora. Permitir `ast.Pow` foi uma adição puramente especulativa que gerou complexidade em cascata: temendo estouro de memória, criou-se regra de mitigação de DoS, uma exceção dedicada e testes adicionais. Em um utilitário desktop monousuário, defesas de "DoS contra si mesmo" são injustificáveis.
* **Recomendação Concreta:**
  Remover completamente o suporte a `ast.Pow` e `ast.Mod` do despachante AST, limitando estritamente a `Add`, `Sub`, `Mult`, `Div`, `UAdd` e `USub`. Ao cortar a potenciação, a possibilidade de estouro exponencial é extirpada na raiz, tornando desnecessários a checagem de expoente, o limite artificial de nós e a classe `ExponentTooLargeError`.

---

### 2.2 Hiper-fragmentação e Abstração em Duas Passadas no Núcleo Matemático
* **Severidade:** 🟡 Major
* **Escopo Afetado:** Seção 5.1 ([`calculator_fan_desktop.md#L77-L81`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L77-L81), [`#L88-L90`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L88-L90)) e Seção 7.1 ([`calculator_fan_desktop.md#L247-L251`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L247-L251), [`#L262-L263`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L262-L263))
* **Evidência no Documento:**
  O núcleo matemático foi decomposto em 4 arquivos (`exceptions.py`, `ast_validator.py`, `decimal_engine.py` e `receipt_generator.py`). O fluxo arquitetural propõe duas passagens: primeiro a string é parseada e validada pelo `ASTValidator`; em seguida, a árvore sintática é repassada para o `DecimalEngine` que a percorre novamente para computar os nós.
* **Racional de Simplicidade (Sobre-engenharia):**
  Para avaliar expressões aritméticas simples, separar validação sintática e computação decimal em duas passadas através de módulos distintos gera código redundante e multiplica testes sem ganho de segurança. Um único despachante recursivo em um único arquivo (`src/core/engine.py`) valida os nós permitidos e computa em `decimal.Decimal` em uma única passagem determinística. Além disso, colocar `receipt_generator.py` dentro de `src/core/` confunde lógica de domínio matemático com formatação de apresentação/relatório.
* **Recomendação Concreta:**
  Unificar `ast_validator.py` e `decimal_engine.py` em um único módulo `src/core/engine.py` (e consolidar os testes em `tests/test_engine.py`). Mover a geração de recibo textual para a camada de ponte (`src/bridge/receipt.py`), mantendo o pacote `core` focado estritamente na aritmética exata.

---

### 2.3 Acoplamento Frágil com Estado Global em `create_file_dialog`
* **Severidade:** 🟡 Major
* **Escopo Afetado:** Seção 5.2 ([`calculator_fan_desktop.md#L132`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L132)) e Seção 7.1 ([`calculator_fan_desktop.md#L253`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L253))
* **Evidência no Documento:**
  O método `export_receipt_txt` invoca diretamente: `webview.windows[0].create_file_dialog(webview.SAVE_DIALOG, ...)`.
* **Racional de Simplicidade / Testabilidade:**
  Acessar `webview.windows[0]` acopla diretamente a classe `DesktopBridgeApi` a uma variável global mutável da biblioteca `pywebview`. Em testes unitários automatizados com `pytest` ([`tests/test_bridge_api.py`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/tests/test_bridge_api.py)), essa amarração exige mockar a lista global `webview.windows`, gerando testes frágeis e propensos a falhas de inicialização de UI headless.
* **Recomendação Concreta:**
  Injetar a referência da janela via construtor na classe `DesktopBridgeApi` (ex.: `def __init__(self, window=None): self._window = window`). Isso elimina dependências de estado global do WebView e permite testar a exportação de recibo de forma limpa com um mock simples de janela.

---

### 2.4 Indefinição do Asset do WebView2 Bootstrapper no Empacotamento
* **Severidade:** 🟡 Major
* **Escopo Afetado:** Seção 5.5 ([`calculator_fan_desktop.md#L198`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L198)) e Seção 7.1 ([`calculator_fan_desktop.md#L259-L260`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L259-L260))
* **Evidência no Documento:**
  A Seção 5.5 declara que, se a chave de registro do WebView2 estiver ausente, a instalação do Inno Setup "executa a instalação silenciosa do Evergreen Bootstrapper oficial". No entanto, a lista unificada de arquivos (`build_scripts/`) contém apenas `calculator_fan.spec`, `installer_inno.iss` e `app_icon.ico` — não há menção de onde vem o executável `MicrosoftEdgeWebview2Setup.exe`.
* **Racional de Simplicidade:**
  O script Inno Setup não pode invocar um arquivo ausente no instalador. Como o escopo do projeto é explicitamente Windows 10 e 11 x64 (Non-Goal NG1), o runtime Edge WebView2 Evergreen já vem integrado nativamente ao sistema operacional na esmagadora maioria das instalações modernas.
* **Recomendação Concreta:**
  Simplificar a checagem no Inno Setup: caso o registro aponte ausência do runtime WebView2, o instalador emite uma mensagem de alerta orientando o usuário a atualizar o sistema ou fornecendo o link oficial da Microsoft. Se a instalação silenciosa for indispensável, o binário oficial `MicrosoftEdgeWebview2Setup.exe` deve ser formalmente adicionado à pasta `build_scripts/assets/`.

---

### 2.5 Método IPC Especulativo não Consumido (`get_app_info`)
* **Severidade:** 🟢 Nit
* **Escopo Afetado:** Seção 5.2 ([`calculator_fan_desktop.md#L142-L144`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L142-L144)) e Seção 7.2 ([`calculator_fan_desktop.md#L288`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L288))
* **Evidência no Documento:**
  Definição do método `get_app_info() -> dict` para retornar metadados da aplicação e confirmação de prontidão do ambiente.
* **Racional de Simplicidade (YAGNI):**
  Nenhum componente de UI consome esse método no frontend. Trata-se de código morto pré-planejado.
* **Recomendação Concreta:**
  Remover `get_app_info()` do contrato da API IPC e focar estritamente nas operações reais do usuário: `calculate()` e `export_receipt_txt()`.

---

### 2.6 Micro-fragmentação de JavaScript no Frontend
* **Severidade:** 🟢 Nit
* **Escopo Afetado:** Seção 5.1 ([`calculator_fan_desktop.md#L66-L67`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L66-L67)), Seção 5.4 ([`calculator_fan_desktop.md#L181-L184`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L181-L184)) e Seção 7.1 ([`calculator_fan_desktop.md#L256-L257`](file:///C:/Users/Pichau/Documents/dev/portifolio/projetos/Imersão%20Alura/Calculator%20Fan%20-%20App/docs/designs/calculator_fan_desktop.md#L256-L257))
* **Evidência no Documento:**
  Divisão da lógica do cliente entre `src/ui/js/app.js` e `src/ui/js/keyboard.js`.
* **Racional de Simplicidade:**
  A aplicação consiste em um visor, 20 teclas e uma gaveta de fita retrátil. Manter a captura de teclado físico em um arquivo separado (`keyboard.js`) e a atualização do visor em outro (`app.js`) introduz acoplamento e variáveis globais compartilhadas no navegador.
* **Recomendação Concreta:**
  Consolidar toda a lógica da interface em um único arquivo `src/ui/js/app.js`, agrupando a escuta de cliques e os atalhos de teclado de forma coesa.

---

## 3. Matriz de Racionalização de Complexidade

| Item | Proposta no Documento | Recomendação de Simplificação (Zoom Out) | Redução de Complexidade |
| :--- | :--- | :--- | :--- |
| **Operadores AST** | Suporte a `Pow`, `Mod`, limites de nós e expoentes | Restringir estritamente a `+`, `-`, `*`, `/` | Elimina defesas de DoS, `ExponentTooLargeError` e testes associados |
| **Núcleo Python** | 4 arquivos (`ast_validator.py`, `decimal_engine.py`, etc.) com 2 passadas | 1 único arquivo `engine.py` com 1 passada | Reduz de 4 para 2 arquivos no backend; elimina repetição de percurso AST |
| **Ponte IPC** | 3 métodos (`calculate`, `export_receipt_txt`, `get_app_info`) | 2 métodos (remover `get_app_info`) | Elimina superfície de API não utilizada |
| **Janela / Dialog** | Chamada estática `webview.windows[0]` | Injeção de dependência `DesktopBridgeApi(window)` | Testes unitários desacoplados e sem efeitos colaterais globais |
| **Frontend JS** | 2 arquivos JS (`app.js`, `keyboard.js`) | 1 arquivo `app.js` consolidado | Sem variáveis globais no DOM |
| **Runtime Installer**| Instalação silenciosa de bootstrapper sem asset declarado | Verificação e alerta com link oficial do WebView2 | Elimina dependência fantasma no Inno Setup |
