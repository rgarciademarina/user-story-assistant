import { mount } from '@vue/test-utils'
import ChatMessage from '@/components/ChatMessage.vue'
import markdownIt from 'markdown-it'

// Mock markdown-it
jest.mock('markdown-it', () => {
  return jest.fn().mockImplementation(() => ({
    render: jest.fn().mockImplementation((content) => {
      // Simular renderizado de Gherkin con keywords
      return content
        .replace(/^\*\*(Dado|Cuando|Entonces|Y)\*\*/gm, '<strong class="gherkin-keyword">$1</strong>')
        .replace(/^(Dado|Cuando|Entonces|Y)\s/gm, '<strong class="gherkin-keyword">$1</strong> ')
        .replace(/^(Característica|Escenario|Esquema del escenario):\s/gm, '<strong class="gherkin-keyword">$1:</strong> ');
    })
  }));
});

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

  describe('Message Class', () => {
    it('returns user-message class when sender is user', () => {
      const wrapper = createWrapper({
        sender: 'user',
        text: 'Test message'
      });
      expect(wrapper.classes()).toContain('user-message');
    });

    it('returns assistant-message class when sender is not user', () => {
      const wrapper = createWrapper({
        sender: 'assistant',
        text: 'Test message'
      });
      expect(wrapper.classes()).toContain('assistant-message');
    });

    it('returns assistant-message class when sender is undefined', () => {
      const wrapper = createWrapper({
        text: 'Test message'
      });
      expect(wrapper.classes()).toContain('assistant-message');
    });
  });

  describe('Rendered Message', () => {
    it('handles invalid message prop with missing sender', () => {
      const wrapper = createWrapper({
        text: 'Test message'
      });
      expect(wrapper.exists()).toBe(true);
    });

    it('handles undefined text', () => {
      expect(() => {
        mount(ChatMessage, { props: { message: { text: undefined } } });
      }).toThrow('Text must be a string');
    });

    it('handles non-string text', () => {
      expect(() => {
        mount(ChatMessage, { props: { message: { text: 123 } } });
      }).toThrow('Text must be a string');
    });

    it('renders Gherkin block with multiple steps', () => {
      const gherkinText = `**Dado** un contexto
**Cuando** ocurre un evento
**Entonces** sucede algo
**Y** además pasa esto`;

      const wrapper = createWrapper({
        sender: 'assistant',
        text: gherkinText
      });

      const renderedContent = wrapper.find('.message-content').html();
      expect(renderedContent).toMatch(/Dado/i);
      expect(renderedContent).toMatch(/Cuando/i);
      expect(renderedContent).toMatch(/Entonces/i);
      expect(renderedContent).toMatch(/Y/i);
    });

    it('renders mixed text with Gherkin blocks', () => {
      const mixedText = `Texto inicial
**Dado** un contexto
Texto intermedio
**Cuando** ocurre un evento
Texto final`;

      const wrapper = createWrapper({
        sender: 'assistant',
        text: mixedText
      });

      const renderedContent = wrapper.find('.message-content').html();
      expect(renderedContent).toContain('Texto inicial');
      expect(renderedContent).toMatch(/Dado/i);
      expect(renderedContent).toContain('Texto intermedio');
      expect(renderedContent).toMatch(/Cuando/i);
      expect(renderedContent).toContain('Texto final');
    });

    it('renders multiple Gherkin blocks', () => {
      const multiBlockText = `**Dado** primer escenario
**Cuando** algo pasa
**Entonces** resultado esperado

**Dado** segundo escenario
**Cuando** otra cosa pasa
**Entonces** otro resultado`;

      const wrapper = createWrapper({
        sender: 'assistant',
        text: multiBlockText
      });

      const renderedContent = wrapper.find('.message-content').html();
      expect(renderedContent).toMatch(/Dado.*primer escenario/si);
      expect(renderedContent).toMatch(/Cuando.*algo pasa/si);
      expect(renderedContent).toMatch(/Entonces.*resultado esperado/si);
      expect(renderedContent).toMatch(/Dado.*segundo escenario/si);
      expect(renderedContent).toMatch(/Cuando.*otra cosa pasa/si);
      expect(renderedContent).toMatch(/Entonces.*otro resultado/si);
    });

    it('handles Gherkin block with trailing Y step', () => {
      const trailingYText = `**Dado** un contexto
**Cuando** ocurre un evento
**Entonces** sucede algo
**Y** además pasa esto`;

      const wrapper = createWrapper({
        sender: 'assistant',
        text: trailingYText
      });

      const renderedContent = wrapper.find('.message-content').html();
      expect(renderedContent).toMatch(/Y.*además pasa esto/si);
    });

    it('handles mixed Gherkin and non-Gherkin text with complex scenarios', () => {
      const complexText = `Texto inicial
**Dado** primer contexto
Texto intermedio
**Cuando** ocurre un evento
**Y** un paso adicional
Texto final
**Entonces** resultado esperado`;

      const wrapper = createWrapper({
        sender: 'assistant',
        text: complexText
      });

      const renderedContent = wrapper.find('.message-content').html();
      expect(renderedContent).toMatch(/Texto inicial/i);
      expect(renderedContent).toMatch(/Dado.*primer contexto/si);
      expect(renderedContent).toMatch(/Texto intermedio/i);
      expect(renderedContent).toMatch(/Cuando.*ocurre un evento/si);
      expect(renderedContent).toMatch(/Y.*un paso adicional/si);
      expect(renderedContent).toMatch(/Texto final/i);
      expect(renderedContent).toMatch(/Entonces.*resultado esperado/si);
    });

    it('handles Gherkin block with non-standard line breaks', () => {
      const irregularText = `**Dado** un contexto
**Cuando** ocurre un evento

**Entonces** resultado esperado

**Y** paso adicional`;

      const wrapper = createWrapper({
        sender: 'assistant',
        text: irregularText
      });

      const renderedContent = wrapper.find('.message-content').html();
      expect(renderedContent).toMatch(/Dado.*un contexto/si);
      expect(renderedContent).toMatch(/Cuando.*ocurre un evento/si);
      expect(renderedContent).toMatch(/Entonces.*resultado esperado/si);
      expect(renderedContent).toMatch(/Y.*paso adicional/si);
    });

    it('handles text with no Gherkin keywords', () => {
      const plainText = `Este es un texto normal
Sin ninguna palabra clave de Gherkin
Solo texto plano`;

      const wrapper = createWrapper({
        sender: 'assistant',
        text: plainText
      });

      const renderedContent = wrapper.find('.message-content').html();
      expect(renderedContent).toContain('Este es un texto normal');
      expect(renderedContent).toContain('Sin ninguna palabra clave de Gherkin');
      expect(renderedContent).toContain('Solo texto plano');
    });

    it('handles Gherkin block with empty lines', () => {
      const textWithEmptyLines = `**Dado** un contexto

**Cuando** ocurre un evento

**Entonces** resultado esperado

**Y** paso adicional`;

      const wrapper = createWrapper({
        sender: 'assistant',
        text: textWithEmptyLines
      });

      const renderedContent = wrapper.find('.message-content').html();
      expect(renderedContent).toMatch(/Dado.*un contexto/si);
      expect(renderedContent).toMatch(/Cuando.*ocurre un evento/si);
      expect(renderedContent).toMatch(/Entonces.*resultado esperado/si);
      expect(renderedContent).toMatch(/Y.*paso adicional/si);
    });

    it('handles Gherkin block ending with non-Gherkin text', () => {
      const textWithTrailingNonGherkin = `**Dado** un contexto
**Cuando** ocurre un evento
**Entonces** resultado esperado
Texto adicional`;

      const wrapper = createWrapper({
        sender: 'assistant',
        text: textWithTrailingNonGherkin
      });

      const renderedContent = wrapper.find('.message-content').html();
      expect(renderedContent).toMatch(/Dado.*un contexto/si);
      expect(renderedContent).toMatch(/Cuando.*ocurre un evento/si);
      expect(renderedContent).toMatch(/Entonces.*resultado esperado/si);
      expect(renderedContent).toContain('Texto adicional');
    });

    it('handles Gherkin block at the end of text', () => {
      const wrapper = mount(ChatMessage, {
        props: {
          message: { text: '**Dado** un contexto\n**Cuando** ocurre un evento\n**Entonces** resultado final' }
        }
      });
      expect(wrapper.text()).toContain('Dado un contexto');
      expect(wrapper.text()).toContain('Cuando ocurre un evento');
      expect(wrapper.text()).toContain('Entonces resultado final');
    });

    it('handles multiple Gherkin blocks with non-Gherkin text', () => {
      const wrapper = mount(ChatMessage, {
        props: {
          message: { 
            text: '**Dado** un contexto inicial\n\nTexto intermedio\n\n**Cuando** ocurre un evento\n**Entonces** resultado final' 
          }
        }
      });
      expect(wrapper.text()).toContain('Dado un contexto inicial');
      expect(wrapper.text()).toContain('Texto intermedio');
      expect(wrapper.text()).toContain('Cuando ocurre un evento');
      expect(wrapper.text()).toContain('Entonces resultado final');
    });

    it('handles empty lines array', () => {
      const wrapper = mount(ChatMessage, {
        props: {
          message: { text: '' }
        }
      });
      expect(wrapper.text()).toBe('');
    });

    it('handles Gherkin block with single line and no continuation', () => {
      const singleLineGherkin = `**Dado** un contexto único`;

      const wrapper = createWrapper({
        sender: 'assistant',
        text: singleLineGherkin
      });

      const renderedContent = wrapper.find('.message-content').html();
      expect(renderedContent).toMatch(/Dado.*un contexto único/si);
    });

    it('handles mixed text with Gherkin block at the very end', () => {
      const mixedTextEndingWithGherkin = `Texto inicial
Más texto
**Dado** un contexto final`;

      const wrapper = createWrapper({
        sender: 'assistant',
        text: mixedTextEndingWithGherkin
      });

      const renderedContent = wrapper.find('.message-content').html();
      expect(renderedContent).toContain('Texto inicial');
      expect(renderedContent).toContain('Más texto');
      expect(renderedContent).toMatch(/Dado.*un contexto final/si);
    });

    it('handles text with Gherkin block in the middle', () => {
      const textWithMiddleGherkin = `Texto antes
**Dado** un contexto medio
Texto después`;

      const wrapper = createWrapper({
        sender: 'assistant',
        text: textWithMiddleGherkin
      });

      const renderedContent = wrapper.find('.message-content').html();
      expect(renderedContent).toContain('Texto antes');
      expect(renderedContent).toMatch(/Dado.*un contexto medio/si);
      expect(renderedContent).toContain('Texto después');
    });
  });
});
