import { Routes } from '@angular/router';
import { ChannelListComponent } from './channel-list/channel-list.component';
import { ChannelCreateComponent } from './channel-create/channel-create.component';

export const ChannelRoutes: Routes = [
  {
    path: '',
    children: [
      {
        path: 'create',
        component: ChannelCreateComponent,
      },
      {
        path: 'update/:id',
        component: ChannelCreateComponent,
      },
      {
        path: 'list',
        component: ChannelListComponent,
      },
    ],
  },
];
