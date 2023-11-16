import { II18n } from './_helpers/i18n/i18n';

export enum INTEGRATION_ID {
  WEBHOOK = 'webhook',
  SLACK = 'slack',
  PUB_SUB = 'pub_sub',
}

export enum INTEGRATION_PARAM_TYPE {
  STRING = 'string',
  INT = 'integer',
  FLOAT = 'float',
  BOOLEAN = 'boolean',
  DATE = 'date',
}

export interface IIntegrationParam {
  type: INTEGRATION_PARAM_TYPE;
  required: boolean;
  code: string;
  name: II18n;
}

export interface IIntegration {
  id: INTEGRATION_ID;
  icon: string;
  name: II18n;
  params: IIntegrationParam[];
}

export interface IChannel {
  id: string;
  slug: string;
  image: string;
  imageNeg: string;
  type: string;
  name: string;
  previewKey: string;
  preview: string;
}

export const Integrations = [
  {
    code: 'pub_sub',
    name: 'Pub/Sub',
    icon: 'share',
    image: '/assets/img/pub-sub.svg',
    imageNeg: '/assets/img/pub-sub-neg.svg',
    preview: 'topic',
    form: [
      {
        code: 'topic',
        name: 'Topic',
        placeholder: 'Write your Pub/Sub topic',

        type: 'text',
        required: true,
      },
    ],
  },
  {
    code: 'webhook',
    name: 'Webhook',
    icon: 'webhook',
    image: '/assets/img/webhook.svg',
    imageNeg: '/assets/img/webhook-neg.svg',
    preview: 'url',
    form: [
      {
        code: 'url',
        name: 'URL',
        placeholder: 'https://example.com',
        type: 'url',
        required: true,
      },
      {
        code: 'headers',
        name: 'Headers',
        counter: 1,
        placeholder_key: 'Authorization',
        placeholder_value: 'Bearer: xyz123=',
        type: 'multi-key-value',
      },
    ],
  },
];
