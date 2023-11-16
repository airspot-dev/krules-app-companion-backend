import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DataViewComponent } from './data-view/data-view.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { DataRoutes } from './data.routes';
import { FlexLayoutModule } from '@angular/flex-layout';
import { MaterialModule } from 'src/app/material.module';
import { GroupTableComponent } from './data-view/group-table/group-table.component';
import { EventSourceComponent } from './event-source/event-source.component';
import { GroupEditComponent } from './group-edit/group-edit.component';
import { DeleteGroupDialogComponent } from './data-view/delete-group-dialog/delete-group-dialog.component';
import { SharedModule } from 'src/app/shared/shared.module';
import { EventSourcingEditComponent } from './event-sourcing-edit/event-sourcing-edit.component';
import { DeleteEntityDialogComponent } from './data-view/delete-entity-dialog/delete-entity-dialog.component';

@NgModule({
  declarations: [
    DataViewComponent,
    GroupTableComponent,
    EventSourceComponent,
    GroupEditComponent,
    DeleteGroupDialogComponent,
    EventSourcingEditComponent,
    DeleteEntityDialogComponent,
  ],
  imports: [
    CommonModule,
    FlexLayoutModule,
    MaterialModule,
    FormsModule,
    SharedModule,
    ReactiveFormsModule,
    RouterModule.forChild(DataRoutes),
  ],
})
export class DataModule {}
