import { Component, OnInit, ViewChild } from '@angular/core';
import { User } from '@angular/fire/auth';
import { NonNullableFormBuilder, Validators } from '@angular/forms';
import { MatTabGroup } from '@angular/material/tabs';
import { ActivatedRoute, Router } from '@angular/router';
import { Configuration } from 'src/app/app.constants';
import { ISetting } from 'src/app/models/setting';
import { AuthService } from 'src/app/service/auth/auth.service';
import { ProfileService } from 'src/app/service/profile/profile.service';
import { SettingService } from 'src/app/service/setting/setting.service';
import { SnackbarService } from 'src/app/service/snackbar/snackbar.service';
@Component({
  selector: 'app-user-setting',
  templateUrl: './user-setting.component.html',
  styleUrls: ['./user-setting.component.scss'],
})
export class UserSettingComponent implements OnInit {
  public brand: any;
  public elementPerPage: number[];
  public tab: number = 0;
  public gloablSettingForm = this.fb.group({
    brandName: [''],
    brandLogoUrl: [''],
  });
  public userSettingForm = this.fb.group({
    elementPerPage: [10, Validators.required],
  });
  @ViewChild('tabGroup') tabGroup?: MatTabGroup;
  constructor(
    _configuration: Configuration,
    private fb: NonNullableFormBuilder,
    private _setting: SettingService,
    private _snackBar: SnackbarService,
    private _route: ActivatedRoute,
    private _profile: ProfileService
  ) {
    this.elementPerPage = _configuration.elementPerPage;
    this.userSettingForm
      .get('elementPerPage')
      ?.setValue(this.elementPerPage[0]);
  }

  async ngOnInit() {
    const profile = await this._profile.get();
    if (profile && profile.exists()) {
      if (profile.data()!['elementPerPage'])
        this.userSettingForm
          .get('elementPerPage')
          ?.setValue(profile.data()!['elementPerPage']);
    }
    const config = (await this._setting.getById('brand/config')).data();
    if (config) {
      if (config['brandName'])
        this.gloablSettingForm.controls.brandName.setValue(config['brandName']);
      if (config['brandLogoUrl'])
        this.gloablSettingForm.controls.brandLogoUrl.setValue(
          config['brandLogoUrl']
        );
    }

    this._route.queryParams.subscribe((q) => {
      if (q && q['tab'] && this.tabGroup) {
        try {
          this.tab = parseInt(q['tab']);
          this.tabGroup.selectedIndex = q['tab'];
        } catch (e) {}
      }
    });
  }

  submitGlobal() {
    const brandSetting: ISetting = this.gloablSettingForm.value;

    if (!this.gloablSettingForm.valid) {
      return;
    }

    this._setting
      .updateBrand(brandSetting)
      .then(() => {
        this._snackBar.ok();
      })
      .catch(() => {
        this._snackBar.error();
      });
  }
  submitProfile() {
    if (!this.userSettingForm.valid) {
      return;
    }
    this._profile
      .update(this.userSettingForm.value)
      .then(() => {
        this._snackBar.ok();
      })
      .catch((err) => {
        this._snackBar.error({ message: err });
      });
  }
}
