import { Injectable } from '@angular/core';
import { ServiceBase } from '../base/_base.service';
import { ISetting } from 'src/app/models/setting';
import { Configuration } from 'src/app/app.constants';
import { AuthService } from '../auth/auth.service';
import { Firestore } from '@angular/fire/firestore';

@Injectable({
  providedIn: 'root',
})
export class SettingService extends ServiceBase<ISetting> {
  constructor(
    _fs: Firestore,
    _configuration: Configuration,
    _auth: AuthService
  ) {
    super('settings', _configuration, _fs, _auth);
  }
  updateBrand(brandSetting: ISetting) {
    return this.updateById('brand/config', brandSetting);
  }
}
