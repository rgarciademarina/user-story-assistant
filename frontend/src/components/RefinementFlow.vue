<template>
  <div class="refinement-flow">
    <div class="header">
      <h2>{{ currentStateLabel }}</h2>
    </div>
    <div class="content-wrapper">
      <div class="chat-container">
        <div v-for="(message, index) in messages" :key="index">
          <ChatMessage :message="message" />
        </div>
        <div v-if="isLoading" class="loading-indicator">
          <span>Cargando...</span>
        </div>
      </div>
    </div>
    <div class="input-container">
      <textarea
        ref="feedbackInput"
        v-model="userInput"
        @keydown.enter="handleKeyPress"
        :placeholder="inputPlaceholder"
        :disabled="isLoading"
      ></textarea>
      <div class="button-container">
        <div class="main-buttons">
          <button @click="sendFeedback" :disabled="isLoading || !userInput.trim()">Enviar</button>
          <button
            v-if="backButtonLabel"
            @click="goBack"
            class="back-button"
          >
            {{ backButtonLabel }}
          </button>
          <button
            v-if="currentStep !== 'finished'"
            @click="advanceStep"
            :class="['advance-button', advanceButtonClass]"
            :disabled="!canAdvance"
          >
            {{ nextButtonLabel }}
          </button>
        </div>
        <div v-if="currentStep === 'refineStory' && !refinedStory" class="jira-input-container">
          <input
            v-model="jiraStoryId"
            :class="['jira-input', { 'is-valid': isValidJiraId }]"
            placeholder="ID de Jira (ej: STORYASIS-1)"
            :disabled="isLoadingJira"
            @keydown.enter="handleKeyPress"
          />
          <button
            @click="fetchJiraStory"
            :disabled="!isValidJiraId || isLoadingJira"
            class="jira-button"
          >
            {{ isLoadingJira ? 'Recuperando...' : 'Recuperar historia' }}
          </button>
        </div>
      </div>
    </div>
    <ToastNotification
      :show="showToast"
      :message="toastMessage"
      :type="toastType"
    />
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import ChatMessage from './ChatMessage.vue';
import ToastNotification from './ToastNotification.vue';

