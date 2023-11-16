import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-dash-button',
  templateUrl: './dash-button.component.html',
  styleUrls: ['./dash-button.component.scss'],
})
export class DashButtonComponent {
  @Input() title: string = 'Add';
  @Input() icon: string = 'add';
}
