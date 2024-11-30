<template>
    <div :class="['message', messageClass]">
      <div class="message-content" v-html="renderedMessage"></div>
    </div>
  </template>
  
  <script>
  import markdownIt from 'markdown-it';

  // Configuración personalizada de markdown-it para Gherkin
  const md = markdownIt({
    html: true,
    breaks: true,
    linkify: true,
    highlight: function (str, lang) {
      // Resaltar palabras clave de Gherkin en español
      if (lang === 'gherkin' || str.includes('**Dado**') || str.includes('**Cuando**')) {
        return str
          .replace(/^\*\*(Dado|Cuando|Entonces|Y)\*\*/gm, '<strong class="gherkin-keyword">$1</strong>')
          .replace(/^(Dado|Cuando|Entonces|Y)\s/gm, '<strong class="gherkin-keyword">$1</strong> ')
          .replace(/^(Característica|Escenario|Esquema del escenario):\s/gm, '<strong class="gherkin-keyword">$1:</strong> ');
      }
      return str;
    }
  });

  export default {
    props: {
      message: {
        type: Object,
        required: true,
        validator: (value) => {
          return value && typeof value.text === 'string' && typeof value.sender === 'string';
        }
      },
    },
    computed: {
      messageClass() {
        return this.message?.sender === 'user' ? 'user-message' : 'assistant-message';
      },
      renderedMessage() {
        const text = this.message?.text;
        // Asegurarse de que text sea una string
        if (!text || typeof text !== 'string') return '';
        
        // Procesar el texto línea por línea
        const lines = text.split('\n');
        const processedLines = [];
        let gherkinBlock = [];
        let inGherkinBlock = false;

        for (let i = 0; i < lines.length; i++) {
          const line = lines[i];
          const nextLine = lines[i + 1] || '';
          
          // Si la línea comienza con **Dado**, **Cuando**, etc., o es una línea "Y" dentro de un bloque
          if (line.match(/^\*\*(Dado|Cuando|Entonces|Y)\*\*/) || 
              (inGherkinBlock && line.match(/^\*\*Y\*\*/))) {
            if (!inGherkinBlock) {
              inGherkinBlock = true;
            }
            gherkinBlock.push(line);
            
            // Si la siguiente línea no es un step de Gherkin, cerrar el bloque
            if (!nextLine.match(/^\*\*(Dado|Cuando|Entonces|Y)\*\*/)) {
              processedLines.push('```gherkin\n' + gherkinBlock.join('\n') + '\n```');
              gherkinBlock = [];
              inGherkinBlock = false;
            }
          } else {
            if (inGherkinBlock) {
              // Si estábamos en un bloque, cerrarlo antes de añadir esta línea
              processedLines.push('```gherkin\n' + gherkinBlock.join('\n') + '\n```');
              gherkinBlock = [];
              inGherkinBlock = false;
            }
            processedLines.push(line);
          }
        }
        
        // Si quedó algún bloque sin cerrar
        if (gherkinBlock.length > 0) {
          processedLines.push('```gherkin\n' + gherkinBlock.join('\n') + '\n```');
        }
        
        return md.render(processedLines.join('\n'));
      },
    },
  };
  </script>
  
  <style scoped>
  .message {
    margin: 10px 0;
    display: flex;
  }
  .user-message {
    justify-content: flex-end;
  }
  .assistant-message {
    justify-content: flex-start;
  }
  .message-content {
    max-width: 70%;
    background-color: #2e2e2e;
    padding: 10px;
    border-radius: 8px;
    color: #fff;
    word-break: break-word;
  }
  .message-content :deep(.gherkin-keyword) {
    color: #42b983;
    font-weight: bold;
  }
  .message-content :deep(pre) {
    background-color: #252525;
    padding: 1rem;
    border-radius: 4px;
    margin: 0.5rem 0;
  }
  .message-content :deep(code) {
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 0.95em;
    background: transparent;
  }
  .user-message .message-content {
    background-color: #4a4a4a;
  }
  </style>