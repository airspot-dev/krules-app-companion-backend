import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChannelListComponent } from './channel-list/channel-list.component';
import { RouterModule } from '@angular/router';
import { MaterialModule } from 'src/app/material.module';
import { SharedModule } from 'src/app/shared/shared.module';
import { ChannelRoutes } from './channel.routes';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ChannelCreateComponent } from './channel-create/channel-create.component';

@NgModule({
  declarations: [ChannelListComponent, ChannelCreateComponent],
  imports: [
    CommonModule,
    MaterialModule,
    SharedModule,
    ReactiveFormsModule,
    RouterModule.forChild(ChannelRoutes),
  ],
})
export class ChannelModule {}
