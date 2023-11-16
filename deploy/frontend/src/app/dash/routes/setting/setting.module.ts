import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IntegrationComponent } from './integration/integration.component';
import { MaterialModule } from 'src/app/material.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { SettingRoutes } from './setting.routes';
import { UserSettingComponent } from './user-setting/user-setting.component';
import { TokenCreateComponent } from './token-create/token-create.component';
import { TokenListComponent } from './token-list/token-list.component';
import { SharedModule } from 'src/app/shared/shared.module';
import { CreateApiKeyDialogComponent } from './token-create/create-api-key-dialog/create-api-key-dialog.component';
import { DeleteApiKeyDialogComponent } from './token-list/delete-api-key-dialog/delete-api-key-dialog.component';
import { HelpApiDialogComponent } from './token-list/help-api-dialog/help-api-dialog.component';

@NgModule({
  declarations: [
    IntegrationComponent,
    UserSettingComponent,
    TokenCreateComponent,
    TokenListComponent,
    CreateApiKeyDialogComponent,
    DeleteApiKeyDialogComponent,
    HelpApiDialogComponent,
  ],
  imports: [
    CommonModule,
    FormsModule,
    SharedModule,
    ReactiveFormsModule,
    MaterialModule,
    RouterModule.forChild(SettingRoutes),
  ],
})
export class SettingModule {}
