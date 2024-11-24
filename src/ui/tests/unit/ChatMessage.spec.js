import { mount } from '@vue/test-utils'
import ChatMessage from '@/components/ChatMessage.vue'

describe('ChatMessage.vue', () => {
  let consoleWarnSpy;

  beforeEach(() => {
    // Silenciar todos los warnings
    consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});
  });

  afterEach(() => {
    consoleWarnSpy.mockRestore();
  });

  const createWrapper = (message) => {
    return mount(ChatMessage, {
      props: {
        message
      }
    })
  }

  test('renderiza correctamente un mensaje de usuario', () => {
    const message = {
      sender: 'user',
      text: 'Mensaje de prueba'
    }
    const wrapper = createWrapper(message)

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.classes()).toContain('message')
    expect(wrapper.classes()).toContain('user-message')
    expect(wrapper.text()).toContain('Mensaje de prueba')
  })

  test('renderiza correctamente un mensaje del asistente', () => {
    const message = {
      sender: 'assistant',
      text: 'Respuesta de prueba'
    }
    const wrapper = createWrapper(message)

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.classes()).toContain('message')
    expect(wrapper.classes()).toContain('assistant-message')
    expect(wrapper.text()).toContain('Respuesta de prueba')
  })

  test('renderiza correctamente markdown', () => {
    const message = {
      sender: 'assistant',
      text: '**texto en negrita** y *texto en cursiva*'
    }
    const wrapper = createWrapper(message)

    const renderedContent = wrapper.find('.message-content').html()
    expect(renderedContent).toContain('<strong>texto en negrita</strong>')
    expect(renderedContent).toContain('<em>texto en cursiva</em>')
  })

  test('maneja correctamente texto vacío', () => {
    const message = {
      sender: 'user',
      text: ''
    }
    const wrapper = createWrapper(message)
    expect(wrapper.find('.message-content').text()).toBe('')
  })

  test('valida las props requeridas', () => {
    const consoleWarn = jest.spyOn(console, 'warn').mockImplementation(() => {})
    
    // Intentar montar sin props debería emitir warning
    const wrapper1 = mount(ChatMessage)
    expect(wrapper1.classes()).toContain('assistant-message') // Valor por defecto
    expect(consoleWarn).toHaveBeenCalledWith(
      '[Vue warn]: Missing required prop: "message"',
      '\n',
      ' at <Anonymous',
      'ref="VTU_COMPONENT"',
      '>',
      '\n',
      ' at <VTUROOT>'
    )
    consoleWarn.mockClear()

    // Props incompletas deberían emitir warning
    const wrapper2 = mount(ChatMessage, {
      props: {
        message: {}
      }
    })
    expect(wrapper2.classes()).toContain('assistant-message')
    expect(consoleWarn).toHaveBeenCalled()
    consoleWarn.mockClear()

    // Props con tipos incorrectos deberían emitir warning
    const wrapper3 = mount(ChatMessage, {
      props: {
        message: {
          sender: 123,
          text: 456
        }
      }
    })
    expect(wrapper3.classes()).toContain('assistant-message')
    expect(consoleWarn).toHaveBeenCalled()
    consoleWarn.mockClear()

    // Props correctas no deberían emitir warning
    const wrapper4 = mount(ChatMessage, {
      props: {
        message: {
          sender: 'user',
          text: 'test'
        }
      }
    })
    expect(wrapper4.classes()).toContain('user-message')
    expect(consoleWarn).not.toHaveBeenCalled()

    consoleWarn.mockRestore()
  })

  it('valida las props requeridas', () => {
    const wrapper = mount(ChatMessage);
    expect(consoleWarnSpy).toHaveBeenCalled();
  });

  it('valida el formato de la prop message', () => {
    const wrapper = mount(ChatMessage, {
      props: {
        message: {
          role: 'user',
          content: 'Test message'
        }
      }
    });
    expect(consoleWarnSpy).toHaveBeenCalled();
  });

  it('renderiza correctamente con props válidas', () => {
    const wrapper = mount(ChatMessage, {
      props: {
        message: {
          text: 'Test message',
          sender: 'user'
        }
      }
    });
    expect(consoleWarnSpy).not.toHaveBeenCalled();
    expect(wrapper.classes()).toContain('user-message');
  });

  test('sanitiza HTML en markdown', () => {
    const message = {
      sender: 'assistant',
      text: '<script>alert("malicioso")</script><p>Contenido seguro</p>'
    }
    const wrapper = createWrapper(message)

    const renderedContent = wrapper.find('.message-content').html()
    expect(renderedContent).toContain('<p>Contenido seguro</p>')
  })
})
