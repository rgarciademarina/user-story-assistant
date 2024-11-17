import { createStore } from 'vuex'
import axios from 'axios'

export default createStore({
  state: {
    sessionId: null,
    story: '',
    refinedStory: '',
    cornerCases: [],
    testingStrategies: [],
  },
  getters: {
  },
  mutations: {
    setSessionId(state, sessionId) {
      state.sessionId = sessionId;
    },
    setStory(state, story) {
      state.story = story;
    },
    setRefinedStory(state, refinedStory) {
      state.refinedStory = refinedStory;
    },
    setCornerCases(state, cornerCases) {
      state.cornerCases = cornerCases;
    },
    setTestingStrategies(state, testingStrategies) {
      state.testingStrategies = testingStrategies;
    },
  },
  actions: {
    async refineStory({ commit, state }, payload) {
      console.log('refineStory action called with payload:', payload);
      if (!payload || !payload.story) {
        console.warn('The "story" field is missing in the payload. Aborting action.');
        return;
      }
      const { story, feedback } = payload;
      const requestData = { story };
      if (feedback) {
        requestData.feedback = feedback;
      }
      if (state.sessionId) {
        requestData.session_id = state.sessionId;
      }
      console.log('Sending request to backend with data:', requestData);
      try {
        const response = await axios.post('/api/refine_story', requestData);
        if (!state.sessionId) {
          commit('setSessionId', response.data.session_id);
        }
        commit('setRefinedStory', response.data.refined_story);
        commit('setStory', story);
      } catch (error) {
        if (error.response) {
          console.error('Error refining story:', error.response.data);
        } else if (error.request) {
          console.error('No response received:', error.request);
        } else {
          console.error('Error setting up request:', error.message);
        }
      }
    },
    async identifyCornerCases({ commit, state }, feedback) {
      const payload = {
        session_id: state.sessionId,
        story: state.refinedStory,
        feedback: feedback,
      };
      try {
        const response = await axios.post('/api/identify_corner_cases', payload);
        commit('setCornerCases', response.data.corner_cases);
      } catch (error) {
        console.error('Error identifying corner cases:', error);
      }
    },
    async proposeTestingStrategy({ commit, state }, feedback) {
      const payload = {
        session_id: state.sessionId,
        story: state.refinedStory,
        corner_cases: state.cornerCases,
        feedback: feedback,
      };
      try {
        const response = await axios.post('/api/propose_testing_strategy', payload);
        commit('setTestingStrategies', response.data.testing_strategies);
      } catch (error) {
        console.error('Error proposing testing strategies:', error);
      }
    },
    resetProcess({ commit }) {
      commit('setSessionId', null);
      commit('setStory', '');
      commit('setRefinedStory', '');
      commit('setCornerCases', []);
      commit('setTestingStrategies', []);
    },
  },
  modules: {
  }
})
