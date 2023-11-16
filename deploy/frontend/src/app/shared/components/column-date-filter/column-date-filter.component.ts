import {
  Component,
  EventEmitter,
  Input,
  Output,
  ViewChild,
} from '@angular/core';
import {
  QueryCompositeFilterConstraint,
  QueryFieldFilterConstraint,
  where,
} from '@angular/fire/firestore';
import { FormControl } from '@angular/forms';
import { generate } from 'shortid';

interface Columns {
  uid: string;
  id: string;
  type: string;
  displayName: string;
}
interface ChipToken {
  uid: string;
  type: string;
  token: string;
}

interface IAutocompleteOptions {
  id: string;
  name: string;
  description: string;
}

export interface ColumnDateFilterEvent {
  hasOnlyFilterRowsEnabled: boolean;
  queries: ColumnDateQueryFilter[];
}

interface FilterType {
  id: string;
  name: string;
  enableFrom: boolean;
  enableTo: boolean;
}

export type ColumnDateQueryFilter =
  | QueryFieldFilterConstraint
  | QueryCompositeFilterConstraint;

@Component({
  selector: 'app-column-date-filter',
  templateUrl: './column-date-filter.component.html',
  styleUrls: ['./column-date-filter.component.scss'],
})
export class ColumnDateFilterComponent {
  filterType = new FormControl<FilterType | null>(null);
  chosenColumns = new FormControl<FilterType[] | null>(null);
  fromDate = new FormControl<Date | null>(null);
  toDate = new FormControl<Date | null>(null);
  filterTypeOptions: FilterType[] = [
    {
      id: 'from',
      name: 'Starting date',
      enableFrom: true,
      enableTo: false,
    },
    {
      id: 'to',
      name: 'Ending date',
      enableFrom: false,
      enableTo: true,
    },
    {
      id: 'between',
      name: 'Between dates',
      enableFrom: true,
      enableTo: true,
    },
  ];
  allColumns: Columns[] = [];
  selectionList: any[] = [];
  @Output() filter = new EventEmitter<any>();

  @Input() set columns(value: any[]) {
    this.allColumns = value.map((x) => ({
      uid: generate(),
      id: x.id,
      type: 'column',
      displayName: x.data().readable_name,
    }));
    this._init();
  }

  private _init() {}

  submit() {
    const filter = this._buildFilter();
    console.log('submitted', filter);
    if (this._validate()) this.filter.emit(filter);
  }

  isDirty() {
    if (
      this.chosenColumns &&
      this.chosenColumns.value &&
      Array.isArray(this.chosenColumns.value) &&
      this.chosenColumns.value.length
    )
      return true;
    if (this.filterType.value) {
      if (
        ['from', 'between'].includes(this.filterType.value.id) &&
        this.fromDate.value
      )
        return true;
      if (
        ['to', 'between'].includes(this.filterType.value.id) &&
        this.toDate.value
      )
        return true;
    }
    return false;
  }

  reset() {
    this.chosenColumns.setValue([]);
    this.filterType.setValue(null);
    this.fromDate.setValue(null);
    this.toDate.setValue(null);
    this.submit();
  }

  private _validate() {
    return true;
  }

  public jumpTo(type: string, element: any) {
    this.chosenColumns.setValue([]);
    this.filterType.setValue(
      this.filterTypeOptions.find((x) => x.id === type)!
    );
    let d;
    if (element.data().datetime.toMillis)
      d = new Date(element.data().datetime.toMillis());
    else d = new Date(element.data().datetime);
    if (type === 'from') {
      this.toDate.setValue(null);
      this.fromDate.setValue(d);
    } else {
      this.fromDate.setValue(null);
      this.toDate.setValue(d);
    }
    this.submit();
  }

  private _buildFilter(): ColumnDateFilterEvent {
    let queries: ColumnDateQueryFilter[] = [];
    let hasOnlyFilterRowsEnabled = false;
    if (
      this.chosenColumns &&
      this.chosenColumns.value &&
      Array.isArray(this.chosenColumns.value) &&
      this.chosenColumns.value.length
    ) {
      hasOnlyFilterRowsEnabled = true;
      queries.push(
        where(
          'changed_properties',
          'array-contains-any',
          this.chosenColumns.value //.map((x) => x.id)
        )
      );
    }
    if (this.filterType.value) {
      if (
        ['from', 'between'].includes(this.filterType.value.id) &&
        this.fromDate.value
      ) {
        hasOnlyFilterRowsEnabled = false;
        // this.fromDate.setHours(0);
        // this.fromDate.setMinutes(0);
        // this.fromDate.setSeconds(0);
        queries.push(where('datetime', '>=', this.fromDate.value));
      }
      if (
        ['to', 'between'].includes(this.filterType.value.id) &&
        this.toDate.value
      ) {
        hasOnlyFilterRowsEnabled = false;
        // this.toDate.setHours(23);
        // this.toDate.setMinutes(59);
        // this.toDate.setSeconds(59);
        queries.push(where('datetime', '<=', this.toDate.value));
      }
    }
    console.log(queries);
    return { hasOnlyFilterRowsEnabled, queries };
  }
}
