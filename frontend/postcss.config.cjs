const { default: tailwindConfig } = require("./tailwind.config.js");

module.exports = {
  plugins: {
    '@tailwindcss/postcss': {},
    autoprefixer: {},
  },
};
