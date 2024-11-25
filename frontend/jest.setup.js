// Suppress punycode warning
const originalWarn = console.warn;
console.warn = (...args) => {
  if (args[0] && args[0].includes('punycode')) {
    return;
  }
  originalWarn.apply(console, args);
};

// Silenciar warnings de Vue durante las pruebas
const warn = console.warn;
console.warn = function (message, ...args) {
  if (message.toString().includes('[Vue warn]')) {
    return;
  }
  warn.apply(console, [message, ...args]);
};

// Setup global test environment
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});
