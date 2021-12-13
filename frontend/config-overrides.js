/* config-overrides.js */

module.exports = {
  // Extend/override the dev server configuration used by CRA
  // See: https://github.com/timarney/react-app-rewired#extended-configuration-options
  devServer: function (configFunction) {
    return function (proxy, allowedHost) {
      // Create the default config by calling configFunction with the proxy/allowedHost parameters
      // Default config: https://github.com/facebook/create-react-app/blob/master/packages/react-scripts/config/webpackDevServer.config.js
      const config = configFunction(proxy, allowedHost);
      // Set loose allow origin header to prevent CORS issues
      config.headers = {
        "Cross-Origin-Embedder-Policy": "require-corp",
        "Cross-Origin-Opener-Policy": "same-origin",
      };
      return config;
    };
  },
};
