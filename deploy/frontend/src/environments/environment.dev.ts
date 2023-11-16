const ServerBase = 'http://localhost:123';
const ApiPrefix = '/api';

export const environment = {
  production: false,
  envName: 'dev',
  server: {
    basePath: ServerBase,
    apiPrefix: ApiPrefix,
    apiBase: `${ServerBase}${ApiPrefix}`,
  },
};
