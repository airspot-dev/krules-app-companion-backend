import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LayoutRuleListComponent } from './layout-rule-list/layout-rule-list.component';
import { LayoutRuleCreateComponent } from './layout-rule-create/layout-rule-create.component';
import { RouterModule } from '@angular/router';
import { LayoutRoutes } from './layout.routes';
import { MaterialModule } from 'src/app/material.module';
import { FlexLayoutModule } from '@angular/flex-layout';
import { SharedModule } from 'src/app/shared/shared.module';

@NgModule({
  declarations: [LayoutRuleListComponent, LayoutRuleCreateComponent],
  imports: [
    CommonModule,
    FlexLayoutModule,
    MaterialModule,
    SharedModule,
    RouterModule.forChild(LayoutRoutes),
  ],
})
export class LayoutModule {}
