import { Routes } from '@angular/router';
import { LayoutRuleCreateComponent } from './layout-rule-create/layout-rule-create.component';
import { LayoutRuleListComponent } from './layout-rule-list/layout-rule-list.component';

export const LayoutRoutes: Routes = [
  {
    path: '',
    children: [
      {
        path: 'create',
        component: LayoutRuleCreateComponent,
      },
      {
        path: 'list',
        component: LayoutRuleListComponent,
      },
    ],
  },
];
