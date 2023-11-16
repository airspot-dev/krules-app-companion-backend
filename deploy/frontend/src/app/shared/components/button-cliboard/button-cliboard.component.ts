import { Component, Input } from '@angular/core';
import { SnackbarService } from 'src/app/service/snackbar/snackbar.service';

@Component({
  selector: 'app-button-cliboard',
  templateUrl: './button-cliboard.component.html',
  styleUrls: ['./button-cliboard.component.scss'],
})
export class ButtonCliboardComponent {
  @Input() text: string = '';
  @Input() hideText: boolean = false;
  @Input() buttonText: string = 'Copy content';
  constructor(private _snackbar: SnackbarService) {}
  copy() {
    const selBox = document.createElement('textarea');
    selBox.style.position = 'fixed';
    selBox.style.left = '0';
    selBox.style.top = '0';
    selBox.style.opacity = '0';
    selBox.value = this.text;
    document.body.appendChild(selBox);
    selBox.focus();
    selBox.select();
    document.execCommand('copy');
    document.body.removeChild(selBox);
    this._snackbar.ok({ message: 'Copied to clipboard' });
  }
}
