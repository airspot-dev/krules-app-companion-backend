import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { AuthService } from 'src/app/service/auth/auth.service';
import { Router } from '@angular/router';
import { User } from 'firebase/auth';
import { FormControl } from '@angular/forms';
import { StateService } from 'src/app/service/state/state.service';
import { OverlayContainer } from '@angular/cdk/overlay';
import { SettingService } from 'src/app/service/setting/setting.service';
import { GlobalsService } from 'src/app/service/globals/globals.service';
import { KrulesService } from 'src/app/service/krules/krules.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss'],
})
export class HeaderComponent implements OnInit {
  brandLogoUrl: string = '/assets/img/logo.png';
  brandName: string = 'KRules Companion';
  menuItems: { icon: string; name: string; route: string }[] = [
    {
      icon: 'database',
      name: 'Data',
      route: 'data/view',
    },
    // {
    //   icon: 'shapes',
    //   name: 'Groups',
    //   route: 'layout/create',
    // },
    {
      icon: 'bolt',
      name: 'Triggers',
      route: 'automation/list',
    },
    {
      icon: 'satellite-dish',
      name: 'Channels',
      route: 'channel/list',
    },
    // {
    //   icon: 'table-columns',
    //   name: 'Layout',
    //   route: 'layout/create',
    // },
    // {
    //   icon: 'gear',
    //   name: 'Settings',
    //   route: 'setting',
    // },
  ];
  public themeSelect = new FormControl(
    this._state.OS.snapshot(this._state.OS.S.theme)
  );
  public subscriptions: string[] = [];
  public activeSubscription: string = '';
  themeMap: Map<string, string> = new Map();
  constructor(
    private _overlay: OverlayContainer,
    private _auth: AuthService,
    private _router: Router,
    private _setting: SettingService,
    private _state: StateService,
    private _global: GlobalsService,
    private _krules: KrulesService
  ) {
    this.themeMap.set('Light', 'light-theme');
    this.themeMap.set('Dark', 'dark-theme');
  }

  async ngOnInit() {
    this._auth.getFireToken().subscribe((token: string) => {
      this._krules.getAvailableProjects(token).then((result: any) => {
        this.subscriptions = result.subscriptions;
        this.activeSubscription = this._auth.getCurrentProject();
      });
    });

    const config = (await this._setting.getById('brand/config')).data();
    if (config) {
      if (config['brandName']) this.brandName = config['brandName'];
      if (config['brandLogoUrl']) this.brandLogoUrl = config['brandLogoUrl'];
    }
    this.themeSelect.valueChanges.subscribe((themeColor) => {
      const theme: string | undefined = this.themeMap.get(themeColor);
      this._state.OS.put(this._state.OS.S.theme, theme);
      this.removeThemeClasses();
      this.addThemeClasses();
    });
    this.removeThemeClasses();
    this.addThemeClasses();
  }

  changeProject(subscription: string) {
    this._auth.setCurrentProject(subscription);
  }

  addThemeClasses() {
    const themeClass: string = this._state.OS.snapshot(this._state.OS.S.theme);
    this._overlay.getContainerElement().classList.add(themeClass);
  }

  removeThemeClasses(classPostfix: string = '-theme') {
    const overlayConatinerClasses =
      this._overlay.getContainerElement().classList;
    const themeClassesToRemove = Array.from(overlayConatinerClasses).filter(
      (item: string) => item.includes(classPostfix)
    );
    if (themeClassesToRemove.length)
      overlayConatinerClasses.remove(...themeClassesToRemove);
  }

  logout() {
    this._auth.logout().subscribe((result) => {
      this._router.navigate(['/login']);
    });
  }
}
