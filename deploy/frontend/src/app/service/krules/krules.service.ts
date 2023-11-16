import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { lastValueFrom, of } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class KrulesService {
  //_host: string = 'https://streams.krules.io';
  _host: string = '';
  _apiPath: string = '/api/v1';
  _basePath: string = `${this._host}${this._apiPath}`;
  constructor(private http: HttpClient) {}

  getAvailableProjects(token: string) {
    const url = `${this._basePath}/user/subscriptions`;
    return lastValueFrom(
      this.http.get(url, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
    );
  }

  deleteGroup(token: string, subscriptionId: string, groupId: string) {
    const url = `${this._basePath}/${subscriptionId}/${groupId}`;
    return this.http.delete(url, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }
  deleteEntity(
    token: string,
    subscriptionId: string,
    groupId: string,
    entityId: string
  ) {
    const url = `${this._basePath}/${subscriptionId}/${groupId}/${entityId}`;
    return this.http.delete(url, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }
}
