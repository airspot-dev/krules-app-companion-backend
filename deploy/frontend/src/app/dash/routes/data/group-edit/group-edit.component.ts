import { CdkDragDrop, moveItemInArray } from '@angular/cdk/drag-drop';
import { Component, OnInit } from '@angular/core';
import { MatTableDataSource } from '@angular/material/table';
import { ActivatedRoute } from '@angular/router';
import { forkJoin } from 'rxjs';
import { AuthService } from 'src/app/service/auth/auth.service';
import { IQueryOptions } from 'src/app/service/base/_base.service';
import { SchemaService } from 'src/app/service/schema/schema.service';
import { SnackbarService } from 'src/app/service/snackbar/snackbar.service';
import { OkSnackbarComponent } from 'src/app/shared/components/ok-snackbar/ok-snackbar.component';

interface ITableElement {
  id: string;
  data: any;
}

@Component({
  selector: 'app-group-edit',
  templateUrl: './group-edit.component.html',
  styleUrls: ['./group-edit.component.scss'],
})
export class GroupEditComponent implements OnInit {
  columns = new MatTableDataSource<ITableElement>([]);
  columnIds: any[] = [
    'drag',
    'visibility',
    'name',
    'columnId',
    // 'visibility',
    /* 'name', */ 'data' /* 'event_sourcing' */,
  ];
  groupId: string | null = null;
  userId: string = '';

  constructor(
    private _snackBar: SnackbarService,
    private _schema: SchemaService,
    private _route: ActivatedRoute,
    private _auth: AuthService
  ) {}

  async ngOnInit() {
    this.groupId = this._route.snapshot.paramMap.get('group_id') || '';
    this.userId = this._auth.user!.uid;
    this._getColumns();
  }

  drop(event: CdkDragDrop<any[]>) {
    // ingore same place
    if (event.currentIndex === event.previousIndex) return;
    let moved = this.columns.data[event.previousIndex].data;

    if (event.currentIndex < event.previousIndex)
      for (let i = event.currentIndex; i < event.previousIndex; i++) {
        const element = this.columns.data[i];
        element.data.userPreferences[this.userId].position++;
      }
    if (event.currentIndex > event.previousIndex)
      for (let i = event.previousIndex; i <= event.currentIndex; i++) {
        const element = this.columns.data[i];
        element.data.userPreferences[this.userId].position--;
      }

    // for (let i = event.currentIndex; i < this.columns.data.length; i++) {
    //   const element = this.columns.data[i];
    //   element.data.userPreferences[this.userId].position++;
    // }
    moved.userPreferences[this.userId].position = event.currentIndex;
    let tasks$ = [];
    for (let i = 0; i < this.columns.data.length; i++) {
      const element = this.columns.data[i];
      tasks$.push(
        this._schema.updateById(element.id, element.data, {
          path: '/' + this.groupId + '/columns',
        })
      );
    }
    forkJoin(tasks$).subscribe((results) => {
      this._snackBar.ok();
    });
    moveItemInArray(this.columns.data, event.previousIndex, event.currentIndex);
  }

  private _sorter(element1: any, element2: any) {
    const uid = this.userId;
    const a = element1.data.userPreferences?.[uid]?.position;
    const b = element2.data.userPreferences?.[uid]?.position;
    if (a === null) {
      return 1;
    }

    if (b === null) {
      return -1;
    }

    if (a === b) {
      return 0;
    }

    return a < b ? -1 : 1;
  }

  private _getColumns() {
    let optionsColumns: IQueryOptions = {
      path: '/' + this.groupId + '/columns',
    };
    this._schema.getAllRealTime(optionsColumns, (columns: any) => {
      this.columns.data = columns.docs.map((x: any) => ({
        id: x.id,
        data: x.data(),
      }));
      console.log(this.columns.data);
      this.columns.data = this.columns.data.sort(this._sorter.bind(this));
      this.columns.data = this.columns.data.map((x, i) => {
        if (!x.data.userPreferences) x.data.userPreferences = {};
        if (!x.data.userPreferences[this.userId])
          x.data.userPreferences[this.userId] = {};
        if (isNaN(x.data.userPreferences[this.userId].position))
          x.data.userPreferences[this.userId].position = i;
        if (!x.data.userPreferences[this.userId].hide_data)
          x.data.userPreferences[this.userId].hide_data = false;
        return x;
      });
    });
  }

  private _getUserPreferencesKey(scope: string) {
    const id = this.userId;
    return `userPreferences.${id}.${scope}`;
  }

  isHidden(scope: string, element: any) {
    if (
      !element.data.userPreferences ||
      !element.data.userPreferences[this.userId]
    )
      return false;
    return !!element.data.userPreferences[this.userId][scope];
  }

  public toggleItem(scope: string, element: any) {
    element.data.userPreferences[this.userId][scope] =
      !element.data.userPreferences[this.userId][scope];
    this._schema
      .updateById(element.id, element.data, {
        path: '/' + this.groupId + '/columns',
      })
      .then(() => {
        this._snackBar.ok();
      })
      .catch(() => {
        this._snackBar.error();
      });
  }

  public saveName(element: any) {
    this._schema
      .updateById(
        element.id,
        { readable_name: element.data['readable_name'] },
        {
          path: '/' + this.groupId + '/columns',
        }
      )
      .then(() => {
        this._snackBar.ok();
      })
      .catch(() => {
        this._snackBar.error();
      });
  }
}
