import { Component } from '@angular/core';
import {
  FormControl,
  FormGroup,
  FormGroupDirective,
  NgForm,
  NonNullableFormBuilder,
  Validators,
} from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { ActivatedRoute, Router } from '@angular/router';
import { ApiKeyCreate, IApiKey } from 'src/app/models/api-key';
import { ApiKeyService } from 'src/app/service/api-key/api-key.service';
import { GlobalsService } from 'src/app/service/globals/globals.service';
import { SnackbarService } from 'src/app/service/snackbar/snackbar.service';
import { CreateApiKeyDialogComponent } from './create-api-key-dialog/create-api-key-dialog.component';
import { ErrorStateMatcher } from '@angular/material/core';

@Component({
  selector: 'app-token-create',
  templateUrl: './token-create.component.html',
  styleUrls: ['./token-create.component.scss'],
})
export class TokenCreateComponent {
  public isUpdating: boolean = false;
  public newApiKey: ApiKeyCreate = new ApiKeyCreate();
  public scopeAllCompleted: { [key: string]: boolean } = {};
  scopes: any[] = [];
  constructor(
    private _dialog: MatDialog,
    private _global: GlobalsService,
    private _snackbar: SnackbarService,
    private _apiKey: ApiKeyService,
    private _route: ActivatedRoute,
    private _router: Router
  ) {
    const id = this._route.snapshot.paramMap.get('id');
    if (id) this.isUpdating = true;

    this._global.getApiKeyPermissions().then((scopes: any) => {
      for (const scope of scopes.docs) {
        this.scopeAllCompleted[scope.data().scope] = false;
        this.newApiKey.scopes[scope.data().scope] = {};
        for (const permission of scope.data().permissions) {
          this.newApiKey.scopes[scope.data().scope][permission.permission] =
            false;
        }
      }
      this.scopes = scopes.docs;
      // IF UPDATING
      if (this.isUpdating && id)
        this._apiKey.getById(id).then((apiKey) => {
          this.newApiKey = new ApiKeyCreate(
            id,
            apiKey.data() as IApiKey,
            this.newApiKey.scopes
          );
          this.rebuildScopeAllCompleted();
        });
    });
  }

  rebuildScopeAllCompleted() {
    Object.keys(this.newApiKey.scopes).forEach((scope) => {
      this.computeAllCompleted(scope);
    });
  }

  someComplete(scope: string) {
    if (!this.newApiKey.scopes || !this.newApiKey.scopes[scope]) return false;
    let atLeastOneCompleted = false;
    Object.keys(this.newApiKey.scopes[scope]).forEach((s) => {
      atLeastOneCompleted =
        atLeastOneCompleted || this.newApiKey.scopes[scope][s];
    });
    return atLeastOneCompleted && !this.scopeAllCompleted[scope];
  }

  createToken() {
    if (this.isDisabled()) return;
    const model = this.newApiKey.toApiKey();

    this._apiKey.create(this.newApiKey.toApiKey()).subscribe(() => {
      this._snackbar.ok({ message: 'API Key created' });
      this._dialog.open(CreateApiKeyDialogComponent, {
        width: '600px',
        exitAnimationDuration: '300ms',
        enterAnimationDuration: '300ms',
        disableClose: true,
        data: { apiKey: model },
      });
    });
  }

  updateToken() {
    if (this.isDisabled()) return;
    const model = this.newApiKey.toApiKey();

    this._apiKey
      .updateById(this.newApiKey.id!, this.newApiKey.toApiKey())
      .then(() => {
        this._snackbar.ok({ message: 'API Key updated' });
        this._router.navigate(['/', 'setting', 'token', 'list']);
      });
  }

  setAll(completed: boolean, scope: string) {
    this.scopeAllCompleted[scope] = completed;
    if (!this.newApiKey.scopes[scope]) {
      return;
    }
    Object.keys(this.newApiKey.scopes[scope]).forEach((s) => {
      this.newApiKey.scopes[scope][s] = completed;
    });
  }

  togglePermission(scope: string, permission: string) {
    this.newApiKey.scopes[scope][permission] =
      !this.newApiKey.scopes[scope][permission];
    this.computeAllCompleted(scope);
  }

  computeAllCompleted(scope: string) {
    let allCompleted = true;
    Object.keys(this.newApiKey.scopes[scope]).forEach((s) => {
      allCompleted = allCompleted && this.newApiKey.scopes[scope][s];
    });
    this.scopeAllCompleted[scope] = allCompleted;
  }

  private _validateIPaddress(ipaddress: string) {
    if (
      /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(
        ipaddress
      )
    ) {
      return true;
    }
    return false;
  }

  checkIps() {
    let allValidIps = true;
    if (this.newApiKey.ipsTextual)
      this.newApiKey.ipsTextual.split(/\r?\n/).forEach((ip) => {
        allValidIps = allValidIps && this._validateIPaddress(ip);
      });
    return allValidIps;
  }

  isDisabled() {
    let ok = true;
    if (!this.newApiKey.name) ok = false;
    if (this.newApiKey.ipsTextual) ok = ok && this.checkIps();
    return !ok;
  }
}
