import { createStore } from 'vuex';
import axios from 'axios';
import store, { finalizeStory } from '@/store';

// Mock axios
jest.mock('axios');

describe('Vuex Store', () => {
  let testStore;

  beforeEach(() => {
    // Create a fresh store instance before each test using the real store configuration
    testStore = createStore({
      ...store._modules.root._rawModule,
      plugins: [] // Disable plugins for testing
    });
    
    // Reset all mocks
    jest.clearAllMocks();
  });

  describe('mutations', () => {
    test('addMessage adds a message to the messages array', () => {
      const message = { text: 'Test message', sender: 'user' };
      testStore.commit('addMessage', message);
      expect(testStore.state.messages).toHaveLength(1);
      expect(testStore.state.messages[0]).toEqual(message);
    });

    test('setCurrentStep updates the current step', () => {
      const step = 'identifyCornerCases';
      testStore.commit('setCurrentStep', step);
      expect(testStore.state.currentStep).toBe(step);
    });

    test('setOriginalStory updates the original story', () => {
      const story = 'Test story';
      testStore.commit('setOriginalStory', story);
      expect(testStore.state.originalStory).toBe(story);
    });

    test('setRefinedStory updates the refined story', () => {
      const story = 'Refined test story';
      testStore.commit('setRefinedStory', story);
      expect(testStore.state.refinedStory).toBe(story);
    });

    test('setCornerCases updates the corner cases', () => {
      const cases = ['case1', 'case2'];
      testStore.commit('setCornerCases', cases);
      expect(testStore.state.cornerCases).toEqual(cases);
    });

    test('setTestingStrategies updates the testing strategies', () => {
      const strategies = ['strategy1', 'strategy2'];
      testStore.commit('setTestingStrategies', strategies);
      expect(testStore.state.testingStrategies).toEqual(strategies);
    });

    test('setSessionId updates the session ID', () => {
      const sessionId = '123';
      testStore.commit('setSessionId', sessionId);
      expect(testStore.state.sessionId).toBe(sessionId);
    });

    test('resetProcess resets all state values', () => {
      // Set some values first
      testStore.commit('setOriginalStory', 'story');
      testStore.commit('setSessionId', '123');
      testStore.commit('addMessage', { text: 'message', sender: 'user' });

      // Reset
      testStore.commit('resetProcess');

      // Verify reset state
      expect(testStore.state.messages).toEqual([]);
      expect(testStore.state.currentStep).toBe('refineStory');
      expect(testStore.state.originalStory).toBe('');
      expect(testStore.state.refinedStory).toBe('');
      expect(testStore.state.cornerCases).toEqual([]);
      expect(testStore.state.testingStrategies).toEqual([]);
      expect(testStore.state.sessionId).toBeNull();
    });
  });

  describe('actions', () => {
    beforeEach(() => {
      // Ensure session_id is null before each test
      testStore.commit('resetProcess');
    });

    test('addMessage commits the correct mutation', () => {
      const message = { text: 'Test message', sender: 'user' };
      testStore.dispatch('addMessage', message);
      expect(testStore.state.messages[0]).toEqual(message);
    });

    test('setCurrentStep commits the correct mutation', () => {
      const step = 'identifyCornerCases';
      testStore.dispatch('setCurrentStep', step);
      expect(testStore.state.currentStep).toBe(step);
    });

    test('resetProcess action resets the store state', () => {
      // Set some initial state
      testStore.commit('setOriginalStory', 'story');
      testStore.commit('setSessionId', '123');
      testStore.commit('addMessage', { text: 'message', sender: 'user' });

      // Call the action
      testStore.dispatch('resetProcess');

      // Verify the state was reset
      expect(testStore.state.messages).toEqual([]);
      expect(testStore.state.currentStep).toBe('refineStory');
      expect(testStore.state.originalStory).toBe('');
      expect(testStore.state.refinedStory).toBe('');
      expect(testStore.state.cornerCases).toEqual([]);
      expect(testStore.state.testingStrategies).toEqual([]);
      expect(testStore.state.sessionId).toBeNull();
    });

    test('refineStory makes the correct API call and commits results', async () => {
      const story = 'Test story';
      const feedback = 'Test feedback';
      const response = { 
        data: { 
          refined_story: 'Refined story',
          refinement_feedback: 'Feedback',
          session_id: '123'
        } 
      };
      
      axios.post.mockResolvedValue(response);
      
      await testStore.dispatch('refineStory', { story, feedback });
      
      expect(axios.post).toHaveBeenCalledWith('/api/v1/refine_story', {
        story,
        feedback
      });
      expect(testStore.state.refinedStory).toBe(response.data.refined_story);
      expect(testStore.state.sessionId).toBe(response.data.session_id);
    });

    test('identifyCornerCases makes the correct API call and commits results', async () => {
      const refinedStory = 'Refined story';
      const feedback = 'Test feedback';
      const response = { 
        data: { 
          corner_cases: ['case1', 'case2'],
          corner_cases_feedback: 'Feedback',
          session_id: '123'
        } 
      };
      
      axios.post.mockResolvedValue(response);
      
      await testStore.dispatch('identifyCornerCases', { refinedStory, feedback });
      
      expect(axios.post).toHaveBeenCalledWith('/api/v1/identify_corner_cases', {
        story: refinedStory,
        feedback,
        existing_corner_cases: []
      });
      expect(testStore.state.cornerCases).toEqual(response.data.corner_cases);
      expect(testStore.state.sessionId).toBe(response.data.session_id);
    });

    test('proposeTestingStrategy makes the correct API call and commits results', async () => {
      const refinedStory = 'Refined story';
      const cornerCases = ['case1', 'case2'];
      const feedback = 'Test feedback';
      const response = { 
        data: { 
          testing_strategies: ['strategy1', 'strategy2'],
          testing_feedback: 'Feedback',
          session_id: '123'
        } 
      };
      
      axios.post.mockResolvedValue(response);
      
      await testStore.dispatch('proposeTestingStrategy', { refinedStory, cornerCases, feedback });
      
      expect(axios.post).toHaveBeenCalledWith('/api/v1/propose_testing_strategy', {
        story: refinedStory,
        corner_cases: cornerCases,
        feedback,
        existing_testing_strategies: []
      });
      expect(testStore.state.testingStrategies).toEqual(response.data.testing_strategies);
      expect(testStore.state.sessionId).toBe(response.data.session_id);
    });

    test('async actions include session_id in payload when it exists', async () => {
      // Set session_id explicitly for this test
      const sessionId = '123';
      testStore.commit('setSessionId', sessionId);
      
      const story = 'Test story';
      const feedback = 'Test feedback';
      
      axios.post.mockResolvedValue({ 
        data: { 
          refined_story: 'Refined story',
          refinement_feedback: 'Feedback',
          session_id: '123'
        } 
      });
      
      await testStore.dispatch('refineStory', { story, feedback });
      
      expect(axios.post).toHaveBeenCalledWith('/api/v1/refine_story', {
        story,
        feedback,
        session_id: sessionId
      });
    });

    test('all async actions include session_id in payload when it exists', async () => {
      const sessionId = '123';
      testStore.commit('setSessionId', sessionId);
      
      // Test identifyCornerCases
      axios.post.mockResolvedValue({ 
        data: { 
          corner_cases: ['case1'],
          corner_cases_feedback: 'Feedback',
          session_id: sessionId
        } 
      });

      await testStore.dispatch('identifyCornerCases', { 
        refinedStory: 'story', 
        feedback: 'feedback' 
      });
      
      expect(axios.post).toHaveBeenCalledWith('/api/v1/identify_corner_cases', 
        expect.objectContaining({
          session_id: sessionId
        })
      );

      // Test proposeTestingStrategy
      axios.post.mockResolvedValue({ 
        data: { 
          testing_strategies: ['strategy1'],
          testing_feedback: 'Feedback',
          session_id: sessionId
        } 
      });

      await testStore.dispatch('proposeTestingStrategy', { 
        refinedStory: 'story', 
        cornerCases: ['case1'], 
        feedback: 'feedback' 
      });
      
      expect(axios.post).toHaveBeenCalledWith('/api/v1/propose_testing_strategy', 
        expect.objectContaining({
          session_id: sessionId
        })
      );
    });

    test('async actions handle API errors', async () => {
      const error = new Error('API Error');
      axios.post.mockRejectedValue(error);
      
      const story = 'Test story';
      const feedback = 'Test feedback';
      
      await expect(testStore.dispatch('refineStory', { story, feedback }))
        .rejects.toThrow('API Error');
    });

    test('async actions update session_id from API response', async () => {
      const newSessionId = '456';
      
      // Test identifyCornerCases
      axios.post.mockResolvedValue({ 
        data: { 
          corner_cases: ['case1'],
          corner_cases_feedback: 'Feedback',
          session_id: newSessionId
        } 
      });

      await testStore.dispatch('identifyCornerCases', { 
        refinedStory: 'story', 
        feedback: 'feedback' 
      });
      
      expect(testStore.state.sessionId).toBe(newSessionId);

      // Test proposeTestingStrategy
      const newerSessionId = '789';
      axios.post.mockResolvedValue({ 
        data: { 
          testing_strategies: ['strategy1'],
          testing_feedback: 'Feedback',
          session_id: newerSessionId
        } 
      });

      await testStore.dispatch('proposeTestingStrategy', { 
        refinedStory: 'story', 
        cornerCases: ['case1'], 
        feedback: 'feedback' 
      });
      
      expect(testStore.state.sessionId).toBe(newerSessionId);
    });

    test('async actions handle responses without session_id', async () => {
      // Test refineStory
      axios.post.mockResolvedValue({ 
        data: { 
          refined_story: 'Refined story',
          refinement_feedback: 'Feedback'
          // No session_id
        } 
      });

      await testStore.dispatch('refineStory', { 
        story: 'story', 
        feedback: 'feedback' 
      });
      
      expect(testStore.state.sessionId).toBeNull();

      // Test identifyCornerCases
      axios.post.mockResolvedValue({ 
        data: { 
          corner_cases: ['case1'],
          corner_cases_feedback: 'Feedback'
          // No session_id
        } 
      });

      await testStore.dispatch('identifyCornerCases', { 
        refinedStory: 'story', 
        feedback: 'feedback' 
      });
      
      expect(testStore.state.sessionId).toBeNull();

      // Test proposeTestingStrategy
      axios.post.mockResolvedValue({ 
        data: { 
          testing_strategies: ['strategy1'],
          testing_feedback: 'Feedback'
          // No session_id
        } 
      });

      await testStore.dispatch('proposeTestingStrategy', { 
        refinedStory: 'story', 
        cornerCases: ['case1'], 
        feedback: 'feedback' 
      });
      
      expect(testStore.state.sessionId).toBeNull();
    });

    test('finalizeStory maneja correctamente el feedback y sessionId', async () => {
      const testStore = createStore({
        state: {
          refinedStory: 'Historia refinada',
          cornerCases: ['Caso 1', 'Caso 2'],
          testingStrategies: ['Test 1', 'Test 2'],
          sessionId: 'test-session-123'
        },
        mutations: {
          setSessionId(state, sessionId) {
            state.sessionId = sessionId;
          }
        },
        actions: {
          async finalizeStory({ commit, state }, { feedback }) {
            const payload = {
              refined_story: state.refinedStory,
              corner_cases: state.cornerCases,
              testing_strategy: state.testingStrategies,
              feedback: feedback || '',
              session_id: state.sessionId
            };

            const response = await axios.post('/api/v1/finalize_story', payload);
            
            if (response.data.session_id) {
              commit('setSessionId', response.data.session_id);
            }

            let finalizationResponse = response.data.finalized_story;
            if (response.data.feedback && response.data.feedback.trim()) {
              finalizationResponse += '\n\n' + response.data.feedback;
            }

            return { finalizationResponse };
          }
        }
      });

      // Mock de axios.post
      axios.post.mockResolvedValueOnce({
        data: {
          session_id: 'new-session-456',
          finalized_story: 'Historia finalizada',
          feedback: 'Feedback adicional'
        }
      });

      const result = await testStore.dispatch('finalizeStory', { feedback: 'Mi feedback' });

      expect(axios.post).toHaveBeenCalledWith('/api/v1/finalize_story', {
        refined_story: 'Historia refinada',
        corner_cases: ['Caso 1', 'Caso 2'],
        testing_strategy: ['Test 1', 'Test 2'],
        feedback: 'Mi feedback',
        session_id: 'test-session-123'
      });

      expect(testStore.state.sessionId).toBe('new-session-456');
      expect(result.finalizationResponse).toBe('Historia finalizada\n\nFeedback adicional');
    });
  });
});
