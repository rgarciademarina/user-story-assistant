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
    isReviewModalOpen: false,
    jiraStoryId: null,
    loadingJira: false,
    composedStory: '',
  },
  mutations: {
    addMessage(state, message) {
      state.messages.push(message);
    },
    setCurrentStep(state, step) {
      state.currentStep = step;
    },
    setLoadingJira(state, isLoading) {
      state.loadingJira = isLoading;
    },
    setIsReviewModalOpen(state, isOpen) {
      state.isReviewModalOpen = isOpen;
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
    setJiraStoryId(state, id) {
      state.jiraStoryId = id;
    },
    setComposedStory(state, story) {
      state.composedStory = story;
    },
    resetProcess(state) {
      state.messages = [];
      state.currentStep = 'refineStory';
      state.originalStory = '';
      state.refinedStory = '';
      state.cornerCases = [];
      state.testingStrategies = [];
      state.sessionId = null;
      state.jiraStoryId = null;
      state.isReviewModalOpen = false;
      state.composedStory = '';
    },
  },
  actions: {
    addMessage({ commit }, message) {
      commit('addMessage', message);
    },
    setCurrentStep({ commit }, step) {
      commit('setCurrentStep', step);
    },
    setLoadingJira({ commit }, isLoading) {
      commit('setLoadingJira', isLoading);
    },
    setIsReviewModalOpen({ commit }, isOpen) {
      commit('setIsReviewModalOpen', isOpen);
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
      const response = await axios.post('/api/v1/refine_story', payload);
      
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

      // Preparar el payload incluyendo el session_id
      const payload = {
        story: refinedStory,
        feedback,
        existing_corner_cases: existingCornerCases
      };
      
      if (state.sessionId) {
        payload.session_id = state.sessionId;
      }

      const response = await axios.post('/api/v1/identify_corner_cases', payload);

      // Mantener el session_id actualizado si el backend lo devuelve
      if (response.data.session_id) {
        commit('setSessionId', response.data.session_id);
      }

      const newCornerCases = response.data.corner_cases;
      commit('setCornerCases', newCornerCases);

      // Preparar la respuesta del LLM
      const cornerCasesResponse = `**Casos Esquina Identificados:**\n${newCornerCases.join('\n')}\n\n**Análisis de Cambios:**\n${response.data.corner_cases_feedback}`;
      return { cornerCasesResponse };
    },
    async proposeTestingStrategy({ commit, state }, { refinedStory, cornerCases, feedback }) {
      // Preparar el payload incluyendo el session_id y las estrategias existentes
      const payload = {
        story: refinedStory,
        corner_cases: cornerCases,
        feedback,
        existing_testing_strategies: state.testingStrategies
      };
      
      if (state.sessionId) {
        payload.session_id = state.sessionId;
      }

      const response = await axios.post('/api/v1/propose_testing_strategy', payload);

      // Mantener el session_id actualizado si el backend lo devuelve
      if (response.data.session_id) {
        commit('setSessionId', response.data.session_id);
      }

      const testingStrategies = response.data.testing_strategies;
      commit('setTestingStrategies', testingStrategies);

      // Preparar la respuesta del LLM
      const testingStrategyResponse = `**Estrategias de Testing Propuestas:**\n${testingStrategies.join('\n')}\n\n**Análisis de Cambios:**\n${response.data.testing_feedback}`;
      return { testingStrategyResponse };
    },
    async finalizeStory({ commit, state }, { feedback }) {
      const payload = {
        refined_story: state.refinedStory,
        corner_cases: state.cornerCases,
        testing_strategy: state.testingStrategies,
        feedback: feedback || ''
      };
      
      if (state.sessionId) {
        payload.session_id = state.sessionId;
      }

      const response = await axios.post('/api/v1/finalize_story', payload);
      
      // Mantener consistencia con otros métodos
      if (response.data.session_id) {
        commit('setSessionId', response.data.session_id);
      }

      // Preparar respuesta para mostrar al usuario
      let finalizationResponse = response.data.finalized_story;
      
      // Si hay feedback, añadirlo como parte de la respuesta
      if (response.data.feedback && response.data.feedback.trim()) {
        finalizationResponse += '\n\n' + response.data.feedback;
      }
      
      return { finalizationResponse };
    },
    async composeStory({ commit, state }, feedback = '') {
      const payload = {
        refined_story: state.refinedStory,
        corner_cases: state.cornerCases,
        testing_strategy: state.testingStrategies,
        feedback: feedback || ''
      };
      
      if (state.sessionId) {
        payload.session_id = state.sessionId;
      }

      const response = await axios.post('/api/v1/finalize_story', payload);
      
      if (response.data.session_id) {
        commit('setSessionId', response.data.session_id);
      }

      let compositionResponse = response.data.finalized_story;
      
      if (response.data.feedback && response.data.feedback.trim()) {
        compositionResponse += '\n\n' + response.data.feedback;
      }

      commit('setComposedStory', compositionResponse);
      return { compositionResponse };
    },
    async updateOrCreateJiraStory({ commit }, { content, jiraId }) {
      try {
        commit('setLoadingJira', true);
        const payload = {
          title: 'User Story',
          description: content
        };

        // Solo añadir story_id si no está vacío
        if (jiraId) {
          payload.story_id = jiraId;
        }

        const response = await axios.post('/api/v1/jira/story', payload);
        
        commit('setJiraStoryId', response.data.story_id);
        return { success: true, data: response.data };
      } catch (error) {
        console.error('Error updating/creating Jira story:', error);
        return { 
          success: false, 
          error: error.response?.data?.detail || 'Error al procesar la solicitud de Jira'
        };
      } finally {
        commit('setLoadingJira', false);
      }
    },
  },
  plugins: [createPersistedState()],
});
