import { COMMA, ENTER, TAB } from '@angular/cdk/keycodes';
import { generate } from 'shortid';
import {
  Component,
  ElementRef,
  EventEmitter,
  Input,
  Output,
  ViewChild,
} from '@angular/core';
import {
  MatAutocompleteSelectedEvent,
  MatAutocompleteModule,
} from '@angular/material/autocomplete';
import { MatChipInputEvent, MatChipsModule } from '@angular/material/chips';
import { Observable, Subject } from 'rxjs';
import { map, startWith, takeUntil } from 'rxjs/operators';
import { MatIconModule } from '@angular/material/icon';
import { NgFor, AsyncPipe } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import {
  QueryCompositeFilterConstraint,
  QueryFieldFilterConstraint,
  WhereFilterOp,
  and,
  documentId,
  or,
  where,
} from '@angular/fire/firestore';
import { FormControl } from '@angular/forms';

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

export type KeyValueQueryFilter =
  | QueryFieldFilterConstraint
  | QueryCompositeFilterConstraint;

@Component({
  selector: 'app-key-value-filter',
  templateUrl: './key-value-filter.component.html',
  styleUrls: ['./key-value-filter.component.scss'],
})
export class KeyValueFilterComponent {
  separatorKeysCodes: number[] = [ENTER, TAB];
  filterCtrl = new FormControl('');
  filteredList!: Observable<Columns[]>;
  private ngUnsubscribe = new Subject<void>();
  @Output() filter = new EventEmitter<KeyValueQueryFilter[]>();
  validOperators: string[] = [
    // '<',
    // '<=',
    '==',
    // '!=',
    // '>=',
    // '>',
    // 'array-contains',
    // 'in',
    // 'array-contains-any',
    // 'not-in',
  ];
  filterTokens: ChipToken[] = [];
  allColumns: Columns[] = [];
  lastColumnsHash: string | null = null;
  idColumn: Columns[] = [
    {
      uid: generate(),
      id: 'id',
      type: 'column',
      displayName: 'ID',
    },
  ];
  operators: Columns[] = [
    {
      uid: generate(),
      id: 'or',
      type: 'operator',
      displayName: 'OR',
    },
    // {
    //   id: 'and',
    //   type: 'operator',
    //   displayName: 'AND',
    // },
  ];
  @ViewChild('filterInput') filterInput:
    | ElementRef<HTMLInputElement>
    | undefined;

  @Input() set columns(value: any[]) {
    if (this.lastColumnsHash === value.map((x) => x.id).join('-')) return;
    this.ngUnsubscribe.next();
    this.ngUnsubscribe.complete();
    this.filterTokens = [];
    this.allColumns = this.idColumn
      .concat(
        value.map((x) => ({
          uid: generate(),
          id: x.id,
          type: 'column',
          displayName: x.data().readable_name,
        }))
      )
      .concat([{ type: 'divider', displayName: '', id: '', uid: '' }])
      .concat(this.operators);
    this._init();
    this.lastColumnsHash = value.map((x) => x.id).join('-');
  }

  constructor() {
    this._init();
  }

  private _init() {
    this.filteredList = this.filterCtrl.valueChanges.pipe(
      startWith(null),
      map((filterStr: string | null) =>
        filterStr && typeof filterStr == 'string'
          ? this._filter(filterStr)
          : this.allColumns.slice()
      ),
      takeUntil(this.ngUnsubscribe)
    );
  }

  private _validateChip(chip: string) {
    if (this._isLogicalOperator(chip)) return true;
    const tokens = chip.split(' ');
    if (tokens.length == 3) {
      const [t1, operator, t2] = tokens.map((x) => x.trim());
      if (t1 !== '' && t2 !== '' && this.validOperators.includes(operator))
        return true;
    }
    return false;
  }

  private _buildFilter(): KeyValueQueryFilter[] {
    console.log('build filter call');
    let queries: KeyValueQueryFilter[] = [];
    let indexMap = this.filterTokens.map((chip, i) =>
      this._isLogicalOperator(chip.token) ? 'operator' : 'column'
    );
    for (let i = 0; i < this.filterTokens.length; i++) {
      // if is a column without logical operator
      if (
        indexMap[i] === 'operator' ||
        (indexMap[i - 1] &&
          indexMap[i - 1] === 'operator' &&
          indexMap[i] === 'column')
      ) {
        continue;
      }
      // if is the first therm of a 'column','operator','column' sequence
      else if (
        indexMap[i] === 'column' &&
        indexMap[i + 1] &&
        indexMap[i + 1] === 'operator' &&
        indexMap[i + 2] &&
        indexMap[i + 2] === 'column'
      ) {
        let [key1, operator1, value1] = this.filterTokens[i].token
          .split(' ')
          .map((x) => x.trim());
        let [key2, operator2, value2] = this.filterTokens[i + 2].token
          .split(' ')
          .map((x) => x.trim());
        let where1, where2;
        if (key1 === 'id')
          where1 = where(documentId(), operator1 as WhereFilterOp, value1);
        else where1 = where(key1, operator1 as WhereFilterOp, value1);
        if (key2 === 'id')
          where2 = where(documentId(), operator2 as WhereFilterOp, value2);
        else where2 = where(key2, operator2 as WhereFilterOp, value2);
        queries.push(or(where1, where2));
        console.log('added or', key1, key2);
      }
      // ignore if is an operator or the is the term after an operator
      else {
        let [key, operator, value] = this.filterTokens[i].token
          .split(' ')
          .map((x) => x.trim());
        if (key === 'id')
          queries.push(where(documentId(), operator as WhereFilterOp, value));
        else queries.push(where(key, operator as WhereFilterOp, value));
        console.log('added column', key);
      }
    }
    return queries;
  }

  add(event: MatChipInputEvent): void {
    if (!this._validateChip(event.value)) return;
    const value = (event.value || '').trim();

    // Add our fruit
    if (value) {
      this.filterTokens.push({
        uid: generate(),
        type: this._isLogicalOperator(value) ? 'operator' : 'column',
        token: value,
      });
    }

    // Clear the input value
    event.chipInput!.clear();

    this.filterCtrl.setValue(null);

    this.filter.emit(this._buildFilter());
  }

  remove(chipUid: string): void {
    const index = this.filterTokens.findIndex((x) => x.uid === chipUid);
    if (index < 0) return;
    this.filterTokens.splice(index, 1);
    this.filter.emit(this._buildFilter());
  }

  private _isLogicalOperator(value: string) {
    return this.operators.map((x) => x.id).indexOf(value) >= 0;
  }

  selected(event: MatAutocompleteSelectedEvent): void {
    let selected = event.option.value.id;
    let isLogicalOperator = this._isLogicalOperator(selected);
    if (isLogicalOperator) {
      this.filterTokens.push({
        uid: generate(),
        type: 'operator',
        token: selected,
      });
      this.filterInput!.nativeElement.value = '';
      this.filterCtrl.setValue(null);
      return;
    }
    let value = `${selected} == `;
    this.filterInput!.nativeElement.value = value;
    this.filterCtrl.setValue(value);
  }

  private _filter(value: string): Columns[] {
    const filterValue = value.toLowerCase();
    const filtered = this.allColumns.filter(
      (column) =>
        column.id.toLowerCase().includes(filterValue) ||
        column.type == 'divider'
    );
    if (filtered.length === 1) return [];
    if (filtered[filtered.length - 1].type === 'divider') {
      filtered.splice(-1);
      return filtered;
    }
    return filtered;
  }
}
