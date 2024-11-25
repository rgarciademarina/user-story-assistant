import { mount } from '@vue/test-utils';
import App from '@/App.vue';
import RefinementFlow from '@/components/RefinementFlow.vue';

// Mock RefinementFlow component to avoid testing its internals
jest.mock('@/components/RefinementFlow.vue', () => ({
  name: 'RefinementFlow',
  render: () => null
}));

describe('App.vue', () => {
  it('renderiza el componente correctamente', () => {
    const wrapper = mount(App);
    expect(wrapper.exists()).toBe(true);
    expect(wrapper.find('#app').exists()).toBe(true);
  });

  it('incluye el componente RefinementFlow', () => {
    const wrapper = mount(App);
    const refinementFlow = wrapper.findComponent(RefinementFlow);
    expect(refinementFlow.exists()).toBe(true);
  });

  it('tiene la estructura correcta del DOM', () => {
    const wrapper = mount(App);
    const appElement = wrapper.find('#app');
    
    // Verificar que el elemento #app existe y contiene RefinementFlow
    expect(appElement.exists()).toBe(true);
    expect(appElement.findComponent(RefinementFlow).exists()).toBe(true);
  });
});
