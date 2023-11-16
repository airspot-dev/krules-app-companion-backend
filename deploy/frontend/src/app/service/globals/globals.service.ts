import { Injectable } from '@angular/core';
import {
  Firestore,
  collection,
  getDocsFromServer,
  query,
} from '@angular/fire/firestore';
import { ServiceBase } from '../base/_base.service';
import { AuthService } from '../auth/auth.service';
import { Configuration } from 'src/app/app.constants';
import { concatAll, map } from 'rxjs';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root',
})
export class GlobalsService {
  constructor(private _fs: Firestore) {}

  getApiKeyPermissions() {
    const path = `/_globals_/apikey_permissions/scopes`;
    let coll = collection(this._fs, path);
    const q = query(coll);
    return getDocsFromServer(q);
  }
}
