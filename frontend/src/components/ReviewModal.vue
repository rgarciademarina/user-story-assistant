<template>
  <div class="modal-overlay" v-if="modelValue">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Revisión final</h2>
        <button class="close-button" @click="close">×</button>
      </div>
      <div class="modal-body">
        <div class="editor-container">
          <div class="editor-wrapper">
            <textarea
              ref="editor"
              v-model="localContent"
              class="markdown-editor"
              @input="updatePreview"
            ></textarea>
          </div>
          <div class="resizer" ref="resizer"></div>
          <div class="preview-wrapper">
            <div class="preview-container" v-html="previewContent"></div>
          </div>
        </div>
        <div class="jira-section">
          <div class="jira-input-container">
            <input
              v-model="jiraId"
              :class="['jira-input', { 'is-valid': isValidJiraId }]"
              placeholder="ID de Jira (ej: STORYASIS-1)"
              :disabled="isLoadingJira"
            />
            <button
              @click="handleJiraAction"
              :disabled="isLoadingJira || !isValidJiraId"
              class="jira-button"
            >
              {{ jiraButtonText }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import MarkdownIt from 'markdown-it';

const md = new MarkdownIt({
  html: true,
  breaks: true,
  linkify: true,
  typographer: true
});

export default {
  name: 'ReviewModal',
  props: {
    modelValue: {
      type: Boolean,
      required: true
    },
    content: {
      type: String,
      required: true
    },
    existingJiraId: {
      type: String,
      default: ''
    },
    isLoadingJira: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      localContent: '',
      jiraId: '',
      previewContent: '',
      cleanup: null
    };
  },
  computed: {
    isValidJiraId() {
      return /^[A-Z]+-\d+$/.test(this.jiraId);
    },
    jiraButtonText() {
      return this.isLoadingJira ? 'Cargando...' : 'Guardar en Jira';
    }
  },
  methods: {
    close() {
      this.$emit('update:modelValue', false);
    },
    handleJiraAction() {
      const jiraContent = this.convertToJiraFormat(this.localContent);
      this.$emit('jira-action', {
        content: jiraContent,
        jiraId: this.jiraId
      });
    },
    convertToJiraFormat(content) {
      let jiraContent = content;
      
      // Convertir encabezados
      jiraContent = jiraContent.replace(/^####\s+(.*?)$/gm, 'h1. $1');
      
      // Convertir elementos markdown a formato Jira
      jiraContent = jiraContent.replace(/\*\*Dado\*\*/g, '*Dado*');
      jiraContent = jiraContent.replace(/\*\*Cuando\*\*/g, '*Cuando*');
      jiraContent = jiraContent.replace(/\*\*Entonces\*\*/g, '*Entonces*');
      
      // Convertir listas
      jiraContent = jiraContent.replace(/^-\s+/gm, '* ');
      
      return jiraContent;
    },
    updatePreview() {
      let processedContent = this.localContent;
      
      // Procesar encabezados especiales
      processedContent = processedContent.replace(/^####\s+(.*?)$/gm, '<h4>$1</h4>');
      
      // Procesar palabras clave con saltos de línea
      processedContent = processedContent.replace(/\*\*Dado\*\*/g, '<strong class="keyword">Dado</strong> ');
      processedContent = processedContent.replace(/\*\*Cuando\*\*/g, '<strong class="keyword">Cuando</strong> ');
      processedContent = processedContent.replace(/\*\*Entonces\*\*/g, '<strong class="keyword">Entonces</strong> ');
      
      this.previewContent = md.render(processedContent);
    },
    setupResizer() {
      const container = this.$el.querySelector('.editor-container');
      const editorWrapper = this.$el.querySelector('.editor-wrapper');
      const previewWrapper = this.$el.querySelector('.preview-wrapper');
      const resizer = this.$refs.resizer;
      let isResizing = false;
      let startX;
      let startWidthLeft;

      const startResize = (e) => {
        isResizing = true;
        startX = e.pageX;
        startWidthLeft = editorWrapper.offsetWidth;
        
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
        document.addEventListener('mousemove', resize);
        document.addEventListener('mouseup', stopResize);
      };

      const resize = (e) => {
        if (!isResizing) return;
        
        const containerWidth = container.offsetWidth;
        const minWidth = containerWidth * 0.2; // 20% minimum width
        
        let newWidth = startWidthLeft + (e.pageX - startX);
        
        // Ensure minimum widths are respected
        if (newWidth < minWidth) {
          newWidth = minWidth;
        } else if (newWidth > containerWidth - minWidth) {
          newWidth = containerWidth - minWidth;
        }
        
        const leftPercent = (newWidth / containerWidth) * 100;
        const rightPercent = 100 - leftPercent;
        
        editorWrapper.style.width = `${leftPercent}%`;
        previewWrapper.style.width = `${rightPercent}%`;
      };

      const stopResize = () => {
        isResizing = false;
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        document.removeEventListener('mousemove', resize);
        document.removeEventListener('mouseup', stopResize);
      };

      resizer.addEventListener('mousedown', startResize);

      // Store cleanup function
      this.cleanup = () => {
        resizer.removeEventListener('mousedown', startResize);
        document.removeEventListener('mousemove', resize);
        document.removeEventListener('mouseup', stopResize);
      };
    }
  },
  watch: {
    content: {
      immediate: true,
      handler(newValue) {
        this.localContent = newValue;
        this.updatePreview();
      }
    },
    existingJiraId: {
      immediate: true,
      handler(newValue) {
        this.jiraId = newValue;
      }
    },
    modelValue: {
      handler(newValue) {
        if (newValue) {
          // When modal becomes visible, ensure resizer is set up
          this.$nextTick(() => {
            this.setupResizer();
          });
        }
      }
    }
  },
  mounted() {
    if (this.modelValue) {
      this.$nextTick(() => {
        this.setupResizer();
      });
    }
  },
  beforeUnmount() {
    if (this.cleanup) {
      this.cleanup();
    }
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #1E1E1E;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  color: #E1E1E1;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #333;
  background-color: #252526;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #E1E1E1;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #E1E1E1;
}

.close-button:hover {
  color: #FFFFFF;
}

.modal-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 1rem;
  overflow: hidden;
}

.editor-container {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
  background-color: #252526;
}

.editor-wrapper,
.preview-wrapper {
  height: 100%;
  display: flex;
  overflow: hidden;
}

.editor-wrapper {
  width: 33.33%;
}

.preview-wrapper {
  width: 66.67%;
}

.markdown-editor {
  width: 100%;
  height: 100%;
  padding: 1rem;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 14px;
  line-height: 1.6;
  border: 1px solid #333;
  border-radius: 3px;
  resize: none;
  outline: none;
  color: #E1E1E1;
  background-color: #252526;
}

.markdown-editor:focus {
  border-color: #0052CC;
  box-shadow: 0 0 0 2px rgba(0, 82, 204, 0.2);
}

.resizer {
  width: 6px;
  cursor: col-resize;
  background-color: #333;
  position: relative;
  z-index: 1;
  transition: background-color 0.2s ease;
}

.resizer:hover,
.resizer:active {
  background-color: #0052CC;
}

.preview-container {
  width: 100%;
  height: 100%;
  padding: 1rem;
  overflow-y: auto;
  border: 1px solid #333;
  border-radius: 3px;
  background-color: #252526;
  color: #E1E1E1;
}

.preview-container :deep(h4) {
  font-size: 1.5em;
  margin: 1.5em 0 0.8em;
  font-weight: 600;
  color: #E1E1E1;
  border-bottom: 1px solid #333;
  padding-bottom: 0.3em;
}

.preview-container :deep(.keyword) {
  color: #569CD6;
  font-weight: 600;
  display: block;
  margin: 1em 0 0.5em;
}

.preview-container :deep(p) {
  margin: 0.8em 0;
  color: #E1E1E1;
}

.preview-container :deep(ul) {
  padding-left: 1.5em;
  margin: 0.8em 0;
}

.preview-container :deep(li) {
  margin: 0.4em 0;
  color: #E1E1E1;
}

.jira-section {
  border-top: 1px solid #333;
  padding-top: 1rem;
  margin-top: 1rem;
}

.jira-input-container {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.jira-input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #333;
  border-radius: 3px;
  font-size: 14px;
  color: #E1E1E1;
  background-color: #252526;
}

.jira-input:focus {
  border-color: #0052CC;
  box-shadow: 0 0 0 2px rgba(0, 82, 204, 0.2);
  outline: none;
}

.jira-input.is-valid {
  border-color: #4EC9B0;
}

.jira-button {
  padding: 0.5rem 1rem;
  background-color: #0052CC;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.jira-button:hover:not(:disabled) {
  background-color: #0747A6;
}

.jira-button:disabled {
  background-color: #333;
  cursor: not-allowed;
}
</style>
