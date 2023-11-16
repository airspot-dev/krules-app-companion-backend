import { Injectable } from '@angular/core';
import { OkSnackbarComponent } from 'src/app/shared/components/ok-snackbar/ok-snackbar.component';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ErrorSnackbarComponent } from 'src/app/shared/components/error-snackbar/error-snackbar.component';

export interface SnackbarOptions {
  message?: string;
}

@Injectable({
  providedIn: 'root',
})
export class SnackbarService {
  constructor(private _snackBar: MatSnackBar) {}

  ok(options: SnackbarOptions = {}) {
    this._snackBar.openFromComponent(OkSnackbarComponent, {
      duration: 2000,
      horizontalPosition: 'left',
      panelClass: 'ok',
      data: {
        message: options.message,
      },
    });
  }
  warn(options: SnackbarOptions = {}) {
    this._snackBar.openFromComponent(OkSnackbarComponent, {
      duration: 3000,
      horizontalPosition: 'left',
      panelClass: 'warn',
    });
  }
  error(options: SnackbarOptions = {}) {
    if (options.message) console.error(options.message);
    this._snackBar.openFromComponent(ErrorSnackbarComponent, {
      duration: 5000,
      horizontalPosition: 'left',
      panelClass: 'error',
    });
  }
}
