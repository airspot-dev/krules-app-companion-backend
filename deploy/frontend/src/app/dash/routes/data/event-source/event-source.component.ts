import {
  AfterViewInit,
  Component,
  EventEmitter,
  OnInit,
  ViewChild,
} from '@angular/core';
import { where } from '@angular/fire/firestore';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { ActivatedRoute } from '@angular/router';
import {
  catchError,
  merge,
  startWith,
  switchMap,
  of as observableOf,
  map,
} from 'rxjs';
import { IQueryOptions } from 'src/app/service/base/_base.service';
import { GroupService } from 'src/app/service/group/group.service';
import { SchemaService } from 'src/app/service/schema/schema.service';
import {
  ColumnDateFilterComponent,
  ColumnDateFilterEvent,
  ColumnDateQueryFilter,
} from 'src/app/shared/components/column-date-filter/column-date-filter.component';
import {
  MAT_DATE_FORMATS,
  MAT_DATE_LOCALE,
  MatDateFormats,
  MAT_NATIVE_DATE_FORMATS,
} from '@angular/material/core';
import { Configuration } from 'src/app/app.constants';
import { ProfileService } from 'src/app/service/profile/profile.service';

export const GRI_DATE_FORMATS: MatDateFormats = {
  ...MAT_NATIVE_DATE_FORMATS,
  display: {
    ...MAT_NATIVE_DATE_FORMATS.display,
    dateInput: {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    } as Intl.DateTimeFormatOptions,
  },
};

@Component({
  selector: 'app-event-source',
  templateUrl: './event-source.component.html',
  styleUrls: ['./event-source.component.scss'],
  providers: [{ provide: MAT_DATE_FORMATS, useValue: GRI_DATE_FORMATS }],
})
export class EventSourceComponent implements AfterViewInit, OnInit {
  public groupId: string = '';
  public id: string = '';

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
    private _route: ActivatedRoute,
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

  ngOnInit(): void {
    this.groupId = this._route.snapshot.paramMap.get('group_id') || '';
    this.id = this._route.snapshot.paramMap.get('id') || '';
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

  jumpTo(type: string, element: any) {
    this.columnsDateFilter.jumpTo(type, element);
  }
}
