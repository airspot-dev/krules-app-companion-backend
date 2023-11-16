export interface IEventSource {
  changed_properties: string[];
  datetime: Date;
  id: string;
  origin_id: string;
  state: any;
}
