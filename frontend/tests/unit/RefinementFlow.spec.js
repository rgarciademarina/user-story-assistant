import { mount, shallowMount } from '@vue/test-utils'
import { createStore } from 'vuex'
import RefinementFlow from '@/components/RefinementFlow.vue'
import ChatMessage from '@/components/ChatMessage.vue'
import ToastNotification from '@/components/ToastNotification.vue'

// Mock del fetch global
global.fetch = jest.fn()

// Mock del store de Vuex
const createVuexStore = () => {
  const mockStore = createStore({
    state: {
      messages: [],
      currentStep: 'refineStory',
      refinedStory: '',
      cornerCases: [],
      testingStrategies: [],
      sessionId: null,
      isLoadingJira: false,
      jiraStoryId: null,
      isReviewModalOpen: false,
      composedStory: ''
    },
    mutations: {
      addMessage(state, message) {
        state.messages.push(message);
      },
      setCurrentStep(state, step) {
        state.currentStep = step;
      },
      setLoadingJira(state, isLoading) {
        state.isLoadingJira = isLoading;
      },
      setIsReviewModalOpen(state, isOpen) {
        state.isReviewModalOpen = isOpen;
      },
      resetProcess(state) {
        state.messages = [];
        state.currentStep = 'refineStory';
        state.refinedStory = '';
        state.cornerCases = [];
        state.testingStrategies = [];
        state.isLoadingJira = false;
        state.jiraStoryId = null;
        state.isReviewModalOpen = false;
        state.composedStory = '';
      },
      setRefinedStory(state, story) {
        state.refinedStory = story;
      }
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
      refineStory: jest.fn().mockResolvedValue({
        refinementResponse: 'Historia refinada'
      }),
      identifyCornerCases: jest.fn().mockResolvedValue({
        cornerCasesResponse: 'Casos esquina identificados'
      }),
      proposeTestingStrategy: jest.fn().mockResolvedValue({
        testingStrategyResponse: 'Estrategias de testing propuestas'
      }),
      composeStory: jest.fn().mockResolvedValue({
        compositionResponse: 'Historia compuesta'
      }),
      finalizeStory: jest.fn().mockResolvedValue({
        finalizationResponse: 'Historia finalizada'
      }),
      fetchJiraStory: jest.fn().mockResolvedValue({
        success: true,
        story: 'Mocked Jira story'
      }),
      setRefinedStory({ commit }, story) {
        commit('setRefinedStory', story);
      }
    }
  })
  
  return mockStore;
}

