import { v4 as uuidv4 } from 'uuid';

export interface IApiKey {
  name: string;
  note?: string;
  ips?: string[];
  createdAt: Date;
  expireAt?: Date;
  key: string;
  scopes: {
    [key: string]: string[];
  };
}

export class ApiKeyCreate {
  id?: string;
  name: string = '';
  note?: string;
  ipsTextual?: string;
  createdAt?: Date;
  expireAt?: Date;
  scopes: {
    [key: string]: {
      [key: string]: boolean;
    };
  } = {};

  constructor();
  constructor(id: string, dbModel: IApiKey, scopes: any);
  constructor(id?: string, dbModel?: IApiKey, scopes?: any) {
    this.id = id;
    if (dbModel) {
      this.name = dbModel.name;
      this.note = dbModel.note;
      this.createdAt = dbModel.createdAt;
      this.expireAt = dbModel.expireAt;
      if (dbModel.ips && dbModel.ips.length)
        this.ipsTextual = dbModel.ips.join('\n');
      if (this.scopes) {
        this.scopes = scopes;
        Object.keys(dbModel.scopes).forEach((scope) => {
          dbModel.scopes[scope].forEach(
            (permission) => (this.scopes[scope][permission] = true)
          );
        });
      }
    }
  }

  toApiKey(): IApiKey {
    let scopes: any = {};
    let ips: string[] = [];
    if (this.ipsTextual) ips = this.ipsTextual.split(/\r?\n/);
    ips = ips.map((x) => x.trim());
    Object.keys(this.scopes).forEach((scope) => {
      scopes[scope] = [];
      Object.keys(this.scopes[scope]).forEach((permission) => {
        if (this.scopes[scope][permission]) scopes[scope].push(permission);
      });
    });
    const obj: IApiKey = {
      name: this.name,
      createdAt: new Date(),
      key: uuidv4(),
      scopes: scopes,
    };

    if (this.note) obj.note = this.note;
    if (ips.length) obj.ips = ips;
    if (this.expireAt) obj.expireAt = this.expireAt;

    return obj;
  }
}
