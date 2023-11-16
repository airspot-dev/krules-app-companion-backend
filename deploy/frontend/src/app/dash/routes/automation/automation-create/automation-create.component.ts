import { Component } from '@angular/core';
import { Validators, NonNullableFormBuilder } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { IAutomation } from 'src/app/models/automation';
import { IChannel, Integrations } from 'src/app/models/intergration';
import { AuthService } from 'src/app/service/auth/auth.service';
import { AutomationService } from 'src/app/service/automation/automation.service';
import { ChannelService } from 'src/app/service/channel/channel.service';
import { SchemaService } from 'src/app/service/schema/schema.service';
import { TreeService } from 'src/app/service/tree/tree.service';

interface GroupNode {
  name: string;
  id: string;
  children?: GroupNode[];
}
interface IAutocompleteOptions {
  id: string;
  name: string;
  description: string;
}
@Component({
  selector: 'app-automation-create',
  templateUrl: './automation-create.component.html',
  styleUrls: ['./automation-create.component.scss'],
})
export class AutomationCreateComponent {
  public isUpdating: boolean = false;
  public automation: IAutomation = {
    name: '',
    entityFields: [],
    entityFieldsRaw: '',
    event: '',
    groupMatch: '',
    channels: [],
    position: -1,
    running: true,
  };
  separator = '.';

  groupTree: GroupNode[] = [];
  groups: IAutocompleteOptions[] = [];
  public lastPosition: number = -1;
  public automations: IAutomation[] = [];
  public channels: IChannel[] = [];
  public integrations = Integrations;
  public currentGroupMatchIndex = -1;
  public groupMatchSuggestions: { icon: string; value: string }[] = [];

  constructor(
    private fb: NonNullableFormBuilder,
    private _schema: SchemaService,
    private _tree: TreeService,
    private _router: Router,
    private _route: ActivatedRoute,
    private _auth: AuthService,
    private _automation: AutomationService,
    private _channel: ChannelService
  ) {
    const id = this._route.snapshot.paramMap.get('id');
    if (id) this.isUpdating = true;
    const promises: any[] = [
      this._automation.getMaxValue('position'),
      this._channel.getAll(),
      this._schema.getAll(),
    ];
    if (this.isUpdating && id) promises.push(this._automation.getById(id));

    Promise.all(promises).then(
      ([automations, channels, groups, automation]) => {
        //   name: '',
        //   entityFields: [],
        //   entityFieldsRaw: '',
        //   event: '',
        //   groupMatch: '',
        //   channels: [],
        //   position: -1,
        //   running: true,
        // };
        if (this.isUpdating) {
          this.automation.id = id!;
          this.automation.createdAt = automation.data().createdAt;
          this.automation.createdBy = automation.data().createdBy;
          this.automation.running = automation.data().running;
          this.automation.position = automation.data().position;
          this.automation.name = automation.data().name;
          this.automation.channels = automation.data().channels;
          this.automation.event = automation.data().event;
          this.automation.entityFieldsRaw = automation
            .data()
            .entityFields.join(',');
          this.automation.groupMatch = automation.data().groupMatch;
        }
        // groups
        this.groups = groups.docs.map((x: any) => ({
          id: x.id,
          name: x.data()['readable_name'] || x['id'],
          description: x.data()['description'] || '',
        }));
        this.groupTree = this._tree.convertStringDelimitedGroupToTree(
          this.groups.map((x) => x.id),
          this.separator
        );
        // channels
        this.channels = this._channel.mapToReadable(channels);
        this._filterGroupMatchSuggestions(this.automation.groupMatch);
        // last position
        const docs = automations.docs;
        if (docs.length) {
          this.lastPosition = docs[0].data()['position'];
          console.log(this.lastPosition);
        }
      }
    );
  }

  groupMatchChange(groupMatch: string) {
    this._filterGroupMatchSuggestions(groupMatch);
  }

  private _filterGroupMatchSuggestions(groupMatch: string) {
    const tokens = groupMatch.split(this.separator);
    let current: GroupNode[] = this.groupTree;
    let lastSelectedElement = null;
    for (const token of tokens) {
      current = (lastSelectedElement?.children || current).filter(
        (x) => x.name.indexOf(token) >= 0
      );
      lastSelectedElement = current.find((x) => x.name === token);
    }
    this.groupMatchSuggestions = [
      {
        icon: '<i class="fa-solid fa-asterisk"></i>',
        value: '*',
      },
    ].concat(current.map((x) => ({ icon: x.name, value: x.name })));
  }

  setGroupMatchSuggestionToken(token: string) {
    let tokens = this.automation.groupMatch.split(this.separator);
    tokens[tokens.length - 1] = token;
    this.automation.groupMatch = tokens.concat(['']).join(this.separator);
    this._filterGroupMatchSuggestions(this.automation.groupMatch);
    if (this.groupMatchSuggestions.length === 1)
      this.automation.groupMatch = this.automation.groupMatch.substring(
        0,
        this.automation.groupMatch.length - 1
      );
  }

  selectChannel(channelId: string) {
    if (this.automation.channels.includes(channelId)) {
      let idx = this.automation.channels.indexOf(channelId);
      this.automation.channels.splice(idx, 1);
    } else this.automation.channels.push(channelId);
  }

  create() {
    this.automation.position = this.lastPosition + 1;
    this.automation.createdAt = new Date();
    this.automation.updatedAt = new Date();
    if (this.automation.entityFieldsRaw)
      this.automation.entityFields = this.automation.entityFieldsRaw
        .split(',')
        .map((x) => x.trim());
    this.automation.createdBy = this._auth.user?.email;
    this.automation.updatedBy = this._auth.user?.email;
    delete this.automation.entityFieldsRaw;
    this._automation.create(this.automation as IAutomation).subscribe(() => {
      this._router.navigate(['/automation/list']);
    });
  }

  update() {
    this.automation.updatedAt = new Date();
    if (this.automation.entityFieldsRaw)
      this.automation.entityFields = this.automation.entityFieldsRaw
        .split(',')
        .map((x) => x.trim());
    this.automation.updatedBy = this._auth.user?.email;
    delete this.automation.entityFieldsRaw;
    this._automation
      .updateById(this.automation.id!, this.automation as IAutomation)
      .then(() => {
        this._router.navigate(['/automation/list']);
      });
  }

  submit() {
    if (this.isUpdating) this.update();
    else this.create();
  }

  resetGroupMatch() {
    this.automation.groupMatch = '';
    this._filterGroupMatchSuggestions('');
  }

  isDisabled() {
    return (
      !this.automation.name ||
      !this.automation.channels.length ||
      !this.automation.event ||
      !this.automation.groupMatch
    );
  }
}
