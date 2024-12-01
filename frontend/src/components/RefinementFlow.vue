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
            :class="[
              'advance-button',
              advanceButtonClass,
              {
                'btn-corner-cases': currentStep === 'cornerCases' || currentStep === 'refineStory',
                'btn-testing-strategy': currentStep === 'testingStrategy',
                'btn-review': currentStep === 'review'
              }
            ]"
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
            :disabled="isJiraButtonDisabled"
            class="jira-button"
            data-test="jira-button"
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
    <ReviewModal
      v-model="isReviewModalOpen"
      :content="composedStory"
      :existing-jira-id="jiraStoryId"
      :is-loading-jira="isLoadingJira"
      @update:modelValue="handleModalVisibility"
      @jira-action="handleJiraAction"
    />
  </div>
</template>

<script>
import { mapState, mapActions, mapMutations } from 'vuex';
import ChatMessage from './ChatMessage.vue';
import ToastNotification from './ToastNotification.vue';
import ReviewModal from './ReviewModal.vue';

export default {
  name: 'RefinementFlow',
  components: {
    ChatMessage,
    ToastNotification,
    ReviewModal
  },
  data() {
    return {
      userInput: '',
      jiraStoryId: '',
      isLoading: false,
      showToast: false,
      toastMessage: '',
      toastType: 'info',
    };
  },
  computed: {
    ...mapState(['messages', 'currentStep', 'refinedStory', 'cornerCases', 'testingStrategies', 'isLoadingJira', 'jiraStoryId', 'isReviewModalOpen', 'composedStory']),
    currentStateLabel() {
      switch (this.currentStep) {
        case 'refineStory':
          return 'Refinamiento';
        case 'cornerCases':
          return 'Casos Esquina';
        case 'testingStrategy':
          return 'Testing';
        case 'composition':
          return 'Composición';
        case 'finished':
          return 'Finalizado';
        default:
          return '';
      }
    },
    nextButtonLabel() {
      switch (this.currentStep) {
        case 'refineStory':
          return 'Identificar casos límite';
        case 'cornerCases':
          return 'Proponer estrategia de pruebas';
        case 'testingStrategy':
          return 'Componer';
        case 'composition':
          return 'Revisar';
        default:
          return '';
      }
    },
    backButtonLabel() {
      if (this.currentStep === 'cornerCases') return 'Refinamiento';
      if (this.currentStep === 'testingStrategy') return 'Casos Esquina';
      if (this.currentStep === 'composition') return 'Testing';
      if (this.currentStep === 'finished') return 'Composición';
      return null;
    },
    advanceButtonClass() {
      return this.currentStep === 'testingStrategy' ? 'next-button' : 'finish-button';
    },
    canAdvance() {
      return true;
    },
    inputPlaceholder() {
      return this.isLoading ? 'Esperando respuesta...' : 'Escribe tu feedback aquí...';
    },
    isValidJiraId() {
      return /^[A-Z]+-\d+$/.test(this.jiraStoryId.trim());
    },
    isJiraButtonDisabled() {
      return !this.isValidJiraId || this.isLoadingJira;
    },
  },
  methods: {
    ...mapActions(['refineStory', 'identifyCornerCases', 'proposeTestingStrategy', 'finalizeStory', 'addMessage', 'resetProcess', 'setCurrentStep', 'fetchJiraStory', 'composeStory', 'updateOrCreateJiraStory']),
    ...mapMutations(['setCurrentStep', 'setIsReviewModalOpen', 'setLoadingJira']),
    async sendFeedback() {
      if (!this.userInput.trim()) return;

      this.isLoading = true;
      try {
        switch (this.currentStep) {
          case 'refineStory':
            await this.handleRefineFeedback(this.userInput);
            break;
          case 'cornerCases':
            await this.handleCornerCasesFeedback(this.userInput);
            break;
          case 'testingStrategy':
            await this.handleTestingStrategyFeedback(this.userInput);
            break;
          case 'composition':
            await this.handleCompositionFeedback(this.userInput);
            break;
          default:
            console.warn('Paso no manejado:', this.currentStep);
        }
        this.userInput = '';
      } catch (error) {
        console.error('Error al procesar feedback:', error);
        this.showToastMessage('Error al procesar el feedback', 'error');
      } finally {
        this.isLoading = false;
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
    async handleCompositionFeedback(feedback = '') {
      const result = await this.$store.dispatch('composeStory', feedback);
      if (result && result.compositionResponse) {
        this.addMessage({ text: result.compositionResponse, sender: 'assistant' });
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

      if (this.currentStep === 'composition') {
        // Abrir modal de revisión
        this.setIsReviewModalOpen(true);
        
        // Finalizar la historia
        this.isLoading = true;
        try {
          await this.finalizeStory();
          
          // Cambiar explícitamente al estado finished
          this.setCurrentStep('finished');
          
          // Agregar mensaje de finalización
          this.addMessage({
            text: 'La historia ha sido finalizada. Puedes revisar todo el proceso o cerrar la ventana.',
            sender: 'system'
          });
        } catch (error) {
          // Manejar cualquier error en la finalización
          this.showToastMessage('Error al finalizar la historia', 'error');
          console.error(error);
        } finally {
          this.isLoading = false;
        }
        return;
      }

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
        this.setCurrentStep('composition');
        this.isLoading = true;
        try {
          // Obtener la composición inicial
          await this.handleCompositionFeedback('');
          // Agregar mensaje de composición
          this.addMessage({
            text: 'Has llegado a la fase de composición. Aquí puedes proporcionar feedback adicional para mejorar la historia de usuario. Cuando estés satisfecho, puedes avanzar para finalizar.',
            sender: 'system'
          });
        } finally {
          this.isLoading = false;
        }
      }
    },
    goBack() {
      if (this.currentStep === 'cornerCases') {
        this.setCurrentStep('refineStory');
      } else if (this.currentStep === 'testingStrategy') {
        this.setCurrentStep('cornerCases');
      } else if (this.currentStep === 'composition') {
        this.setCurrentStep('testingStrategy');
      } else if (this.currentStep === 'finished') {
        this.setCurrentStep('composition');
      }
      this.focusInput();
    },
    focusInput() {
      // Asegurarnos de que el textarea existe y no está deshabilitado
      if (this.$refs.feedbackInput && !this.isLoading) {
        this.$nextTick(() => {
          this.$refs.feedbackInput.focus();
        });
      }
    },
    async fetchJiraStory() {
      try {
        this.setLoadingJira(true);
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
        this.setLoadingJira(false);
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
    async handleJiraAction({ content, jiraId }) {
      const result = await this.updateOrCreateJiraStory({ content, jiraId });
      if (result.success) {
        const action = result.data.action === 'created' ? 'creada' : 'actualizada';
        this.showToastMessage(`Historia ${action} correctamente en Jira: ${result.data.story_id}`, 'success');
      } else {
        this.showToastMessage(result.error, 'error');
      }
    },
    handleModalVisibility(isOpen) {
      this.setIsReviewModalOpen(isOpen);
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

/* Estilos para los botones de avance */
.btn-corner-cases, .btn-testing-strategy, .btn-review {
  background-color: #34c759;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  white-space: nowrap;
}

.btn-corner-cases:disabled, .btn-testing-strategy:disabled, .btn-review:disabled {
  background-color: #666;
  cursor: not-allowed;
}
</style>