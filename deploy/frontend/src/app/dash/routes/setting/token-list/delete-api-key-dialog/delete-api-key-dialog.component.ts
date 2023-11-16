import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { IApiKey } from 'src/app/models/api-key';
import { ApiKeyService } from 'src/app/service/api-key/api-key.service';
import { SnackbarService } from 'src/app/service/snackbar/snackbar.service';

export interface DeleteApiKeyDialogData {
  apiKeyId: string;
  apiKey: IApiKey;
}

@Component({
  selector: 'app-delete-api-key-dialog',
  templateUrl: './delete-api-key-dialog.component.html',
  styleUrls: ['./delete-api-key-dialog.component.scss'],
})
export class DeleteApiKeyDialogComponent {
  constructor(
    @Inject(MAT_DIALOG_DATA) public data: DeleteApiKeyDialogData,
    private _apiKey: ApiKeyService,
    private _snackbar: SnackbarService
  ) {}

  delete() {
    this._apiKey.deleteById(this.data.apiKeyId).subscribe(() => {
      this._snackbar.ok({ message: 'API Key deleted' });
    });
  }
}
