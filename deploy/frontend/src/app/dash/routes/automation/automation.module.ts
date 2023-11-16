import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AutomationCreateComponent } from './automation-create/automation-create.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { AutomationRoutes } from './automation.routes';
import { FlexLayoutModule } from '@angular/flex-layout';
import { MaterialModule } from 'src/app/material.module';
import { AutomationListComponent } from './automation-list/automation-list.component';
import { SharedModule } from 'src/app/shared/shared.module';
import { DeleteAutomationDialogComponent } from './automation-list/delete-automation-dialog/delete-automation-dialog.component';
@NgModule({
  declarations: [
    AutomationCreateComponent,
    AutomationListComponent,
    DeleteAutomationDialogComponent,
  ],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MaterialModule,
    FlexLayoutModule,
    SharedModule,
    RouterModule.forChild(AutomationRoutes),
  ],
})
export class AutomationModule {}
