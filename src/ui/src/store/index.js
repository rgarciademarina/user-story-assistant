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
    testingStrategies: [],
    sessionId: null,
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
    setTestingStrategies(state, testingStrategies) {
      state.testingStrategies = testingStrategies;
    },
    setSessionId(state, sessionId) {
      state.sessionId = sessionId;
    },
    resetProcess(state) {
      state.messages = [];
      state.currentStep = 'refineStory';
      state.originalStory = '';
      state.refinedStory = '';
      state.cornerCases = [];
      state.sessionId = null;
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
    async refineStory({ commit, state }, { story, feedback }) {
      commit('setOriginalStory', story);
      // Preparar el payload incluyendo el session_id si existe
      const payload = {
        story,
        feedback,
      };
      if (state.sessionId) {
        payload.session_id = state.sessionId;
      }
      
      // Realizar la llamada al backend
      const response = await axios.post('/api/refine_story', payload);
      
      // Guardar el session_id de la respuesta
      if (response.data.session_id) {
        commit('setSessionId', response.data.session_id);
      }
      
      const refinedStory = response.data.refined_story;
      commit('setRefinedStory', refinedStory);
      
      // Preparar la respuesta del LLM
      const refinementResponse = `**Historia Refinada:**\n${refinedStory}\n\n**Cambios Realizados:**\n${response.data.refinement_feedback}`;
      return { refinementResponse };
    },
    async identifyCornerCases({ commit, state }, { refinedStory, feedback }) {
      const existingCornerCases = state.cornerCases;

      const response = await axios.post('/api/identify_corner_cases', {
        story: refinedStory,
        feedback,
        existing_corner_cases: existingCornerCases,
      });

      const cornerCases = response.data.corner_cases;
      commit('setCornerCases', cornerCases);

      const cornerCasesText = cornerCases.join('\n');
      const cornerCasesResponse = `**Casos Esquina Actualizados:**\n${cornerCasesText}\n\n**Análisis de Cambios:**\n${response.data.corner_cases_feedback}`;
      return { cornerCasesResponse };
    },
    async proposeTestingStrategy({ commit, state }, { refinedStory, cornerCases, feedback }) {
      const existingTestingStrategies = state.testingStrategies;

      const response = await axios.post('/api/propose_testing_strategy', {
        story: refinedStory,
        corner_cases: cornerCases,
        feedback,
        existing_testing_strategies: existingTestingStrategies,
      });

      const testingStrategies = response.data.testing_strategies;
      commit('setTestingStrategies', testingStrategies);

      const testingStrategiesText = testingStrategies.join('\n');
      const testingStrategyResponse = `**Estrategias de Testing Propuestas:**\n${testingStrategiesText}\n\n**Análisis de Cambios:**\n${response.data.testing_feedback}`;
      return { testingStrategyResponse };
    },
  },
  plugins: [createPersistedState()],
});
