const ServerBase = '';
const ApiPrefix = '/api/v1';

export const environment = {
  production: true,
  envName: 'production',
  server: {
    basePath: ServerBase,
    apiPrefix: ApiPrefix,
    apiBase: `${ServerBase}${ApiPrefix}`,
  },
};
