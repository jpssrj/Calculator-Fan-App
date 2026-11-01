/**
 * CALCULATOR FAN - GERENCIADOR UNIFICADO DE INTERFACE E PONTE IPC (APP.JS)
 * Orquestra as regras da calculadora, atalhos de hardware e comunicação nativa via PyWebView.
 */

(function () {
  'use strict';

  // Elementos do DOM
  const mainDisplay = document.getElementById('main-display');
  const subDisplay = document.getElementById('sub-display');
  const activeOpBadge = document.getElementById('active-op-badge');
  const tapeDrawer = document.getElementById('tape-drawer');
  const tapeEntries = document.getElementById('tape-entries');
  const btnToggleHistory = document.getElementById('btn-toggle-history');
  const btnCloseTape = document.getElementById('btn-close-tape');
  const btnClearTape = document.getElementById('btn-clear-tape');
  const btnExportTape = document.getElementById('btn-export-tape');
  const sessionTimeEl = document.getElementById('tape-session-time');

  // Estado da Aplicação
  const state = {
    expression: '',        // Expressão em construção (ex: "12 + 45")
    lastResult: null,      // Último resultado retornado pela API
    isCalculated: false,   // Indica se o visor exibe o resultado final
    isError: false,        // Indica se está em estado de erro
    historyTape: []        // Pilha de registros da sessão
  };

  /**
   * Atualiza os visores da calculadora.
   */
  function updateDisplay() {
    if (state.isError) {
      mainDisplay.classList.add('is-error');
      activeOpBadge.textContent = 'ERRO';
      return;
    }

    mainDisplay.classList.remove('is-error');

    if (state.isCalculated && state.lastResult !== null) {
      mainDisplay.textContent = state.lastResult;
      subDisplay.textContent = `${state.expression} =`;
      activeOpBadge.textContent = 'DONE';
    } else {
      const displayValue = state.expression.trim() || '0';
      mainDisplay.textContent = displayValue;
      subDisplay.innerHTML = '&nbsp;';

      const lastToken = state.expression.trim().split(' ').pop();
      if (['+', '-', '×', '÷'].includes(lastToken)) {
        activeOpBadge.textContent = `OP: ${lastToken}`;
      } else {
        activeOpBadge.textContent = state.expression ? 'DIGIT' : 'IDLE';
      }
    }
  }

  /**
   * Trata a inserção de dígitos, operadores e parênteses.
   */
  function handleInsert(value) {
    if (state.isError) {
      state.isError = false;
      state.expression = '';
    }

    const isOp = ['+', '-', '×', '÷'].includes(value);

    // Se acabou de calcular:
    if (state.isCalculated) {
      state.isCalculated = false;
      if (isOp) {
        state.expression = `${state.lastResult} ${value} `;
        updateDisplay();
        return;
      } else {
        state.expression = '';
      }
    }

    if (isOp) {
      const trimmed = state.expression.trim();
      if (!trimmed) {
        if (value === '-') {
          state.expression = '-';
        }
        updateDisplay();
        return;
      }

      const tokens = trimmed.split(' ');
      const lastToken = tokens[tokens.length - 1];

      // Substitui o operador anterior se for consecutivo
      if (['+', '-', '×', '÷'].includes(lastToken)) {
        tokens[tokens.length - 1] = value;
        state.expression = tokens.join(' ') + ' ';
      } else {
        state.expression = `${trimmed} ${value} `;
      }
    } else {
      state.expression += value;
    }

    updateDisplay();
  }

  /**
   * Trata a inserção do ponto decimal com validação de duplicidade e normalização de vírgula.
   */
  function handleDecimal() {
    if (state.isError || state.isCalculated) {
      state.isError = false;
      state.isCalculated = false;
      state.expression = '0.';
      updateDisplay();
      return;
    }

    const tokens = state.expression.trim().split(' ');
    const currentToken = tokens[tokens.length - 1] || '';

    if (currentToken.includes('.')) {
      return;
    }

    if (!currentToken || ['+', '-', '×', '÷', '('].includes(currentToken)) {
      state.expression += (state.expression.endsWith(' ') ? '' : ' ') + '0.';
    } else {
      state.expression += '.';
    }

    updateDisplay();
  }

  /**
   * Inverte o sinal (positivo/negativo) do operando ativo.
   */
  function handleNegate() {
    if (state.isCalculated && state.lastResult !== null) {
      state.isCalculated = false;
      state.expression = state.lastResult.startsWith('-')
        ? state.lastResult.substring(1)
        : `-${state.lastResult}`;
      updateDisplay();
      return;
    }

    const trimmed = state.expression.trim();
    if (!trimmed) {
      state.expression = '-';
      updateDisplay();
      return;
    }

    const tokens = trimmed.split(' ');
    let lastToken = tokens[tokens.length - 1];

    if (/^-?\d+(\.\d+)?$/.test(lastToken)) {
      if (lastToken.startsWith('-')) {
        tokens[tokens.length - 1] = lastToken.substring(1);
      } else {
        tokens[tokens.length - 1] = `-${lastToken}`;
      }
      state.expression = tokens.join(' ');
      updateDisplay();
    }
  }

  /**
   * Apaga o último caractere ou operador.
   */
  function handleBackspace() {
    if (state.isError || state.isCalculated) {
      handleClearAll();
      return;
    }

    let expr = state.expression.trimEnd();
    if (expr.length > 0) {
      state.expression = expr.slice(0, -1).trimEnd();
    }
    updateDisplay();
  }

  /**
   * Limpa todo o visor e reseta o estado (AC).
   */
  function handleClearAll() {
    state.expression = '';
    state.lastResult = null;
    state.isCalculated = false;
    state.isError = false;
    updateDisplay();
  }

  /**
   * Envia a expressão para avaliação segura através da ponte IPC PyWebView.
   */
  async function handleCalculate() {
    let rawExpr = state.expression.trim();
    if (!rawExpr || state.isCalculated) return;

    // Normalização defensiva de vírgula ABNT2 para ponto
    rawExpr = rawExpr.replace(/,/g, '.');

    activeOpBadge.textContent = 'CALC...';

    try {
      let data;
      if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.calculate === 'function') {
        data = await window.pywebview.api.calculate(rawExpr);
      } else {
        // Fallback para desenvolvimento em navegador sem PyWebView
        data = { status: 'error', error: 'PONTE IPC NÃO INICIALIZADA' };
      }

      if (data && data.status === 'success') {
        state.lastResult = data.result;
        state.isCalculated = true;
        state.isError = false;

        appendTapeEntry(rawExpr, data.result);
        updateDisplay();
      } else {
        state.isError = true;
        state.lastResult = null;
        mainDisplay.textContent = (data && data.error) ? data.error : 'SINTAXE INVÁLIDA';
        updateDisplay();
      }
    } catch (err) {
      state.isError = true;
      mainDisplay.textContent = 'ERRO INTERNO NO MOTOR';
      updateDisplay();
    }
  }

  /**
   * Registra uma nova entrada na Fita de Histórico.
   */
  function appendTapeEntry(expr, result) {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('pt-BR', { hour12: false });

    const entry = {
      id: Date.now(),
      timestamp: timeStr,
      expression: expr,
      result: result
    };

    state.historyTape.unshift(entry);
    renderTape();
  }

  /**
   * Renderiza os itens da Fita de Histórico.
   */
  function renderTape() {
    if (state.historyTape.length === 0) {
      tapeEntries.innerHTML = `
        <div class="tape-empty-state">
          <p>NENHUM CÁLCULO REGISTRADO</p>
          <small>Execute uma operação para imprimir na fita.</small>
        </div>
      `;
      return;
    }

    tapeEntries.innerHTML = state.historyTape.map(item => `
      <div class="tape-item" data-id="${item.id}">
        <span class="tape-item-time">[${item.timestamp}]</span>
        <div class="tape-item-expr">${escapeHtml(item.expression)}</div>
        <div class="tape-item-result-row">
          <span class="tape-item-result">= ${escapeHtml(item.result)}</span>
          <button class="btn-recall" data-result="${escapeHtml(item.result)}" title="Carregar resultado no visor">
            RECALL
          </button>
        </div>
      </div>
    `).join('');

    // Listener para botões de recall
    tapeEntries.querySelectorAll('.btn-recall').forEach(btn => {
      btn.addEventListener('click', function () {
        const val = this.getAttribute('data-result');
        state.isCalculated = false;
        state.isError = false;
        state.expression = val;
        updateDisplay();
      });
    });
  }

  /**
   * Exporta a fita de histórico via caixa de diálogo nativa do Windows no PyWebView.
   */
  async function exportTapeAsTxt() {
    if (state.historyTape.length === 0) {
      alert('A fita está vazia. Realize cálculos antes de exportar.');
      return;
    }

    const defaultName = `recibo_calculator_fan_${new Date().toISOString().slice(0, 10)}.txt`;

    if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.export_receipt_txt === 'function') {
      const originalText = btnExportTape.querySelector('span').textContent;
      btnExportTape.querySelector('span').textContent = 'SALVANDO...';

      try {
        const res = await window.pywebview.api.export_receipt_txt(state.historyTape, defaultName);
        if (res.status === 'success') {
          btnExportTape.querySelector('span').textContent = 'RECIBO SALVO!';
          setTimeout(() => {
            btnExportTape.querySelector('span').textContent = originalText;
          }, 2000);
        } else if (res.status === 'cancelled') {
          btnExportTape.querySelector('span').textContent = originalText;
        } else {
          alert('Falha ao gravar arquivo de recibo no disco.');
          btnExportTape.querySelector('span').textContent = originalText;
        }
      } catch (e) {
        alert('Erro ao acionar exportação de arquivo.');
        btnExportTape.querySelector('span').textContent = originalText;
      }
    } else {
      // Fallback navegador
      alert('Recurso disponível apenas no aplicativo Desktop.');
    }
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function toggleTapeDrawer() {
    tapeDrawer.classList.toggle('is-hidden');
    btnToggleHistory.classList.toggle('is-active', !tapeDrawer.classList.contains('is-hidden'));
  }

  function handleAction(action, value) {
    switch (action) {
      case 'insert':
        handleInsert(value);
        break;
      case 'decimal':
        handleDecimal();
        break;
      case 'negate':
        handleNegate();
        break;
      case 'backspace':
        handleBackspace();
        break;
      case 'clear-all':
        handleClearAll();
        break;
      case 'calculate':
        handleCalculate();
        break;
      case 'toggle-history':
        toggleTapeDrawer();
        break;
      default:
        console.warn('Ação desconhecida:', action);
    }
  }

  // Mapa de Teclado Físico
  const KEY_MAP = {
    '0': { action: 'insert', value: '0' },
    '1': { action: 'insert', value: '1' },
    '2': { action: 'insert', value: '2' },
    '3': { action: 'insert', value: '3' },
    '4': { action: 'insert', value: '4' },
    '5': { action: 'insert', value: '5' },
    '6': { action: 'insert', value: '6' },
    '7': { action: 'insert', value: '7' },
    '8': { action: 'insert', value: '8' },
    '9': { action: 'insert', value: '9' },
    '.': { action: 'decimal' },
    ',': { action: 'decimal' },
    '+': { action: 'insert', value: '+' },
    '-': { action: 'insert', value: '-' },
    '*': { action: 'insert', value: '×' },
    '/': { action: 'insert', value: '÷' },
    '(': { action: 'insert', value: '(' },
    ')': { action: 'insert', value: ')' },
    'Enter': { action: 'calculate' },
    '=': { action: 'calculate' },
    'Backspace': { action: 'backspace' },
    'Delete': { action: 'backspace' },
    'Escape': { action: 'clear-all' },
    'c': { action: 'clear-all' },
    'C': { action: 'clear-all' },
    'h': { action: 'toggle-history' },
    'H': { action: 'toggle-history' }
  };

  function triggerButtonFeedback(keyConfig) {
    let selector = '';
    if (keyConfig.action === 'insert' && keyConfig.value) {
      selector = `.key[data-value="${keyConfig.value}"]`;
    } else if (keyConfig.action === 'calculate') {
      selector = '.key[data-action="calculate"]';
    } else if (keyConfig.action === 'clear-all') {
      selector = '.key[data-action="clear-all"]';
    } else if (keyConfig.action === 'backspace') {
      selector = '.key[data-action="backspace"]';
    } else if (keyConfig.action === 'decimal') {
      selector = '.key[data-action="decimal"]';
    } else if (keyConfig.action === 'toggle-history') {
      selector = '#btn-toggle-history';
    }

    if (selector) {
      const btn = document.querySelector(selector);
      if (btn) {
        btn.classList.add('is-pressed');
        setTimeout(() => {
          btn.classList.remove('is-pressed');
        }, 120);
      }
    }
  }

  // Listeners de Clique
  document.querySelectorAll('.key').forEach(button => {
    button.addEventListener('click', () => {
      const action = button.getAttribute('data-action');
      const value = button.getAttribute('data-value');
      handleAction(action, value);
    });
  });

  btnToggleHistory.addEventListener('click', toggleTapeDrawer);
  btnCloseTape.addEventListener('click', toggleTapeDrawer);

  btnClearTape.addEventListener('click', () => {
    state.historyTape = [];
    renderTape();
  });

  btnExportTape.addEventListener('click', exportTapeAsTxt);

  // Listener Global de Teclado Físico e Numpad
  window.addEventListener('keydown', function (e) {
    // Bloqueia F5 e Ctrl+R para evitar perda do histórico da sessão
    if (e.key === 'F5' || ((e.ctrlKey || e.metaKey) && (e.key === 'r' || e.key === 'R'))) {
      e.preventDefault();
      return;
    }

    const key = e.key;
    const mapping = KEY_MAP[key];
    if (!mapping) return;

    // Prevenção de rolagem com Enter e Backspace no navegador
    if (['Enter', 'Backspace', '/', ' '].includes(key) || (key === 'h' && !e.ctrlKey && !e.metaKey)) {
      e.preventDefault();
    }

    triggerButtonFeedback(mapping);
    handleAction(mapping.action, mapping.value);
  });

  // Supressão de menu de contexto padrão do navegador
  document.addEventListener('contextmenu', function (e) {
    e.preventDefault();
  });

  // Inicializa a hora da sessão
  if (sessionTimeEl) {
    sessionTimeEl.textContent = `SESSÃO: ${new Date().toLocaleTimeString('pt-BR')}`;
  }

  // Render inicial
  updateDisplay();
  renderTape();
})();
