import { Component, OnInit } from '@angular/core';
import { MessagingService } from './service/messaging/messaging.service';
import { AuthService } from './service/auth/auth.service';
import { GlobalsService } from './service/globals/globals.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent implements OnInit {
  title = 'krules';
  message: any;
  constructor(
    private _auth: AuthService,
    private _messaging: MessagingService
  ) {
    this._auth.init();
  }
  ngOnInit(): void {
    this._messaging.requestPermission();
    this._messaging.receiveMessaging();
    this.message = this._messaging.currentMessage;
  }
}
