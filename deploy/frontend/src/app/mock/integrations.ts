import {
  IIntegration,
  INTEGRATION_ID,
  INTEGRATION_PARAM_TYPE,
} from '../models/intergration';

export const integrations: IIntegration[] = [
  {
    id: INTEGRATION_ID.WEBHOOK,
    icon: 'https://cdn.icon-icons.com/icons2/2248/PNG/512/webhook_icon_138018.png',
    name: {
      it: 'Webhook',
      en: 'Webhook',
    },
    params: [
      {
        type: INTEGRATION_PARAM_TYPE.STRING,
        required: true,
        code: 'token',
        name: {
          it: 'Token Api',
          en: 'Api token',
        },
      },
      {
        type: INTEGRATION_PARAM_TYPE.STRING,
        required: true,
        code: 'channel',
        name: {
          it: 'Canale',
          en: 'channel',
        },
      },
    ],
  },
  {
    id: INTEGRATION_ID.SLACK,
    icon: 'https://cdn-icons-png.flaticon.com/512/3800/3800024.png',
    name: {
      it: 'Slack',
      en: 'Slack',
    },
    params: [
      {
        type: INTEGRATION_PARAM_TYPE.STRING,
        required: true,
        code: 'channel_name',
        name: {
          it: 'Nome',
          en: 'Name',
        },
      },
      {
        type: INTEGRATION_PARAM_TYPE.STRING,
        required: true,
        code: 'channel_url',
        name: {
          it: 'Url webhook',
          en: 'Webhook url',
        },
      },
    ],
  },
];
