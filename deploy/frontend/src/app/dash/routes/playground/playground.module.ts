import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TestTableComponent } from './test-table/test-table.component';
import { PlaygroundRoutes } from './playground.routes';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { MaterialModule } from 'src/app/material.module';
import { SharedModule } from 'src/app/shared/shared.module';

@NgModule({
  declarations: [TestTableComponent],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    SharedModule,
    MaterialModule,
    RouterModule.forChild(PlaygroundRoutes),
  ],
})
export class PlaygroundModule {}
