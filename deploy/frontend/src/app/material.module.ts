import { NgModule } from '@angular/core';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatCardModule } from '@angular/material/card';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatMenuModule } from '@angular/material/menu';
import { MatTableModule } from '@angular/material/table';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import {
  MatPaginatorIntl,
  MatPaginatorModule,
} from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatSelectModule } from '@angular/material/select';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatDialogModule } from '@angular/material/dialog';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatTreeModule } from '@angular/material/tree';
import { MatRadioModule } from '@angular/material/radio';
import { MatChipsModule } from '@angular/material/chips';
import { DragDropModule } from '@angular/cdk/drag-drop';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatTabsModule } from '@angular/material/tabs';
import {
  NgxMatDatetimePickerModule,
  NgxMatNativeDateModule,
} from '@angular-material-components/datetime-picker';
import { CustomPaginator } from './models/custom-paginator-config';
import { MatStepperModule } from '@angular/material/stepper';
import {MatTooltipModule} from '@angular/material/tooltip';

const modules = [
  NgxMatDatetimePickerModule,
  NgxMatNativeDateModule,
  MatDialogModule,
  DragDropModule,
  MatTabsModule,
  MatTreeModule,
  MatRadioModule,
  MatSnackBarModule,
  MatButtonToggleModule,
  MatFormFieldModule,
  MatCheckboxModule,
  MatChipsModule,
  MatCardModule,
  MatAutocompleteModule,
  MatStepperModule,
  MatInputModule,
  MatButtonModule,
  MatToolbarModule,
  MatIconModule,
  MatSidenavModule,
  MatListModule,
  MatSortModule,
  MatSelectModule,
  MatMenuModule,
  MatTableModule,
  MatPaginatorModule,
  MatProgressSpinnerModule,
  MatGridListModule,
  MatSlideToggleModule,
  MatDatepickerModule,
  MatNativeDateModule,
  MatTooltipModule,
];

@NgModule({
  imports: modules,
  exports: modules,
  providers: [{ provide: MatPaginatorIntl, useValue: CustomPaginator() }],
})
export class MaterialModule {}
