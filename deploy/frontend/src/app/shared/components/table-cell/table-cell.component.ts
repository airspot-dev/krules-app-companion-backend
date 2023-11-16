import { AfterViewInit, Component, ContentChild, Input } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { TableCellDialogComponent } from './table-cell-dialog/table-cell-dialog.component';

@Component({
  selector: 'app-table-cell',
  templateUrl: './table-cell.component.html',
  styleUrls: ['./table-cell.component.scss'],
})
export class TableCellComponent implements AfterViewInit {
  public maxWidth = 20;
  private _text: string = '';
  @Input() highlight: boolean = false;
  @Input() highlightAccent: boolean = false;
  @Input() set text(value: string) {
    this._text = value;
  }
  constructor(public dialog: MatDialog) {}
  get text() {
    return this._text;
  }

  openDialog() {
    const dialogRef = this.dialog.open(TableCellDialogComponent, {
      data: { text: this.text },
    });

    dialogRef.afterClosed().subscribe((result) => {
      console.log(`Dialog result: ${result}`);
    });
  }

  ngAfterViewInit(): void {}
}
