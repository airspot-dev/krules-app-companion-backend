import { IOutput } from './output';
import { II18n } from './_helpers/i18n/i18n';

export enum APP_EVENT_TYPE {
  ON_CHANGE = 'on_change',
}

export interface IAppEventParam {
  parameter: string;
  description: II18n;
}

export interface IAppEvent {
  type: APP_EVENT_TYPE;
  params: IAppEventParam[];
}

export interface IAutomation {
  id?: string;
  name: string;
  entityFields: string[];
  entityFieldsRaw?: string;
  event: string;
  position: number;
  running: boolean;
  channels: string[];
  groupMatch: string;
  createdAt?: Date;
  updatedAt?: Date;
  createdBy?: string | null;
  updatedBy?: string | null;
}
