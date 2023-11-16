import { AfterViewInit, Component, ViewChild } from '@angular/core';
import {
  FormBuilder,
  FormControl,
  FormGroup,
  Validators,
} from '@angular/forms';
import { Integrations } from 'src/app/models/intergration';
import { generate } from 'shortid';
import { ChannelService } from 'src/app/service/channel/channel.service';
import { SnackbarService } from 'src/app/service/snackbar/snackbar.service';
import { ActivatedRoute, Router } from '@angular/router';
import { MatStepper } from '@angular/material/stepper';
import slugify from 'slugify';
import { where } from '@angular/fire/firestore';

@Component({
  selector: 'app-channel-edit',
  templateUrl: './channel-create.component.html',
  styleUrls: ['./channel-create.component.scss'],
})
export class ChannelCreateComponent implements AfterViewInit {
  public isUpdating: boolean = false;
  public id?: string | null;
  duration: number = 200;
  channelChooseForm: FormGroup = new FormGroup({
    channel: new FormControl('', [Validators.required]),
  });
  channelParamsForm: FormGroup = new FormGroup({
    name: new FormControl('', Validators.required),
  });
  choosenIntegration: any = { form: [] };
  integrations = Integrations;
  @ViewChild('stepper') private _stepper!: MatStepper;

  constructor(
    private _channel: ChannelService,
    private _router: Router,
    private _route: ActivatedRoute,
    private _snackbar: SnackbarService
  ) {
    this.id = this._route.snapshot.paramMap.get('id');
    if (this.id) this.isUpdating = true;
  }
  ngAfterViewInit(): void {
    if (this.isUpdating && this.id)
      this._channel.getById(this.id).then((channel) => {
        if (channel) {
          const data = channel.data();
          if (data) {
            this.channelChooseForm.controls['channel'].setValue(data['code']);
            this._stepper.next();
            this.buildParamsForm(channel);
          }
        }
      });
  }

  buildParamsForm(channel?: any) {
    this.choosenIntegration = this.integrations.find(
      (x) => this.channelChooseForm.controls['channel'].value === x.code
    );
    const formGroupFields: any = {
      integration: new FormControl(this.choosenIntegration.code),
      name: new FormControl(
        channel ? channel.data()['name'] : '',
        Validators.required
      ),
    };
    for (const formItem of this.choosenIntegration.form) {
      if (formItem.type == 'multi-key-value') {
        if (!channel) {
          const keyValueId = generate();
          formGroupFields[`${formItem.code}_${keyValueId}`] = new FormGroup({
            key: new FormControl(''),
            value: new FormControl(''),
          });
        } else {
          const keyValues = channel.data()['params'][formItem.code];
          Object.keys(keyValues).forEach((key) => {
            const keyValueId = generate();
            formGroupFields[`${formItem.code}_${keyValueId}`] = new FormGroup({
              key: new FormControl(key),
              value: new FormControl(keyValues[key]),
            });
          });
        }
      } else {
        let validators = [];
        if (formItem.required) validators.push(Validators.required);
        formGroupFields[formItem.code] = new FormControl(
          channel ? channel.data()['params'][formItem.code] : '',
          formItem
        );
      }
    }
    this.channelParamsForm = new FormGroup(formGroupFields);
  }

  getMultiKeyValueArray(formItemCode: string): string[] {
    const group: any = this.channelParamsForm.controls;
    if (!group) return [];
    const controls: string[] = [];
    Object.keys(group).forEach((controlKey) => {
      if (controlKey.indexOf(formItemCode) >= 0) {
        controls.push(controlKey);
      }
    });
    return controls;
  }

  addKeyValue(formItemCode: string) {
    const keyValueId = generate();

    this.channelParamsForm.addControl(
      `${formItemCode}_${keyValueId}`,
      new FormGroup({
        key: new FormControl(''),
        value: new FormControl(''),
      })
    );
    console.log(this.channelParamsForm);
    // const idx = this.choosenIntegration.form.findIndex(
    //   (x: any) => x.code === formItem
    // );
    // this.choosenIntegration.form[idx].counter++;
  }

  deleteMultiItem(formItemCode: string) {
    this.channelParamsForm.removeControl(formItemCode);
  }

  isDisabledFirstStep() {
    return !this.channelChooseForm.controls['channel'].value;
  }

  private async _getSlug(name: string, iteration = 0): Promise<string> {
    let slug = slugify(name);
    if (iteration != 0) slug = `${slug}-${iteration}`;
    const docs = await this._channel.getAll({
      query: [where('slug', '==', slug)],
    });
    if (docs.empty) return slug;
    else return this._getSlug(name, iteration + 1);
  }

  private async _formatChannel(isUpdating: boolean) {
    const raw = this.channelParamsForm.getRawValue();
    const slug = isUpdating ? raw.slug : await this._getSlug(raw.name);

    const channel: any = {
      name: raw.name,
      code: raw.integration,
      slug: slug,
      params: {},
    };
    for (const formItem of this.choosenIntegration.form) {
      if (formItem.type === 'multi-key-value') {
        channel.params[formItem.code] = {};
        Object.keys(raw).forEach((key) => {
          if (key.indexOf(formItem.code) >= 0)
            channel.params[formItem.code][raw[key].key] = raw[key].value;
        });
      } else channel.params[formItem.code] = raw[formItem.code];
    }

    return channel;
  }

  async createChannel() {
    const channel = await this._formatChannel(false);
    console.log(channel);
    this._channel.create(channel).subscribe((response) => {
      this._snackbar.ok({
        message: 'Channel created',
      });
      this._router.navigate(['/channel/list']);
    });
  }

  async updateChannel() {
    const channel = await this._formatChannel(true);
    console.log(channel);
    this._channel.updateById(this.id!, channel).then((response) => {
      this._snackbar.ok({
        message: 'Channel created',
      });
      this._router.navigate(['/channel/list']);
    });
  }

  disabled() {
    return !this.channelChooseForm.valid || !this.channelParamsForm.valid;
  }
}