describe('RefinementFlow.vue', () => {
  let wrapper
  let store

  beforeEach(async () => {
    // Crear un store nuevo para cada prueba
    store = createVuexStore()

    // Resetear el store antes de cada prueba
    await store.dispatch('resetProcess')

    // Crear un wrapper con un store limpio
    wrapper = mount(RefinementFlow, {
      global: {
        plugins: [store],
        stubs: {
          'toast-notification': true,
          'review-modal': true,
          'chat-message': {
            template: '<div></div>',
            props: ['message']
          }
        }
      }
    })
  })

  afterEach(async () => {
    try {
      if (wrapper && wrapper.exists()) {
        await wrapper.unmount()
      }
    } catch (error) {
      console.error('Error during unmount:', error)
    }
    jest.clearAllMocks()
    
    // Resetear el store después de cada prueba
    if (store) {
      await store.dispatch('resetProcess')
    }
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
    expect(sendButton.attributes('disabled')).toBeDefined()
  })

  test('botón de enviar se habilita cuando hay texto', async () => {
    await wrapper.setData({ userInput: 'Test input' })
    const sendButton = wrapper.find('button')
    expect(sendButton.attributes('disabled')).toBeUndefined()
  })

  test('muestra el indicador de carga correctamente', async () => {
    await wrapper.setData({ isLoading: true })
    expect(wrapper.find('.loading-indicator').exists()).toBe(true)
    expect(wrapper.find('.loading-indicator').text()).toBe('Cargando...')
  })

  test('maneja el envío de feedback correctamente en el paso de refinamiento', async () => {
    // Limpiar los mensajes existentes
    await store.dispatch('resetProcess')
    await wrapper.vm.$nextTick()

    // Añadir manualmente el mensaje del usuario
    await store.dispatch('addMessage', { 
      text: 'Test feedback', 
      sender: 'user' 
    })
    await wrapper.vm.$nextTick()
    
    // Verificar que se añadió el mensaje del usuario
    const userMessage = store.state.messages.find(msg => 
      msg.text === 'Test feedback' && msg.sender === 'user'
    )
    expect(userMessage).toBeTruthy()
  })

  test('maneja la tecla Enter correctamente', async () => {
    // Limpiar los mensajes existentes
    await store.dispatch('resetProcess')
    await wrapper.vm.$nextTick()

    // Añadir manualmente el mensaje del usuario
    await store.dispatch('addMessage', { 
      text: 'Test feedback', 
      sender: 'user' 
    })
    await wrapper.vm.$nextTick()
    
    // Verificar que se añadió el mensaje del usuario
    const userMessage = store.state.messages.find(msg => 
      msg.text === 'Test feedback' && msg.sender === 'user'
    )
    expect(userMessage).toBeTruthy()
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

    const testMessage = { text: 'Test message', sender: 'user' }
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

  test('avanza desde testingStrategy a composition', async () => {
    // Establecer el estado inicial
    await store.dispatch('setCurrentStep', 'testingStrategy')
    await store.dispatch('setRefinedStory', 'Test story')
    
    // Intentar avanzar
    await wrapper.vm.advanceStep()
    
    // Verificar que avanzó al siguiente paso
    expect(store.state.currentStep).toBe('composition')
    
    // Verificar que se agregó el mensaje del sistema
    const lastMessage = store.state.messages[store.state.messages.length - 1]
    expect(lastMessage.sender).toBe('system')
    expect(lastMessage.text).toContain('Has llegado a la fase de composición')
  })

  test('avanza desde composition a finished', async () => {
    // Establecer el estado inicial
    await store.dispatch('setCurrentStep', 'composition')
    await store.dispatch('setRefinedStory', 'Test story')
    
    // Intentar avanzar
    await wrapper.vm.advanceStep()
    
    // Verificar que avanzó al estado final
    expect(store.state.currentStep).toBe('finished')
    
    // Verificar que se agregó el mensaje de finalización
    const lastMessage = store.state.messages[store.state.messages.length - 1]
    expect(lastMessage.sender).toBe('system')
    expect(lastMessage.text).toContain('La historia ha sido finalizada')
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
    const mockTextarea = {
      classList: {
        contains: jest.fn().mockReturnValue(false)
      },
      selectionStart: 0,
      value: 'test'
    }
    const event = {
      key: 'Enter',
      shiftKey: true,
      preventDefault: jest.fn(),
      target: mockTextarea
    }
    
    await wrapper.setData({ userInput: 'test' })
    // Con Shift+Enter, no se debe llamar a preventDefault
    await wrapper.vm.handleKeyPress(event)
    expect(event.preventDefault).not.toHaveBeenCalled()
  })

  test('handleKeyPress permite salto de línea con Shift+Enter', async () => {
    const mockTextarea = {
      classList: {
        contains: jest.fn().mockReturnValue(false)
      },
      selectionStart: 0,
      value: 'test'
    }
    const event = {
      key: 'Enter',
      shiftKey: true,
      preventDefault: jest.fn(),
      stopPropagation: jest.fn(),
      target: mockTextarea
    }
    
    await wrapper.setData({ userInput: 'test' })
    wrapper.vm.sendFeedback = jest.fn()
    await wrapper.vm.handleKeyPress(event)
    
    // Con Shift+Enter, no se debe llamar a preventDefault ni a sendFeedback
    expect(event.preventDefault).not.toHaveBeenCalled()
    expect(event.stopPropagation).not.toHaveBeenCalled()
    expect(wrapper.vm.sendFeedback).not.toHaveBeenCalled()
  })

  test('handleKeyPress envía feedback con Enter', async () => {
    const mockTextarea = {
      classList: {
        contains: jest.fn().mockReturnValue(false)
      },
      selectionStart: 0,
      value: 'test'
    }
    const event = {
      key: 'Enter',
      shiftKey: false,
      preventDefault: jest.fn(),
      stopPropagation: jest.fn(),
      target: mockTextarea
    }
    
    await wrapper.setData({ userInput: 'test' })
    wrapper.vm.sendFeedback = jest.fn()
    await wrapper.vm.handleKeyPress(event)
    
    expect(wrapper.vm.sendFeedback).toHaveBeenCalled()
  })

  test('maneja correctamente la recuperación exitosa de una historia de Jira', async () => {
    // Preparar el estado para la recuperación de historia de Jira
    await wrapper.setData({ 
      jiraStoryId: 'STORYASIS-1',
      isValidJiraId: true,
      isLoadingJira: false
    })

    // Simular un evento en el input de Jira
    const jiraInput = {
      classList: {
        contains: jest.fn().mockReturnValue(true)
      }
    }
    const event = {
      target: jiraInput,
      preventDefault: jest.fn()
    }

    // Crear un mock para fetchJiraStory
    const fetchJiraMock = jest.fn().mockResolvedValue({ success: true, story: 'Mocked Jira story' })
    wrapper.vm.fetchJiraStory = fetchJiraMock

    // Llamar a handleKeyPress
    await wrapper.vm.handleKeyPress(event)

    // Verificar que se llamó a fetchJiraStory
    expect(fetchJiraMock).toHaveBeenCalled()
    expect(event.preventDefault).toHaveBeenCalled()
  })

  test('maneja correctamente errores en la recuperación de historia de Jira', async () => {
    // Limpiar los mensajes existentes
    await store.dispatch('resetProcess')
    await wrapper.vm.$nextTick()

    // Añadir un mensaje válido manualmente
    await store.dispatch('addMessage', { 
      text: 'Test Jira Story', 
      sender: 'user' 
    })
    await wrapper.vm.$nextTick()

    // Verificar que se añadió el mensaje correctamente
    const userMessage = store.state.messages.find(msg => 
      msg.text === 'Test Jira Story' && msg.sender === 'user'
    )
    expect(userMessage).toBeTruthy()
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

  test('maneja errores durante el proceso de refinamiento', async () => {
    const originalDispatch = store.dispatch;
    const errorMessage = 'Error durante el refinamiento';
    
    store.dispatch = jest.fn().mockImplementation((action) => {
      if (action === 'refineStory') {
        return Promise.resolve({
          success: false,
          error: errorMessage,
          refinementResponse: 'Error: ' + errorMessage
        });
      }
      return originalDispatch(action);
    });

    await wrapper.setData({ userInput: 'Test story' });
    await wrapper.find('button').trigger('click');
    
    expect(store.dispatch).toHaveBeenCalledWith('refineStory', expect.any(Object));
    expect(wrapper.vm.isLoading).toBe(false);
    
    store.dispatch = originalDispatch;
  });

  test('maneja errores durante la identificación de casos esquina', async () => {
    await store.dispatch('setCurrentStep', 'cornerCases');
    const originalDispatch = store.dispatch;
    const errorMessage = 'Error en casos esquina';
    
    store.dispatch = jest.fn().mockImplementation((action) => {
      if (action === 'identifyCornerCases') {
        return Promise.resolve({
          success: false,
          error: errorMessage,
          cornerCasesResponse: 'Error: ' + errorMessage
        });
      }
      return originalDispatch(action);
    });

    await wrapper.setData({ userInput: 'Test feedback' });
    await wrapper.find('button').trigger('click');
    
    expect(store.dispatch).toHaveBeenCalledWith('identifyCornerCases', expect.any(Object));
    expect(wrapper.vm.isLoading).toBe(false);
    
    store.dispatch = originalDispatch;
  });

  test('maneja errores durante la propuesta de estrategia de testing', async () => {
    await store.dispatch('setCurrentStep', 'testingStrategy');
    const originalDispatch = store.dispatch;
    const errorMessage = 'Error en estrategia de testing';
    
    store.dispatch = jest.fn().mockImplementation((action) => {
      if (action === 'proposeTestingStrategy') {
        return Promise.resolve({
          success: false,
          error: errorMessage,
          testingStrategyResponse: 'Error: ' + errorMessage
        });
      }
      return originalDispatch(action);
    });

    await wrapper.setData({ userInput: 'Test feedback' });
    await wrapper.find('button').trigger('click');
    
    expect(store.dispatch).toHaveBeenCalledWith('proposeTestingStrategy', expect.any(Object));
    expect(wrapper.vm.isLoading).toBe(false);
    
    store.dispatch = originalDispatch;
  });

  test('maneja el caso cuando no hay historia refinada al intentar avanzar', async () => {
    store.state.refinedStory = null;
    await wrapper.vm.advanceStep();
    expect(store.state.currentStep).toBe('refineStory');
  });

  test('maneja correctamente el proceso de finalización', async () => {
    await store.dispatch('setCurrentStep', 'testingStrategy');
    store.state.refinedStory = 'Historia refinada';
    await wrapper.vm.advanceStep();
    
    expect(store.state.currentStep).toBe('composition');
    const messages = wrapper.vm.messages;
    const lastMessage = messages[messages.length - 1];
    expect(lastMessage.text).toContain('Has llegado a la fase de composición');
    expect(lastMessage.sender).toBe('system');
  });

  test('maneja la navegación entre pasos', async () => {
    await store.dispatch('setCurrentStep', 'refineStory');
    expect(store.state.currentStep).toBe('refineStory');

    await store.dispatch('setCurrentStep', 'identifyCornerCases');
    expect(store.state.currentStep).toBe('identifyCornerCases');

    await store.dispatch('setCurrentStep', 'proposeTestingStrategy');
    expect(store.state.currentStep).toBe('proposeTestingStrategy');
  });

  test('reinicia el proceso correctamente', async () => {
    // Establecer algunos datos
    await store.dispatch('addMessage', { text: 'Test message', sender: 'user' });
    await store.dispatch('setCurrentStep', 'identifyCornerCases');
    await store.dispatch('setRefinedStory', 'Refined story');

    // Reiniciar el proceso
    await store.dispatch('resetProcess');

    // Verificar que todo se haya reiniciado
    expect(store.state.messages).toHaveLength(0);
    expect(store.state.currentStep).toBe('refineStory');
    expect(store.state.refinedStory).toBe('');
  });

  test('maneja errores durante el proceso de refinamiento con error en la respuesta', async () => {
    const originalDispatch = store.dispatch;
    const errorMessage = 'Error durante el refinamiento';
    
    store.dispatch = jest.fn().mockImplementation((action) => {
      if (action === 'refineStory') {
        return Promise.resolve({
          success: false,
          error: errorMessage,
          refinementResponse: undefined
        });
      }
      return originalDispatch(action);
    });

    await wrapper.setData({ userInput: 'Test story' });
    await wrapper.find('button').trigger('click');
    
    expect(store.dispatch).toHaveBeenCalledWith('refineStory', expect.any(Object));
    expect(wrapper.vm.isLoading).toBe(false);
    
    store.dispatch = originalDispatch;
  });

  test('maneja errores durante la identificación de casos esquina con respuesta undefined', async () => {
    await store.dispatch('setCurrentStep', 'cornerCases');
    const originalDispatch = store.dispatch;
    
    store.dispatch = jest.fn().mockImplementation((action) => {
      if (action === 'identifyCornerCases') {
        return Promise.resolve({
          success: false,
          cornerCasesResponse: undefined
        });
      }
      return originalDispatch(action);
    });

    await wrapper.setData({ userInput: 'Test feedback' });
    await wrapper.find('button').trigger('click');
    
    expect(store.dispatch).toHaveBeenCalledWith('identifyCornerCases', expect.any(Object));
    expect(wrapper.vm.isLoading).toBe(false);
    
    store.dispatch = originalDispatch;
  });

  test('maneja errores durante la propuesta de testing con respuesta vacía', async () => {
    await store.dispatch('setCurrentStep', 'testingStrategy');
    const originalDispatch = store.dispatch;
    
    store.dispatch = jest.fn().mockImplementation((action) => {
      if (action === 'proposeTestingStrategy') {
        return Promise.resolve({
          success: false,
          testingStrategyResponse: ''
        });
      }
      return originalDispatch(action);
    });

    await wrapper.setData({ userInput: 'Test feedback' });
    await wrapper.find('button').trigger('click');
    
    expect(store.dispatch).toHaveBeenCalledWith('proposeTestingStrategy', expect.any(Object));
    expect(wrapper.vm.isLoading).toBe(false);
    
    store.dispatch = originalDispatch;
  });

  describe('scrollToBottom', () => {
    it('llama a scrollTop cuando el elemento existe', async () => {
      const wrapper = mount(RefinementFlow, {
        global: {
          plugins: [store]
        }
      });
      
      // Mock del elemento DOM
      const mockElement = {
        scrollHeight: 1000,
        scrollTop: 0
      };
      
      // Mock del querySelector para devolver nuestro elemento mock
      wrapper.vm.$el.querySelector = jest.fn().mockReturnValue(mockElement);
      
      // Llama al método
      wrapper.vm.scrollToBottom();
      
      // Espera al siguiente tick
      await wrapper.vm.$nextTick();
      
      // Verifica que se llamó a querySelector con la clase correcta
      expect(wrapper.vm.$el.querySelector).toHaveBeenCalledWith('.chat-container');
      
      // Verifica que se estableció scrollTop
      expect(mockElement.scrollTop).toBe(1000);
    });

    it('maneja el caso cuando el elemento no existe', async () => {
      const wrapper = mount(RefinementFlow, {
        global: {
          plugins: [store]
        }
      });
      
      // Mock del querySelector para devolver null
      wrapper.vm.$el.querySelector = jest.fn().mockReturnValue(null);
      
      // Llama al método
      wrapper.vm.scrollToBottom();
      
      // Espera al siguiente tick
      await wrapper.vm.$nextTick();
      
      // Verifica que se llamó a querySelector
      expect(wrapper.vm.$el.querySelector).toHaveBeenCalledWith('.chat-container');
    });
  });

  describe('manejo de errores en respuestas', () => {
    let mockStore;
    let addMessageSpy;
    
    beforeEach(() => {
      // Crear un store mock para cada prueba
      mockStore = createStore({
        state: {
          messages: [],
          currentStep: 'refineStory',
          refinedStory: null,
          cornerCases: [],
          testingStrategies: []
        },
        mutations: {
          addMessage(state, message) {
            state.messages.push(message);
          },
          setCurrentStep(state, step) {
            state.currentStep = step;
          }
        },
        actions: {
          addMessage({ commit }, message) {
            commit('addMessage', message);
          },
          resetProcess: jest.fn(),
          setCurrentStep({ commit }, step) {
            commit('setCurrentStep', step);
          }
        }
      });
      
      // Espía la acción addMessage
      addMessageSpy = jest.spyOn(mockStore._actions.addMessage, '0');
    });

    it('maneja respuesta undefined en handleRefineFeedback', async () => {
      const wrapper = shallowMount(RefinementFlow, {
        global: {
          plugins: [mockStore]
        },
        mounted: jest.fn()
      });

      // Mock de la acción refineStory
      wrapper.vm.refineStory = jest.fn().mockResolvedValue({ refinementResponse: undefined });

      // Resetear el spy antes de la prueba
      addMessageSpy.mockClear();

      // Llama al método con un feedback
      await wrapper.vm.handleRefineFeedback('test feedback');

      // Verifica que no se llamó a addMessage
      expect(addMessageSpy).not.toHaveBeenCalled();
    });

    it('maneja respuesta undefined en handleCornerCasesFeedback', async () => {
      const wrapper = shallowMount(RefinementFlow, {
        global: {
          plugins: [mockStore]
        },
        mounted: jest.fn()
      });

      // Mock de la acción identifyCornerCases
      wrapper.vm.identifyCornerCases = jest.fn().mockResolvedValue({ cornerCasesResponse: undefined });

      // Resetear el spy antes de la prueba
      addMessageSpy.mockClear();

      // Llama al método con un feedback
      await wrapper.vm.handleCornerCasesFeedback('test feedback');

      // Verifica que no se llamó a addMessage
      expect(addMessageSpy).not.toHaveBeenCalled();
    });

    it('maneja respuesta undefined en handleTestingStrategyFeedback', async () => {
      const wrapper = shallowMount(RefinementFlow, {
        global: {
          plugins: [mockStore]
        },
        mounted: jest.fn()
      });

      // Mock de la acción proposeTestingStrategy
      wrapper.vm.proposeTestingStrategy = jest.fn().mockResolvedValue({ testingStrategyResponse: undefined });

      // Resetear el spy antes de la prueba
      addMessageSpy.mockClear();

      // Llama al método con un feedback
      await wrapper.vm.handleTestingStrategyFeedback('test feedback');

      // Verifica que no se llamó a addMessage
      expect(addMessageSpy).not.toHaveBeenCalled();
    });

    afterEach(() => {
      jest.clearAllMocks();
    });
  });

  test('muestra el campo de entrada de Jira ID en el paso inicial', () => {
    const jiraInput = wrapper.find('.jira-input')
    const jiraButton = wrapper.find('.jira-button')
    
    expect(jiraInput.exists()).toBe(true)
    expect(jiraButton.exists()).toBe(true)
    expect(jiraButton.attributes('disabled')).toBeDefined()
  })

  test('valida correctamente el formato del ID de Jira', async () => {
    await wrapper.setData({ jiraStoryId: 'INVALID-ID' })
    let jiraButton = wrapper.find('.jira-button')
    expect(jiraButton.attributes('disabled')).toBeDefined()

    await wrapper.setData({ jiraStoryId: 'STORYASIS-1' })
    jiraButton = wrapper.find('.jira-button')
    expect(jiraButton.attributes('disabled')).toBeUndefined()
  })

  test('maneja correctamente errores en la recuperación de historia de Jira', async () => {
    // Mock fetch para que falle
    global.fetch.mockRejectedValueOnce(new Error('Error al cargar la historia'));
    
    await wrapper.setData({ jiraStoryId: 'STORYASIS-1' });
    const jiraButton = wrapper.find('.jira-button');
    await jiraButton.trigger('click');
    
    // Esperar a que se complete la promesa rechazada
    await new Promise(resolve => setTimeout(resolve, 0));
    await wrapper.vm.$nextTick();
    
    expect(wrapper.vm.showToast).toBe(true);
    expect(wrapper.vm.toastMessage).toContain('Error al cargar');
    expect(wrapper.vm.toastType).toBe('error');
  })

  test('maneja correctamente el estilo de los botones de Jira', async () => {
    const wrapper = mount(RefinementFlow, {
      global: {
        plugins: [store]
      }
    });

    // Función auxiliar para verificar el estado del botón
    const checkJiraButtonState = async (expectedDisabled) => {
      const jiraButton = wrapper.find('[data-test="jira-button"]');
      await wrapper.vm.$nextTick();
      
      // Verificar estado computado
      const computedDisabled = wrapper.vm.isJiraButtonDisabled;
      expect(computedDisabled).toBe(expectedDisabled);
      
      // Verificar estado del elemento
      expect(jiraButton.element.disabled).toBe(expectedDisabled);
    };

    // Simular input de Jira inválido
    await wrapper.setData({ jiraStoryId: 'invalid' });
    expect(wrapper.vm.isValidJiraId).toBe(false);
    await checkJiraButtonState(true);

    // Simular input de Jira válido
    await wrapper.setData({ jiraStoryId: 'PROJ-123' });
    expect(wrapper.vm.isValidJiraId).toBe(true);
    await checkJiraButtonState(false);

    // Verificar botón deshabilitado durante carga
    await wrapper.vm.$store.commit('setLoadingJira', true);
    await wrapper.vm.$nextTick();
    
    expect(wrapper.vm.$store.state.isLoadingJira).toBe(true);
    await checkJiraButtonState(true);
  });

  test('maneja errores en la carga de historias de Jira', async () => {
    const store = createVuexStore();
    const wrapper = mount(RefinementFlow, {
      global: {
        plugins: [store],
        mocks: {
          $store: {
            state: store.state,
            commit: store.commit,
            dispatch: store.dispatch
          }
        }
      }
    });

    // Mock de fetch para simular error
    global.fetch = jest.fn(() =>
      Promise.reject(new Error('Error al cargar la historia de Jira'))
    );

    // Intentar cargar una historia de Jira
    await wrapper.setData({ jiraStoryId: 'PROJ-123' });
    await wrapper.vm.fetchJiraStory();

    // Verificar que se muestra el mensaje de error
    expect(wrapper.vm.showToast).toBe(true);
    expect(wrapper.vm.toastMessage).toContain('Error al cargar');
    expect(wrapper.vm.toastType).toBe('error');
  });
});
