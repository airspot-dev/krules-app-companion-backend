import { AfterViewInit, Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { MatAutocompleteSelectedEvent } from '@angular/material/autocomplete';
import { MatDialog } from '@angular/material/dialog';
import { from, map, Observable, startWith } from 'rxjs';
import { AuthService } from 'src/app/service/auth/auth.service';
import { GroupService } from 'src/app/service/group/group.service';
import { SchemaService } from 'src/app/service/schema/schema.service';
import { DeleteGroupDialogComponent } from './delete-group-dialog/delete-group-dialog.component';
import { ActivatedRoute, Router } from '@angular/router';
import {
  MatTreeFlatDataSource,
  MatTreeFlattener,
} from '@angular/material/tree';
import { FlatTreeControl } from '@angular/cdk/tree';
import { TreeService } from 'src/app/service/tree/tree.service';

interface IAutocompleteOptions {
  id: string;
  name: string;
  description: string;
  _deleting?: boolean;
}

interface ExampleFlatNode {
  expandable: boolean;
  name: string;
  id: string;
  level: number;
}

interface GroupNode {
  name: string;
  id: string;
  children?: GroupNode[];
}

@Component({
  selector: 'app-data-view',
  templateUrl: './data-view.component.html',
  styleUrls: ['./data-view.component.scss'],
})
export class DataViewComponent implements OnInit {
  selectedGroup = new FormControl('');
  groupId: string | null = null;
  group: IAutocompleteOptions | undefined;
  selectionList: any[] = [];
  groups: IAutocompleteOptions[] = [];
  collapsed: boolean = false;
  isLive: boolean = true;
  viewType: 'tree' | 'list' = 'list';
  filteredOptions: Observable<IAutocompleteOptions[]> = from([]);

  treeControl = new FlatTreeControl<ExampleFlatNode>(
    (node) => node.level,
    (node) => node.expandable
  );
  private _transformer = (node: GroupNode, level: number) => {
    return {
      expandable: !!node.children && node.children.length > 0,
      name: node.name,
      id: node.id,
      level: level,
    };
  };

  treeFlattener = new MatTreeFlattener(
    this._transformer,
    (node) => node.level,
    (node) => node.expandable,
    (node) => node.children
  );

  dataSource = new MatTreeFlatDataSource(this.treeControl, this.treeFlattener);

  constructor(
    public dialog: MatDialog,
    private _tree: TreeService,
    private _schema: SchemaService,
    private _route: ActivatedRoute,
    private _router: Router
  ) {}

  hasChild = (_: number, node: ExampleFlatNode) => node.expandable;

  openDialog(): void {
    this.dialog.open(DeleteGroupDialogComponent, {
      width: '600px',
      exitAnimationDuration: '300ms',
      enterAnimationDuration: '300ms',
      data: { group: this.group },
    });
  }

  updateGroupByList(element: any) {
    const group = element[0];
    this.selectedGroup.setValue(group);
    // this.selectedGroup.reset();
    this.groupId = group;
    this.group = this.groups.find((x) => x.id === this.groupId);
  }

  updateGroupByAutocomplete({
    option: { value },
  }: MatAutocompleteSelectedEvent) {
    this.selectionList = [value];
    this.updateGroupByList(this.selectionList);
  }

  clickNode(id: string) {
    this.updateGroupByAutocomplete({
      option: { value: id },
    } as MatAutocompleteSelectedEvent);
  }

  private _getFirstGroupId(
    groups: IAutocompleteOptions[],
    startupGroupIdFromQuery: string | null
  ) {
    // check if startupGroupIdFromQuery is elegible
    if (startupGroupIdFromQuery) {
      const g = groups.find((x) => x.id);
      if (!g?._deleting) return startupGroupIdFromQuery;
    }
    const filtered = groups.filter((x) => !x._deleting);
    return startupGroupIdFromQuery || filtered.length ? filtered[0].id : null;
  }

  ngOnInit() {
    const startupGroupId = this._route.snapshot.queryParamMap.get('group-id');

    this._schema.getAllReactive().subscribe((groups) => {
      this.groups = groups.map((x) => ({
        id: x['id'],
        name: x['readable_name'] || x['id'],
        description: x['description'] || '',
        _deleting: x['_deleting'],
      }));
      const tree = this._tree.convertStringDelimitedGroupToTree(
        this.groups.filter((x) => !x._deleting).map((x) => x.id),
        '.'
      );
      this.dataSource.data = tree;
      // first group id
      let firstGroup = this._getFirstGroupId(this.groups, startupGroupId);
      // check if group is deleting
      if (startupGroupId || this.groups.length) {
        this.updateGroupByAutocomplete({
          option: { value: firstGroup },
        } as MatAutocompleteSelectedEvent);
      }
    });
    this.filteredOptions = this.selectedGroup.valueChanges.pipe(
      // startWith(),
      map((value) => this._filter(value || ''))
    );
    const params = { ...this._route.snapshot.queryParams };
    delete params['group-id'];
    this._router.navigate([], {
      queryParams: {
        'group-id': null,
      },
      queryParamsHandling: 'merge',
    });
  }

  // filter values for group autocomplete
  private _filter(value: string): IAutocompleteOptions[] {
    const filterValue = value.toLowerCase();
    return this.groups.filter(
      (option) =>
        !option._deleting &&
        (option.id.toLowerCase().includes(filterValue) ||
          option.name.toLowerCase().includes(filterValue) ||
          (option.description &&
            option.description.toLowerCase().includes(filterValue)))
    );
  }

  editGroup() {
    return `/data/group/edit/${this.groupId}`;
  }
}
