import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { getMessaging, getToken, Messaging } from '@angular/fire/messaging';
import { Configuration } from 'src/app/app.constants';
import { FirebaseApp } from '@angular/fire/app';

@Injectable({
  providedIn: 'root',
})
export class MessagingService {
  currentMessage = new BehaviorSubject<any>(null);
  _config: Configuration;
  _messaging: Messaging;
  constructor(_config: Configuration, private _fApp: FirebaseApp) {
    this._config = _config;
    this._messaging = getMessaging(_fApp);
  }

  requestPermission() {
    getToken(this._messaging).then(
      (currentToken) => {},
      (error) => {
        console.error('Unable to get permission to notify...');
        console.error(error);
      }
    );
  }

  receiveMessaging() {}
}
