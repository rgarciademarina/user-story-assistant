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
        v-model="userInput"
        @keydown.enter="handleKeyPress"
        :placeholder="inputPlaceholder"
        :disabled="isLoading"
      ></textarea>
      <div class="button-group">
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
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import ChatMessage from './ChatMessage.vue';

export default {
  components: {
    ChatMessage,
  },
  data() {
    return {
      userInput: '',
      isLoading: false,
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
      if (this.currentStep === 'testingStrategy') return 'Finalizar';
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
  },
  methods: {
    ...mapActions([
      'refineStory',
      'identifyCornerCases',
      'proposeTestingStrategy',
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
      }
    },
    async handleRefineFeedback(feedback) {
    if (!this.$store.state.refinedStory) {
      const payload = { story: feedback, feedback: '' };
      const result = await this.refineStory(payload);
      this.addMessage({ text: result.refinementResponse, sender: 'assistant' });
      return;
    }
      const story = this.$store.state.refinedStory;
      const payload = { story, feedback };
      const result = await this.refineStory(payload);
      this.addMessage({ text: result.refinementResponse, sender: 'assistant' });
    },
    async handleCornerCasesFeedback(feedback) {
      const refinedStory = this.$store.state.refinedStory;
      const existingCornerCases = this.$store.state.cornerCases; // Obtenemos los casos esquina existentes

      const payload = { refinedStory, feedback, existingCornerCases };
      const result = await this.identifyCornerCases(payload);
      this.addMessage({ text: result.cornerCasesResponse, sender: 'assistant' });
    },
    async handleTestingStrategyFeedback(feedback) {
      const refinedStory = this.$store.state.refinedStory;
      const cornerCases = this.$store.state.cornerCases;
      const existingTestingStrategies = this.$store.state.testingStrategies;
      const payload = { refinedStory, cornerCases, feedback, existingTestingStrategies };
      const result = await this.proposeTestingStrategy(payload);
      this.addMessage({ text: result.testingStrategyResponse, sender: 'assistant' });
    },
    async advanceStep() {
      if (this.isLoading) return;

      if (this.currentStep === 'refineStory') {
        if (!this.refinedStory) return;
        this.setCurrentStep('cornerCases');
        this.isLoading = true;
        try {
          await this.handleCornerCasesFeedback(''); // Enviar feedback vacío para avanzar
        } finally {
          this.isLoading = false;
        }
      } else if (this.currentStep === 'cornerCases') {
        this.setCurrentStep('testingStrategy');
        this.isLoading = true;
        try {
          await this.handleTestingStrategyFeedback(''); // Enviar feedback vacío para avanzar
        } finally {
          this.isLoading = false;
        }
      } else if (this.currentStep === 'testingStrategy') {
        this.setCurrentStep('finished');
        this.addMessage({
          text: '¡El proceso ha finalizado exitosamente!',
          sender: 'assistant',
        });
      }
    },
    goBack() {
      if (this.currentStep === 'testingStrategy') {
        this.setCurrentStep('cornerCases');
      } else if (this.currentStep === 'cornerCases') {
        this.setCurrentStep('refineStory');
      }
    },
    previousUserStory() {
      const storyMessage = this.messages.find(
        (message) => message.sender === 'userStory'
      );
      return storyMessage ? storyMessage.text : '';
    },
    handleKeyPress(event) {
      if (event.shiftKey) {
        // Permitir el salto de línea
        return;
      } else {
        // Prevenir el salto de línea y enviar el mensaje
        event.preventDefault();
        this.sendFeedback();
      }
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const chatContainer = this.$el.querySelector('.chat-container');
        chatContainer.scrollTop = chatContainer.scrollHeight;
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
</style>