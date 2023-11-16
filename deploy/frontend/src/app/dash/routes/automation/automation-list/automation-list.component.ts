import { CdkDragDrop } from '@angular/cdk/drag-drop';
import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { forkJoin } from 'rxjs';
import { IAutomation } from 'src/app/models/automation';
import { IChannel, Integrations } from 'src/app/models/intergration';
import { AutomationService } from 'src/app/service/automation/automation.service';
import { ChannelService } from 'src/app/service/channel/channel.service';
import { SnackbarService } from 'src/app/service/snackbar/snackbar.service';
import { DeleteAutomationDialogComponent } from './delete-automation-dialog/delete-automation-dialog.component';
import { MatDialog } from '@angular/material/dialog';

export interface PeriodicElement {
  name: string;
  position: number;
  weight: number;
  symbol: string;
}

@Component({
  selector: 'app-automation-list',
  templateUrl: './automation-list.component.html',
  styleUrls: ['./automation-list.component.scss'],
})
export class AutomationListComponent implements OnInit {
  automations: IAutomation[] = [];
  automationsRaw: any[] = [];
  displayedColumns: string[] = [
    'drag',
    'status',
    'name',
    'groupMatch',
    'event',
    'field',
    // 'position',
    'channel',
    'actions',
  ];
  channels: IChannel[] = [];
  constructor(
    private _dialog: MatDialog,
    private _automation: AutomationService,
    private _channel: ChannelService,
    private _snackBar: SnackbarService
  ) {}
  ngOnInit(): void {
    this._automation
      .getAllReactive({
        order: {
          position: 'asc',
        },
      })
      .subscribe((automations) => {
        this._channel.getAll().then((channels) => {
          this.channels = this._channel.mapToReadable(channels);
          this.automationsRaw = [...automations];
          console.log(this.channels);
          this.automations = automations as IAutomation[];
          this.automations = this.automations.map((automation: any) => {
            automation.channelInfos = [];
            for (const channelId of automation.channels) {
              let findedChannel = this.channels.find(
                (channel) => channel.id === channelId
              );
              if (findedChannel) {
                automation.channelInfos.push({
                  name: findedChannel.name,
                  image: findedChannel.image,
                });
              }
            }
            return automation;
          });
        });
      });
  }

  createAutomation() {
    return '/automation/create';
  }

  async togglePause(automation: IAutomation) {
    const toWrite = { ...automation };
    toWrite.running = !automation.running;
    toWrite.updatedAt = new Date();
    await this._automation.updateById(toWrite.id!, toWrite);
  }
  delete(automation: IAutomation) {
    this._dialog.open(DeleteAutomationDialogComponent, {
      width: '600px',
      exitAnimationDuration: '300ms',
      enterAnimationDuration: '300ms',
      data: { automation },
    });
  }

  drop(event: CdkDragDrop<any[]>) {
    // ingore same place
    if (event.currentIndex === event.previousIndex) return;
    let moved = this.automationsRaw[event.previousIndex];
    console.log(
      moved.name,
      'from',
      event.previousIndex,
      'to',
      event.currentIndex
    );
    if (event.currentIndex < event.previousIndex)
      for (let i = event.currentIndex; i < event.previousIndex; i++) {
        const automation = this.automationsRaw[i];
        automation.position++;
      }
    if (event.currentIndex > event.previousIndex)
      for (let i = event.previousIndex; i <= event.currentIndex; i++) {
        const automation = this.automationsRaw[i];
        automation.position--;
      }
    moved.position = event.currentIndex;
    let tasks$ = [];
    for (let i = 0; i < this.automationsRaw.length; i++) {
      const automation = this.automationsRaw[i];
      tasks$.push(this._automation.updateById(automation.id, automation));
    }
    forkJoin(tasks$).subscribe((results) => {
      this._snackBar.ok();
    });
  }
}
