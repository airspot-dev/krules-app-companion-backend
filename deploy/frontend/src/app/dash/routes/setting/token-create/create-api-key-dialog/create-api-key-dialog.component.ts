import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { IApiKey } from 'src/app/models/api-key';

export interface CreateApiKeyDialogData {
  apiKey: IApiKey;
}

@Component({
  selector: 'app-create-api-key-dialog',
  templateUrl: './create-api-key-dialog.component.html',
  styleUrls: ['./create-api-key-dialog.component.scss'],
})
export class CreateApiKeyDialogComponent {
  constructor(
    private _router: Router,
    @Inject(MAT_DIALOG_DATA) public data: CreateApiKeyDialogData
  ) {}

  dismiss() {
    this._router.navigate(['/setting/token/list']);
  }
}