export default {
  components: {
    ChatMessage,
    ToastNotification,
  },
  data() {
    return {
      userInput: '',
      isLoading: false,
      jiraStoryId: '',
      isLoadingJira: false,
      showToast: false,
      toastMessage: '',
      toastType: 'info',
    };
  },
  computed: {
    ...mapState(['messages', 'currentStep', 'refinedStory', 'cornerCases', 'testingStrategies']),
    currentStateLabel() {
      switch (this.currentStep) {
        case 'refineStory':
          return 'Refinamiento';
        case 'cornerCases':
          return 'Casos Esquina';
        case 'testingStrategy':
          return 'Testing';
        case 'finished':
          return 'Proceso Completado';
        default:
          return '';
      }
    },
    nextButtonLabel() {
      if (this.currentStep === 'refineStory') return 'Casos Esquina';
      if (this.currentStep === 'cornerCases') return 'Testing';
      if (this.currentStep === 'testingStrategy') return 'Composición';
      return null;
    },
    backButtonLabel() {
      if (this.currentStep === 'cornerCases') return 'Refinamiento';
      if (this.currentStep === 'testingStrategy') return 'Casos Esquina';
      return null;
    },
    advanceButtonClass() {
      return this.currentStep === 'testingStrategy' ? 'finish-button' : 'next-button';
    },
    canAdvance() {
      if (this.currentStep === 'refineStory') {
        // Solo permitir avanzar si hay una historia refinada
        return !!this.refinedStory;
      }
      return true;
    },
    inputPlaceholder() {
      return this.isLoading ? 'Esperando respuesta...' : 'Escribe tu feedback aquí...';
    },
    isValidJiraId() {
      return /^[A-Z]+-\d+$/.test(this.jiraStoryId.trim());
    },
  },
  methods: {
    ...mapActions([
      'refineStory',
      'identifyCornerCases',
      'proposeTestingStrategy',
      'finalizeStory',
      'addMessage',
      'resetProcess',
      'setCurrentStep',
    ]),
    async sendFeedback() {
      if (!this.userInput.trim()) return;

      // Agregar el mensaje del usuario al historial
      this.addMessage({ text: this.userInput, sender: 'user' });
      const feedback = this.userInput;
      this.userInput = '';
      this.isLoading = true;

      try {
        if (this.currentStep === 'refineStory') {
          await this.handleRefineFeedback(feedback);
        } else if (this.currentStep === 'cornerCases') {
          await this.handleCornerCasesFeedback(feedback);
        } else if (this.currentStep === 'testingStrategy') {
          await this.handleTestingStrategyFeedback(feedback);
        }
      } finally {
        this.isLoading = false;
        this.focusInput();
      }
    },
    async handleRefineFeedback(feedback) {
      if (!this.$store.state.refinedStory) {
        const payload = { story: feedback, feedback: '' };
        const result = await this.refineStory(payload);
        if (result && result.refinementResponse !== undefined) {
          this.addMessage({ text: result.refinementResponse, sender: 'assistant' });
        }
        return;
      }
      const story = this.$store.state.refinedStory;
      const payload = { story, feedback };
      const result = await this.refineStory(payload);
      if (result && result.refinementResponse !== undefined) {
        this.addMessage({ text: result.refinementResponse, sender: 'assistant' });
      }
    },
    async handleCornerCasesFeedback(feedback) {
      const refinedStory = this.$store.state.refinedStory;
      const existingCornerCases = this.$store.state.cornerCases;

      const payload = { refinedStory, feedback, existingCornerCases };
      const result = await this.identifyCornerCases(payload);
      if (result && result.cornerCasesResponse !== undefined) {
        this.addMessage({ text: result.cornerCasesResponse, sender: 'assistant' });
      }
    },
    async handleTestingStrategyFeedback(feedback) {
      const refinedStory = this.$store.state.refinedStory;
      const cornerCases = this.$store.state.cornerCases;
      const existingTestingStrategies = this.$store.state.testingStrategies;
      const payload = { refinedStory, cornerCases, feedback, existingTestingStrategies };
      const result = await this.proposeTestingStrategy(payload);
      if (result && result.testingStrategyResponse !== undefined) {
        this.addMessage({ text: result.testingStrategyResponse, sender: 'assistant' });
      }
    },
    async finalizeStory() {
      this.isLoading = true;
      try {
        const result = await this.$store.dispatch('finalizeStory', {
          feedback: this.userInput || ''
        });
        
        // Mostrar respuesta del backend
        if (result && result.finalizationResponse) {
          this.addMessage({ 
            text: result.finalizationResponse, 
            sender: 'assistant' 
          });
        }
      } catch (error) {
        this.showToastMessage('Error al finalizar la historia', 'error');
        console.error(error);
        throw error; // Relanzar para que advanceStep maneje el error
      } finally {
        this.isLoading = false;
        this.userInput = ''; // Limpiar input después de finalizar
      }
    },
    async advanceStep() {
      if (this.isLoading) return;

      if (this.currentStep === 'refineStory') {
        // Verificar que hay una historia refinada antes de avanzar
        if (!this.refinedStory) {
          return;
        }
        this.setCurrentStep('cornerCases');
        this.isLoading = true;
        try {
          // Obtener los casos esquina iniciales y mostrar la respuesta
          await this.handleCornerCasesFeedback('');
        } finally {
          this.isLoading = false;
          // Agregar mensaje del sistema para casos esquina
          this.addMessage({
            text: 'Por favor, proporciona feedback sobre los casos esquina identificados o sugiere nuevos casos.',
            sender: 'system'
          });
        }
      } else if (this.currentStep === 'cornerCases') {
        this.setCurrentStep('testingStrategy');
        this.isLoading = true;
        try {
          // Obtener las estrategias de testing iniciales y mostrar la respuesta
          await this.handleTestingStrategyFeedback('');
        } finally {
          this.isLoading = false;
          // Agregar mensaje del sistema para estrategia de testing
          this.addMessage({
            text: 'Por favor, proporciona feedback sobre las estrategias de testing propuestas.',
            sender: 'system'
          });
        }
      } else if (this.currentStep === 'testingStrategy') {
        this.isLoading = true;
        try {
          // Llamar al método de finalización de historia
          await this.finalizeStory();
          // Establecer el estado como finalizado después de la llamada exitosa
          this.setCurrentStep('finished');
        } catch (error) {
          // Manejar cualquier error en la finalización
          this.showToastMessage('Error al finalizar la historia', 'error');
          console.error(error);
        } finally {
          this.isLoading = false;
        }
        this.focusInput();
      }
      this.focusInput();
    },
    goBack() {
      if (this.currentStep === 'cornerCases') {
        this.setCurrentStep('refineStory');
      } else if (this.currentStep === 'testingStrategy') {
        this.setCurrentStep('cornerCases');
      }
      this.focusInput();
    },
    focusInput() {
      this.$nextTick(() => {
        if (this.$refs.feedbackInput && this.currentStep !== 'finished') {
          this.$refs.feedbackInput.focus();
        }
      });
    },
    async fetchJiraStory() {
      this.isLoadingJira = true;
      try {
        const response = await fetch(`/api/v1/jira/story/${this.jiraStoryId}`);
        if (!response.ok) {
          throw new Error(response.status === 404 ? 'Historia no encontrada' : 'Error al recuperar la historia');
        }
        const data = await response.json();
        this.userInput = `${data.title}\n\n${data.description || ''}`;
        this.showToastMessage('Historia recuperada correctamente', 'success');
      } catch (error) {
        this.showToastMessage(error.message, 'error');
      } finally {
        this.isLoadingJira = false;
      }
    },
    showToastMessage(message, type = 'info') {
      this.toastMessage = message;
      this.toastType = type;
      this.showToast = true;
      setTimeout(() => {
        this.showToast = false;
      }, 3000);
    },
    previousUserStory() {
      const storyMessage = this.messages.find(
        (message) => message.sender === 'userStory'
      );
      return storyMessage ? storyMessage.text : '';
    },
    handleKeyPress(event) {
      // Si es el campo de Jira y el ID es válido, recuperar la historia
      if (event.target.classList.contains('jira-input')) {
        if (this.isValidJiraId && !this.isLoadingJira) {
          event.preventDefault();
          this.fetchJiraStory();
        }
        return;
      }

      // Si es el textarea
      if (event.shiftKey) {
        // Permitir el salto de línea con Shift+Enter
        return;
      }
      
      // Enviar el feedback
      event.preventDefault();
      this.sendFeedback();
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const chatContainer = this.$el.querySelector('.chat-container');
        if (chatContainer) {
          chatContainer.scrollTop = chatContainer.scrollHeight;
        }
      });
    },
    addMessage(message) {
      this.$store.dispatch('addMessage', message);
      this.scrollToBottom();
    },
  },
  mounted() {
    // Resetear el proceso al cargar el componente
    this.resetProcess();
    this.setCurrentStep('refineStory');
    // Solicitar la historia de usuario inicial
    this.addMessage({
      text: 'Por favor, ingresa la historia de usuario que deseas refinar.',
      sender: 'assistant',
    });
  },
};
</script>

<style scoped>
@import '../styles/RefinementFlow.css';

/* Sobreescribir estilos del contenedor de input */
.input-container {
  padding: 0.75rem 2rem;
}

.input-container textarea {
  margin-bottom: 0.5rem;
  min-height: 100px;
  padding: 0.75rem;
}

.button-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.main-buttons {
  display: flex;
  gap: 5px;
}

.jira-input-container {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.jira-input {
  width: 150px;
  padding: 6px 10px;
  border: 1px solid #444;
  border-radius: 4px;
  background-color: #2e2e2e;
  color: #fff;
  font-size: 14px;
}

.jira-input.is-valid {
  border-color: #28a745;
}

.jira-button {
  padding: 6px 12px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  white-space: nowrap;
}

.jira-button:disabled {
  background-color: #666;
  cursor: not-allowed;
}

/* Ajustar tamaño de todos los botones para que sean más compactos */
button {
  padding: 6px 12px;
  font-size: 14px;
}
</style>