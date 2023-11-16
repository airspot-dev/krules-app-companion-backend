import { INTEGRATION_ID } from './intergration';

export enum OUTPUT_ENUM {
  SET_PROPERTY = 'set_property',
  NOTIFY = 'notify',
}

export interface IOutput {
  id: OUTPUT_ENUM;
  integrations: INTEGRATION_ID[];
}
