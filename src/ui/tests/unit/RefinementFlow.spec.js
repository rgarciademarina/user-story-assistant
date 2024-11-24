import { mount } from '@vue/test-utils'
import { createStore } from 'vuex'
import RefinementFlow from '@/components/RefinementFlow.vue'
import ChatMessage from '@/components/ChatMessage.vue'

// Mock del store de Vuex
const createVuexStore = () => {
  return createStore({
    state: {
      messages: [],
      currentStep: 'refineStory',
      originalStory: '',
      refinedStory: '',
      cornerCases: [],
      testingStrategies: [],
      sessionId: null
    },
    mutations: {
      addMessage(state, message) {
        state.messages.push(message);
      },
      setCurrentStep(state, step) {
        state.currentStep = step;
      },
      resetProcess(state) {
        state.messages = [];
        state.currentStep = 'refineStory';
        state.originalStory = '';
        state.refinedStory = '';
        state.cornerCases = [];
        state.testingStrategies = [];
        state.sessionId = null;
      },
      setRefinedStory(state, story) {
        state.refinedStory = story;
      }
    },
    actions: {
      resetProcess({ commit }) {
        commit('resetProcess');
      },
      refineStory: jest.fn().mockResolvedValue({
        refinementResponse: 'Mocked refinement response'
      }),
      identifyCornerCases: jest.fn().mockResolvedValue({
        cornerCasesResponse: 'Mocked corner cases response'
      }),
      proposeTestingStrategy: jest.fn().mockResolvedValue({
        testingStrategyResponse: 'Mocked testing strategy response'
      }),
      setCurrentStep({ commit }, step) {
        commit('setCurrentStep', step);
      },
      addMessage({ commit }, message) {
        commit('addMessage', message);
      },
      setRefinedStory({ commit }, story) {
        commit('setRefinedStory', story);
      }
    }
  })
}

describe('RefinementFlow.vue', () => {
  let wrapper
  let store

  beforeEach(() => {
    store = createVuexStore()
    wrapper = mount(RefinementFlow, {
      global: {
        plugins: [store],
        components: {
          ChatMessage
        },
        stubs: {
          ChatMessage: true // Stub del componente ChatMessage
        }
      },
      data() {
        return {
          userInput: '',
          isLoading: false
        }
      }
    })
  })

  afterEach(() => {
    wrapper.unmount()
    jest.clearAllMocks()
  })

  test('renderiza correctamente', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.refinement-flow').exists()).toBe(true)
  })

  test('muestra el placeholder correcto en el textarea', () => {
    const textarea = wrapper.find('textarea')
    expect(textarea.exists()).toBe(true)
    expect(textarea.attributes('placeholder')).toBe('Escribe tu feedback aquí...')
  })

  test('botón de enviar está deshabilitado cuando no hay texto', async () => {
    await wrapper.setData({ userInput: '' })
    const sendButton = wrapper.find('button')
    expect(sendButton.element.disabled).toBe(true)
  })

  test('botón de enviar se habilita cuando hay texto', async () => {
    await wrapper.setData({ userInput: 'Test input' })
    const sendButton = wrapper.find('button')
    expect(sendButton.element.disabled).toBe(false)
  })

  test('muestra el indicador de carga correctamente', async () => {
    await wrapper.setData({ isLoading: true })
    expect(wrapper.find('.loading-indicator').exists()).toBe(true)
    expect(wrapper.find('.loading-indicator').text()).toBe('Cargando...')
  })

  test('maneja el envío de feedback correctamente en el paso de refinamiento', async () => {
    await wrapper.setData({ userInput: 'Test feedback' })
    const sendButton = wrapper.find('button')
    await sendButton.trigger('click')
    
    // Esperar a que se procese la acción asíncrona
    await wrapper.vm.$nextTick()
    
    // Verificar que se añadió el mensaje del usuario
    expect(store.state.messages.length).toBeGreaterThan(1) // Ya hay un mensaje inicial
  })

  test('maneja la tecla Enter correctamente', async () => {
    await wrapper.setData({ userInput: 'Test feedback' })
    const textarea = wrapper.find('textarea')
    await textarea.trigger('keydown.enter')
    
    // Esperar a que se procese la acción asíncrona
    await wrapper.vm.$nextTick()
    
    expect(store.state.messages.length).toBeGreaterThan(1) // Ya hay un mensaje inicial
  })

  test('muestra el estado actual correctamente', async () => {
    await store.dispatch('setCurrentStep', 'refineStory')
    await wrapper.vm.$nextTick()
    const header = wrapper.find('.header h2')
    expect(header.exists()).toBe(true)
    expect(header.text()).toBe('Refinamiento')
  })

  test('renderiza los mensajes correctamente', async () => {
    // Limpiar los mensajes existentes
    await store.dispatch('resetProcess')
    await wrapper.vm.$nextTick()

    const testMessage = { role: 'user', content: 'Test message' }
    await store.dispatch('addMessage', testMessage)
    await wrapper.vm.$nextTick()
    
    // Verificar que solo existe el mensaje que acabamos de añadir
    expect(store.state.messages.length).toBe(1)
    expect(store.state.messages[0]).toEqual(testMessage)
  })

  test('maneja el cambio de paso correctamente', async () => {
    await store.dispatch('setRefinedStory', 'Test story')
    await wrapper.vm.advanceStep()
    expect(store.state.currentStep).toBe('cornerCases')
  })
})
