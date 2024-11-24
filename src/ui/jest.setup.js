// Suprimir warning de punycode
const originalWarn = console.warn;
console.warn = (...args) => {
  if (args[0] && args[0].includes('punycode')) {
    return;
  }
  originalWarn.apply(console, args);
};
