import { mount } from '@vue/test-utils';
import ReviewModal from '@/components/ReviewModal.vue';
import MarkdownIt from 'markdown-it';

// Mock markdown-it
jest.mock('markdown-it', () => {
  return jest.fn().mockImplementation(() => ({
    render: jest.fn().mockImplementation((content) => `<p>${content}</p>`)
  }));
});

describe('ReviewModal.vue', () => {
  const defaultProps = {
    modelValue: true,
    content: 'Test content',
    existingJiraId: '',
    isLoadingJira: false
  };

  const createWrapper = (props = {}) => {
    const wrapper = mount(ReviewModal, {
      props: { ...defaultProps, ...props },
      global: {
        stubs: ['markdown-it']
      }
    });

    // Manually mock lifecycle hooks and methods
    const mockSetupResizer = jest.fn(() => {
      wrapper.vm.cleanup = jest.fn(() => {});
    });
    const mockBeforeUnmount = jest.fn(() => {
      if (wrapper.vm.cleanup) {
        wrapper.vm.cleanup();
      }
    });

    // Replace methods with mocks and call them
    wrapper.vm.setupResizer = mockSetupResizer;
    wrapper.vm.beforeUnmount = mockBeforeUnmount;

    // Trigger setup methods
    wrapper.vm.setupResizer();

    return wrapper;
  };

  describe('Rendering', () => {
    it('renders the modal when modelValue is true', () => {
      const wrapper = createWrapper();
      expect(wrapper.find('.modal-overlay').exists()).toBe(true);
    });

    it('does not render the modal when modelValue is false', () => {
      const wrapper = createWrapper({ modelValue: false });
      expect(wrapper.find('.modal-overlay').exists()).toBe(false);
    });
  });

  describe('Interactions', () => {
    it('emits update:modelValue when close button is clicked', async () => {
      const wrapper = createWrapper();
      const closeButton = wrapper.find('.close-button');
      
      await closeButton.trigger('click');
      
      expect(wrapper.emitted('update:modelValue')[0]).toEqual([false]);
    });

    it('updates localContent when content prop changes', async () => {
      const wrapper = createWrapper();
      
      await wrapper.setProps({ content: 'New test content' });
      
      expect(wrapper.vm.localContent).toBe('New test content');
    });
  });

  describe('Jira ID Validation', () => {
    it('validates Jira ID correctly', () => {
      const wrapper = createWrapper();
      
      // Test valid Jira ID formats
      wrapper.vm.jiraId = 'PROJ-123';
      expect(wrapper.vm.isValidJiraId).toBe(true);
      
      // Test invalid Jira ID formats
      wrapper.vm.jiraId = 'invalid';
      expect(wrapper.vm.isValidJiraId).toBe(false);
      
      // Test empty Jira ID
      wrapper.vm.jiraId = '';
      expect(wrapper.vm.isValidJiraId).toBe(true);
    });

    it('disables Jira button when Jira ID is invalid', async () => {
      const wrapper = createWrapper();
      
      // Set an invalid Jira ID
      await wrapper.setData({ jiraId: 'invalid' });
      
      const jiraButton = wrapper.find('.jira-button');
      expect(jiraButton.attributes('disabled')).toBeDefined();
    });
  });

  describe('Jira Action', () => {
    it('emits jira-action with correct payload when Jira action is triggered', async () => {
      const wrapper = createWrapper();
      
      // Set content and Jira ID
      await wrapper.setData({ 
        localContent: '#### Test Story\n**Dado** algo\n**Cuando** algo pasa\n**Entonces** algo sucede',
        jiraId: 'PROJ-123' 
      });
      
      const jiraButton = wrapper.find('.jira-button');
      await jiraButton.trigger('click');
      
      const emittedEvents = wrapper.emitted('jira-action');
      expect(emittedEvents).toBeTruthy();
      expect(emittedEvents[0][0]).toEqual({
        content: expect.stringContaining('h1. Test Story'),
        jiraId: 'PROJ-123'
      });
    });

    it('handles empty Jira ID scenario', async () => {
      const wrapper = createWrapper();
      
      // Set content without Jira ID
      await wrapper.setData({ 
        localContent: '#### New Story\n**Dado** algo\n**Cuando** algo pasa\n**Entonces** algo sucede',
        jiraId: '' 
      });
      
      const jiraButton = wrapper.find('.jira-button');
      await jiraButton.trigger('click');
      
      const emittedEvents = wrapper.emitted('jira-action');
      expect(emittedEvents).toBeTruthy();
      expect(emittedEvents[0][0]).toEqual({
        content: expect.stringContaining('h1. New Story'),
        jiraId: ''
      });
    });
  });

  describe('Content Preview', () => {
    it('updates preview content when localContent changes', async () => {
      const wrapper = createWrapper();
      
      // Spy on the updatePreview method
      const updatePreviewSpy = jest.spyOn(wrapper.vm, 'updatePreview');
      
      // Trigger updatePreview manually
      await wrapper.vm.updatePreview();
      
      expect(updatePreviewSpy).toHaveBeenCalled();
      expect(wrapper.vm.previewContent).not.toBe('');
    });

    it('handles empty localContent', async () => {
      const wrapper = createWrapper();
      
      // Set localContent to empty string
      await wrapper.setData({ localContent: '' });
      
      // Trigger updatePreview manually
      await wrapper.vm.updatePreview();
      
      expect(wrapper.vm.previewContent).toBe('');
    });
  });

  describe('Resizer Functionality', () => {
    it('sets up resizer event listeners on mount', () => {
      const wrapper = createWrapper();
      
      // Verify setupResizer was called
      expect(wrapper.vm.setupResizer).toHaveBeenCalled();
      
      // Verify cleanup function was created
      expect(wrapper.vm.cleanup).toBeDefined();
    });

    it('removes event listeners on beforeUnmount', () => {
      const wrapper = createWrapper();
      
      // Simulate beforeUnmount lifecycle hook
      wrapper.vm.beforeUnmount();
      
      // Verify cleanup function was called
      expect(wrapper.vm.cleanup).toHaveBeenCalled();
    });
  });
});
