import { Injectable } from '@angular/core';
import { Firestore } from '@angular/fire/firestore';
import { Configuration } from 'src/app/app.constants';
import { IAutomation } from 'src/app/models/automation';
import { AuthService } from '../auth/auth.service';
import { ServiceBase } from '../base/_base.service';
import { IChannel, Integrations } from 'src/app/models/intergration';

@Injectable({
  providedIn: 'root',
})
export class ChannelService extends ServiceBase<IAutomation> {
  private _integrations = Integrations;
  constructor(
    _fs: Firestore,
    _configuration: Configuration,
    _auth: AuthService
  ) {
    super('settings/channels', _configuration, _fs, _auth);
  }

  mapToReadable(data: any) {
    return data.docs.map((doc: any) => {
      let type = doc.data().code;

      const integration = this._integrations.find((x) => x.code === type);

      const obj: IChannel = {
        id: doc.id,
        name: doc.data().name,
        slug: doc.data().slug,
        type: integration!.name,
        image: integration!.image,
        imageNeg: integration!.imageNeg,
        previewKey: integration!.preview,
        preview: doc.data()['params'][integration!.preview],
      };
      return obj;
    });
  }
}
