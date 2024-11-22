import { createStore } from 'vuex';
import createPersistedState from 'vuex-persistedstate';
import axios from 'axios';

export default createStore({
  state: {
    messages: [],
    currentStep: 'refineStory',
    originalStory: '',
    refinedStory: '',
    cornerCases: [],
  },
  mutations: {
    addMessage(state, message) {
      state.messages.push(message);
    },
    setCurrentStep(state, step) {
      state.currentStep = step;
    },
    setOriginalStory(state, story) {
      state.originalStory = story;
    },
    setRefinedStory(state, story) {
      state.refinedStory = story;
    },
    setCornerCases(state, cases) {
      state.cornerCases = cases;
    },
    resetProcess(state) {
      state.messages = [];
      state.currentStep = 'refineStory';
      state.originalStory = '';
      state.refinedStory = '';
      state.cornerCases = [];
    },
  },
  actions: {
    addMessage({ commit }, message) {
      commit('addMessage', message);
    },
    setCurrentStep({ commit }, step) {
      commit('setCurrentStep', step);
    },
    resetProcess({ commit }) {
      commit('resetProcess');
    },
    async refineStory({ commit }, { story, feedback }) {
      commit('setOriginalStory', story);
      // Realizar la llamada al backend
      const response = await axios.post('/api/refine_story', {
        story,
        feedback,
      });
      const refinedStory = response.data.refined_story;
      commit('setRefinedStory', refinedStory);
      // Preparar la respuesta del LLM
      const refinementResponse = `**Historia Refinada:**\n${refinedStory}\n\n**Cambios Realizados:**\n${response.data.refinement_feedback}`;
      return { refinementResponse };
    },
    async identifyCornerCases({ commit, state }, { refinedStory, feedback }) {
      const existingCornerCases = state.cornerCases; // Obtenemos los casos esquina existentes

      // Realizar la llamada al backend
      const response = await axios.post('/api/identify_corner_cases', {
        story: refinedStory,
        feedback,
        existing_corner_cases: existingCornerCases, // Enviamos los casos esquina existentes
      });

      const cornerCases = response.data.corner_cases;
      commit('setCornerCases', cornerCases); // Guardamos los nuevos casos esquina

      const cornerCasesText = cornerCases
        .map((item, index) => `${index + 1}. ${item}`)
        .join('\n');
      const cornerCasesResponse = `**Casos Esquina Actualizados:**\n${cornerCasesText}\n\n**Análisis de Cambios:**\n${response.data.corner_cases_feedback}`;
      return { cornerCasesResponse };
    },
    async proposeTestingStrategy(_, { refinedStory, cornerCases, feedback }) {
      // Realizar la llamada al backend
      const response = await axios.post('/api/propose_testing_strategy', {
        story: refinedStory,
        corner_cases: cornerCases,
        feedback,
      });
      const testingStrategies = response.data.testing_strategies;
      const testingStrategiesText = testingStrategies
        .map((item, index) => `${index + 1}. ${item}`)
        .join('\n');
      const testingStrategyResponse = `**Estrategias de Testing Propuestas:**\n${testingStrategiesText}\n\n**Análisis de Cambios:**\n${response.data.testing_feedback}`;
      return { testingStrategyResponse };
    },
  },
  plugins: [createPersistedState()],
});
