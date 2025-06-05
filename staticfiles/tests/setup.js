/**
 * Настройка окружения для Jest тестов
 */

import '@testing-library/jest-dom';

// Мокируем Vue 3
global.Vue = {
  createApp: jest.fn(() => ({
    data: jest.fn(() => ({})),
    mounted: jest.fn(),
    methods: {},
    mount: jest.fn()
  }))
};

// Мокируем axios
global.axios = {
  defaults: {
    headers: {
      common: {}
    }
  },
  get: jest.fn(() => Promise.resolve({ data: {} })),
  post: jest.fn(() => Promise.resolve({ data: {} })),
  put: jest.fn(() => Promise.resolve({ data: {} })),
  delete: jest.fn(() => Promise.resolve({ data: {} }))
};

// Мокируем Bootstrap модалы
global.bootstrap = {
  Modal: jest.fn().mockImplementation(() => ({
    show: jest.fn(),
    hide: jest.fn()
  })),
  Modal: {
    getInstance: jest.fn(() => ({
      hide: jest.fn()
    }))
  }
};

// Мокируем localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Мокируем window.location
delete window.location;
window.location = {
  hostname: 'localhost',
  port: '3000',
  href: 'http://localhost:3000'
};

// Мокируем setTimeout и clearTimeout
global.setTimeout = jest.fn((fn) => fn());
global.clearTimeout = jest.fn();

// Очистка моков перед каждым тестом
beforeEach(() => {
  jest.clearAllMocks();
  localStorageMock.getItem.mockClear();
  localStorageMock.setItem.mockClear();
  localStorageMock.removeItem.mockClear();
  localStorageMock.clear.mockClear();
}); 