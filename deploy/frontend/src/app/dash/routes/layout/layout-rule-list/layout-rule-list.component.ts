import { Component } from '@angular/core';

@Component({
  selector: 'app-layout-rule-list',
  templateUrl: './layout-rule-list.component.html',
  styleUrls: ['./layout-rule-list.component.scss'],
})
export class LayoutRuleListComponent {
  displayedColumns: string[] = ['type', 'target', 'condition'];
  rapresentations: any[] = [];
}
