const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:5000', // Flask запускается в этом же контейнере
    defaultCommandTimeout: 10000,
    requestTimeout: 10000,
    responseTimeout: 10000,
    viewportWidth: 1280,
    viewportHeight: 720,
    chromeWebSecurity: false,
    supportFile: false,
    setupNodeEvents(on, config) {},
  },
});
