import { mount } from '@vue/test-utils'
import FeedbackForm from '@/components/FeedbackForm.vue'

describe('FeedbackForm.vue', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(FeedbackForm)
  })

  afterEach(() => {
    wrapper.unmount()
  })

  test('renderiza correctamente', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('textarea').exists()).toBe(true)
    expect(wrapper.find('button').exists()).toBe(true)
    expect(wrapper.find('label').text()).toBe('Proporciona Feedback (Opcional):')
  })

  test('actualiza el modelo cuando se escribe en el textarea', async () => {
    const textarea = wrapper.find('textarea')
    await textarea.setValue('Test feedback')
    expect(wrapper.vm.feedback).toBe('Test feedback')
  })

  test('emite el evento submit con el feedback y limpia el campo', async () => {
    const testFeedback = 'Test feedback'
    await wrapper.setData({ feedback: testFeedback })
    
    await wrapper.find('button').trigger('click')
    
    // Verificar que se emitió el evento con el valor correcto
    expect(wrapper.emitted('submit')).toBeTruthy()
    expect(wrapper.emitted('submit')[0]).toEqual([testFeedback])
    
    // Verificar que se limpió el campo
    expect(wrapper.vm.feedback).toBe('')
  })

  test('el botón está habilitado incluso sin feedback', () => {
    const button = wrapper.find('button')
    expect(button.element.disabled).toBeFalsy()
  })
})
