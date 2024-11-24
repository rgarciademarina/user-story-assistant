import { mount, shallowMount } from '@vue/test-utils'
import UserStoryForm from '@/components/UserStoryForm.vue'

describe('UserStoryForm.vue', () => {
  let wrapper
  let consoleSpy

  beforeEach(() => {
    consoleSpy = jest.spyOn(console, 'log')
    wrapper = mount(UserStoryForm)
  })

  afterEach(() => {
    consoleSpy.mockRestore()
    wrapper.unmount()
  })

  test('renderiza correctamente', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.findAll('textarea')).toHaveLength(2)
    expect(wrapper.find('button').exists()).toBe(true)
    
    const labels = wrapper.findAll('label')
    expect(labels).toHaveLength(2)
    expect(labels[0].text()).toBe('Historia de Usuario:')
    expect(labels[1].text()).toBe('Feedback (Opcional):')
  })

  test('actualiza los modelos cuando se escriben en los textareas', async () => {
    const [storyTextarea, feedbackTextarea] = wrapper.findAll('textarea')
    
    await storyTextarea.setValue('Test story')
    expect(wrapper.vm.localStory).toBe('Test story')
    
    await feedbackTextarea.setValue('Test feedback')
    expect(wrapper.vm.localFeedback).toBe('Test feedback')
  })

  test('emite el evento submit con la historia y feedback', async () => {
    const testStory = 'Test story'
    const testFeedback = 'Test feedback'
    const [storyTextarea, feedbackTextarea] = wrapper.findAll('textarea')
    const submitButton = wrapper.find('button')

    // Llenar el formulario
    await storyTextarea.setValue(testStory)
    await feedbackTextarea.setValue(testFeedback)

    // Enviar el formulario
    await submitButton.trigger('click')

    // Verificar los logs
    expect(consoleSpy).toHaveBeenCalledWith('UserStoryForm - submitForm - localStory:', testStory)
    expect(consoleSpy).toHaveBeenCalledWith('UserStoryForm - submitForm - localFeedback:', testFeedback)

    // Verificar que se emitió el evento con los valores correctos
    expect(wrapper.emitted('submit')).toBeTruthy()
    expect(wrapper.emitted('submit')[0]).toEqual([{
      story: testStory,
      feedback: testFeedback
    }])
  })

  test('requiere la historia de usuario pero no el feedback', async () => {
    const form = wrapper.find('form')
    const [storyTextarea] = wrapper.findAll('textarea')
    const submitButton = wrapper.find('button')
    
    // Verificar estado inicial
    expect(submitButton.element.disabled).toBe(true)
    expect(wrapper.vm.isValid).toBe(false)
    
    // Intentar enviar sin historia
    wrapper.vm.validateForm()
    await submitButton.trigger('click')
    expect(wrapper.emitted('submit')).toBeFalsy()
    expect(wrapper.vm.showError).toBe(true)
    expect(wrapper.find('.error-message').exists()).toBe(true)
    
    // Enviar con historia válida
    await storyTextarea.setValue('Test story')
    expect(submitButton.element.disabled).toBe(false)
    expect(wrapper.vm.isValid).toBe(true)
    
    await submitButton.trigger('click')
    expect(wrapper.emitted('submit')).toBeTruthy()
    expect(wrapper.emitted('submit')[0]).toEqual([{
      story: 'Test story',
      feedback: ''
    }])
    expect(wrapper.vm.showError).toBe(false)
    expect(wrapper.find('.error-message').exists()).toBe(false)
  })

  test('maneja espacios en blanco en la validación', async () => {
    const [storyTextarea] = wrapper.findAll('textarea')
    const submitButton = wrapper.find('button')
    
    // Intentar con solo espacios en blanco
    await storyTextarea.setValue('   ')
    expect(submitButton.element.disabled).toBe(true)
    expect(wrapper.vm.isValid).toBe(false)
    
    wrapper.vm.validateForm()
    await submitButton.trigger('click')
    expect(wrapper.emitted('submit')).toBeFalsy()
    expect(wrapper.vm.showError).toBe(true)
    
    // Probar con texto válido pero con espacios
    await storyTextarea.setValue('  Test story  ')
    expect(submitButton.element.disabled).toBe(false)
    expect(wrapper.vm.isValid).toBe(true)
    
    await submitButton.trigger('click')
    expect(wrapper.emitted('submit')).toBeTruthy()
    expect(wrapper.emitted('submit')[0]).toEqual([{
      story: 'Test story',
      feedback: ''
    }])
    expect(wrapper.vm.showError).toBe(false)
  })

  test('limpia el mensaje de error al escribir texto válido', async () => {
    const [storyTextarea] = wrapper.findAll('textarea')
    const submitButton = wrapper.find('button')
    
    // Provocar error
    wrapper.vm.validateForm()
    await submitButton.trigger('click')
    expect(wrapper.vm.showError).toBe(true)
    
    // Escribir texto válido
    await storyTextarea.setValue('Test story')
    expect(wrapper.vm.showError).toBe(false)
  })

  test('mantiene el estado de error al escribir texto inválido', async () => {
    const [storyTextarea] = wrapper.findAll('textarea')
    const submitButton = wrapper.find('button')
    
    // Provocar error inicial
    wrapper.vm.validateForm()
    expect(wrapper.vm.showError).toBe(true)
    
    // Escribir texto inválido (solo espacios)
    await storyTextarea.setValue('   ')
    expect(wrapper.vm.showError).toBe(true)
  })

  test('mantiene los datos del formulario después de un envío fallido', async () => {
    const [storyTextarea, feedbackTextarea] = wrapper.findAll('textarea')
    const submitButton = wrapper.find('button')
    
    // Establecer valores iniciales
    await storyTextarea.setValue('   ')
    await feedbackTextarea.setValue('Some feedback')
    
    // Intentar enviar con historia inválida
    wrapper.vm.validateForm()
    await submitButton.trigger('click')
    
    // Verificar que los valores se mantienen
    expect(wrapper.vm.localStory).toBe('   ')
    expect(wrapper.vm.localFeedback).toBe('Some feedback')
  })

  test('limpia el feedback después de un envío exitoso', async () => {
    const [storyTextarea, feedbackTextarea] = wrapper.findAll('textarea')
    const submitButton = wrapper.find('button')
    
    // Establecer valores iniciales
    await storyTextarea.setValue('Valid story')
    await feedbackTextarea.setValue('Some feedback')
    
    // Enviar formulario
    await submitButton.trigger('click')
    
    // Verificar que el feedback se limpió pero la historia se mantiene
    expect(wrapper.vm.localStory).toBe('Valid story')
    expect(wrapper.vm.localFeedback).toBe('')
  })

  test('inicializa el estado usando la función data', () => {
    // Verificar que data es una función
    expect(typeof UserStoryForm.data).toBe('function')
    
    // Obtener el estado inicial
    const state = UserStoryForm.data()
    
    // Verificar que es un objeto con las propiedades correctas
    expect(state).toBeDefined()
    expect(typeof state).toBe('object')
    expect(Object.keys(state).sort()).toEqual(['localStory', 'localFeedback', 'showError'].sort())
    
    // Verificar los valores iniciales
    expect(state.localStory).toBe('')
    expect(state.localFeedback).toBe('')
    expect(state.showError).toBe(false)
  })

  test('el estado inicial se clona correctamente', () => {
    const wrapper = shallowMount(UserStoryForm)
    const state1 = wrapper.vm.$data
    const state2 = UserStoryForm.data()
    
    // Verificar que los objetos son diferentes pero tienen los mismos valores
    expect(state1).not.toBe(state2)
    expect(state1).toEqual(state2)
    
    // Modificar un estado no debe afectar al otro
    state1.localStory = 'modified'
    const state3 = UserStoryForm.data()
    expect(state3.localStory).toBe('')
    
    wrapper.unmount()
  })

  test('el componente mantiene su estado independiente', () => {
    const wrapper1 = shallowMount(UserStoryForm)
    const wrapper2 = shallowMount(UserStoryForm)
    
    // Modificar el estado del primer componente
    wrapper1.vm.localStory = 'modified'
    
    // Verificar que el segundo componente no se ve afectado
    expect(wrapper2.vm.localStory).toBe('')
    
    // Verificar que un nuevo componente tiene el estado inicial correcto
    const wrapper3 = shallowMount(UserStoryForm)
    expect(wrapper3.vm.localStory).toBe('')
    
    wrapper1.unmount()
    wrapper2.unmount()
    wrapper3.unmount()
  })

  test('maneja correctamente el cambio de datos', async () => {
    const [storyTextarea, feedbackTextarea] = wrapper.findAll('textarea')
    
    // Cambiar valores
    await storyTextarea.setValue('New story')
    await feedbackTextarea.setValue('New feedback')
    
    // Verificar cambios en el estado
    expect(wrapper.vm.localStory).toBe('New story')
    expect(wrapper.vm.localFeedback).toBe('New feedback')
  })

  test('valida correctamente historias con diferentes contenidos', () => {
    // Historia vacía
    wrapper.vm.localStory = ''
    expect(wrapper.vm.isValid).toBe(false)

    // Historia con solo espacios
    wrapper.vm.localStory = '   '
    expect(wrapper.vm.isValid).toBe(false)

    // Historia con espacios al inicio y final
    wrapper.vm.localStory = '  valid story  '
    expect(wrapper.vm.isValid).toBe(true)

    // Historia normal
    wrapper.vm.localStory = 'valid story'
    expect(wrapper.vm.isValid).toBe(true)
  })

  test('maneja correctamente el ciclo de vida del componente', async () => {
    // Crear una instancia con shallowMount
    const wrapper = shallowMount(UserStoryForm, {
      attachTo: document.createElement('div') // Para probar el ciclo de vida completo
    })
    
    // Verificar estado inicial
    expect(wrapper.vm.localStory).toBe('')
    expect(wrapper.vm.localFeedback).toBe('')
    expect(wrapper.vm.showError).toBe(false)
    
    // Modificar valores
    await wrapper.setData({
      localStory: 'test story',
      localFeedback: 'test feedback'
    })
    
    // Verificar que los valores se actualizaron
    expect(wrapper.vm.localStory).toBe('test story')
    expect(wrapper.vm.localFeedback).toBe('test feedback')
    
    // Desmontar
    wrapper.unmount()
    
    // Crear una nueva instancia
    const newWrapper = shallowMount(UserStoryForm)
    
    // Verificar que el estado se reinició
    expect(newWrapper.vm.localStory).toBe('')
    expect(newWrapper.vm.localFeedback).toBe('')
    expect(newWrapper.vm.showError).toBe(false)
    
    // Limpiar
    newWrapper.unmount()
  })

  test('inicializa el estado usando la función data', () => {
    // Verificar que data es una función
    expect(typeof UserStoryForm.data).toBe('function')
    
    // Crear un contexto mock para this
    const context = {}
    const state = UserStoryForm.data.call(context)
    
    // Verificar que es un objeto con las propiedades correctas
    expect(state).toBeDefined()
    expect(typeof state).toBe('object')
    expect(Object.keys(state)).toEqual(['localStory', 'localFeedback', 'showError'])
    
    // Verificar los valores iniciales
    expect(state.localStory).toBe('')
    expect(state.localFeedback).toBe('')
    expect(state.showError).toBe(false)
    
    // Verificar que cada llamada retorna un nuevo objeto
    const state2 = UserStoryForm.data.call(context)
    expect(state2).not.toBe(state)
    expect(state2).toEqual(state)
  })

  test('el componente tiene un nombre definido', () => {
    expect(UserStoryForm.name).toBe('UserStoryForm')
  })

  test('data retorna un nuevo objeto cada vez', () => {
    const wrapper = shallowMount(UserStoryForm)
    const vm1 = wrapper.vm
    const vm2 = shallowMount(UserStoryForm).vm
    
    // Verificar que los objetos son diferentes pero tienen los mismos valores
    expect(vm1.$data).not.toBe(vm2.$data)
    expect(vm1.$data).toEqual(vm2.$data)
    
    // Modificar un objeto no debe afectar al otro
    vm1.localStory = 'modified'
    expect(vm2.localStory).toBe('')
    
    wrapper.unmount()
  })

  test('data es una función que retorna un objeto', () => {
    expect(typeof UserStoryForm.data).toBe('function')
    expect(UserStoryForm.data.length).toBe(0)
    expect(Object.prototype.toString.call(UserStoryForm.data())).toBe('[object Object]')
  })
})
