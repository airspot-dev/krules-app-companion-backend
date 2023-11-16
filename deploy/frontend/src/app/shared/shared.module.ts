import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DashButtonComponent } from './components/dash-button/dash-button.component';
import { FlexLayoutModule } from '@angular/flex-layout';
import { MaterialModule } from '../material.module';
import { MaterialElevationDirective } from './directives/material-elevation.directive';
import { DataBackButtonComponent } from './components/data-back-button/data-back-button.component';
import { RouterModule } from '@angular/router';
import { OkSnackbarComponent } from './components/ok-snackbar/ok-snackbar.component';
import { ErrorSnackbarComponent } from './components/error-snackbar/error-snackbar.component';
import { ColumnDateFilterComponent } from './components/column-date-filter/column-date-filter.component';
import { KeyValueFilterComponent } from './components/key-value-filter/key-value-filter.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { BrowserModule } from '@angular/platform-browser';
import { TableFixedDirective } from './directives/table-fixed.directive';
import { TableCellComponent } from './components/table-cell/table-cell.component';
import { ButtonCliboardComponent } from './components/button-cliboard/button-cliboard.component';
import { TableCellDialogComponent } from './components/table-cell/table-cell-dialog/table-cell-dialog.component';
import { MonacoEditorModule } from 'ngx-monaco-editor-v2';
import { ChannelCardComponent } from './components/channel-card/channel-card.component';
import { TableResizeDirective } from './directives/table-resize.directive';
import { DeleteChannelDialogComponent } from './components/channel-card/delete-channel-dialog/delete-channel-dialog.component';

@NgModule({
  declarations: [
    DashButtonComponent,
    MaterialElevationDirective,
    DataBackButtonComponent,
    OkSnackbarComponent,
    ErrorSnackbarComponent,
    ColumnDateFilterComponent,
    KeyValueFilterComponent,
    TableFixedDirective,
    TableCellComponent,
    ButtonCliboardComponent,
    TableCellDialogComponent,
    ChannelCardComponent,
    TableResizeDirective,
    DeleteChannelDialogComponent,
  ],
  exports: [
    DashButtonComponent,
    DataBackButtonComponent,
    MaterialElevationDirective,
    KeyValueFilterComponent,
    ColumnDateFilterComponent,
    ButtonCliboardComponent,
    TableFixedDirective,
    ChannelCardComponent,
    TableCellComponent,
    TableResizeDirective,
  ],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MaterialModule,
    FlexLayoutModule,
    RouterModule,
    FormsModule,
    MonacoEditorModule,
  ],
})
export class SharedModule {}
