import { Routes } from '@angular/router';
import { TestTableComponent } from './test-table/test-table.component';

export const PlaygroundRoutes: Routes = [
  {
    path: '',
    children: [
      {
        path: 'table',
        component: TestTableComponent,
      },
    ],
  },
];
