import { Injectable } from '@angular/core';
import { Firestore } from '@angular/fire/firestore';
import { Configuration } from 'src/app/app.constants';
import { IAutomation } from 'src/app/models/automation';
import { AuthService } from '../auth/auth.service';
import { ServiceBase } from '../base/_base.service';

@Injectable({
  providedIn: 'root',
})
export class AutomationService extends ServiceBase<IAutomation> {
  constructor(
    _fs: Firestore,
    _configuration: Configuration,
    _auth: AuthService
  ) {
    super('settings/automations', _configuration, _fs, _auth);
  }
}
