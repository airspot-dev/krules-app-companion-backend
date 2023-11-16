// This file can be replaced during build by using the `fileReplacements` array.
// `ng build` replaces `environment.ts` with `environment.prod.ts`.
// The list of file replacements can be found in `angular.json`.

const ServerBase = 'http://localhost:1234';
const ApiPrefix = '/api';
declare var require: any;
const config = require('../firebase_config.json');

export const environment = {
  firebase: config,
  production: false,
  elementPerPage: [10, 25, 50],
  server: {
    basePath: ServerBase,
    apiPrefix: ApiPrefix,
    apiBase: `${ServerBase}${ApiPrefix}`,
  },
};

/*
 * For easier debugging in development mode, you can import the following file
 * to ignore zone related error stack frames such as `zone.run`, `zoneDelegate.invokeTask`.
 *
 * This import should be commented out in production mode because it will have a negative impact
 * on performance if an error is thrown.
 */
// import 'zone.js/plugins/zone-error';  // Included with Angular CLI.
