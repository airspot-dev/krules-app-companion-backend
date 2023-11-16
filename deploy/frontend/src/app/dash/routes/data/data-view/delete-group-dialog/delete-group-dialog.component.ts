import { Component, Inject } from '@angular/core';
import { MatDialog, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { GroupService } from 'src/app/service/group/group.service';
import { SchemaService } from 'src/app/service/schema/schema.service';

export interface DeleteGroupDialogData {
  group: any;
}

@Component({
  selector: 'app-delete-group-dialog',
  templateUrl: './delete-group-dialog.component.html',
  styleUrls: ['./delete-group-dialog.component.scss'],
})
export class DeleteGroupDialogComponent {
  public groupConfirm: string | null = null;
  constructor(
    @Inject(MAT_DIALOG_DATA) public data: DeleteGroupDialogData,
    private _group: GroupService,
    private _schema: SchemaService
  ) {}

  deleteGroup() {
    this._schema
      .updateById(this.data.group.id, { _deleting: true }, { merge: true })
      .then(() => {
        this._group.deleteGroup(this.data.group.id).subscribe(() => {});
      });
  }
}
