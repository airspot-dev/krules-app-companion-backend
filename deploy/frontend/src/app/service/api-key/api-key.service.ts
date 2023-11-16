import { Injectable } from '@angular/core';
import { Firestore } from '@angular/fire/firestore';
import { Configuration } from 'src/app/app.constants';
import { AuthService } from '../auth/auth.service';
import { ServiceBase } from '../base/_base.service';
import { IApiKey } from 'src/app/models/api-key';

@Injectable({
  providedIn: 'root',
})
export class ApiKeyService extends ServiceBase<IApiKey> {
  constructor(
    _fs: Firestore,
    _configuration: Configuration,
    _auth: AuthService
  ) {
    super('settings/api-key', _configuration, _fs, _auth);
  }
}
