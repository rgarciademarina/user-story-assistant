<template>
    <div>
      <h1>Asistente de Refinamiento de Historias de Usuario</h1>
  
      <div v-if="currentStep === 'refineStory'">
        <h2>Paso 1: Refinar Historia de Usuario</h2>
        <UserStoryForm @submit="handleRefineStory" />
        <div v-if="refinedStory">
          <h3>Historia Refinada:</h3>
          <p>{{ refinedStory }}</p>
          <FeedbackForm @submit="handleRefineFeedback" />
          <button @click="proceedToCornerCases">Continuar a Casos Esquina</button>
        </div>
      </div>
  
      <div v-else-if="currentStep === 'cornerCases'">
        <h2>Paso 2: Identificar Casos Esquina</h2>
        <div v-if="cornerCases.length">
          <h3>Casos Esquina Identificados:</h3>
          <ul>
            <li v-for="(caseItem, index) in cornerCases" :key="index">{{ caseItem }}</li>
          </ul>
          <FeedbackForm @submit="handleCornerCasesFeedback" />
          <button @click="proceedToTestingStrategy">Continuar a Estrategias de Testing</button>
          <button @click="goBackToRefineStory">Volver a Refinar Historia</button>
        </div>
      </div>
  
      <div v-else-if="currentStep === 'testingStrategy'">
        <h2>Paso 3: Proponer Estrategia de Testing</h2>
        <div v-if="testingStrategies.length">
          <h3>Estrategias de Testing Recomendadas:</h3>
          <ul>
            <li v-for="(strategy, index) in testingStrategies" :key="index">{{ strategy }}</li>
          </ul>
          <FeedbackForm @submit="handleTestingStrategyFeedback" />
          <button @click="finishProcess">Finalizar</button>
          <button @click="goBackToCornerCases">Volver a Casos Esquina</button>
        </div>
      </div>
  
      <div v-else-if="currentStep === 'finished'">
        <h2>Proceso Completado</h2>
        <p>¡La historia de usuario ha sido refinada exitosamente!</p>
        <button @click="resetProcess">Empezar de Nuevo</button>
      </div>
    </div>
  </template>
  
  <script>
  import { mapState, mapActions } from 'vuex';
  import UserStoryForm from './UserStoryForm.vue';
  import FeedbackForm from './FeedbackForm.vue';
  
  export default {
    components: {
      UserStoryForm,
      FeedbackForm,
    },
    data() {
      return {
        currentStep: 'refineStory',
      };
    },
    computed: {
      ...mapState(['refinedStory', 'cornerCases', 'testingStrategies']),
    },
    methods: {
      ...mapActions(['refineStory', 'identifyCornerCases', 'proposeTestingStrategy', 'resetProcess']),
      async handleRefineStory({ story, feedback }) {
        console.log('handleRefineStory called with:', { story, feedback });
        this.$store.commit('setStory', story);
        await this.refineStory({ story, feedback });
      },
      async handleRefineFeedback(feedback) {
        await this.refineStory(feedback);
      },
      proceedToCornerCases() {
        this.currentStep = 'cornerCases';
        this.identifyCornerCases('');
      },
      async handleCornerCasesFeedback(feedback) {
        await this.identifyCornerCases(feedback);
      },
      proceedToTestingStrategy() {
        this.currentStep = 'testingStrategy';
        this.proposeTestingStrategy('');
      },
      async handleTestingStrategyFeedback(feedback) {
        await this.proposeTestingStrategy(feedback);
      },
      finishProcess() {
        this.currentStep = 'finished';
      },
      goBackToRefineStory() {
        this.currentStep = 'refineStory';
      },
      goBackToCornerCases() {
        this.currentStep = 'cornerCases';
      },
      resetProcess() {
        this.resetProcess();
        this.currentStep = 'refineStory';
      },
    },
  };
  </script>
  
  <style scoped>
  /* Estilos personalizados */
  h1, h2, h3 {
    color: #333;
  }
  button {
    margin: 10px 5px;
    padding: 10px 20px;
    background-color: #42b983;
    color: white;
    border: none;
    cursor: pointer;
  }
  button:hover {
    background-color: #358a6b;
  }
  textarea {
    width: 100%;
    min-height: 80px;
    margin-bottom: 10px;
  }
  label {
    display: block;
    margin-top: 10px;
  }
  </style>