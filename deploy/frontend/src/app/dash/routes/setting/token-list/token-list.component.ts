import { AfterViewInit, Component } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { IApiKey } from 'src/app/models/api-key';
import { ApiKeyService } from 'src/app/service/api-key/api-key.service';
import { DeleteApiKeyDialogComponent } from './delete-api-key-dialog/delete-api-key-dialog.component';
import { HelpApiDialogComponent } from './help-api-dialog/help-api-dialog.component';

@Component({
  selector: 'app-token-list',
  templateUrl: './token-list.component.html',
  styleUrls: ['./token-list.component.scss'],
})
export class TokenListComponent implements AfterViewInit {
  keys: any[] = [];
  displayedColumns: string[] = [
    'name',
    'createdAt',
    'expireAt',
    'key',
    'actions',
  ];
  constructor(private _dialog: MatDialog, private _apiKey: ApiKeyService) {}
  ngAfterViewInit(): void {
    this._apiKey.getAllRealTime({}, (response: any) => {
      this.keys = response.docs.map((x: any) => {
        x.hidden = true;
        return x;
      });
    });
  }

  getDate(ts: any) {
    if (ts && ts.toDate) return ts.toDate();
    return null;
  }

  displayText(isHidden: boolean, text: string) {
    if (!isHidden) return text;
    return text.replace(/./g, '●');
  }

  openGuideDialog() {
    this._dialog.open(HelpApiDialogComponent, {
      width: '600px',
      exitAnimationDuration: '300ms',
      enterAnimationDuration: '300ms',
    });
  }

  delete(apiKey: any) {
    this._dialog.open(DeleteApiKeyDialogComponent, {
      width: '600px',
      exitAnimationDuration: '300ms',
      enterAnimationDuration: '300ms',
      data: { apiKey: apiKey.data(), apiKeyId: apiKey.id },
    });
  }
}
