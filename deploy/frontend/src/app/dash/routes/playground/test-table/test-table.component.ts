import { Component, EventEmitter, ViewChild } from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { ActivatedRoute } from '@angular/router';
import { merge, startWith, switchMap } from 'rxjs';
import { Configuration } from 'src/app/app.constants';
import { IQueryOptions } from 'src/app/service/base/_base.service';
import { GroupService } from 'src/app/service/group/group.service';
import { ProfileService } from 'src/app/service/profile/profile.service';
import { SchemaService } from 'src/app/service/schema/schema.service';
import {
  ColumnDateFilterComponent,
  ColumnDateQueryFilter,
  ColumnDateFilterEvent,
} from 'src/app/shared/components/column-date-filter/column-date-filter.component';

@Component({
  selector: 'app-test-table',
  templateUrl: './test-table.component.html',
  styleUrls: ['./test-table.component.scss'],
})
export class TestTableComponent {
  public groupId: string = 'arpa.sync';
  public id: string = '192.168.5.121-20230614T0933';

  public elementPerPage: number[];
  public itemsPerPage: number;
  private hasOnlyFilterRowsEnabled = false;
  public resultsLength = 0;
  private _currentPage = 0;
  data: any[] = [];
  columns: any[] = [];
  columnIds: any[] = [];
  @ViewChild(MatPaginator) paginator: any = MatPaginator;
  @ViewChild('columnDateFilter') columnsDateFilter!: ColumnDateFilterComponent;
  @ViewChild(MatSort, { static: true }) sort: MatSort = new MatSort();
  public JSON = JSON;
  filterChanged = new EventEmitter();
  public filterStr = '';
  public loaded = false;
  public filterQuery: ColumnDateQueryFilter[] = [];

  constructor(
    _configuration: Configuration,
    private _schema: SchemaService,
    private _group: GroupService,
    private _profile: ProfileService
  ) {
    this.elementPerPage = _configuration.elementPerPage;
    this.itemsPerPage = this.elementPerPage[0];
    this._profile.get().then((profile) => {
      if (profile && profile.exists()) {
        if (profile.data()!['elementPerPage']) {
          this.itemsPerPage = profile.data()!['elementPerPage'];
        }
      }
    });
  }

  private _getColumns() {
    let options: IQueryOptions = {
      path: '/' + this.groupId + '/columns',
    };
    return this._schema.getAll(options).then((columns) => {
      this.columns = columns.docs;
      this.columnIds = (
        this.hasOnlyFilterRowsEnabled ? ['datetime', 'action'] : ['datetime']
      ).concat(this.columns!.map((x) => 'state.' + x['id']));
    });
  }

  public thereIsNoData(data: any) {
    if (Array.isArray(data) && !data.length) return true;
    return false;
  }

  private async _count() {
    const response = await this._group.countEventSourcing(
      this.groupId,
      this.id,
      this.filterQuery as any
    );
    this.resultsLength = response.data().count;
  }

  private _getData() {
    let options: IQueryOptions = {
      pageNumber: this.paginator.pageIndex + 1,
      pageSize: this.paginator.pageSize,
    };
    if (this.data && this.data.length) {
      if (this._currentPage > this.paginator.pageIndex) {
        options.endBefore = this.data[0].data()[this.sort.active];
        console.log('endBefore', options.endBefore);
      }
      if (this._currentPage < this.paginator.pageIndex) {
        options.startAfter =
          this.data[this.data.length - 1].data()[this.sort.active];
        console.log('startAfter', options.startAfter);
      }
    }
    if (this.sort.active) {
      options.order = { [`${this.sort.active}`]: this.sort.direction };
    }
    if (this.filterQuery) {
      options.query = this.filterQuery;
    }

    return this._group
      .getAllEventSourcing(this.groupId, this.id, options)
      .then((data: any) => {
        this._currentPage = this.paginator.pageIndex;
        if (!this.loaded) this.loaded = true;
        this.data = data.docs;
        this._count();
      });
  }

  async ngAfterViewInit() {
    this.sort.sortChange.subscribe(() => (this.paginator.pageIndex = 0));
    merge(this.filterChanged, this.sort.sortChange, this.paginator.page)
      .pipe(
        startWith({}),
        switchMap(async () => {
          this._getColumns().then(() => {
            this._getData();
          });
        })
      )
      .subscribe((data) => {});
  }

  editGroup() {
    return `/data/group/edit/${this.groupId}`;
  }

  isChanged(column: any, element: any) {
    return element.data().changed_properties.indexOf(column.id) >= 0;
  }

  filterEvt(evt: ColumnDateFilterEvent) {
    this.filterQuery = evt.queries;
    this.filterChanged.emit(evt);
    this.hasOnlyFilterRowsEnabled = evt.hasOnlyFilterRowsEnabled;
  }

  convertDate(element: any) {
    const d = element.data().datetime;
    if (d.toDate) return d.toDate();
    try {
      return new Date(d);
    } catch (e) {
      console.error('error converting date', d);
      console.error(e);
    }
  }
}
