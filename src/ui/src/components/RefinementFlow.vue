<template>
  <div class="refinement-flow">
    <div class="header">
      <h2>{{ currentStateLabel }}</h2>
    </div>
    <div class="chat-container">
      <div v-for="(message, index) in messages" :key="index">
        <ChatMessage :message="message" />
      </div>
      <div v-if="isLoading" class="loading-indicator">
        <span>Cargando...</span>
      </div>
    </div>
    <div class="input-container">
      <textarea v-model="userInput" @keyup.enter="sendFeedback"></textarea>
      <button @click="sendFeedback">Enviar</button>
      <button
        v-if="currentStep !== 'finished'"
        @click="advanceStep"
        :class="['advance-button', advanceButtonClass]"
      >
        {{ nextButtonLabel }}
      </button>
      <button v-if="backButtonLabel" @click="goBack" class="back-button">
        {{ backButtonLabel }}
      </button>
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
    ...mapState(['messages', 'currentStep']),
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
      if (this.currentStep === 'testingStrategy') return 'Refinamiento';
      return null;
    },
    advanceButtonClass() {
      return this.currentStep === 'testingStrategy' ? 'finish-button' : 'next-button';
    },
  },
  methods: {
    ...mapActions(['refineStory', 'identifyCornerCases', 'proposeTestingStrategy', 'addMessage', 'resetProcess', 'setCurrentStep']),
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
      const story = this.$store.state.originalStory || this.previousUserMessage();
      const payload = { story, feedback };
      const result = await this.refineStory(payload);
      // Agregar la respuesta del LLM al historial
      this.addMessage({ text: result.refinementResponse, sender: 'assistant' });
    },
    async handleCornerCasesFeedback(feedback) {
      const refinedStory = this.$store.state.refinedStory;
      const payload = { refinedStory, feedback };
      const result = await this.identifyCornerCases(payload);
      this.addMessage({ text: result.cornerCasesResponse, sender: 'assistant' });
    },
    async handleTestingStrategyFeedback(feedback) {
      const refinedStory = this.$store.state.refinedStory;
      const cornerCases = this.$store.state.cornerCases;
      const payload = { refinedStory, cornerCases, feedback };
      const result = await this.proposeTestingStrategy(payload);
      this.addMessage({ text: result.testingStrategyResponse, sender: 'assistant' });
    },
    async advanceStep() {
      if (this.isLoading) return;
      if (this.currentStep === 'refineStory') {
        this.setCurrentStep('cornerCases');
        await this.sendFeedback(); // Enviar feedback vacío para avanzar
      } else if (this.currentStep === 'cornerCases') {
        this.setCurrentStep('testingStrategy');
        await this.sendFeedback(); // Enviar feedback vacío para avanzar
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
        this.setCurrentStep('refineStory');
      } else if (this.currentStep === 'cornerCases') {
        this.setCurrentStep('refineStory');
      }
    },
    previousUserMessage() {
      const reversedMessages = [...this.messages].reverse();
      for (const message of reversedMessages) {
        if (message.sender === 'user') return message.text;
      }
      return '';
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
.refinement-flow {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #1e1e1e;
  color: #fff;
}
.header {
  padding: 10px;
  text-align: center;
  background-color: #333;
  border-bottom: 1px solid #444;
}
.chat-container {
  flex: 1;
  padding: 10px;
  overflow-y: auto;
}
.input-container {
  display: flex;
  padding: 10px;
  background-color: #333;
  align-items: center;
}
textarea {
  flex: 1;
  resize: none;
  background-color: #2e2e2e;
  color: #fff;
  border: 1px solid #444;
  border-radius: 5px;
  padding: 10px;
  margin-right: 10px;
  height: 50px;
}
button {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 10px 15px;
  cursor: pointer;
  margin-left: 5px;
  border-radius: 5px;
}
button:hover {
  background-color: #358a6b;
}
.advance-button {
  background-color: #28a745;
}
.finish-button {
  background-color: #007bff;
}
.back-button {
  background-color: #dc3545;
}
.loading-indicator {
  text-align: center;
  color: #aaa;
  margin-top: 10px;
}
</style>