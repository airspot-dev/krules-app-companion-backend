import { Component, Inject } from '@angular/core';
import { where } from '@angular/fire/firestore';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { AutomationService } from 'src/app/service/automation/automation.service';
import { SnackbarService } from 'src/app/service/snackbar/snackbar.service';

export interface DeleteChannelDialogData {
  automation: any;
}

@Component({
  selector: 'app-delete-automation-dialog',
  templateUrl: './delete-automation-dialog.component.html',
  styleUrls: ['./delete-automation-dialog.component.scss'],
})
export class DeleteAutomationDialogComponent {
  constructor(
    @Inject(MAT_DIALOG_DATA) public data: DeleteChannelDialogData,
    private _automation: AutomationService,
    private _snackbar: SnackbarService
  ) {}

  delete() {
    this._automation
      .getAll({
        order: { position: 'asc' },
        query: [where('position', '>', this.data.automation.position)],
      })
      .then((automations) => {
        let promises = [];
        for (const automation of automations.docs) {
          promises.push(
            this._automation.incrementFiledById(automation.id, 'position', -1)
          );
        }
        Promise.all(promises).then((res) => {
          this._automation.deleteById(this.data.automation.id).subscribe(() => {
            this._snackbar.ok({ message: 'Automation deleted' });
          });
        });
      });
  }
}
