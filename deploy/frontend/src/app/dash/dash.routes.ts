import { NgModule } from '@angular/core';
import { canActivate, redirectUnauthorizedTo } from '@angular/fire/auth-guard';
import { RouterModule, Routes } from '@angular/router';
import { DashboardComponent } from './layout/dashboard/dashboard.component';
const redirectUnauthorizedToLogin = () => redirectUnauthorizedTo(['login']);

const routes: Routes = [
  {
    path: '',
    component: DashboardComponent,
    children: [
      {
        path: 'data',
        loadChildren: () =>
          import('./routes/data/data.module').then(
            (module) => module.DataModule
          ),
        ...canActivate(redirectUnauthorizedToLogin),
      },
      {
        path: 'playground',
        loadChildren: () =>
          import('./routes/playground/playground.module').then(
            (module) => module.PlaygroundModule
          ),
        ...canActivate(redirectUnauthorizedToLogin),
      },
      {
        path: 'layout',
        loadChildren: () =>
          import('./routes/layout/layout.module').then(
            (module) => module.LayoutModule
          ),
        ...canActivate(redirectUnauthorizedToLogin),
      },
      {
        path: 'setting',
        loadChildren: () =>
          import('./routes/setting/setting.module').then(
            (module) => module.SettingModule
          ),
        ...canActivate(redirectUnauthorizedToLogin),
      },
      {
        path: 'automation',
        loadChildren: () =>
          import('./routes/automation/automation.module').then(
            (module) => module.AutomationModule
          ),
        ...canActivate(redirectUnauthorizedToLogin),
      },
      {
        path: 'channel',
        loadChildren: () =>
          import('./routes/channel/channel.module').then(
            (module) => module.ChannelModule
          ),
        ...canActivate(redirectUnauthorizedToLogin),
      },
    ],
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class DashRoutingModule {}
