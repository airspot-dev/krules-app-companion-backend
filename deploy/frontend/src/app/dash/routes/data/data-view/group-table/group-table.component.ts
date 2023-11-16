import {
  AfterViewInit,
  Component,
  EventEmitter,
  Input,
  ViewChild,
} from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import {
  catchError,
  merge,
  startWith,
  switchMap,
  of as observableOf,
  Subject,
  takeUntil,
  Observable,
  map,
} from 'rxjs';
import { Configuration } from 'src/app/app.constants';
import { AuthService } from 'src/app/service/auth/auth.service';
import { IQueryOptions } from 'src/app/service/base/_base.service';
import { GroupService } from 'src/app/service/group/group.service';
import { ProfileService } from 'src/app/service/profile/profile.service';
import { SchemaService } from 'src/app/service/schema/schema.service';
import { KeyValueQueryFilter } from 'src/app/shared/components/key-value-filter/key-value-filter.component';
import { DeleteEntityDialogComponent } from '../delete-entity-dialog/delete-entity-dialog.component';
@Component({
  selector: 'app-group-table',
  templateUrl: './group-table.component.html',
  styleUrls: ['./group-table.component.scss'],
})
export class GroupTableComponent {
  columns: any[] = [];
  columnIds: any[] = [];
  dataSource: MatTableDataSource<any> = new MatTableDataSource<any>();
  group: string | null = null;
  public elementPerPage: number[];
  public itemsPerPage: number;
  public resultsLength = 0;
  private _currentPage = 0;
  public filterQuery: KeyValueQueryFilter[] = [];
  private groupUnsubscribe: any;
  public _collapsed = false;
  private _userId: string = '';
  public loaded = false;
  @ViewChild(MatPaginator) paginator: any = MatPaginator;
  @ViewChild(MatSort) sort: any = MatSort;
  private filterChanged = new EventEmitter<KeyValueQueryFilter[]>();

  @Input() set groupId(value: string | null) {
    this.group = value;
    if (this.group) this._refreshTable();
  }
  @Input() set collapsed(value: boolean) {
    this._collapsed = !!value;
    // this.calcTableDimensions();
  }

  // @Input() set isLive(value: boolean) {
  //   this.isLive$.emit(value)
  //   console.log(value);
  // }

  constructor(
    _configuration: Configuration,
    public dialog: MatDialog,
    private _schema: SchemaService,
    private _groups: GroupService,
    private _auth: AuthService,
    private _profile: ProfileService
  ) {
    this.elementPerPage = _configuration.elementPerPage;
    this.itemsPerPage = this.elementPerPage[0];
    this._userId = this._auth.user!.uid;
    this._profile.get().then((profile) => {
      if (profile && profile.exists()) {
        if (profile.data()!['elementPerPage']) {
          this.itemsPerPage = profile.data()!['elementPerPage'];
        }
      }
    });
  }

  private _blink(id: string) {
    var element = document.getElementById(id);
    if (!element) return;
    element.classList.add('modified-animation');
  }

  private _sorter(element1: any, element2: any) {
    const uid = this._auth.user!.uid;
    const a = element1.data().userPreferences?.[uid]?.position;
    const b = element2.data().userPreferences?.[uid]?.position;
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

  private async _getColumns() {
    let options: IQueryOptions = {
      path: '/' + this.group + '/columns',
    };
    const columns = await this._schema.getAll(options);
    this.columns = columns.docs!.filter((x: any) => {
      if (x.id === '_last_update') return false;
      if (!x.data().userPreferences || !x.data().userPreferences[this._userId])
        return true;
      return !x.data().userPreferences[this._userId].hide_data;
    });
    this.columns = this.columns.sort(this._sorter.bind(this));

    this.columnIds = ['_last_update'].concat(
      this.columns!.map((x: any) => x['id'])
    );
    this.columnIds.push('actions');
  }

  private _getGroupData(group: string) {
    this._cleanSubscriptions();

    let options: IQueryOptions = {
      path: '/' + group,
      pageNumber: this.paginator.pageIndex + 1,
      pageSize: this.paginator.pageSize,
    };
    if (this.sort.active && this.sort.direction) {
      if (this._currentPage > this.paginator.pageIndex)
        options.endBefore = this.dataSource.data[0].data()[this.sort.active];
      if (this._currentPage < this.paginator.pageIndex)
        options.startAfter =
          this.dataSource.data[this.dataSource.data.length - 1].data()[
            this.sort.active
          ];
      if (this.sort.active) {
        options.order = { [this.sort.active]: this.sort.direction };
      }
    } else {
      if (this._currentPage > this.paginator.pageIndex)
        options.endBefore = this.dataSource.data[0].id;
      if (this._currentPage < this.paginator.pageIndex)
        options.startAfter =
          this.dataSource.data[this.dataSource.data.length - 1].id;
    }
    if (this.filterQuery) options.query = this.filterQuery;
    let firstTime = true;
    this.groupUnsubscribe = this._groups.getAllRealTime(
      options,
      (snapshot: any) => {
        this.dataSource.data = snapshot.docs;

        this._getGroupDataCount();
        if (!firstTime)
          setTimeout(() => {
            snapshot.docChanges().forEach((change: any) => {
              this._blink(change.doc.id);
            });
          }, 50);
        firstTime = false;
        if (!this.loaded) this.loaded = true;
      }
    );
  }
  private _getGroupDataCount() {
    let options: IQueryOptions = {
      path: '/' + this.group,
    };
    return this._groups.count(options).then((data) => {
      this._currentPage = this.paginator.pageIndex;
      this.resultsLength = data.data().count;
    });
  }

  clearSort() {
    this.sort.sort({ id: '', start: 'asc', disableClear: false });
    this.paginator.pageIndex = 0;
    this.filterQuery = [];
  }

  filterEvt(evt: KeyValueQueryFilter[]) {
    this.filterQuery = evt;
    this.filterChanged.emit(evt);
  }

  private async _refreshTable() {
    this.clearSort();
    merge(this.filterChanged, this.sort.sortChange, this.paginator.page)
      .pipe(
        startWith({}),
        switchMap(async () => {
          this._getColumns().then(() => {
            this._getGroupData(this.group!);
          });
        })
      )
      .subscribe((data) => {});
  }
  getLink(id: string) {
    return `/data/group/${this.group}/item/${id}`;
  }
  private _cleanSubscriptions() {
    if (this.groupUnsubscribe) {
      this.groupUnsubscribe();
    }
  }

  isDeleting(entity: any) {
    return entity.data()._deleting;
  }

  convertDate(element: any) {
    const d = element.data().LAST_UPDATE || element.data()._last_update;
    if (d.toDate) return d.toDate();
    try {
      return new Date(d);
    } catch (e) {
      console.error('error converting date', d);
      console.error(e);
    }
  }

  deleteEntity(entityId: string) {
    this.dialog.open(DeleteEntityDialogComponent, {
      width: '600px',
      exitAnimationDuration: '300ms',
      enterAnimationDuration: '300ms',
      data: {
        groupId: this.group,
        entityId: entityId,
      },
    });
  }
}
