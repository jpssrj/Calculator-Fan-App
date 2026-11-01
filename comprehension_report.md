## Feature Specification Paraphrase

### O que o documento propõe
O documento propõe a transformação da Calculadora Fan de uma aplicação web local em um aplicativo desktop nativo e autocontido (`.exe`) para Windows 10 e 11 (64-bit), distribuído com instalador oficial via Inno Setup. A solução preserva a identidade visual Neubrutalista original (contornos de 3.5px, sombras duras de 5px, feedback mecânico tátil e gaveta de fita de recibo com topo serrilhado). A comunicação entre a interface gráfica e o motor aritmético abandona o protocolo HTTP e adota uma ponte de comunicação inter-processo (IPC) direta gerenciada pelo `pywebview` sobre o componente nativo Microsoft Edge WebView2. Os cálculos são avaliados de forma determinística por inspeção de nós da Árvore de Sintaxe Abstrata (`ast`) e pelo módulo `decimal.Decimal` com precisão IEEE 754 de 34 dígitos, mantendo o histórico de operações estritamente em memória volátil com opção de exportação em arquivo `.txt`.

### Como o sistema existente funciona, segundo este documento
Conforme descrito no documento, a versão legada da Calculadora Fan opera como um serviço web que requer a inicialização prévia de um servidor Python local (FastAPI/Uvicorn em `127.0.0.1`) via terminal e acesso por navegador web padrão. Essa arquitetura impõe fricção de configuração de ambiente ao usuário comum, polui a área de trabalho do navegador com abas e atalhos concorrentes, e introduz riscos de colisão de portas TCP e alertas invasivos do Windows Defender Firewall para conexões de rede locais.

---

## Implementation Plan Paraphrase

### O que o documento propõe
O plano propõe a criação de uma árvore de 21 arquivos organizada em módulos de domínio aritmético (`src/core/`), camada de ponte IPC (`src/bridge/`), interface gráfica desacoplada (`src/ui/`), automação de compilação/instalador (`build_scripts/`) e suíte de testes unitários (`tests/`). A execução é estruturada em 5 fases sequenciais: (1) motor aritmético de alta precisão e validação AST; (2) camada IPC e ciclo de vida da janela desktop; (3) frontend Neubrutalista com captura de teclado físico e Numpad; (4) empacotamento com PyInstaller (`--onedir`) e geração de instalador via Inno Setup; e (5) documentação técnica e auditoria final com Pytest.

### Como o sistema existente funciona, segundo este documento
O plano não descreve código preexistente no repositório desktop novo, assumindo uma construção greenfield dos módulos desktop baseada na especificação do design document e na transposição dos componentes de interface e regras matemáticas da versão web anterior.

---

## Comprehension Findings

### 1. Schema de retorno e consumo indefinidos para `get_app_info()`
* **Severidade:** 🟡 Major
* **Escopo Afetado:** Seção 5.2 (*Contrato da Interface IPC*), linhas 142–144.
* **Descrição da Discrepância & Racional:** Enquanto os métodos `calculate()` e `export_receipt_txt()` contam com especificações detalhadas de parâmetros de entrada e schemas JSON para casos de sucesso e erro, o método `get_app_info() -> dict` limita-se a declarar: *"Retorna metadados da aplicação, versão do motor Python e confirmação de prontidão do ambiente"*. Não há especificação formal das chaves do dicionário retornado (ex.: `{"app_version": "1.0.0", "python_version": "3.11.x", "ready": true}`). Além disso, o documento não explicita se esse método é consumido na inicialização pelo `app.js` ou se é apenas um utilitário para depuração/testes.

### 2. Dependência e estratégia de distribuição do Microsoft Edge WebView2 Bootstrapper
* **Severidade:** 🟡 Major
* **Escopo Afetado:** Seção 5.5 (*Instalador Padronizado com Inno Setup*), linha 198 e Seção 7.1 (*Lista Unificada de Arquivos*).
* **Descrição da Discrepância & Racional:** O documento afirma que a rotina de pré-instalação verifica o registro do sistema e, se o WebView2 estiver ausente, *"executa a instalação silenciosa do Evergreen Bootstrapper oficial"*. No entanto, a tabela de arquivos (Seção 7.1) não lista nenhum executável de bootstrapper (como `MicrosoftEdgeWebview2Setup.exe`) dentro de `build_scripts/assets/`, nem esclarece se o instalador do Inno Setup fará download dinâmico em tempo de execução ou se o instalador standalone deve ser embutido no pacote. Essa omissão gera uma suposição oculta sobre o suporte a instalações em ambientes sem acesso à internet.

### 3. Ambiguidade na conversão de vírgula decimal (`,`) versus ponto (`.`)
* **Severidade:** 🟡 Major
* **Escopo Afetado:** Seção 5.4 (*Mapeamento de Teclado Físico*), linha 181 versus Seção 5.3 (*Parser Seguro com AST*), linhas 149–156.
* **Descrição da Discrepância & Racional:** A especificação de entrada por teclado físico define a captura tanto de ponto quanto de vírgula (`.`, `,`) para separador decimal. No entanto, o motor matemático submete a string diretamente a `ast.parse(expr, mode='eval')`. Na sintaxe Python padrão, o caractere vírgula `,` é interpretado como delimitador de tupla (gerando nó `ast.Tuple`), o que é expressamente rejeitado pela whitelist de segurança com `SecuritySyntaxError`. O documento não especifica em qual camada (se no listener do frontend `keyboard.js` / `app.js` antes da invocação IPC, ou em etapa de sanitização prévia no `ast_validator.py`) a vírgula deve ser normalizada para ponto.

### 4. Mecanismo e comportamento do botão de resgate (*Recall*) não detalhados
* **Severidade:** 🟢 Nit
* **Escopo Afetado:** Seção 5.4 (*Design System Neubrutalista Puro*), linha 179.
* **Descrição da Discrepância & Racional:** O texto cita a existência de um *"botão de resgate (Recall)"* em cada registro da fita de recibo, mas não define a ação provocada pelo seu clique: se o valor do resultado é carregado no visor principal, se a expressão completa é recolocada no visor de edição, ou se substitui o operando atual. Para um desenvolvedor recém-chegado, a regra de negócio da microinteração de *Recall* permanece ambígua.

### 5. Jargão de transporte ("Pipe Interno Win32") e acoplamento por índice global de janela
* **Severidade:** 🟢 Nit
* **Escopo Afetado:** Seção 5.1 (*Diagrama Mermaid*), linha 86 e Seção 5.2, linha 132.
* **Descrição da Discrepância & Racional:** O diagrama arquitetural rotula a ponte IPC como *"Pipe Interno Win32"*, enquanto a implementação real do `pywebview` sob o Edge WebView2 utiliza a API nativa de interop COM/Host Objects (`window.chrome.webview.hostObjects`). Adicionalmente, a chamada para salvar arquivo descrita na Seção 5.2 utiliza `webview.windows[0].create_file_dialog()`, pressupondo acesso direto à lista global estática `webview.windows`, o que pode acarretar falhas por índice ou estado não inicializado caso a instância ativa da janela não seja explicitamente injetada na classe `DesktopBridgeApi`.

### 6. Acrônimo sem definição explícita (`AC`)
* **Severidade:** 🟢 Nit
* **Escopo Afetado:** Seção 5.4 (*Mapeamento de Teclado Físico*), linha 182.
* **Descrição da Discrepância & Racional:** O termo `"limpeza total AC"` é empregado sem explicitar seu significado padrão de calculadoras (*All Clear*), o que deve ser mantido explícito para leitores sem conhecimento prévio do projeto.
