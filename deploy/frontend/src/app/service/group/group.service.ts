import { Injectable } from '@angular/core';
import {
  collection,
  collectionData,
  doc,
  Firestore,
  getDoc,
  where,
} from '@angular/fire/firestore';
import {
  catchError,
  concatAll,
  filter,
  map,
  Observable,
  switchMap,
} from 'rxjs';
import { Configuration } from 'src/app/app.constants';
import { IGroup } from 'src/app/models/group';
import { AuthService } from '../auth/auth.service';
import { IQueryOptions, ServiceBase } from '../base/_base.service';
import { User, UserProfile } from '@angular/fire/auth';
import { HttpClient } from '@angular/common/http';
import { KrulesService } from '../krules/krules.service';

@Injectable({
  providedIn: 'root',
})
export class GroupService extends ServiceBase<IGroup> {
  constructor(
    private _fs: Firestore,
    _configuration: Configuration,
    _auth: AuthService,
    private _krules: KrulesService,
    private http: HttpClient
  ) {
    super('groups', _configuration, _fs, _auth);
  }

  deleteGroup(groupId: string) {
    return this._auth.getFireToken().pipe(
      map((accessToken: string) => {
        return this._krules.deleteGroup(
          accessToken,
          this._getSubscriptionId(),
          groupId
        );
      }),
      concatAll()
    );
  }
  deleteEntity(groupId: string, entityId: string) {
    return this._auth.getFireToken().pipe(
      map((accessToken: string) => {
        return this._krules.deleteEntity(
          accessToken,
          this._getSubscriptionId(),
          groupId,
          entityId
        );
      }),
      concatAll()
    );
  }
  // /0/groups/crypto.prices/adausdt.p/event_sourcing
  countEventSourcing(groupId: string, entityId: string, query = []) {
    const options = {
      path: `/${groupId}/${entityId}/event_sourcing`,
      query: query,
    };
    return this.count(options);
  }

  getAllEventSourcing(
    groupId: string,
    entityId: string,
    options: IQueryOptions = {}
  ) {
    options.query = options.query || [];
    options.path = `/${groupId}/${entityId}/event_sourcing`;
    return this.getAll(options);
  }
}
