import { Component, Inject, Input, inject } from '@angular/core';
import {
  MAT_SNACK_BAR_DATA,
  MatSnackBarRef,
} from '@angular/material/snack-bar';

@Component({
  selector: 'app-ok-snackbar',
  templateUrl: './ok-snackbar.component.html',
  styleUrls: ['./ok-snackbar.component.scss'],
})
export class OkSnackbarComponent {
  @Input()
  message: string = 'Operation successful!';
  snackBarRef = inject(MatSnackBarRef);
  constructor(@Inject(MAT_SNACK_BAR_DATA) public data: any) {
    if (data.message) this.message = data.message;
  }
}
