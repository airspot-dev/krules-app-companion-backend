import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-data-back-button',
  templateUrl: './data-back-button.component.html',
  styleUrls: ['./data-back-button.component.scss'],
})
export class DataBackButtonComponent {
  @Input() public group: string = '';
}
