import { Injectable } from '@angular/core';
import { Firestore } from '@angular/fire/firestore';
import { Configuration } from 'src/app/app.constants';
import { ISchema } from 'src/app/models/schema';
import { AuthService } from '../auth/auth.service';
import { ServiceBase } from '../base/_base.service';
import { User } from '@angular/fire/auth';

@Injectable({
  providedIn: 'root',
})
export class ProfileService extends ServiceBase<ISchema> {
  private _user: User | undefined;
  constructor(
    _fs: Firestore,
    _configuration: Configuration,
    _auth: AuthService
  ) {
    super('settings/profile', _configuration, _fs, _auth);
    this.user = _auth.user;
  }

  get() {
    return super.getById(this.user!.uid);
  }

  update(model: ISchema) {
    return super.updateById(this.user!.uid, model);
  }
}
