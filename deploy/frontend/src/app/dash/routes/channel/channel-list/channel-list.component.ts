import { Component } from '@angular/core';
import { Configuration } from 'src/app/app.constants';
import { IChannel, Integrations } from 'src/app/models/intergration';
import { ChannelService } from 'src/app/service/channel/channel.service';

@Component({
  selector: 'app-channel-list',
  templateUrl: './channel-list.component.html',
  styleUrls: ['./channel-list.component.scss'],
})
export class ChannelListComponent {
  columns: string[] = ['datetime', 'name'];

  public channels: IChannel[] = [];
  public integrations = Integrations;
  constructor(_configuration: Configuration, private _channel: ChannelService) {
    this._channel.getAllRealTime(
      {},
      (result: any) => (this.channels = this._channel.mapToReadable(result))
    );
  }
  createChannel() {
    return '/channel/create';
  }
}
