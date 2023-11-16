import { Injectable } from '@angular/core';
import { environment } from '../environments/environment';

@Injectable()
export class Configuration {
  public server = {
    basePath: environment.server.basePath,
    apiBase: environment.server.apiBase,
  };
  public firebase = environment.firebase;
  public elementPerPage = environment.elementPerPage;
}
