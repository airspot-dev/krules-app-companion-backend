import { Routes } from '@angular/router';
import { DataViewComponent } from './data-view/data-view.component';
import { EventSourceComponent } from './event-source/event-source.component';
import { GroupEditComponent } from './group-edit/group-edit.component';

export const DataRoutes: Routes = [
  {
    path: '',
    children: [
      {
        path: 'view',
        component: DataViewComponent,
      },
      {
        path: 'group/:group_id/item/:id',
        component: EventSourceComponent,
      },
      {
        path: 'group/edit/:group_id',
        component: GroupEditComponent,
      },
    ],
  },
];
