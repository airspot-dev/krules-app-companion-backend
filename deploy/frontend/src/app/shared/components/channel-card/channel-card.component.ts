import { Component, Input } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { IChannel } from 'src/app/models/intergration';
import { ChannelService } from 'src/app/service/channel/channel.service';
import { SnackbarService } from 'src/app/service/snackbar/snackbar.service';
import { DeleteChannelDialogComponent } from './delete-channel-dialog/delete-channel-dialog.component';

@Component({
  selector: 'app-channel-card',
  templateUrl: './channel-card.component.html',
  styleUrls: ['./channel-card.component.scss'],
})
export class ChannelCardComponent {
  @Input()
  public small: boolean = false;
  @Input()
  public isClickable: boolean = false;
  @Input()
  public isSelected: boolean = false;
  @Input()
  public channel?: IChannel;
  constructor(
    private _dialog: MatDialog,
    private _channel: ChannelService,
    private _router: Router,
    private _snackbar: SnackbarService
  ) {}

  edit() {
    if (this.channel) return `/channel/update/${this.channel.id}`;
    return '';
  }
  delete() {
    if (!this.channel) return;
    this._dialog.open(DeleteChannelDialogComponent, {
      width: '600px',
      exitAnimationDuration: '300ms',
      enterAnimationDuration: '300ms',
      data: { channel: this.channel },
    });
  }
}
