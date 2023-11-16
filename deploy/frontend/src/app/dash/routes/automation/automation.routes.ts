import { Routes } from '@angular/router';
import { AutomationCreateComponent } from './automation-create/automation-create.component';
import { AutomationListComponent } from './automation-list/automation-list.component';

export const AutomationRoutes: Routes = [
  {
    path: '',
    children: [
      {
        path: 'create',
        component: AutomationCreateComponent,
      },
      {
        path: 'update/:id',
        component: AutomationCreateComponent,
      },
      {
        path: 'list',
        component: AutomationListComponent,
      },
    ],
  },
];
