import { Injectable } from '@angular/core';
import { Firestore } from '@angular/fire/firestore';
import { Configuration } from 'src/app/app.constants';
import { ISchema } from 'src/app/models/schema';
import { AuthService } from '../auth/auth.service';
import { ServiceBase } from '../base/_base.service';

@Injectable({
  providedIn: 'root',
})
export class SchemaService extends ServiceBase<ISchema> {
  constructor(
    _fs: Firestore,
    _configuration: Configuration,
    _auth: AuthService
  ) {
    super('settings/schemas', _configuration, _fs, _auth);
  }
}
