import { Routes } from '@angular/router';
import { IntegrationComponent } from './integration/integration.component';
import { UserSettingComponent } from './user-setting/user-setting.component';
import { TokenCreateComponent } from './token-create/token-create.component';
import { TokenListComponent } from './token-list/token-list.component';

export const SettingRoutes: Routes = [
  {
    path: '',
    children: [
      {
        path: 'integration',
        component: IntegrationComponent,
      },
      {
        path: 'token/create',
        component: TokenCreateComponent,
      },
      {
        path: 'token/edit/:id',
        component: TokenCreateComponent,
      },
      {
        path: 'token/list',
        component: TokenListComponent,
      },
      {
        path: '',
        component: UserSettingComponent,
      },
    ],
  },
];
