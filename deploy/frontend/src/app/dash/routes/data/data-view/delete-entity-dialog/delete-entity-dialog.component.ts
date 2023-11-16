import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { GroupService } from 'src/app/service/group/group.service';
import { SchemaService } from 'src/app/service/schema/schema.service';
import { DeleteGroupDialogData } from '../delete-group-dialog/delete-group-dialog.component';

export interface DeleteEntityDialogData {
  entityId: any;
  groupId: any;
}

@Component({
  selector: 'app-delete-entity-dialog',
  templateUrl: './delete-entity-dialog.component.html',
  styleUrls: ['./delete-entity-dialog.component.scss'],
})
export class DeleteEntityDialogComponent {
  public entityConfirm: string | null = null;
  constructor(
    @Inject(MAT_DIALOG_DATA) public data: DeleteEntityDialogData,
    private _group: GroupService,
    private _schema: SchemaService
  ) {}

  deleteEntity() {
    this._group
      .updateById(
        this.data.entityId,
        { _deleting: true },
        {
          path: '/' + this.data.groupId,
          merge: true,
        }
      )
      .then(() => {});
    this._group
      .deleteEntity(this.data.groupId, this.data.entityId)
      .subscribe(() => {});
  }
}
