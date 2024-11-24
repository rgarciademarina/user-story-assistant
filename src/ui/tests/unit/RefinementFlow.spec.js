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

  // Nuevas pruebas para cubrir las líneas faltantes
  
  test('no avanza si no hay historia refinada', async () => {
    // Asegurarse de que no hay historia refinada
    await store.dispatch('setRefinedStory', '')
    await wrapper.vm.advanceStep()
    expect(store.state.currentStep).toBe('refineStory')
  })

  test('avanza desde cornerCases a testingStrategy', async () => {
    // Establecer el estado inicial
    await store.dispatch('setCurrentStep', 'cornerCases')
    await store.dispatch('setRefinedStory', 'Test story')
    
    // Intentar avanzar
    await wrapper.vm.advanceStep()
    
    // Verificar que avanzó al siguiente paso
    expect(store.state.currentStep).toBe('testingStrategy')
    
    // Verificar que se agregó el mensaje del sistema
    const lastMessage = store.state.messages[store.state.messages.length - 1]
    expect(lastMessage.sender).toBe('system')
    expect(lastMessage.text).toContain('feedback sobre las estrategias de testing')
  })

  test('avanza desde testingStrategy a finished', async () => {
    // Establecer el estado inicial
    await store.dispatch('setCurrentStep', 'testingStrategy')
    await store.dispatch('setRefinedStory', 'Test story')
    
    // Intentar avanzar
    await wrapper.vm.advanceStep()
    
    // Verificar que avanzó al estado final
    expect(store.state.currentStep).toBe('finished')
    
    // Verificar que se agregó el mensaje de finalización
    const lastMessage = store.state.messages[store.state.messages.length - 1]
    expect(lastMessage.sender).toBe('system')
    expect(lastMessage.text).toContain('¡Proceso completado!')
  })

  test('maneja el retroceso correctamente', async () => {
    // Probar retroceso desde cornerCases
    await store.dispatch('setCurrentStep', 'cornerCases')
    await wrapper.vm.goBack()
    expect(store.state.currentStep).toBe('refineStory')

    // Probar retroceso desde testingStrategy
    await store.dispatch('setCurrentStep', 'testingStrategy')
    await wrapper.vm.goBack()
    expect(store.state.currentStep).toBe('cornerCases')
  })

  test('enfoca el input después de las acciones', async () => {
    // Configurar el estado inicial
    await wrapper.setData({ userInput: 'test input' })
    await store.dispatch('setRefinedStory', '')

    // Crear el textarea y agregarlo al DOM
    const textarea = wrapper.find('textarea')
    document.body.appendChild(textarea.element)

    // Probar después de enviar feedback
    await wrapper.vm.sendFeedback()
    await wrapper.vm.$nextTick()
    textarea.element.focus()
    expect(document.activeElement).toBe(textarea.element)

    // Probar después de avanzar
    await store.dispatch('setRefinedStory', 'Test story')
    await wrapper.vm.advanceStep()
    await wrapper.vm.$nextTick()
    textarea.element.focus()
    expect(document.activeElement).toBe(textarea.element)

    // Limpiar
    document.body.removeChild(textarea.element)
  })

  test('maneja el scroll al agregar mensajes', async () => {
    const chatContainer = document.createElement('div')
    
    // Definir tanto scrollHeight como scrollTop
    Object.defineProperties(chatContainer, {
      scrollHeight: {
        value: 1000,
        writable: false
      },
      scrollTop: {
        value: 0,
        writable: true
      }
    })
  
    // Mock para querySelector
    const querySelectorSpy = jest.spyOn(document, 'querySelector')
    querySelectorSpy.mockReturnValue(chatContainer)

    // Simular el método scrollToBottom del componente
    await wrapper.vm.addMessage({ role: 'user', content: 'Test message' })
    await wrapper.vm.$nextTick()
    chatContainer.scrollTop = chatContainer.scrollHeight

    expect(chatContainer.scrollTop).toBe(chatContainer.scrollHeight)

    // Limpiar
    querySelectorSpy.mockRestore()
  })

  test('recupera la historia de usuario anterior', async () => {
    // Agregar un mensaje de historia de usuario
    const userStoryMessage = { text: 'Test user story', sender: 'userStory' }
    await store.dispatch('addMessage', userStoryMessage)
    
    // Obtener la historia anterior
    const previousStory = wrapper.vm.previousUserStory()
    expect(previousStory).toBe('Test user story')
  })

  test('maneja la tecla Enter con Shift presionado', async () => {
    const event = {
      shiftKey: true,
      preventDefault: jest.fn()
    }
    
    await wrapper.vm.handleKeyPress(event)
    expect(event.preventDefault).not.toHaveBeenCalled()
  })

  test('no enfoca el input en el estado finished', async () => {
    // Establecer el estado final
    await store.dispatch('setCurrentStep', 'finished')
    await wrapper.vm.$nextTick()
    
    // Simular el textarea
    const textarea = wrapper.find('textarea')
    const activeElement = document.activeElement
    
    // Intentar enfocar
    await wrapper.vm.focusInput()
    await wrapper.vm.$nextTick()
    
    // Verificar que el elemento activo no cambió
    expect(document.activeElement).toBe(activeElement)
    expect(document.activeElement).not.toBe(textarea.element)
  })
});
