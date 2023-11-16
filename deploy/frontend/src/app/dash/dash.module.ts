import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MaterialModule } from '../material.module';
import { FormsModule } from '@angular/forms';
import { DashRoutingModule } from './dash.routes';
import { DashboardComponent } from './layout/dashboard/dashboard.component';
import { HeaderComponent } from './layout/header/header.component';
import { MonacoEditorModule } from 'ngx-monaco-editor-v2';

@NgModule({
  declarations: [DashboardComponent, HeaderComponent],
  imports: [CommonModule, MaterialModule, FormsModule, DashRoutingModule],
})
export class DashModule {}
