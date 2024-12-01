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
        validator(value) {
          // Null o undefined no permitidos
          if (value === null || value === undefined) {
            throw new Error('Message cannot be null or undefined');
          }
          
          // Solo se permiten objetos, no arrays ni otros tipos
          if (typeof value !== 'object' || Array.isArray(value)) {
            throw new Error('Message must be an object');
          }
          
          // Debe ser un objeto no vacío
          if (Object.keys(value).length === 0) {
            throw new Error('Message object cannot be empty');
          }
          
          // Debe tener propiedad text
          if (!Object.prototype.hasOwnProperty.call(value, 'text')) {
            throw new Error('Message must have a text property');
          }
          
          // Text debe ser string
          if (value.text === null || typeof value.text !== 'string') {
            throw new Error('Text must be a string');
          }
          
          // Sender opcional pero con restricciones
          if (Object.prototype.hasOwnProperty.call(value, 'sender')) {
            // Sender debe ser undefined o string
            if (value.sender !== undefined && typeof value.sender !== 'string') {
              throw new Error('Sender must be a string or undefined');
            }
          }
          
          // No se permiten propiedades extra
          const allowedProperties = ['text', 'sender'];
          const extraProperties = Object.keys(value).filter(
            prop => !allowedProperties.includes(prop)
          );
          
          if (extraProperties.length > 0) {
            throw new Error(`Message object has unknown properties: ${extraProperties.join(', ')}`);
          }
          
          return true;
        }
      }
    },
    computed: {
      messageClass() {
        // Manejo explícito de diferentes casos de sender
        if (!this.message) return 'assistant-message';
        
        const sender = this.message.sender;
        if (sender === undefined) return 'assistant-message';
        
        return sender === 'user' ? 'user-message' : 'assistant-message';
      },
      renderedMessage() {
        // Manejo de casos edge para el mensaje
        if (!this.message || !this.message.text) {
          return '';
        }
        
        const text = this.message.text;
        
        // Verificación adicional de tipo
        if (typeof text !== 'string') {
          return '';
        }
        
        const lines = text.split('\n');
        const processedLines = this.processLines(lines);
        
        return processedLines.map(line => this.highlight(line)).join('\n');
      },
    },
    methods: {
      processLines(lines) {
        // Manejo de array vacío
        if (lines.length === 0) {
          return [];
        }
        
        const processedLines = [];
        let gherkinBlock = [];
        let inGherkinBlock = false;

        for (let i = 0; i < lines.length; i++) {
          const line = lines[i];
          const nextLine = lines[i + 1] || '';
          
          // Detección de palabras clave de Gherkin
          const isGherkinKeyword = line.match(/^\*\*(Dado|Cuando|Entonces|Y)\*\*/);
          const isYLine = inGherkinBlock && line.match(/^\*\*Y\*\*/);
          
          // Bloque Gherkin
          if (isGherkinKeyword || isYLine) {
            // Iniciar bloque Gherkin si no está activo
            if (!inGherkinBlock) {
              inGherkinBlock = true;
            }
            gherkinBlock.push(line);
            
            // Verificar cierre de bloque Gherkin
            const isNextLineGherkin = nextLine.match(/^\*\*(Dado|Cuando|Entonces|Y)\*\*/);
            if (!isNextLineGherkin) {
              processedLines.push('```gherkin\n' + gherkinBlock.join('\n') + '\n```');
              gherkinBlock = [];
              inGherkinBlock = false;
            }
          } 
          // Líneas no Gherkin
          else {
            // Cerrar bloque Gherkin previo si estaba activo
            if (inGherkinBlock) {
              processedLines.push('```gherkin\n' + gherkinBlock.join('\n') + '\n```');
              gherkinBlock = [];
              inGherkinBlock = false;
            }
            
            // Agregar líneas no vacías
            if (line.trim() !== '') {
              processedLines.push(line);
            }
          }
          
          // Manejar última línea en bloque Gherkin
          if (i === lines.length - 1 && inGherkinBlock) {
            processedLines.push('```gherkin\n' + gherkinBlock.join('\n') + '\n```');
          }
        }
        
        return processedLines;
      },
      highlight(text) {
        // Remove unused lang parameter
        return md.render(text);
      }
    }
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