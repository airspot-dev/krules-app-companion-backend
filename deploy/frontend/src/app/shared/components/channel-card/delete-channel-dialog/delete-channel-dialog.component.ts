import { Component, Inject } from '@angular/core';
import { where } from '@angular/fire/firestore';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { AutomationService } from 'src/app/service/automation/automation.service';
import { ChannelService } from 'src/app/service/channel/channel.service';
import { SnackbarService } from 'src/app/service/snackbar/snackbar.service';

export interface DeleteChannelDialogData {
  channel: any;
}

@Component({
  selector: 'app-delete-channel-dialog',
  templateUrl: './delete-channel-dialog.component.html',
  styleUrls: ['./delete-channel-dialog.component.scss'],
})
export class DeleteChannelDialogComponent {
  private _loaded: boolean = false;
  hasAutomations: boolean = false;
  automations: any[] = [];
  get disabled() {
    return !this._loaded || this.hasAutomations;
  }
  constructor(
    @Inject(MAT_DIALOG_DATA) public data: DeleteChannelDialogData,
    private _channel: ChannelService,
    private _automation: AutomationService,
    private _snackbar: SnackbarService
  ) {
    this._automation
      .getAll({
        query: [where('channels', 'array-contains', this.data.channel.id)],
      })
      .then((automations) => {
        this.automations = automations.docs;
        if (automations.docs.length) this.hasAutomations = true;
        this._loaded = true;
      })
      .catch((e) => {});
  }

  delete() {
    this._channel.deleteById(this.data.channel.id).subscribe(() => {
      this._snackbar.ok({ message: 'Channel deleted' });
    });
  }
}
